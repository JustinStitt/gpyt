from assistant import Assistant
from gpyt import API_KEY, ARGS, INTRO, MODEL, PROMPT

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    LoadingIndicator,
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
        # await self.run_action(f"app.action_fetch_assistant_response('{user_input}')")
        await app.fetch_assistant_response(user_input)


class AssistantResponse(Static):
    """
    Each User/Assistant interaction

    is_dummy indicates that this widget is soon to be removed from the dom
    and is being used purely for the loading indicator while awaiting assistant
    response.
    """

    def __init__(self, markdown: str = "", question: str = "", is_dummy=False):
        super().__init__()
        self.markdown = markdown
        self.question = question
        self.loading_indicator = LoadingIndicator() if is_dummy else Label()

    def compose(self) -> ComposeResult:
        yield Label(f"😀: {self.question}", classes="convo")
        yield Label("🤖:", classes="convo")
        response_view = Markdown(self.markdown)
        container = Container(
            response_view, self.loading_indicator, id="response-container"
        )
        container.border_subtitle = "message-id: 0x18239123"
        yield container


class AssistantResponses(Static):
    """Container for individual AssistantResponse widgets"""

    def compose(self) -> ComposeResult:
        self.container = ScrollableContainer()

        yield self.container

    def add_response(
        self, markdown: str, question: str, dummy_response: AssistantResponse
    ) -> None:
        new_response = AssistantResponse(markdown=markdown, question=question)
        self.container.mount(new_response)
        dummy_response.remove()
        new_response.scroll_visible()


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

    async def fetch_assistant_response(self, user_input: str) -> None:
        dummy_assistant_response = AssistantResponse(question=user_input, is_dummy=True)
        self.assistant_responses.container.mount(dummy_assistant_response)
        dummy_assistant_response.scroll_visible()
        assistant_response_markdown = await self.assistant.get_response(user_input)
        self.assistant_responses.add_response(
            markdown=assistant_response_markdown,
            question=user_input,
            dummy_response=dummy_assistant_response,
        )

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark


class gpyt(AssistantApp):
    """Used strictly for the purposes of renaming the Header widget."""

    def __init__(self, assistant: Assistant):
        super().__init__(assistant=assistant)


if __name__ == "__main__":
    gpt = Assistant(api_key=API_KEY or "", model=MODEL, prompt=PROMPT)
    app = gpyt(assistant=gpt)
    app.run()
