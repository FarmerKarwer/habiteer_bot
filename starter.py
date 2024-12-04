import sys
import os
import json
import traceback

# Add the src folder to sys.path
sys.path.append(os.path.abspath('./src'))

from src.index import handler, handler_long

SAMPLE_EVENTPATH = "events/using_command.json"
some_context = "Sample context"

if __name__ == "__main__":
    try:
        use_handler = handler_long(event = SAMPLE_EVENTPATH, context=some_context)
        print(use_handler['message'])
    except KeyboardInterrupt:
        print("\nBot has been stopped. Exiting gracefully...")
    except Exception as e:
        print("Something Went Wrong", e)
        traceback.print_exc()