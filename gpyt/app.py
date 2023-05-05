import json
import os
import pyperclip
from pathlib import Path
from typing import Callable, Generator
from rich.style import Style

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    Static,
)

from gpyt import API_KEY, INTRO, MODEL, PROMPT

from .assistant import Assistant
from .conversation import Conversation, Message
from .id import get_id


class UserInput(Container):
    """
    User-facing input box

    Handles special keywords by mapping to callbacks handling special behavior

    save -> save the current conversation to disk
    """

    def __init__(self):
        super().__init__()
        self.keyword_mappings: dict[str, Callable] = {
            # "save": app.save_active_conversation_to_disk,
            "new": app.start_new_conversation,
            "clear": app.start_new_conversation,
        }

    def compose(self) -> ComposeResult:
        yield Label(f"🤖: {INTRO}", id="help-text")
        self.inp = Input(placeholder="How far away is the Sun?", id="user-input")
        self.inp.focus()
        yield self.inp

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


class ConversationOption(ListItem):
    ELLIPSIFY_CUTOFF = 35

    def __init__(self, conversation: Conversation):
        super().__init__()
        self.conversation = conversation

    def compose(self) -> ComposeResult:
        yield Label(self._ellipsify_long_summary(self.conversation.summary))

    def _ellipsify_long_summary(self, summary: str) -> str:
        if len(summary) < ConversationOption.ELLIPSIFY_CUTOFF:
            return summary

        summary = summary[: ConversationOption.ELLIPSIFY_CUTOFF - 2] + "..."
        return summary

    def select(self) -> None:
        # app.assistant_responses.setup_from_presaved_conversation(self.conversation)
        app.on_select_previous_conversation(self.conversation)


class StartNewConversationOption(ListItem):
    def compose(self) -> ComposeResult:
        yield Label("<-- Start a new conversation -->", id="new-convo-option")

    def watch_highlighted(self, value: bool) -> None:
        super().watch_highlighted(value)
        if value:
            self.add_class("highlighted")
        else:
            self.remove_class("highlighted")

    def select(self) -> None:
        app.start_new_conversation()


class VimLikeListView(ListView):
    BINDINGS = [("j", "cursor_down", "Cursor Down"), ("k", "cursor_up", "Cursor Up")]

    def action_select_cursor(self) -> None:
        selected = self.highlighted_child

        assert isinstance(selected, StartNewConversationOption) or isinstance(
            selected, ConversationOption
        ), "Invalid selection type"

        selected.select()

    def on_focus(self, event) -> None:
        if app.past_conversations.has_class("hidden"):
            user_input = app.query_one("#user-input")
            app.set_focus(user_input)


class PastConversations(Container):
    def compose(self) -> ComposeResult:
        self.start_new_conversation_option = StartNewConversationOption()
        self.options = VimLikeListView(self.start_new_conversation_option)
        yield self.options

    def add_conversation_option(self, conversation: Conversation) -> None:
        option = ConversationOption(conversation)
        self.options.mount(option, before=1)


class AssistantResponse(Static):
    """Each User/Assistant interaction"""

    def __init__(self, question: str = "", id: str = ""):
        super().__init__()
        self.question = question
        self._id = id
        self.response_view = Markdown()
        self._last_content = ""

    def compose(self) -> ComposeResult:
        self.user_question = Label(f"😀: {self.question}", classes="convo")
        yield self.user_question
        yield Label("🤖:", classes="convo")
        container = Container(self.response_view, id="response-container")
        container.border_subtitle = f"message-id: 0x{self._id}"
        yield container

    def on_click(self) -> None:
        pyperclip.copy(self._last_content)

    @work()
    def update_response(self, content: str) -> None:
        app.call_from_thread(self.response_view.update, content)
        self._last_content = content


class AssistantResponses(Static):
    """Container for individual AssistantResponse widgets"""

    def __init__(self):
        super().__init__()
        self.container = ScrollableContainer()

    def compose(self) -> ComposeResult:
        yield self.container

    def setup_from_presaved_conversation(self, conversation: Conversation) -> None:
        """Load conversation into conversation history widget from Conversation model"""

        app.active_conversation = conversation
        app._set_summary_title_id(conversation.summary, conversation.id)
        new_history = []

        all_user_messages = [m for m in conversation.log if m.role == "user"]
        all_assistant_messages = [m for m in conversation.log if m.role == "assistant"]

        for user_message, assistant_response in zip(
            all_user_messages, all_assistant_messages
        ):
            assert (
                user_message.role == "user"
            ), "Improper role for setup from presaved convesation"

            new_response = AssistantResponse(
                question=user_message.content, id=user_message.id
            )
            self.container.mount(new_response)
            assert (
                assistant_response.role == "assistant"
            ), "Improper role for setup from presaved convesation"
            new_response.update_response(assistant_response.content)
            new_history.append({"role": "user", "content": user_message.content})
            new_history.append(
                {"role": "assistant", "content": assistant_response.content}
            )

        app.assistant.set_history(new_history)
        app.past_conversations.add_class("hidden")
        app.focus_user_input()

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

        app.call_from_thread(app.save_active_conversation_to_disk)


