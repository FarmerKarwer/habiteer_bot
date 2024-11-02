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

# def update_user_data_while_picking_habit(filepath, new_data):
#     """
#     Updates a specific key for a user within a JSON file.
    
#     Parameters:
#     - file_path (str): Path to the JSON file.
#     - user_id (str): The user ID whose data needs updating.
#     - key (str): The key to update or append within the user's data.
#     - value: The value to append or update for the specified key.
    
#     Returns:
#     - None
#     """
#     if os.path.exists(filepath):
#         with open(filepath, "r") as json_file:
#             try:
#                 data = json.load(json_file)
#             except json.JSONDecodeError:
#                 data = []  # Initialize as an empty list if the file is empty or corrupted
#     else:
#         data = []  # Initialize as an empty list if the file does not exist

#     # Ensure the data is in list format to allow appending
#     if not isinstance(data, list):
#         data = [data]

#     data.append(new_data)
#     return data


# def retrieve_user_data_while_picking_habit(file_path, user_id, key):
#     """
#     Retrieves specific data for a user from a JSON file.

#     Parameters:
#     - file_path (str): Path to the JSON file.
#     - user_id (str): The user ID whose data needs to be retrieved.
#     - key (str): The key to retrieve within the user's data.

#     Returns:
#     - The value associated with the key if found, otherwise a message indicating the key or user is missing.
#     """
#     try:
#         # Step 1: Read the JSON data from the file
#         with open(file_path, 'r') as file:
#             data = json.load(file)
        
#         # Step 2: Check if user_id exists
#         if user_id not in data:
#             return f"User ID {user_id} not found in the file."
        
#         # Step 3: Check if the key exists within the user's data
#         if key in data[user_id]:
#             return data[user_id][key]
#         else:
#             return f"Key '{key}' not found for User ID '{user_id}'."
    
#     except FileNotFoundError:
#         return f"The file {file_path} was not found."
#     except json.JSONDecodeError:
#         return "Error decoding JSON. Please check the file format."
#     except Exception as e:
#         return f"An error occurred: {e}"

# def delete_user_data(file_path, user_id):
#     """
#     Deletes all data for a specific user from a JSON file.

#     Parameters:
#     - file_path (str): Path to the JSON file.
#     - user_id (str): The user ID whose data needs to be deleted.

#     Returns:
#     - str: A message indicating success or if the user was not found.
#     """
#     try:
#         # Step 1: Read the JSON data from the file
#         with open(file_path, 'r') as file:
#             data = json.load(file)
        
#         # Step 2: Check if user_id exists
#         if user_id in data:
#             # Step 3: Delete the user data
#             del data[user_id]
            
#             # Step 4: Write the updated data back to the file
#             with open(file_path, 'w') as file:
#                 json.dump(data, file, indent=4)
            
#             return f"Data for User ID '{user_id}' has been deleted successfully."
#         else:
#             return f"User ID '{user_id}' not found in the file."
    
#     except FileNotFoundError:
#         return f"The file {file_path} was not found."
#     except json.JSONDecodeError:
#         return "Error decoding JSON. Please check the file format."
#     except Exception as e:
#         return f"An error occurred: {e}"