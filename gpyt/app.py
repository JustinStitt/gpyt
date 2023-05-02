import pyperclip

from gpyt import API_KEY, ARGS, INTRO, MODEL, PROMPT

from .assistant import Assistant
from .exception import ContinueIteration
from .debug import debug


def handle_exit():
    """
    Invoked by the user via `exit` or `quit`.

    Gracefully exits the script.
    """
    print("\n🤖: Thanks for chatting!")
    exit(0)


def handle_copy(message: str):
    """
    Invoked by the user via `copy` or `yank`.

    Copies to user's system clipboard.
    """
    pyperclip.copy(message)
    print(f"\n🔧: Copied previous GPT response to clipboard!\n")


def handle_user_input(user_input: str, previous_gpt_response: str):
    """
    Handles the specific meta commands that the user can enter.

    raises ContinueIteration if GPT should not respond to the command.
    """
    if user_input.lower() in ("exit", "quit"):
        handle_exit()

    if user_input.lower() in ("copy", "yank"):
        handle_copy(previous_gpt_response)
        raise ContinueIteration()


def main():
    """
    Main loop which handles user interaction and gpt feedback loop.

    Some dogma: maintain readability.
    """
    gpt = Assistant(
        api_key=API_KEY or "", model=MODEL, prompt=PROMPT, memory=not ARGS.no_memory
    )

    print(f"\n🤖: {INTRO}", flush=True, end="\n\n")
    previous_gpt_response = INTRO  # for handle_copy purposes

    while 1:
        user_input = input("🙂> ")

        try:
            handle_user_input(user_input, previous_gpt_response)
        except ContinueIteration:
            debug(
                f"Special command '{user_input}' entered. ContinueIteration raised!\n",
            )
            continue

        gpt_response = gpt.get_response(user_input)
        previous_gpt_response = gpt_response
        print(f"\n🤖: {gpt_response}", flush=True, end="\n\n")


if __name__ == "__main__":
    main()
