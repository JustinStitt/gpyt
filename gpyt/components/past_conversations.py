from textual.containers import Container
from textual.app import ComposeResult
from .conversation_option import StartNewConversationOption, ConversationOption
from .vim_list import VimLikeListView
from ..conversation import Conversation


class PastConversations(Container):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = app

    def compose(self) -> ComposeResult:
        self.start_new_conversation_option = StartNewConversationOption(app=self._app)
        self.options = VimLikeListView(self.start_new_conversation_option)
        yield self.options

    def add_conversation_option(self, conversation: Conversation) -> None:
        option = ConversationOption(conversation, app=self._app)
        self.options.mount(option, before=1)
