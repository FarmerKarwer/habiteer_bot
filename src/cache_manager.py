from dotenv import load_dotenv
import boto3
import os

load_dotenv()

class CacheManager:
    def __init__(self):
        self.connection = boto3.resource(
            'dynamodb',
            endpoint_url='https://docapi.serverless.yandexcloud.net/ru-central1/b1gg2cdr6pv9ip92ua8l/etnhfdk8dqldn3bmf07q',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name='ru-central1'
        )

        self.message_history_table = self.connection.Table('Cache/previous_messages')
        self.button_selection_table = self.connection.Table('Cache/button_selection')
        self.key_phrase_table = self.connection.Table('Cache/key_phrase')
        self.picking_habit_table = self.connection.Table('Cache/picking_habit')
        self.creating_report_table = self.connection.Table('Cache/creating_report')
        self.updating_habit_table = self.connection.Table('Cache/updating_habit')

    def save_previous_message(self, data):
        self.message_history_table.put_item(Item=data)

    def get_previous_message(self, user_id):
        response = self.message_history_table.get_item(Key={'user_id': user_id})
        return response.get('Item')

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
    cache = CacheManager()
    res = cache.get_previous_message(940985788)
    print(res)
