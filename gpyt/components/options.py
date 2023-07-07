from textual.app import ComposeResult
from textual.widgets import RadioButton, RadioSet


class Options(RadioSet):
    BINDINGS = [
        ("j", "next_button", "Cursor Down"),
        ("k", "previous_button", "Cursor Up"),
    ]

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = app

    def compose(self) -> ComposeResult:
        self.border_title = "Options"
        self.border_subtitle = "Use Space to Select"

        self.use_default = RadioButton(
            "Use GPT 3.5 (paid, default)", id="use_default_model"
        )
        self.use_free = RadioButton("Use Free Model (experimental)", id="use_free_gpt")
        self.use_palm = RadioButton("Use PaLM 2 (Google)", id="use_palm")
        self.use_gpt4 = RadioButton("Use GPT4 (Access Required)", id="use_gpt4")

        yield self.use_default
        yield self.use_free
        yield self.use_palm
        yield self.use_gpt4

    def on_radio_set_changed(self, event):
        option = event.pressed.id
        if "use" in option:
            self._app.use_free_gpt = False
            self._app.use_default_model = False
            self._app.use_palm = False
            self._app.use_gpt4 = False

        if hasattr(self._app, option):
            self._app.__dict__[option] = True
            self._app.adjust_model_border_title()
