from gpyt import app

try:
    app.run()

except KeyboardInterrupt:
    print("\n🔧 KeyboardInterrupt detected, cleaning up and quitting.")
