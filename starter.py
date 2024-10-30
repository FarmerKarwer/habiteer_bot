from index import handler
import os
import json
import traceback
from utils import load_json

def get_event_filenames(folder_path="events"):
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            return filename

def load_event(event_name):
    filepath = f'events/{event_name}.json'
    return load_json(filepath)

some_context = "Sample context"

if __name__ == "__main__":
    all_events = get_event_filenames()
    #print(f"Enter one of the events (without '.json'). The available events are: {all_events}")
    try:
        #chosen_event = input()
        #using_command = load_event(chosen_event)
        using_command = "events/using_command.json"
        use_handler = handler(event = using_command, context=some_context)
        print(use_handler['statusCode']) 
    except Exception as e:
        print("Something Went Wrong", e)
        traceback.print_exc()