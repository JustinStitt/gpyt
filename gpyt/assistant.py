import openai
from typing import Generator


class Assistant:
    """
    Represents an OpenAI GPT assistant.

    It can generate responses based on user input and conversation history.
    """

    def __init__(self, *, api_key: str, model: str, prompt: str, memory: bool = True):
        self.api_key = api_key
        self.model = model
        self.prompt = prompt
        self.memory = memory
        self.messages = [
            {"role": "system", "content": self.prompt},
        ]
        openai.api_key = self.api_key

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

    def log_assistant_response(self, final_response: str) -> None:
        if not self.memory:
            return

        self.messages.append({"role": "assistant", "content": final_response})


def _test() -> None:
    from gpyt import API_KEY, MODEL, PROMPT

    gpt = Assistant(api_key=API_KEY or "", model=MODEL, prompt=PROMPT)

    # response = gpt.get_response("Hi, how are you!")
    response_iterator = gpt.get_response_stream("hi how are you!")
    for response in response_iterator:
        try:
            print(response["choices"][0]["delta"]["content"], end="", flush=True)
        except:
            continue


if __name__ == "__main__":
    _test()
