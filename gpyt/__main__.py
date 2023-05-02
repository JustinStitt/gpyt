from .app import main

try:
    main()
except KeyboardInterrupt:
    print("\n🔧 KeyboardInterrupt detected, cleaning up and quitting.")
