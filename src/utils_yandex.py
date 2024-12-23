import json
import os
import boto3

s3 = boto3.client(
    's3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=os.getenv('ACCESS_KEY'),
    aws_secret_access_key=os.getenv('SECRET_KEY')
)
bucket_name = os.getenv('BUCKET')

def save_data_to_cache(filepath, data):
    update_callback_history(filepath, data)
    print(f"Data have been saved successfully to {filepath}")
    
def update_callback_history(filepath, new_data):
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=filepath)
        file_content = obj['Body'].read().decode('utf-8')
        users_data = json.loads(file_content) if file_content else []
    except s3.exceptions.NoSuchKey:
        users_data = []

    # Check if user already exists
    found = False
    for i, user_data in enumerate(users_data):
        if user_data['user_id'] == new_data['user_id']:
            users_data[i] = new_data  # Update existing user
            found = True
            break
        
    # Add new user if not found
    if not found:
        users_data.append(new_data)

    s3.put_object(
        Bucket=bucket_name,
        Key=filepath,
        Body=json.dumps(users_data)
        )

def update_user_value(object_key, user_id, key, new_value):
    """
    Update the specified key with a new value for a given user in JSON data
    stored in an S3 object.
    
    :param object_key: The key (path) of the JSON file in S3.
    :param user_id: The ID of the user whose value should be updated.
    :param key: The key in the user's data to update.
    :param new_value: The new value to assign to the specified key.
    """
    try:
        # Step 1: Load the JSON data from the S3 object
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        data = json.loads(response['Body'].read().decode('utf-8'))
        
        # Step 2: Find the user with the specified user_id
        user_found = False
        for user in data:
            if user['user_id'] == user_id:
                # Step 3: Update the specified key with the new value
                user[key] = new_value
                user_found = True
                break

        # Step 4: Save the updated JSON back to the S3 object
        if user_found:
            s3.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=json.dumps(data, ensure_ascii=False, indent=4),
                ContentType='application/json'
            )
            print(f"Updated {key} for user_id {user_id} to {new_value}.")
        else:
            print(f"User with user_id {user_id} not found.")
    except s3.exceptions.NoSuchKey:
        print(f"The object with key '{object_key}' does not exist in bucket '{bucket_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_cached_data(filepath, user_id, chat_id, property):
    # Extract filename from filepath
    
    try:
        # Get object from S3
        obj = s3.get_object(Bucket=bucket_name, Key=filepath)
        file_content = obj['Body'].read().decode('utf-8')
        data = json.loads(file_content) if file_content else []
        
        # Find the entry that matches the specified user_id and chat_id
        for entry in data:
            if entry.get("user_id") == user_id:
                return entry.get(property)
                
        # Return None if no matching entry is found
        print("No matching entry found for the given user_id and chat_id.")
        return None
        
    except s3.exceptions.NoSuchKey:
        print(f"Error: File does not exist in bucket.")
        return None
    except json.JSONDecodeError:
        print(f"Error: JSON file is empty or corrupted.")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return None

def delete_user_records(filepath, user_id):
    
    try:
        # Get object from S3
        obj = s3.get_object(Bucket=bucket_name, Key=filepath)
        file_content = obj['Body'].read().decode('utf-8')
        data = json.loads(file_content) if file_content else []
        
        # Filter out records with the specified user_id
        updated_data = [user for user in data if user['user_id'] != user_id]
        
        # Save updated data back to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=filepath,
            Body=json.dumps(updated_data)
        )
        
        # Provide feedback
        if len(data) != len(updated_data):
            print(f"Deleted records for user_id {user_id}.")
        else:
            print(f"No records found for user_id {user_id}.")
            
    except s3.exceptions.NoSuchKey:
        print(f"Error: File does not exist in bucket.")
    except json.JSONDecodeError:
        print(f"Error: JSON file is empty or corrupted.")
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")