class AssistantApp(App):
    """Base app for all user->assistant interactions"""

    BINDINGS = [
        ("ctrl+b", "toggle_dark", "Toggle Dark Mode"),
        ("ctrl+n", "toggle_sidebar", "Past Conversations"),
        ("ctrl+c", "handle_exit", "Quit"),
        ("up", "scroll_convo_up", "Scroll Up Convo"),
        ("down", "scroll_convo_down", "Scroll Down Convo"),
    ]

    CSS_PATH = "styles.cssx"

    def __init__(self, assistant: Assistant):
        super().__init__()
        self.assistant = assistant
        self.conversations: list[Conversation] = []
        self.active_conversation: Conversation | None = None
        self._convo_ids_added: set[str] = set()

    def compose(self) -> ComposeResult:
        header = Header(show_clock=True)
        header.tall = False
        yield header
        yield Footer()
        self.assistant_responses = AssistantResponses()
        self.assistant_responses.border_title = "Conversation History"

        user_input = UserInput()
        user_input.border_subtitle = "Press Enter To Submit"
        yield user_input
        yield self.assistant_responses
        self.past_conversations = PastConversations(classes="hidden")
        self.past_conversations.border_title = "Past Conversations"
        yield self.past_conversations

    def get_saved_conversations_path(self) -> Path:
        """Return the path where conversations are to be saved/loaded from"""
        GPT_CACHE_DIR = os.getenv("GPT_CACHE_DIR")
        HOME_DIR = os.getenv("HOME")

        if not GPT_CACHE_DIR:
            # if no GPT_CACHE_DIR env provided, default to $HOME... ensure it exists!
            assert HOME_DIR, "Missing $HOME env var"

        return Path(
            GPT_CACHE_DIR if GPT_CACHE_DIR else HOME_DIR,  # type: ignore
            ".cache",
            "gpyt",
            "conversations",
        )

    def load_saved_conversations(self) -> None:
        """Load conversations from saved conversation path"""
        conversations_path = self.get_saved_conversations_path()
        conversation_file_paths = conversations_path.glob(pattern=r"*.json")
        conversation_file_paths = sorted(
            conversation_file_paths, key=lambda f: f.stat().st_mtime
        )

        for path in conversation_file_paths:
            with open(path, "r") as fd:
                raw_json = json.load(fd)
                conversation = Conversation.parse_obj(raw_json)
                self.conversations.append(conversation)
                self._convo_ids_added.add(conversation.id)
                self.past_conversations.add_conversation_option(conversation)

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
        print("SAVING: ", conversation.id)

        conversations_path = self.get_saved_conversations_path()

        os.makedirs(conversations_path, exist_ok=True)

        path = Path(conversations_path, f"convo-{conversation.id}.json")
        with open(path, "w") as fd:
            json.dump(conversation.dict(), fd)

        self._add_active_as_option()

        return str(path)

    def _set_summary_title_id(self, summary: str, id: str) -> None:
        self.assistant_responses.border_title = f"Conversation History - {summary}"
        self.assistant_responses.border_subtitle = f"convo-id: 0x{id}"

    def _setup_fresh_convo(self, initial_user_input: str) -> None:
        summary = self.assistant.get_conversation_summary(initial_user_input)
        new_convo = Conversation(id=get_id(), summary=summary, log=[])
        self._set_summary_title_id(summary, new_convo.id)
        self.conversations.append(new_convo)
        self.active_conversation = new_convo

    def clear_active_conversation(self) -> None:
        self.assistant_responses.remove()
        self.assistant_responses = AssistantResponses()
        self.mount(self.assistant_responses)
        self.assistant_responses.border_title = "Conversation History"

    def _add_active_as_option(self) -> None:
        if not self.active_conversation:
            return
        exists_already = Path(
            self.get_saved_conversations_path(),
            f"convo-{self.active_conversation.id}.json",
        ).exists()

        if exists_already and self.active_conversation.id not in self._convo_ids_added:
            self.past_conversations.add_conversation_option(self.active_conversation)

        self._convo_ids_added.add(self.active_conversation.id)

    def start_new_conversation(self, add_option: bool = True) -> None:
        """Save current conversation, clear it, start a new fresh one"""
        if not self.active_conversation:
            return

        self.save_active_conversation_to_disk()
        if add_option:
            self._add_active_as_option()
        self.clear_active_conversation()
        self.active_conversation = None
        self.action_toggle_sidebar()

    @work()
    def fetch_assistant_response(self, user_input: str) -> None:
        if self.active_conversation is None:
            self._setup_fresh_convo(user_input)

        assert self.active_conversation, "No active conversation during log write"
        user_message = Message(id=get_id(), role="user", content=user_input)
        self.active_conversation.log.append(user_message)

        try:
            assistant_response_stream = self.assistant.get_response_stream(user_input)
        except:
            assistant_response_stream = self.assistant.error_fallback_message

        app.call_from_thread(
            self.assistant_responses.add_response,
            message=user_message,
            stream=assistant_response_stream,
        )

    def on_select_previous_conversation(self, conversation: Conversation) -> None:
        self.start_new_conversation(add_option=False)
        self.assistant_responses.setup_from_presaved_conversation(conversation)
        self.assistant_responses.container.scroll_end(duration=2.0, easing="in_quart")

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_toggle_sidebar(self) -> None:
        if not self.past_conversations.has_class("opened-gt-once"):
            try:
                self.load_saved_conversations()
            except:
                self.past_conversations.add_conversation_option(
                    Conversation(
                        summary=f"Failed to load conversations from {self.get_saved_conversations_path()}",
                        id="-1",
                        log=[],
                    )
                )
        self.past_conversations.add_class("opened-gt-once")
        self.past_conversations.toggle_class("hidden")
        if self.past_conversations.has_class("hidden"):
            app.focus_user_input()
            return
        self.set_focus(self.past_conversations.options)

    def focus_user_input(self) -> None:
        inp = self.query_one("#user-input")
        inp.focus()

    def action_handle_exit(self) -> None:
        exit()

    def action_scroll_convo_up(self) -> None:
        self.assistant_responses.container.scroll_relative(y=-4)

    def action_scroll_convo_down(self) -> None:
        self.assistant_responses.container.scroll_relative(y=4)


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
