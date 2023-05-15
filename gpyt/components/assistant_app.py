import json
import os
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


from gpyt.free_assistant import FreeAssistant
from ..args import USE_EXPERIMENTAL_FREE_MODEL
from ..assistant import Assistant
from ..conversation import Conversation, Message
from ..id import get_id
from .assistant_responses import AssistantResponses
from .options import Options
from .past_conversations import PastConversations
from .user_input import UserInput


class AssistantApp(App):

    """Base app for all user->assistant interactions"""

    BINDINGS = [
        ("ctrl+b", "toggle_dark", "Toggle Dark Mode"),
        ("ctrl+n", "toggle_sidebar", "Past Conversations"),
        ("ctrl+c", "handle_exit", "Quit"),
        ("up", "scroll_convo_up", "Scroll Up Convo"),
        ("down", "scroll_convo_down", "Scroll Down Convo"),
        ("ctrl+o", "toggle_settings", "Settings"),
    ]

    CSS_PATH = "styles.cssx"

    def __init__(self, assistant: Assistant, free_assistant: FreeAssistant):
        super().__init__()
        self.assistant = assistant
        self._free_assistant = free_assistant
        self.conversations: list[Conversation] = []
        self.active_conversation: Conversation | None = None
        self._convo_ids_added: set[str] = set()
        self.use_free_gpt = USE_EXPERIMENTAL_FREE_MODEL

    def _get_assistant(self) -> Assistant | FreeAssistant:
        return self.assistant if not self.use_free_gpt else self._free_assistant

    def compose(self) -> ComposeResult:
        header = Header(show_clock=True)
        header.tall = False
        yield header
        yield Footer()
        self.assistant_responses = AssistantResponses(app=self)
        self.assistant_responses.border_title = "Conversation History"

        self.user_input = UserInput(app=self)
        self.user_input.border_subtitle = "Press Enter To Submit"
        yield self.user_input
        yield self.assistant_responses
        self.past_conversations = PastConversations(classes="hidden", app=self)
        self.past_conversations.border_title = "Past Conversations"
        self.past_conversations.border_subtitle = "Press Enter to Select"
        yield self.past_conversations
        yield Options(classes="hidden", app=self)

    def get_saved_conversations_path(self) -> Path:
        """Return the path where conversations are to be saved/loaded from"""
        GPT_CACHE_DIR = os.getenv("GPT_CACHE_DIR")
        HOME_DIR = os.getenv("HOME")

        if not GPT_CACHE_DIR:
            # if no GPT_CACHE_DIR env provided, default to $HOME... ensure it exists!
            assert HOME_DIR, "Missing $HOME env var"

        return Path(
            GPT_CACHE_DIR if GPT_CACHE_DIR else HOME_DIR,  # type: ignore
            ".cache",
            "gpyt",
            "conversations",
        )

    def load_saved_conversations(self) -> None:
        """Load conversations from saved conversation path"""
        conversations_path = self.get_saved_conversations_path()
        conversation_file_paths = conversations_path.glob(pattern=r"*.json")
        conversation_file_paths = sorted(
            conversation_file_paths, key=lambda f: f.stat().st_mtime
        )

        for path in conversation_file_paths:
            with open(path, "r") as fd:
                raw_json = json.load(fd)
                conversation = Conversation.parse_obj(raw_json)
                self.conversations.append(conversation)
                self._convo_ids_added.add(conversation.id)
                self.past_conversations.add_conversation_option(conversation)

    def save_active_conversation_to_disk(self) -> str:
        """Save the active conversation to disk and return the file path"""
        return self.save_conversation_to_disk()

    def save_conversation_to_disk(
        self, conversation: Conversation | None = None
    ) -> str:
        """
        Save conversation to disk and return the file path.
        Will use active conversation if no conversation is given.
        """
        if not conversation:
            assert (
                self.active_conversation
            ), "When not supplied a conversation to save to disk, there must be an active conversation!"
            conversation = self.active_conversation
        print("SAVING: ", conversation.id)

        conversations_path = self.get_saved_conversations_path()

        os.makedirs(conversations_path, exist_ok=True)

        path = Path(conversations_path, f"convo-{conversation.id}.json")
        with open(path, "w") as fd:
            json.dump(conversation.dict(), fd)

        self._add_active_as_option()

        return str(path)

    def _set_summary_title_id(self, summary: str, id: str) -> None:
        self.assistant_responses.border_title = f"Conversation History - {summary}"
        self.assistant_responses.border_subtitle = f"convo-id: 0x{id}"

    def _setup_fresh_convo(self, initial_user_input: str) -> None:
        summary = self._get_assistant().get_conversation_summary(initial_user_input)
        new_convo = Conversation(id=get_id(), summary=summary, log=[])
        self._set_summary_title_id(summary, new_convo.id)
        self.conversations.append(new_convo)
        self.active_conversation = new_convo

    def clear_active_conversation(self) -> None:
        """
        Clears the active conversation by removing all messages from the
        current conversation history and resetting it.
        """
        self.assistant_responses.remove()
        self.assistant_responses = AssistantResponses(app=self)
        self.mount(self.assistant_responses)
        self.assistant_responses.border_title = "Conversation History"

    def _add_active_as_option(self) -> None:
        """
        Adds the active conversation as an option to the list of past
        conversations, if it does not already exist.
        """
        if not self.active_conversation:
            return
        exists_already = Path(
            self.get_saved_conversations_path(),
            f"convo-{self.active_conversation.id}.json",
        ).exists()

        if exists_already and self.active_conversation.id not in self._convo_ids_added:
            self.past_conversations.add_conversation_option(self.active_conversation)

        self._convo_ids_added.add(self.active_conversation.id)

    def start_new_conversation(self, add_option: bool = True) -> None:
        """Save current conversation, clear it, start a new fresh one"""
        if not self.active_conversation:
            return

        self.save_active_conversation_to_disk()
        if add_option:
            self._add_active_as_option()
        self.clear_active_conversation()
        self.active_conversation = None
        self.action_toggle_sidebar()

    @work()
    def fetch_assistant_response(self, user_input: str) -> None:
        if self.active_conversation is None:
            self._setup_fresh_convo(user_input)

        assert self.active_conversation, "No active conversation during log write"
        user_message = Message(id=get_id(), role="user", content=user_input)
        self.active_conversation.log.append(user_message)

        try:
            assistant_response_stream = self._get_assistant().get_response_stream(
                user_input
            )
        except:
            assistant_response_stream = self._get_assistant().error_fallback_message

        self.app.call_from_thread(
            self.assistant_responses.add_response,
            message=user_message,
            stream=assistant_response_stream,
        )

    def on_select_previous_conversation(self, conversation: Conversation) -> None:
        self.start_new_conversation(add_option=False)
        self.assistant_responses.setup_from_presaved_conversation(conversation)
        self.assistant_responses.container.scroll_end(duration=2.0, easing="in_quart")

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_toggle_sidebar(self) -> None:
        if not self.past_conversations.has_class("opened-gt-once"):
            try:
                self.load_saved_conversations()
            except:
                self.past_conversations.add_conversation_option(
                    Conversation(
                        summary=f"Failed to load conversations from {self.get_saved_conversations_path()}",
                        id="-1",
                        log=[],
                    )
                )
        self.past_conversations.add_class("opened-gt-once")
        self.past_conversations.toggle_class("hidden")
        if self.past_conversations.has_class("hidden"):
            self.focus_user_input()
            return
        self.set_focus(self.past_conversations.options)

    def action_toggle_settings(self) -> None:
        options = self.query_one(Options)
        options.toggle_class("hidden")
        if options.has_class("hidden"):
            self.focus_user_input()
            return
        self.set_focus(options.use_free)

    def focus_user_input(self) -> None:
        inp = self.query_one("#user-input")
        inp.focus()

    def action_handle_exit(self) -> None:
        exit()

    def action_scroll_convo_up(self) -> None:
        self.assistant_responses.container.scroll_relative(y=-4)

    def action_scroll_convo_down(self) -> None:
        self.assistant_responses.container.scroll_relative(y=4)