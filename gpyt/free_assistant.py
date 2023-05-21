from typing import Generator

from gpt4free import you

from .config import API_ERROR_FALLBACK

from .assistant import Assistant


class FreeAssistant(Assistant):
    def __init__(self):
        self.error_fallback_message = API_ERROR_FALLBACK
        self.chat: list[dict[str, str]] = []

    def set_history(self, history: list[dict[str, str]]) -> None:
        self.clear_history()
        for i in range(0, len(history) - 1, 2):
            user = history[i]
            assistant = history[i + 1]
            self.chat.append(
                {"question": user["content"], "answer": assistant["content"]}
            )

    def clear_history(self) -> None:
        """reset internal message queue"""
        self.chat.clear()

    def get_response_stream(self, user_input: str) -> Generator:
        """Uses a free gpt3.5 provider, Theb. Lacks system prompt"""
        response = self.get_response(user_input)
        for i in range(0, len(response), 8):
            yield response[i : i + 8]

    def log_assistant_response(self, final_response: str) -> None:  # pyright: ignore
        ...

    def get_response(self, user_input: str, memorize=True) -> str:
        response = you.Completion.create(prompt=user_input, chat=self.chat).text
        assert response, "None response for FreeAssistant `You`"

        if memorize:
            self.chat.append({"question": user_input, "answer": response})
        return response

    def get_conversation_summary(self, initial_message: str) -> str:
        pre_prompt = """Summarize the following question in 6 words or less. be
        concise and fully grasp the main idea of the question. If what follows
        is not a question just summarize the idea of the statement itself\n"""

        message = pre_prompt + initial_message

        return self.get_response(message, memorize=False)


if __name__ == "__main__":
    agent = FreeAssistant()
    for token in agent.get_response_stream("How far away is the moon in inches?"):
        print(token, end="", flush=True)
