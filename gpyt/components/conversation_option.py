from textual.widgets import Label, ListItem
from textual.app import ComposeResult
from ..conversation import Conversation


class StartNewConversationOption(ListItem):
    def __init__(self, app):
        super().__init__()
        self._app = app

    def compose(self) -> ComposeResult:
        yield Label("<-- Start a new conversation -->", id="new-convo-option")

    def watch_highlighted(self, value: bool) -> None:
        super().watch_highlighted(value)
        if value:
            self.add_class("highlighted")
        else:
            self.remove_class("highlighted")

    def select(self) -> None:
        self._app.start_new_conversation()


class ConversationOption(ListItem):
    ELLIPSIFY_CUTOFF = 35

    def __init__(self, conversation: Conversation, app):
        super().__init__()
        self.conversation = conversation
        self._app = app

    def compose(self) -> ComposeResult:
        yield Label(self._ellipsify_long_summary(self.conversation.summary))

    def _ellipsify_long_summary(self, summary: str) -> str:
        if len(summary) < ConversationOption.ELLIPSIFY_CUTOFF:
            return summary

        summary = summary[: ConversationOption.ELLIPSIFY_CUTOFF - 2] + "..."
        return summary

    def select(self) -> None:
        self._app.on_select_previous_conversation(self.conversation)
        # app.assistant_responses.setup_from_presaved_conversation(self.conversation)
