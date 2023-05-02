import openai


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

    def get_response(self, user_input: str) -> str:
        """
        Use OpenAI API to retrieve a ChatCompletion response from a GPT model.

        Memory can be configured so that the assistant forgets previous messages
        you or it has sent. (saves tokens ($$$) as well)
        """
        if not self.memory:
            self.clear_history()
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = openai.ChatCompletion.create(  # type: ignore
                model=self.model, messages=self.messages
            )["choices"][0]["message"]
        except:
            return "Could not generate Assistant completion. Ensure you've configured an API_KEY and are connected to the internet!"

        if self.memory:
            self.messages.append(response)

        return response["content"]
