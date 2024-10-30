import json
import os

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def save_to_json(filepath, data):
    with open(filepath, "w") as json_file:
        json.dump(data, json_file, indent=4)

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

    # Append the new data to the list
    data.append(new_data)
    return data