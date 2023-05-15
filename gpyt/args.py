import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--free", help="Use the gpt4free model. (experimental)", action="store_true"
)
args = parser.parse_args()

USE_EXPERIMENTAL_FREE_MODEL = args.free
