from typing import Generator

import openai

from .config import API_ERROR_FALLBACK, SUMMARY_PROMPT


class Assistant:
    """
    Represents an OpenAI GPT assistant.

    It can generate responses based on user input and conversation history.
    """

    kDEFAULT_SUMMARY_FALLTHROUGH = "User Question"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        prompt: str,
        memory: bool = True,
    ):
        self.api_key = api_key
        self.model = model
        self.prompt = prompt
        self.summary_prompt = SUMMARY_PROMPT
        self.memory = memory
        self.messages = [
            {"role": "system", "content": self.prompt},
        ]
        self.error_fallback_message = API_ERROR_FALLBACK
        openai.api_key = self.api_key

    def set_history(self, new_history: list):
        """Reassign all message history except for system message"""
        sys_prompt = self.messages[0]
        self.messages = new_history[::]
        self.messages.insert(0, sys_prompt)

    def clear_history(self):
        """
        Wipe all message history during this conversation, except for the
        first system message
        """
        self.messages = [self.messages[0]]

    def get_response_stream(self, user_input: str) -> Generator:
        """
        Use OpenAI API to retrieve a ChatCompletion response from a GPT model.

        Memory can be configured so that the assistant forgets previous messages
        you or it has sent. (saves tokens ($$$) as well)
        """
        if not self.memory:
            self.clear_history()
        self.messages.append({"role": "user", "content": user_input})

        response = openai.ChatCompletion.create(  # type: ignore
            model=self.model,
            messages=self.messages,
            stream=True,
        )

        return response  # type: ignore

    def get_response(self, user_input: str) -> str:
        """Get an entire string back from the assistant"""
        messages = [
            {"role": "system", "content": self.summary_prompt},
            {"role": "user", "content": user_input.rstrip()},
        ]
        response = openai.ChatCompletion.create(model=self.model, messages=messages)

        return response["choices"][0]["message"]["content"]  # type: ignore

    def get_conversation_summary(self, initial_message: str) -> str:
        """Generate a short 6 word or less summary of the user\'s first message"""
        try:
            summary = self.get_response(initial_message)
        except:
            return Assistant.kDEFAULT_SUMMARY_FALLTHROUGH

        return summary

    def log_assistant_response(self, final_response: str) -> None:
        if not self.memory:
            return

        self.messages.append({"role": "assistant", "content": final_response})


def _test() -> None:
    from gpyt import API_KEY, MODEL, PROMPT

    gpt = Assistant(api_key=API_KEY or "", model=MODEL, prompt=PROMPT)

    # response = gpt.get_response("How do I make carrot cake?")
    summary = gpt.get_conversation_summary("How do I get into Dirt Biking?")
    print(f"{summary = }")
    # response_iterator = gpt.get_response_stream("hi how are you!")
    # for response in response_iterator:
    #     try:
    #         print(response["choices"][0]["delta"]["content"], end="", flush=True)
    #     except:
    #         continue


if __name__ == "__main__":
    _test()
