"""
This module provides functionality to send reminders to users.
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


def send_daily_report():
	reports = db.view_all_reports()
	for report in reports:
		report_weekday = json.loads(report["on_weekdays"])
		report_time = report["on_time"]
		
		user_now = get_user_time_now(report["user_id"])
		user_weekday_number = user_now.weekday() + 1
		user_time_hhmm = user_now.strftime("%H:%M")

		is_time_to_send = (user_time_hhmm == report_time) and (user_weekday_number in report_weekday)
		is_time_to_send = True # get rid of this line in production

		if is_time_to_send:
			tied_habits = db.get_user_habits_linked_to_report(report["id"])
			if len(tied_habits)==0:
				continue
			elif len(tied_habits)==1:
				habit_id = tied_habits[0]["h.id"]
				habit_info = db.get_habit_by_id(habit_id)[0]
				chat_id = report["user_id"]
				reply = get_reply('report').replace('[habit]', habit_info["name"])
				keyboard = get_button('scr_report')
				continue
				send_text_message(reply, chat_id, keyboard=keyboard)
			else:
				habit_id = tied_habits[0]["id"]
				chat_id = report["user_id"]
				reply = get_reply('report').replace('[habit]', db.get_habit_name(habit_id))
				keyboard = get_button('scr_report')
				continue
				send_text_message(reply, chat_id, keyboard=keyboard)

def send_srbai_report():
	chat_id = 940985788
	reply = get_reply('srbai_report').replace('[habit]', "тестовая привычка")
	send_text_message(reply, chat_id, keyboard=get_button('scr_srbai_report'))

def send_repetition_reminder():
	pass

def send_trigger_reminder():
	pass

def send_single_notification():
	pass

def send_avoid_trigger_reminder():
	pass

if __name__=="__main__":
	send_daily_report()