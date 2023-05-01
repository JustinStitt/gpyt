from gpyt import API_KEY, MODEL, PROMPT
import argparse

from .assistant import Assistant

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

args = arg_parser.parse_args()
print(args)


def handle_exit():
    print("\n🤖: Thanks for chatting!")
    exit(0)


def main():
    gpt = Assistant(
        api_key=API_KEY or "", model=MODEL, prompt=PROMPT, memory=not args.no_memory
    )

    while 1:
        user_input = input("🙂> ")
        if user_input.lower() in ("exit", "quit"):
            handle_exit()

        gpt_response = gpt.get_response(user_input)
        print(f"\n🤖: {gpt_response}", flush=True, end="\n\n")


if __name__ == "__main__":
    main()
