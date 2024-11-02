import os
import requests
import ydb
import secrets

YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')

IAM = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', json={
    'yandexPassportOauthToken': YANDEX_TOKEN
}).json()

driver_config = ydb.DriverConfig(
    'grpcs://ydb.serverless.yandexcloud.net:2135', '/ru-central1/b1gg2cdr6pv9ip92ua8l/etnhfdk8dqldn3bmf07q',
    credentials=ydb.credentials.AccessTokenCredentials(f'Bearer {IAM['iamToken']}')
)

driver = ydb.Driver(driver_config)
driver.wait(fail_fast=True, timeout=5)
pool = ydb.SessionPool(driver)

def execute_query(query):
    # create the transaction and execute query.
    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

def select_all(tablename):
	query = f"SELECT * FROM {tablename}"
	result = execute_query(query)[0].rows
	return result

def generate_unique_uuid():
    while True:
        # Generate a new UUID
        new_uuid = secrets.randbits(64)

        # Check if this UUID already exists in the database
        res = execute_query(f"SELECT 1 FROM habits WHERE id = {new_uuid}")[0].rows
        if len(res)==0:
            # If no duplicate is found, return the new UUID
            return new_uuid

def add_habit(habit, creation_datetime, user_id, unique_id = generate_unique_uuid()):
	query = f"""
	INSERT INTO habits (id, name, creation_datetime, user_id)
	VALUES ({unique_id}, '{habit}', CAST('{creation_datetime}' AS Timestamp), {user_id});
	"""
	execute_query(query)

def view_habits(user_id):
	query = f"""
	SELECT name, creation_datetime, last_updated, type, trigger_type, 
	trigger_action_desc, repetition_reminder_time, trigger_reminder_time, 
	linked_habit, avoid_trigger_notif_time, ignore_trigger_notif_time, habit_hardening_desc, single_notif_time 
	FROM habits WHERE user_id={user_id}
	"""
	result = execute_query(query)[0].rows
	return result

if __name__=="__main__":
	res = select_all("habits")
	print(generate_unique_uuid())