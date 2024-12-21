import json
import os
import re
from datetime import datetime, timezone
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

def sum_arrays(arr1, arr2):
    # Check if arrays have the same length
    if len(arr1) != len(arr2):
        raise ValueError("Arrays must be of the same length")

    # Sum elements at corresponding positions
    return [a + b for a, b in zip(arr1, arr2)]

def unix_to_timestamp(unix_time):
    # Convert the Unix timestamp to a datetime object
    dt = datetime.fromtimestamp(unix_time, tz=timezone.utc)
    
    # Format the datetime object in ISO 8601 format with milliseconds
    formatted_time = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    return formatted_time

def format_numbered_list(items: List[str], capitalize: bool = True) -> str:
    """
    Formats a list of strings into a numbered, newline-separated string.

    Args:
        items (List[str]): The list of strings to format.
        capitalize (bool, optional): Whether to capitalize each item. Defaults to True.

    Returns:
        str: A numbered, newline-separated string with each item optionally capitalized.
    """
    if capitalize:
        items = (item.capitalize() for item in items)
    else:
        items = (item for item in items)
    
    return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))

def extract_numbered_items(text: str) -> List[str]:
    """
    Extracts items from a numbered multi-line string.

    Each line should start with a number followed by a period and a space (e.g., "1. Item").

    Args:
        text (str): The input string containing numbered items separated by newlines.

    Returns:
        List[str]: A list of extracted items without their numbering.
    """
    items = []
    for line in text.strip().split('\n'):
        if line:
            match = re.match(r'^\d+\.\s+(.*)', line)
            if match:
                item = match.group(1).strip()
                items.append(item)
            else:
                print("Warning! Lines do not match the expected pattern. Handling is skipped")
                continue
    return items

def parse_numbers(text: str) -> List[int]:
    """Parses numbers and ranges from a given text."""
    numbers = []
    # Split the input by commas
    parts = text.split(',')
    for part in parts:
        part = part.strip()  # Remove any surrounding whitespace
        if '-' in part:
            # Split the range into start and end
            try:
                start, end = part.split('-')
                start, end = int(start), int(end)
                if start > end:
                    raise ValueError(f"Invalid range: {part}")
                # Extend the numbers list with the range
                numbers.extend(range(start, end + 1))
            except ValueError as ve:
                raise ValueError(f"Invalid range format: '{part}'. Error: {ve}")
        else:
            # Convert single number to integer and append
            try:
                number = int(part)
                numbers.append(number)
            except ValueError:
                raise ValueError(f"Invalid number format: '{part}'")
    return numbers

def parse_time_from_string(input_string):
    """
    Validates and parses time in the format HH:MM from a string.
    The string must contain only the time in this format, otherwise raises a ValueError.

    :param input_string: The input string to validate and parse.
    :return: A string representing time in HH:MM format.
    """
    # Regular expression for matching the exact format HH:MM
    time_pattern = r'^([01]\d|2[0-3]):[0-5]\d$'
    match = re.fullmatch(time_pattern, input_string.strip())
    
    if match:
        return match.group(0)  # Return the matched time
    else:
        raise ValueError("Input string must contain only time in HH:MM format.")

def weekdays_to_numbers(weekdays, start_from_sunday=False):
    # Define the mapping
    if start_from_sunday:
        weekday_map = {'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6}
    else:  # ISO 8601 standard
        weekday_map = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6, 'sun': 7}
    
    # Convert the list of weekdays to corresponding numbers
    return [weekday_map[day.lower()] for day in weekdays if day.lower() in weekday_map]

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

# List conditions
def check_all_in_range(input_list, min=1, max=10):
    # Check if all items are between 1 and 10
    if not all(min <= item <= max for item in input_list):
        raise ValueOutOfRangeError("All items must be between 1 and 10.")

def check_matching_lengths(list1, list2):
    """Checks if two lists have matching lengths."""
    if len(list1) != len(list2):
        raise ListLengthMismatchError("The lengths of the lists do not match.")

def check_minimum_length(input_list, min_length=5):
    """Ensures the list meets the minimum required length."""
    if len(input_list) < min_length:
        raise ListTooShortError(f"The list has fewer than {min_length} entries.")
