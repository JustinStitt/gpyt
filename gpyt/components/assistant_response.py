import pyperclip
from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Markdown, Static


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
        self.app.call_from_thread(self.response_view.update, content)
        self._last_content = content
