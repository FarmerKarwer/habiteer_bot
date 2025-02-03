from dotenv import load_dotenv
import boto3
import os

load_dotenv()

class CacheManager:
    def __init__(self, table_name):
        self.table = boto3.resource(
            'dynamodb',
            endpoint_url='https://docapi.serverless.yandexcloud.net/ru-central1/b1gg2cdr6pv9ip92ua8l/etnhfdk8dqldn3bmf07q',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name='ru-central1'
        ).Table('Cache/'+table_name)

    # Save data to the table
    def save(self, user_id, value, ttl=None):
        item = {'user_id': user_id, 'data': value}
        if ttl:
            item['ttl'] = ttl  # Optional TTL field
        self.table.put_item(Item=item)

    # Get data from the table
    def get(self, user_id):
        response = self.table.get_item(Key={'user_id': user_id})
        return response.get('Item')

    # Delete data from the table
    def delete(self, user_id):
        self.table.delete_item(Key={'user_id': user_id})

if __name__ == "__main__":
    cache = CacheManager('previous_messages')
    res = cache.get(123)
    print(res)
