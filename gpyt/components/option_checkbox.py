from textual.widgets import Checkbox


class OptionCheckbox(Checkbox):
    def __init__(self, app, setting: str, text: str, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self._app = app

        self.setting = setting
        self._assign_default_state()

    def _assign_default_state(self) -> None:
        if hasattr(self.app, self.setting):
            current_setting_state = self.app.__dict__[self.setting]
            self.value = current_setting_state

    def on_checkbox_changed(self) -> None:
        if hasattr(self.app, self.setting):
            self.app.__dict__[self.setting] = self.value
            if self.setting == "use_free_gpt":
                self._app.user_input.border_title = (
                    "🌐 Internet Enabled" if self.value else ""
                )
