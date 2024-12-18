import os
import requests
import ydb
import secrets

class DatabaseClient:
	def __init__(self):
		self.YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')
		self.IAM = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', 
			json={'yandexPassportOauthToken': self.YANDEX_TOKEN}).json()

		driver_config = ydb.DriverConfig(
			'grpcs://ydb.serverless.yandexcloud.net:2135', 
			'/ru-central1/b1gg2cdr6pv9ip92ua8l/etnhfdk8dqldn3bmf07q',
			credentials=ydb.credentials.AccessTokenCredentials(f'Bearer {self.IAM['iamToken']}')
			)

		driver = ydb.Driver(driver_config)
		driver.wait(fail_fast=True, timeout=5)
		self.pool = ydb.SessionPool(driver)

	def execute_query(self, query):
		# create the transaction and execute query.
		return self.pool.retry_operation_sync(lambda s: s.transaction().execute(
			query,
			commit_tx=True,
			settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
			))

	def select_all(self, tablename):
		query = f"SELECT * FROM {tablename}"
		result = self.execute_query(query)[0].rows
		return result

	def generate_unique_uuid(self):
		while True:
			# Generate a new UUID
			new_uuid = secrets.randbits(64)

			# Check if this UUID already exists in the database
			res = self.execute_query(f"SELECT 1 FROM habits WHERE id = {new_uuid}")[0].rows
			if len(res)==0:
				# If no duplicate is found, return the new UUID
				return new_uuid

	def add_habit(self, habit, creation_datetime, user_id, unique_id=None, aspiration=None):
		if unique_id is None:
			unique_id = self.generate_unique_uuid()
		query = f"""
		INSERT INTO habits (id, name, creation_datetime, user_id, aspiration)
		VALUES ({unique_id}, '{habit}', CAST('{creation_datetime}' AS Timestamp), {user_id}, '{aspiration}');
		"""
		self.execute_query(query)

	def update_habit(self, unique_id, column, value):
		query = f"""
		UPDATE habits
		SET {column} = {value}
		WHERE id={unique_id};
		"""
		self.execute_query(query)

	def view_habits(self, user_id):
		query = f"""
		SELECT * 
		FROM habits WHERE user_id={user_id}
		"""
		result = self.execute_query(query)[0].rows
		return result

	def delete_habit(self, unique_id):
		query = f"""
		DELETE FROM habits WHERE id={unique_id}
		"""
		self.execute_query(query)

	def delete_user_data(self, user_id):
		query = f"""
		DELETE FROM habits WHERE user_id={user_id}
		"""
		self.execute_query(query)

if __name__=="__main__":
	db = DatabaseClient()
	res = db.select_all("habits")
	print(res)
	print(db.generate_unique_uuid())