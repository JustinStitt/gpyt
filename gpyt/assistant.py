import openai


class Assistant:
    def __init__(self, *, api_key: str, model: str, prompt: str, memory: bool = True):
        self.api_key = api_key
        self.model = model
        self.prompt = prompt
        self.memory = memory
        self.messages = [
            {"role": "system", "content": self.prompt},
        ]

    def clear_history(self):
        self.messages = [self.messages[0]]

    def get_response(self, user_input: str) -> str:
        if self.memory:
            self.messages.append({"role": "user", "content": user_input})

        response = openai.ChatCompletion.create(  # type: ignore
            model=self.model, messages=self.messages
        )["choices"][0]["message"]

        if self.memory:
            self.messages.append({"role": "assistant", "content": response})

        return response["content"]
