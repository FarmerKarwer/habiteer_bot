import json
import os
import re
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Dict, List, Optional
from exceptions import (
    ValueOutOfRangeError,
    ListTooShortError,
    ListLengthMismatchError,
)

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def save_to_json(filepath, new_data):
    with open(filepath, "w") as json_file:
        json.dump(new_data, json_file, indent=4)

def append_to_json(filepath, new_data):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding='utf-8') as json_file:
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

def update_user_value(file_path, user_id, key, new_value):
    # Step 1: Load the JSON data from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Step 2: Find the user with the specified user_id
    user_found = False
    for user in data:
        if user['user_id'] == user_id:
            # Step 3: Update the specified key with the new value
            user[key] = new_value
            user_found = True
            break
    
    # Step 4: Save the updated JSON back to the file
    if user_found:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Updated {key} for user_id {user_id} to {new_value}.")
    else:
        print(f"User with user_id {user_id} not found.")

def delete_user_records(file_path, user_id):
    # Step 1: Load the JSON data from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Step 2: Filter out records with the specified user_id
    updated_data = [user for user in data if user['user_id'] != user_id]
    
    # Step 3: Save the updated JSON back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(updated_data, file, ensure_ascii=False, indent=4)
    
    # Provide feedback
    if len(data) != len(updated_data):
        print(f"Deleted records for user_id {user_id}.")
    else:
        print(f"No records found for user_id {user_id}.")

# Getting cache data
def get_cached_data(filepath, user_id, chat_id, property):
    # Check if file exists and read data if so
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                print("Error: JSON file is empty or corrupted.")
                return None
    else:
        print("Error: File does not exist.")
        return None

    # Find the entry that matches the specified user_id and chat_id
    for entry in data:
        if entry.get("user_id") == user_id and entry.get("chat_id") == chat_id:
            return entry.get(property)

    # Return None if no matching entry is found
    print("No matching entry found for the given user_id and chat_id.")
    return None

# Saving to cache
def save_data_to_cache(filepath, data):
    new_data = append_to_json(filepath=filepath, new_data=data)
    save_to_json(filepath=filepath, new_data=new_data)
    print(f"Data have been saved successfully to {filepath}")
