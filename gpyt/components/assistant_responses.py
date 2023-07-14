from textual import work
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import LoadingIndicator, Static
from typing import Generator

from ..conversation import Conversation, Message
from ..id import get_id
from .assistant_response import AssistantResponse


class AssistantResponses(Static):
    """Container for individual AssistantResponse widgets"""

    def __init__(self, app):
        super().__init__()
        self.container = ScrollableContainer()
        self._app = app

    def compose(self) -> ComposeResult:
        yield self.container

    def setup_from_presaved_conversation(self, conversation: Conversation) -> None:
        """Load conversation into conversation history widget from Conversation model"""

        self._app.active_conversation = conversation
        self._app._set_summary_title_id(conversation.summary, conversation.id)
        new_history = []

        all_user_messages = [m for m in conversation.log if m.role == "user"]
        all_assistant_messages = [m for m in conversation.log if m.role == "assistant"]

        for user_message, assistant_response in zip(
            all_user_messages, all_assistant_messages
        ):
            assert (
                user_message.role == "user"
            ), "Improper role for setup from presaved convesation"

            new_response = AssistantResponse(
                question=user_message.content, id=user_message.id
            )
            self.container.mount(new_response)
            assert (
                assistant_response.role == "assistant"
            ), "Improper role for setup from presaved convesation"
            new_response.update_response(assistant_response.content)
            new_history.append({"role": "user", "content": user_message.content})
            new_history.append(
                {"role": "assistant", "content": assistant_response.content}
            )

        self._app._get_assistant().set_history(new_history)
        self._app.past_conversations.add_class("hidden")
        self._app.focus_user_input()

    @work()
    def add_response(self, stream: Generator, message: Message) -> None:
        new_response = AssistantResponse(question=message.content, id=message.id)
        self._app.call_from_thread(self.container.mount, new_response)
        self._app.call_from_thread(new_response.scroll_visible)
        self._app.scrolled_during_response_stream = False
        markdown = ""
        update_frequency = 10
        i = 0
        for data in stream:
            i += 1
            try:  # HACK: should check for attr, not try/except
                if self._app.use_free_gpt or self._app.use_palm:
                    markdown = markdown + data
                else:
                    markdown = markdown + data["choices"][0]["delta"]["content"]
                if i % update_frequency == 0:
                    self._app.call_from_thread(new_response.update_response, markdown)
                    if not self._app.scrolled_during_response_stream:
                        self._app.call_from_thread(self.container.scroll_end)
            except:
                continue

        self._app.call_from_thread(new_response.update_response, markdown)
        self._app.call_from_thread(
            new_response.user_question.scroll_visible, duration=2, easing="out_back"
        )
        self._app._get_assistant().log_assistant_response(markdown)
        assistant_message = Message(id=get_id(), role="assistant", content=markdown)
        assert self._app.active_conversation, "No active conversation during log write"
        self._app.active_conversation.log.append(assistant_message)

        self._app.call_from_thread(self._app.save_active_conversation_to_disk)

        loading_indicator = self.query_one(LoadingIndicator)
        if loading_indicator:
            self._app.call_from_thread(loading_indicator.remove)
            print("deleting loading indicator")
