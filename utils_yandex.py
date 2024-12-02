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

    
def update_callback_history(new_data):
    try:
        obj = s3.get_object(Bucket=bucket_name, Key="callback_history.json")
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
        Key="callback_history.json",
        Body=json.dumps(users_data)
        )

def get_cached_data(user_id, chat_id, property):
    filename = ''
    
    try:
        # Get object from S3
        obj = s3.get_object(Bucket=bucket_name, Key=filename)
        file_content = obj['Body'].read().decode('utf-8')
        data = json.loads(file_content) if file_content else []
        
        # Find the entry that matches the specified user_id and chat_id
        for entry in data:
            if entry.get("user_id") == user_id and entry.get("chat_id") == chat_id:
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

def delete_user_records(user_id):
    filename = ''

    
    try:
        # Get object from S3
        obj = s3.get_object(Bucket=bucket_name, Key=filename)
        file_content = obj['Body'].read().decode('utf-8')
        data = json.loads(file_content) if file_content else []
        
        # Filter out records with the specified user_id
        updated_data = [user for user in data if user['user_id'] != user_id]
        
        # Save updated data back to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
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
