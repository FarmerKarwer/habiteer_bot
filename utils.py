import json
import os

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def save_to_json(filepath, new_data):
    with open(filepath, "w") as json_file:
        json.dump(new_data, json_file, indent=4)

def append_to_json(filepath, new_data):
    if os.path.exists(filepath):
        with open(filepath, "r") as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                data = []  # Initialize as an empty list if the file is empty or corrupted
    else:
        data = []  # Initialize as an empty list if the file does not exist

    # Ensure the data is in list format to allow appending
    if not isinstance(data, list):
        data = [data]

    # Filter data to find the max ID for this specific (user_id, chat_id) combination
    user_id = new_data.get("user_id")
    chat_id = new_data.get("chat_id")
    relevant_entries = [entry for entry in data if entry.get("user_id") == user_id and entry.get("chat_id") == chat_id]
    last_id_for_pair = max((entry.get("id", 0) for entry in relevant_entries), default=0)
    
    # Assign the next sequential ID for the specific (user_id, chat_id) pair
    new_data["id"] = last_id_for_pair + 1

    data = [entry for entry in data if not (entry.get("user_id") == new_data.get("user_id") and entry.get("chat_id") == new_data.get("chat_id"))]

    # Append the new data to the list
    data.append(new_data)
    return data