import argparse
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

INTRO = "I'm here to help. Ask me anything!"

MODEL = "gpt-3.5-turbo"

arg_parser = argparse.ArgumentParser(
    prog="gpyt", description="Infer with GPT on the command line!"
)

arg_parser.add_argument(
    "--no-memory",
    action="store_true",
    required=False,
    default=False,
    help="Disable assistant memory during conversation. (saves tokens, $$$)",
)

arg_parser.add_argument(
    "--debug",
    action="store_true",
    required=False,
    default=False,
    help="Enable debug mode (for development).",
)


ARGS = arg_parser.parse_args()

DEBUG = ARGS.debug
