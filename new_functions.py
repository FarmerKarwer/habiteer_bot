import json
import boto3
import os

s3 = boto3.client(
    's3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=os.getenv('ACCESS_KEY'),
    aws_secret_access_key=os.getenv('SECRET_KEY')
)
bucket_name = os.getenv('BUCKET')



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
