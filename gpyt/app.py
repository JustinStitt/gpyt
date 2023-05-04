import json
from typing import Generator, Callable
import os
from pathlib import Path


from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Label, Markdown, Static

from gpyt import API_KEY, ARGS, INTRO, MODEL, PROMPT, SUMMARY_PROMPT

from .assistant import Assistant
from .conversation import Conversation, Message
from .id import get_id


class UserInput(Static):
    """
    User-facing input box

    Handles special keywords by mapping to callbacks handling special behavior

    save -> save the current conversation to disk
    """

    def __init__(self):
        super().__init__()
        self.keyword_mappings: dict[str, Callable] = {
            "save": app.save_active_conversation_to_disk
        }

    def compose(self) -> ComposeResult:
        yield Label(f"🤖: {INTRO}", id="help-text")
        yield Input(placeholder="How far away is the Sun?", id="user-input")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_input = event.input.value
        event.input.value = ""

        # empty queries are useless
        if len(user_input) < 1:
            return

        keyword_callback = self.keyword_mappings.get(user_input.strip().lower(), None)
        if keyword_callback:
            keyword_callback()
            return  # don't give anything to the assistant if we use a special callback

        app.fetch_assistant_response(user_input)


class AssistantResponse(Static):
    """Each User/Assistant interaction"""

    def __init__(self, question: str = "", id: str = ""):
        super().__init__()
        self.question = question
        self._id = id
        self.response_view = Markdown()

    def compose(self) -> ComposeResult:
        self.user_question = Label(f"😀: {self.question}", classes="convo")
        yield self.user_question
        yield Label("🤖:", classes="convo")
        container = Container(self.response_view, id="response-container")
        container.border_subtitle = f"message-id: 0x{self._id}"
        yield container

    @work()
    def update_response(self, content: str) -> None:
        app.call_from_thread(self.response_view.update, content)


class AssistantResponses(Static):
    """Container for individual AssistantResponse widgets"""

    def compose(self) -> ComposeResult:
        self.container = ScrollableContainer()

        yield self.container

    @work()
    def add_response(self, stream: Generator, message: Message) -> None:
        new_response = AssistantResponse(question=message.content, id=message.id)
        app.call_from_thread(self.container.mount, new_response)
        app.call_from_thread(new_response.scroll_visible)
        markdown = ""
        update_frequency = 10
        i = 0
        for data in stream:
            i += 1
            try:  # HACK: should check for attr, not try/except
                markdown = markdown + data["choices"][0]["delta"]["content"]
                if i % update_frequency == 0:
                    app.call_from_thread(new_response.update_response, markdown)
                    app.call_from_thread(self.container.scroll_end)
            except:
                continue

        app.call_from_thread(new_response.update_response, markdown)
        # app.call_from_thread(self.container.scroll_page_up)
        app.call_from_thread(
            new_response.user_question.scroll_visible, duration=2, easing="out_back"
        )
        app.assistant.log_assistant_response(markdown)
        assistant_message = Message(id=get_id(), role="assistant", content=markdown)
        assert app.active_conversation, "No active conversation during log write"
        app.active_conversation.log.append(assistant_message)


class AssistantApp(App):
    """Base app for all user->assistant interactions"""

    BINDINGS = [("ctrl+b", "toggle_dark", "Toggle Dark Mode")]

    CSS_PATH = "styles.cssx"

    def __init__(self, assistant: Assistant):
        super().__init__()
        self.assistant = assistant
        self.conversations: list[Conversation] = []
        self.active_conversation: Conversation | None = None

    def compose(self) -> ComposeResult:
        header = Header(show_clock=True)
        header.tall = False
        yield header
        yield Footer()
        self.assistant_responses = AssistantResponses()
        self.assistant_responses.border_title = f"Conversation History{self.active_conversation.summary if self.active_conversation else ''}"
        user_input = UserInput()
        user_input.border_subtitle = "Press Enter To Submit"
        yield user_input
        yield self.assistant_responses

    def save_active_conversation_to_disk(self) -> str:
        """Save the active conversation to disk and return the file path"""
        return self.save_conversation_to_disk()

    def save_conversation_to_disk(
        self, conversation: Conversation | None = None
    ) -> str:
        """
        Save conversation to disk and return the file path.
        Will use active conversation if no conversation is given.
        """
        if not conversation:
            assert (
                self.active_conversation
            ), "When not supplied a conversation to save to disk, there must be an active conversation!"
            conversation = self.active_conversation

        GPT_CACHE_DIR = os.getenv("GPT_CACHE_DIR")
        HOME_DIR = os.getenv("HOME")

        if not GPT_CACHE_DIR:
            # if no GPT_CACHE_DIR env provided, default to $HOME... ensure it exists!
            assert HOME_DIR, "Missing $HOME env var"

        conversations_path = Path(
            GPT_CACHE_DIR if GPT_CACHE_DIR else HOME_DIR,  # type: ignore
            ".cache",
            "gpyt",
            "conversations",
        )
        print(f"{conversations_path = }")
        os.makedirs(conversations_path, exist_ok=True)

        path = Path(conversations_path, f"convo-{conversation.id}.json")
        with open(path, "w") as fd:
            json.dump(conversation.dict(), fd)

        return str(path)

    def _setup_fresh_convo(self, initial_user_input: str) -> None:
        summary = self.assistant.get_conversation_summary(initial_user_input)
        new_convo = Conversation(id=get_id(), summary=summary, log=[])
        self.assistant_responses.border_title = (
            f"Conversation History - {new_convo.summary}"
        )
        self.conversations.append(new_convo)
        self.active_conversation = new_convo
        self.assistant_responses.border_subtitle = f"convo-id: 0x{new_convo.id}"

    @work()
    def fetch_assistant_response(self, user_input: str) -> None:
        if self.active_conversation is None:
            self._setup_fresh_convo(user_input)

        assert self.active_conversation, "No active conversation during log write"
        user_message = Message(id=get_id(), role="user", content=user_input)
        self.active_conversation.log.append(user_message)

        assistant_response_stream = self.assistant.get_response_stream(user_input)

        app.call_from_thread(
            self.assistant_responses.add_response,
            message=user_message,
            stream=assistant_response_stream,
        )

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark


class gpyt(AssistantApp):
    """Used strictly for the purposes of renaming the Header widget."""

    def __init__(self, assistant: Assistant):
        super().__init__(assistant=assistant)


def main():
    app.run()


gpt = Assistant(api_key=API_KEY or "", model=MODEL, prompt=PROMPT)
app = gpyt(assistant=gpt)

if __name__ == "__main__":
    main()
