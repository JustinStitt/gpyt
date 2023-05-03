import openai_async
import asyncio


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

    def clear_history(self):
        """
        Wipe all message history during this conversation, except for the
        first system message
        """
        self.messages = [self.messages[0]]

    async def get_response(self, user_input: str) -> str:
        """
        Use OpenAI API to retrieve a ChatCompletion response from a GPT model.

        Memory can be configured so that the assistant forgets previous messages
        you or it has sent. (saves tokens ($$$) as well)
        """
        if not self.memory:
            self.clear_history()
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = await openai_async.chat_complete(  # type: ignore
                api_key=self.api_key,
                timeout=30,
                payload={"model": self.model, "messages": self.messages},
            )
        except:
            return "Could not generate Assistant completion. Ensure you've configured an API_KEY and are connected to the internet! This could also be due to a timeout, check your latency to openai!"

        message = response.json()["choices"][0]["message"]

        if self.memory:
            self.messages.append(message)

        return message["content"]


async def _test() -> None:
    from gpyt import API_KEY, MODEL, PROMPT

    gpt = Assistant(api_key=API_KEY or "", model=MODEL, prompt=PROMPT)

    response = await gpt.get_response("Hi, how are you!")
    print(response)


if __name__ == "__main__":
    asyncio.run(_test())
