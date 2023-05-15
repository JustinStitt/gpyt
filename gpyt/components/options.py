from textual.app import ComposeResult
from textual.containers import Container

from .option_checkbox import OptionCheckbox


class Options(Container):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = app

    def compose(self) -> ComposeResult:
        self.border_title = "Options"
        self.border_subtitle = "Use Space to Toggle"
        self.use_free = OptionCheckbox(
            setting="use_free_gpt", text="Use Free Model (experimental)", app=self._app
        )
        yield self.use_free
