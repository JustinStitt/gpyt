import os

from dotenv import find_dotenv, get_key

ENV_PATH = find_dotenv()

API_KEY = get_key(dotenv_path=ENV_PATH, key_to_get="OPENAI_API_KEY")

# try to get from os envrionment variables

if API_KEY is None:
    API_KEY = os.getenv("OPENAI_API_KEY") or None

assert (
    API_KEY is not None
), """

❗Missing OpenAI API Key ❗

Steps to fix this issue:

    1) Get an OpenAI Key from https://platform.openai.com/account/api-keys
    2) Create a `.env` file located in your $HOME directory.
    3) add `OPENAI_API_KEY="your_api_key"` to the `.env` file.
    4) or, you can run `$ EXPORT OPENAI_API_KEY="your_api_key"` to set a key for the active shell session.
    5) rerun this program with `$ gpyt` or `$ python -m gpyt`

"""

PROMPT = """
You are a helpful assistant. Be accurate and concise with your responses.
You are being used as a command-line tool by the user and you may be asked
technical/programming type questions.

Use basic Markdown syntax.

Use # for big ideas or ## for smaller ideas.

Use lists with "*" or "1), 2), ... n)" when it makes sense to list things (like stages or parts)

For intermediate to complex topics (like science, or large processes) only you should
summarize the user's question into less than four words, and
place them in a markdown header as the first line of your response.

For example, if the user is asking about football use this format

# Football

<the rest of your response>

--end intermediate to complex topics instructions--
"""

SUMMARY_PROMPT = "Summarize the user's input in 6 words or less. Try to capture the big idea. DO NOT USE more than 6 words and DO NOT answer their question. Simply echo back to them your summary."

API_ERROR_MESSAGE = """
❗ There was an error with OpenAI.

# Diagnostics

Make sure that:
    1) You have a proper OPENAI_API_KEY configured at `$HOME/.env` starting with "sk-"
    2) You have configured Billing over at https://platform.openai.com/account/billing
    3) You aren't getting rate limited (9000 tokens per minute)

Try Again Later.
"""
API_ERROR_FALLBACK = [{"choices": [{"delta": {"content": API_ERROR_MESSAGE}}]}]


INTRO = "Ask me anything. I'll try to assist you!"

AVAILABLE_MODELS = ("gpt-3.5-turbo", "gpt4")
MODEL = "gpt-3.5-turbo"
