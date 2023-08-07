from typing import Generator

import litellm 
from litellm import completion
import traceback
import tiktoken
import sys, os

from .config import (
    API_ERROR_FALLBACK,
    SUMMARY_PROMPT,
    APPROX_PROMPT_TOKEN_USAGE,
    PRICING_LOOKUP,
    MODEL_MAX_CONTEXT,
)


class LiteAssistant:
    """
    Represents an OpenAI GPT assistant.

    It can generate responses based on user input and conversation history.
    """

    kDEFAULT_SUMMARY_FALLTHROUGH = "User Question"

    def __init__(
        self,
        *,
        model_keys: dict,
        model: str,
        prompt: str,
        memory: bool = True,
    ):
        for key in model_keys:
            if key == "ANTHROPIC_API_KEY":
                litellm.anthropic_key = model_keys[key]
            if key == "COHERE_API_KEY":
                litellm.cohere_key = model_keys[key]
            if key == "REPLICATE_API_KEY":
                litellm.replicate_key = model_keys[key]
        self.model = model
        self.prompt = prompt
        self.summary_prompt = SUMMARY_PROMPT
        self.memory = memory
        self.messages = [
            {"role": "system", "content": self.prompt},
        ]
        self.error_fallback_message = API_ERROR_FALLBACK
        self._encoding_engine = tiktoken.get_encoding(
            "cl100k_base"
        )  # gpt3.5/gpt4 encoding engine
        self.input_tokens_this_convo = APPROX_PROMPT_TOKEN_USAGE
        self.output_tokens_this_convo = 10
        self.price_of_this_convo = self.get_default_price_of_prompt()

    def set_history(self, new_history: list):
        """Reassign all message history except for system message"""
        sys_prompt = self.messages[0]
        self.messages = new_history[::]
        self.messages.insert(0, sys_prompt)

    def get_tokens_used(self, message: str) -> int:
        return len(self._encoding_engine.encode(message))

    def get_default_price_of_prompt(self) -> float:
        return self.get_approximate_price(
            self.get_tokens_used(self.prompt), 0
        ) + self.get_approximate_price(self.get_tokens_used(self.summary_prompt), 10)

    def tokens_used_this_convo(self) -> int:
        num = self.input_tokens_this_convo + self.output_tokens_this_convo
        has_limit = MODEL_MAX_CONTEXT.get(self.model, None)
        if not has_limit:
            return 0

        return num

    def update_token_usage_for_input(self, in_message: str, out_message: str) -> None:
        in_tokens_used = self.get_tokens_used(in_message)
        out_tokens_used = self.get_tokens_used(out_message)
        self.input_tokens_this_convo += self.input_tokens_this_convo + in_tokens_used
        self.output_tokens_this_convo += self.output_tokens_this_convo + out_tokens_used
        self.price_of_this_convo += self.get_approximate_price(
            self.input_tokens_this_convo, self.output_tokens_this_convo
        )

    def get_approximate_price(self, _in: int | float, _out: int | float) -> float:
        known_pricing = PRICING_LOOKUP.get(self.model, None)
        if not known_pricing:
            return 0.0
        in_price_ratio = PRICING_LOOKUP[self.model][0]
        out_price_ratio = PRICING_LOOKUP[self.model][1]

        limit = MODEL_MAX_CONTEXT.get(self.model, None)
        if not limit:
            return 0

        _in = min(_in, limit / 2)
        _out = min(_out, limit / 2)

        return (_in / 1000) * in_price_ratio + (_out / 1000) * out_price_ratio

    def clear_history(self):
        """
        Wipe all message history during this conversation, except for the
        first system message
        """
        self.messages = [self.messages[0]]
        self.input_tokens_this_convo = APPROX_PROMPT_TOKEN_USAGE
        self.output_tokens_this_convo = 10
        self.price_of_this_convo = self.get_default_price_of_prompt()

    def get_response_stream(self, user_input: str) -> Generator:
        """
        Use OpenAI API to retrieve a ChatCompletion response from a GPT model.

        Memory can be configured so that the assistant forgets previous messages
        you or it has sent. (saves tokens ($$$) as well)
        """
        if not self.memory:
            self.clear_history()
        self.messages.append({"role": "user", "content": user_input})

        response = completion(  # type: ignore
            model=self.model,
            messages=self.messages,
            stream=True,
        )
        # print(type(response))
        if isinstance(response, dict):
            # fake stream output if model doesn't support it
            tmp_response = response
            text_response = response['choices'][0]['message']['content']
            tmp_response['choices'][0]['delta'] = {"content": ""}
            for i in range(0, len(text_response), 8):
                tmp_response['choices'][0]['delta']['content'] = text_response[i : i + 8]
                yield tmp_response

        # print(response["usage"])
        return None

        # return response  # type: ignore

    def get_response(self, user_input: str) -> str:
        """Get an entire string back from the assistant"""
        messages = [
            {"role": "system", "content": self.summary_prompt},
            {"role": "user", "content": user_input.rstrip()},
        ]
        response = completion(model=self.model, messages=messages)

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
    from config import PROMPT
    model_keys={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
    gpt = LiteAssistant(model_keys=model_keys, model="claude-instant-1", prompt=PROMPT)

    # response = gpt.get_response("How do I make carrot cake?")
    # summary = gpt.get_conversation_summary("How do I get into Dirt Biking?")
    # print(f"{summary = }")
    response_iterator = gpt.get_response_stream("hi how are you!")
    for response in response_iterator:
        try:
            print(response["choices"][0]["delta"]["content"], end="", flush=True)
        except:
            traceback.print_exc()
            continue


if __name__ == "__main__":
    _test()
