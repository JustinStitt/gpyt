from gpyt import app


def main():
    try:
        app.run()

    except KeyboardInterrupt:
        print("\n🔧 KeyboardInterrupt detected, cleaning up and quitting.")


main()
