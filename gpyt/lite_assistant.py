from typing import Generator
import litellm 
from litellm import completion
import google.generativeai as palm
import tiktoken
import os
from .assistant import Assistant
from .config import API_ERROR_FALLBACK, PROMPT
import dotenv
dotenv.load_dotenv()
from .config import (
    API_ERROR_FALLBACK,
    APPROX_PROMPT_TOKEN_USAGE,
)


class LiteAssistant(Assistant):
    API_ERROR_MESSAGE = """There was an ERROR with the model API\n## Diagnostics\n* Make sure you have a PALM_API_KEY set at `~/.env`\n* Make sure you aren't being rate-limited."""

    def __init__(self, api_key: str, model: str, memory: bool = True):
        self.error_fallback_message = API_ERROR_FALLBACK
        self.chat: list[dict[str, str]] = []
        self.model = model
        self.api_key = api_key
        self.memory = memory
        self.messages = []
        self.error_fallback_message = LiteAssistant.API_ERROR_MESSAGE
        self.input_tokens_this_convo = APPROX_PROMPT_TOKEN_USAGE
        self.output_tokens_this_convo = 10
        self.prompt, self.summary_prompt = ("", "")

        self._encoding_engine = tiktoken.get_encoding(
            "cl100k_base"
        )  
        self.price_of_this_convo = self.get_default_price_of_prompt()

    def set_history(self, new_history: list[dict[str, str]]):
        self.clear_history()
        for message in new_history:
            self.messages.append(message["content"])

    def clear_history(self) -> None:
        """reset internal message queue"""
        self.messages.clear()

    def get_response_stream(self, user_input: str) -> Generator:
        """Fake a stream output with PaLM 2"""
        response = self.get_response(user_input)
        for i in range(0, len(response), 8):
            yield response[i : i + 8]

    def log_assistant_response(self, final_response: str) -> None:  # pyright: ignore
        ...

    def get_response(self, user_input: str) -> str:
        if not self.memory:
            self.clear_history()
        self.messages.append({"role": "user", "content": user_input})

        response = completion(  # type: ignore
            model=self.model,
            messages=self.messages,
            stream=True,
            api_key=self.api_key # optional param, litellm will read it from the os.getenv by default
        )

        return response  # type: ignore

    def _bad_key(self) -> bool:
        return not self.api_key or (type(self.api_key) is str and len(self.api_key) < 1)

    def get_conversation_summary(self, initial_message: str) -> str:
        """Generate a short 6 word or less summary of the user\'s first message"""
        try:
            summary = self.get_response(initial_message)
        except:
            return Assistant.kDEFAULT_SUMMARY_FALLTHROUGH
        
        return summary

if __name__ == "__main__":
    ...
    agent = LiteAssistant(model="claude-instant-1")
    print(agent.get_conversation_summary("What is the third closest moon from Saturn"))
    while 1:
        user_inp = input("> ")
        msg = agent.get_response(user_input=user_inp)
        print("\n", msg)
