import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--free", help="Use the gpt4free model. (experimental)", action="store_true"
)
parser.add_argument(
    "--palm", help="Use PaLM 2, Google's Premier LLM (new)", action="store_true"
)

parser.add_argument(
    "--gpt4",
    help="Use GPT4 (your API_KEY must have been granted access.)",
    action="store_true",
)


args = parser.parse_args()

USE_EXPERIMENTAL_FREE_MODEL = args.free
USE_PALM_MODEL = args.palm
USE_GPT4 = args.gpt4
