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

def load_json():
    try:
        obj = s3.get_object(Bucket=bucket_name, Key="callback_history.json")
        file_content = obj['Body'].read().decode('utf-8')
        users_data = json.loads(file_content) if file_content else []
        return users_data
    except s3.exceptions.NoSuchKey:
        users_data = []
        return users_data
    
def append_to_json(new_data):
    users_data = load_json()

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