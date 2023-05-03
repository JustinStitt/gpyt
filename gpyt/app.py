from .assistant import Assistant
from gpyt import API_KEY, ARGS, INTRO, MODEL, PROMPT
from typing import Generator

from textual import work
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    Markdown,
    Static,
    Label,
    Input,
)


class UserInput(Static):
    """User-facing input box"""

    def compose(self) -> ComposeResult:
        yield Label(f"🤖: {INTRO}", id="help-text")
        yield Input(placeholder="How far away is the Sun?", id="user-input")
        # yield Button("Submit", variant="success", id="submit")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_input = event.input.value
        event.input.value = ""
        app.fetch_assistant_response(user_input)


class AssistantResponse(Static):
    """
    Each User/Assistant interaction
    """

    def __init__(self, question: str = ""):
        super().__init__()
        self.question = question
        self.response_view = Markdown()

    def compose(self) -> ComposeResult:
        self.user_question = Label(f"😀: {self.question}", classes="convo")
        yield self.user_question
        yield Label("🤖:", classes="convo")
        container = Container(self.response_view, id="response-container")
        container.border_subtitle = "message-id: 0x18239123"
        yield container

    @work()
    def update_response(self, content: str) -> None:
        app.call_from_thread(self.response_view.update, content)
        # self.response_view.update(content)


class AssistantResponses(Static):
    """Container for individual AssistantResponse widgets"""

    def compose(self) -> ComposeResult:
        self.container = ScrollableContainer()

        yield self.container

    @work()
    def add_response(self, stream: Generator, question: str) -> None:
        new_response = AssistantResponse(question=question)
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
        print("scrolling up")


class AssistantApp(App):
    """Base app for all user->assistant interactions"""

    BINDINGS = [("ctrl+b", "toggle_dark", "Toggle Dark Mode")]

    CSS_PATH = "styles.cssx"

    def __init__(self, assistant: Assistant):
        super().__init__()
        self.assistant = assistant

    def compose(self) -> ComposeResult:
        header = Header(show_clock=True)
        header.tall = False
        yield header
        yield Footer()
        self.assistant_responses = AssistantResponses()
        self.assistant_responses.border_title = "Conversation History"
        user_input = UserInput()
        user_input.border_subtitle = "Press Enter To Submit"
        # yield ScrollableContainer(user_input, assistant_responses)
        yield user_input
        yield self.assistant_responses

    def test(self, x: int) -> int:
        return x + 4

    @work()
    def fetch_assistant_response(self, user_input: str) -> None:
        # self.run_worker(self.assistant.get_response_stream(user_input))
        assistant_response_stream = self.assistant.get_response_stream(user_input)

        app.call_from_thread(
            self.assistant_responses.add_response,
            question=user_input,
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
