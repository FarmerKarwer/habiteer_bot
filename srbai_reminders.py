"""
This module provides functionality to send SRBAI reminders to users.
"""
import datetime
import json
import random
from zoneinfo import ZoneInfo

from src.database import DatabaseClient
from src.cache_manager import CacheManager
from src.tg_methods import send_text_message
from src.config import REPORT_REPLIES_FILEPATH, REPORT_BUTTONS_FILEPATH

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

replies = load_json(REPORT_REPLIES_FILEPATH)
db = DatabaseClient()
cache = CacheManager()

def get_button(screen_name, buttons_filepath=REPORT_BUTTONS_FILEPATH):
	"""Retrieves the button configuration for a given screen."""
	buttons = load_json(buttons_filepath)
	return json.dumps(buttons[screen_name])

def get_reply(screen_name):
	return random.choice(replies[screen_name])

def get_user_time_now(user_id):
	"""
	Get the current time for a user based on their timezone.

	Args:
		user_id (int): The ID of the user.

	Returns:
		datetime: The current datetime for the user in their timezone.

	Notes:
		- If the user's timezone is not found in the database, it defaults to "Europe/Moscow".
		- The user's timezone is expected to be stored in the database as a string in the format "utc±offset".
	"""
	user_utc = db.get_user_property(user_id, "timezone")
	if user_utc is None:
		user_timezone = ZoneInfo("Europe/Moscow")
	else:
		offset_hours = int(user_utc.replace("utc", ""))
		tz_name = f"Etc/GMT{'+' if offset_hours < 0 else '-'}{abs(offset_hours)}"
		user_timezone = ZoneInfo(tz_name)
	return datetime.datetime.now(user_timezone)

def is_time_to_send(started_tracking_at, status):
	"""
    Check if it is time to send the SRBAI report.

    Args:
        started_tracking_at (int): The timestamp in microseconds since the Unix epoch when the user started tracking the habit.
		status (str): The status of the habit.

    Returns:
        bool: True if at least one day has passed since started_tracking_at, False otherwise.
    """
	
	# Convert microseconds to seconds and then to a datetime object.
	start_dt = datetime.datetime.fromtimestamp(started_tracking_at / 1e6)
	# Get the current datetime.
	now_dt = datetime.datetime.now()
	# Calculate the time difference.
	days_passed = (now_dt - start_dt).days
	
	if status in ("started", "srbai_reschedule_1m") and days_passed==30:
		return True
	elif status=="srbai_reschedule_1d" and days_passed==1:
		return True
	else:
		return False

def send_srbai_report():
	all_eligible_habits = db.get_all_habit_ids_eligible_for_srbai()
	for habit in all_eligible_habits:
		habit_id = habit['id']
		latest_log = db.get_latest_habit_log_for_srbai(habit_id)
		if latest_log:
			status = latest_log[0]['status']
			started_tracking_at = latest_log[0]['timestamp']
			if is_time_to_send(started_tracking_at, status)==False:# Change to True in production
				habit_info = db.get_habit_by_id(habit_id)[0]
				chat_id = habit_info['user_id']
				reply = get_reply('srbai_report').replace('[habit]', habit_info['name'])
				send_text_message(reply, chat_id, keyboard=get_button('scr_srbai_report'))
	
if __name__=="__main__":
	send_srbai_report()