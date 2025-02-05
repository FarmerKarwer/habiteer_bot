from dotenv import load_dotenv
import json
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

    def save_updating_habit_info(self, user_id, data):
        item = {'user_id': user_id, 'data': json.dumps(data)}
        self.updating_habit_table.put_item(Item=item)

    def get_updating_habit_info(self, user_id, habit_property=None):
        response = self.updating_habit_table.get_item(Key={'user_id': user_id}).get('Item')
        if habit_property:
            return json.loads(response.get('data')).get(habit_property, None)
        return json.loads(response.get('data'))

    def update_updating_habit_info(self, user_id, key, value):
        try:
            response = self.updating_habit_table.get_item(Key={'user_id': user_id})
            item = response.get('Item')
            if not item:
                print(f"No item found for user_id: {user_id}")
                return

            # Deserialize the JSON string into a Python dictionary
            data = json.loads(item.get('data', '{}'))

            # Update the specific key-value pair
            data[key] = value

            # Serialize the dictionary back into a JSON string
            updated_data_json = json.dumps(data)

            # Update the item in the table
            self.updating_habit_table.update_item(
                Key={'user_id': user_id},
                UpdateExpression="SET #data = :data",
                ExpressionAttributeNames={
                    '#data': 'data'  # Use ExpressionAttributeNames to handle reserved keywords
                },
                ExpressionAttributeValues={
                    ':data': updated_data_json
                }
            )
            print(f"Data updated successfully for user_id: {user_id}")
        except Exception as e:
            print(f"Error updating data for user_id {user_id}: {e}")

    def delete_updating_habit_info(self, user_id):
        self.updating_habit_table.delete_item(Key={'user_id': user_id})

    def get_button_selection(self, user_id, prop=None):
        response = self.button_selection_table.get_item(Key={'user_id': user_id}).get('Item')
        if prop and response:
            response = response.get(prop, None)
            if prop=="user_selections":
                response = json.loads(response)
            return response
        return response

    def save_button_selection(self, data):
        self.button_selection_table.put_item(Item=data)

    def update_button_selection(self, user_id, updates):
        """
        Update specific attributes of an item in the `button_selection` table.
        
        Args:
            user_id (str): The primary key of the item to update.
            updates (dict): A dictionary of attributes to update.
                            Example: {"previous_screen": "scr_2", "user_selections": '["sat", "sun"]'}
        """
        try:
            # Construct the update expression
            update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
            expression_attr_names = {f"#{k}": k for k in updates.keys()}
            expression_attr_values = {f":{k}": v for k, v in updates.items()}

            response = self.button_selection_table.update_item(
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

    def delete_button_selection(self, user_id):
        self.button_selection_table.delete_item(Key={'user_id': user_id})

    # Save data to the table
    def save(self, user_id, value):
        item = {'user_id': user_id, 'data': value}
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
    res = cache.get_updating_habit_info(940985788)
    print(res)
