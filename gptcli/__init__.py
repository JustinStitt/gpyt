import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY") or None

assert API_KEY is not None, "⚠ Missing API KEY: Please set one. ⚠"

PROMPT = """
You are a helpful assistant. Be accurate and concise with your responses.
You are being used as a command-line tool by the user and you may be asked
technical/programming type questions.
"""

MODEL = "gpt-3.5-turbo"
