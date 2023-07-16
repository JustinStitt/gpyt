import asyncio
import os
import signal
import subprocess
from contextlib import contextmanager, redirect_stdout, redirect_stderr
import tempfile
from typing import Callable, Iterator

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Input, Label

from ..config import INTRO


class UserInput(Container):
    """
    User-facing input box

    Handles special keywords by mapping to callbacks handling special behavior

    save -> save the current conversation to disk
    """

    BINDINGS = []

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

    @contextmanager
    def open_external_editor(self) -> Iterator[None]:
        driver = self._app._driver
        if driver is None:
            exit(1)

        driver.stop_application_mode()
        user_input = ""
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
            tf.close()
            # Open the temporary file with env-set editor
            # proc = await asyncio.create_subprocess_exec(
            #     os.getenv("EDITOR") or "vi", tf.name
            # )

            # await proc.wait()

            subprocess.run([os.getenv("EDITOR") or "vi", tf.name])
            # Read the file again after the user has finished editing
            with open(tf.name, "r") as f:
                user_input = f.read()

            # remove the temporary file
            os.unlink(tf.name)

        driver.start_application_mode()
        # self._app.refresh()
        self._app.fetch_assistant_response(user_input)

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
