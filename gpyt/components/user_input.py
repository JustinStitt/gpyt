from typing import Callable

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input, Label

from ..config import INTRO


class UserInput(Container):
    """
    User-facing input box

    Handles special keywords by mapping to callbacks handling special behavior

    save -> save the current conversation to disk
    """

    def __init__(self, app):
        super().__init__()
        self._app = app
        self.keyword_mappings: dict[str, Callable] = {
            # "save": app.save_active_conversation_to_disk,
            "new": self._app.start_new_conversation,
            "clear": self._app.start_new_conversation,
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

        self._app.fetch_assistant_response(user_input)
