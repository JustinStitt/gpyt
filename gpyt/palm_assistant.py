import os
from typing import Generator

import google.generativeai as palm

from .assistant import Assistant
from .config import API_ERROR_FALLBACK, PROMPT


class PalmAssistant(Assistant):
    EXAMPLES = [
        ("How far is the sun?", "Distance to Sun"),
        ("How do I make a cake if I have some ingredients", "Baking a Cake"),
        ("Write a for loop in C#", "C# For Loop"),
        ("Hello!", "Greeting"),
    ]
    SUMMARY_PROMPT = """Summarize the following question in 6 words or less. be
        concise and fully grasp the main idea of the question. If what follows
        is not a question just summarize the idea of the statement itself


        input: How far is the moon?
        summary Distance to Moon?
        input: Write a for loop in C#
        summary C# For Loops.
        input: How do I bake a cake?
        summary Baking a Cake.
        """

    def __init__(self, api_key):
        self.error_fallback_message = API_ERROR_FALLBACK
        self.chat: list[dict[str, str]] = []
        self.api_key = api_key
        assert self.api_key and len(self.api_key), "Missing PaLM 2 API KEY"
        palm.configure(api_key=self.api_key)
        self.messages = []

    def clear_history(self) -> None:
        """reset internal message queue"""
        self.chat.clear()

    def get_response_stream(self, user_input: str) -> Generator:
        """Fake a stream output with PaLM 2"""
        response = self.get_response(user_input)
        for i in range(0, len(response), 8):
            yield response[i : i + 8]

    def log_assistant_response(self, final_response: str) -> None:  # pyright: ignore
        ...

    def get_response(self, user_input: str) -> str:
        self.messages.append(user_input)
        response = palm.chat(context=PROMPT, messages=self.messages).last
        self.messages.append(response)
        return response

    def get_conversation_summary(self, initial_message: str) -> str:
        prompt = f"{PalmAssistant.SUMMARY_PROMPT}\ninput: {initial_message}\nsummary"
        response = palm.generate_text(prompt=prompt)
        return response.result


if __name__ == "__main__":
    agent = PalmAssistant()
    print(agent.get_conversation_summary("What is the third closest moon from Saturn"))
    # while 1:
    #     user_inp = input("> ")
    #     msg = agent.get_response(user_input=user_inp)
    #     print("\n", msg)
