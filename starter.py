import sys
import os
import json
import traceback

# Add the src folder to sys.path
sys.path.append(os.path.abspath('./src'))

from src.index import handler

SAMPLE_EVENTPATH = "events/using_command.json"
some_context = "Sample context"

if __name__ == "__main__":
    try:
        # last_update_id = get_updates()['result'][-1]['update_id']
        # print(last_update_id)
        use_handler = handler(event = SAMPLE_EVENTPATH, context=some_context)
        print(use_handler['message']) 
    except Exception as e:
        print("Something Went Wrong", e)
        traceback.print_exc()