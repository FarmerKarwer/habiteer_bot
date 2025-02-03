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

    def save_picking_habit_info(self, data):
        self.picking_habit_table.put_item(Item=data)

    def get_picking_habit_info(self, user_id):
        response = self.picking_habit_table.get_item(Key={'user_id': user_id})
        return response.get('Item')

    def update_picking_habit_info(self, user_id, updates):
        """
        Update specific attributes of an item in the `picking_habit` table.
        
        Args:
            user_id (str): The primary key of the item to update.
            updates (dict): A dictionary of attributes to update.
                            Example: {"aspiration": "I want to be healthy", "habits": '["habit1"]'}
        """
        try:
            # Construct the update expression
            update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
            expression_attr_names = {f"#{k}": k for k in updates.keys()}
            expression_attr_values = {f":{k}": v for k, v in updates.items()}

            response = self.picking_habit_table.update_item(
                Key={'user_id': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attr_names,
                ExpressionAttributeValues=expression_attr_values,
                ReturnValues='UPDATED_NEW'  # Return the updated attributes
            )
            return response.get('Attributes')
        
        except Exception as e:
            print(f"Error updating item: {e}")
            return None

    def delete_picking_habit_info(self, user_id):
        self.picking_habit_table.delete_item(Key={'user_id': user_id})

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
    res = cache.get_picking_habit_info(940985788)
    print(res)
