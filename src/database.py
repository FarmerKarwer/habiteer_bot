import os
import requests
import ydb
import secrets
from datetime import datetime

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

	def select_user(self, user_id):
		query = f"SELECT * FROM users WHERE id={user_id}"
		result = self.execute_query(query)[0].rows
		return result

	def add_user(self, user_id, username, first_name, last_name, language, created_at):
		query = f"""
		INSERT INTO users (id, username, first_name, last_name, language, created_at)
		VALUES ({user_id}, {username}, {first_name}, {last_name}, {language}, {created_at});
		"""
		self.execute_query(query)

	def add_habit(self, habit, creation_datetime, user_id, aspiration=None):
		unique_id = self.autoincrement_id("id", "habits")
		query = f"""
		INSERT INTO habits (id, name, creation_datetime, user_id, aspiration)
		VALUES ({unique_id}, '{habit}', CAST('{creation_datetime}' AS Timestamp), {user_id}, '{aspiration}');
		"""
		self.execute_query(query)

	def add_habit_log(self, user_id, habit_id, status, timestamp):
		unique_id = self.autoincrement_id("id", "habit_logs")
		date = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
		query = f"""
		INSERT INTO habit_logs (id, user_id, habit_id, date, status, timestamp)
		VALUES ({unique_id}, {user_id}, {habit_id}, CAST('{date}' AS Date), '{status}', CAST('{timestamp}' AS Timestamp));
		"""
		self.execute_query(query)

	def update_habit(self, unique_id, column, value):
		query = f"""
		UPDATE habits
		SET {column} = {value}
		WHERE id={unique_id};
		"""
		self.execute_query(query)

	def update_habit_with_null(self, unique_id, column):
		query = f"""
		UPDATE habits
		SET {column} = NULL
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

	def get_habit_by_id(self, habit_id):
		query = f"""
		SELECT * 
		FROM habits WHERE id={habit_id}
		"""
		result = self.execute_query(query)[0].rows
		return result

	def get_habit_logs_for_habit(self, user_id, habit_id, status=None):
		query = f"""
		SELECT * 
		FROM habit_logs WHERE user_id={user_id} AND habit_id={habit_id} 
		"""
		if status:
			query = f"""
			SELECT * 
			FROM habit_logs WHERE user_id={user_id} AND habit_id={habit_id} AND status='{status}'
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

	def view_reports(self, user_id):
		query = f"""
		SELECT * 
		FROM user_reports WHERE user_id={user_id}
		"""
		result = self.execute_query(query)[0].rows
		return result

	def add_report(self, user_id, timestamp, on_weekdays, on_time):
		unique_id = self.autoincrement_id("id", "user_reports")
		existing_reports_num = len(self.view_reports(user_id))
		name = f"Отчет {existing_reports_num+1}"
		date = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
		query = f"""
		INSERT INTO user_reports (id, user_id, name, start_date, created_at, on_weekdays, on_time)
		VALUES ({unique_id}, {user_id}, '{name}', CAST('{date}' AS Date), CAST('{timestamp}' AS Timestamp), '{on_weekdays}', '{on_time}');
		"""
		self.execute_query(query)

	def update_report(self, report_id, column, value):
		query = f"""
		UPDATE user_reports
		SET {column} = {value}
		WHERE id={report_id};
		"""
		self.execute_query(query)

	def get_report(self, user_id, report_num):
		name = f"Отчет {report_num}"
		query = f"""
		SELECT * 
		FROM user_reports WHERE user_id={user_id} AND name='{name}';
		"""
		result = self.execute_query(query)[0].rows
		return result

	def get_report_by_id(self, report_id):
		query = f"""
		SELECT * 
		FROM user_reports WHERE id={report_id};
		"""
		result = self.execute_query(query)[0].rows
		return result

	def get_user_habits_linked_to_report(self, report_id):
		query = f"""
		SELECT h.id
		FROM habits h
		JOIN user_reports ur ON h.report_id = ur.id
		WHERE ur.id = {report_id};
		"""
		result = self.execute_query(query)[0].rows
		return result

	def delete_report(self, report_id):
		query = f"""
		DELETE FROM user_reports WHERE id={report_id};
		"""
		self.execute_query(query)

	def send_review(self, user_id, text, timestamp):
		unique_id = self.autoincrement_id("id", "reviews")
		query = f"""
		INSERT INTO reviews (id, user_id, text, timestamp)
		VALUES ({unique_id}, {user_id}, '{text}', CAST('{timestamp}' AS Timestamp));
		"""
		self.execute_query(query)

	def autoincrement_id(self, col_with_id, tablename):
		query = f"""
		SELECT MAX({col_with_id}) 
		FROM {tablename}
		"""
		max_id = self.execute_query(query)[0].rows[0]['column0']
		return (max_id or 0) + 1

if __name__=="__main__":
	db = DatabaseClient()
	res = db.select_all("habits")
	print(res)