from textual.widgets import ListView
from .conversation_option import StartNewConversationOption, ConversationOption


class VimLikeListView(ListView):
    BINDINGS = [("j", "cursor_down", "Cursor Down"), ("k", "cursor_up", "Cursor Up")]

    def action_select_cursor(self) -> None:
        selected = self.highlighted_child

        assert isinstance(selected, StartNewConversationOption) or isinstance(
            selected, ConversationOption
        ), f"Invalid selection type {type(selected)}"

        selected.select()

    def on_focus(self, _) -> None:
        if self.parent and self.parent.has_class("hidden"):
            user_input = self.app.query_one("#user-input")
            self.app.set_focus(user_input)
