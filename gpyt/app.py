from gpyt import API_KEY, MODEL, PROMPT, DEBUG, ARGS, INTRO

from .assistant import Assistant


def handle_exit():
    print("\n🤖: Thanks for chatting!")
    exit(0)


def main():
    gpt = Assistant(
        api_key=API_KEY or "", model=MODEL, prompt=PROMPT, memory=not ARGS.no_memory
    )

    print(f"\n🤖: {INTRO}", flush=True, end="\n\n")

    while 1:
        user_input = input("🙂> ")
        if user_input.lower() in ("exit", "quit"):
            handle_exit()

        gpt_response = gpt.get_response(user_input)
        print(f"\n🤖: {gpt_response}", flush=True, end="\n\n")


if __name__ == "__main__":
    main()
