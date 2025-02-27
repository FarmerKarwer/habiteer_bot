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

def is_time_to_send(report):
	report_weekday = json.loads(report["on_weekdays"])
	report_time = report["on_time"]
	
	user_now = get_user_time_now(report["user_id"])
	user_weekday_number = user_now.weekday() + 1
	user_time_hhmm = user_now.strftime("%H:%M")

	is_time_to_send = (user_time_hhmm == report_time) and (user_weekday_number in report_weekday)
	return is_time_to_send


def send_daily_report():
	reports = db.view_all_reports()
	for report in reports:
		if is_time_to_send(report)==False: # Remove ==False in production
			tied_habits = db.get_user_habits_linked_to_report(report["id"])
			if len(tied_habits)==0:
				continue
			elif len(tied_habits)==1:
				habit_id = tied_habits[0]["h.id"]
				habits_info = db.get_habit_by_id(habit_id)
				habit_info = habits_info[0]
				cache.save_daily_report_info(report["user_id"], one_habit=True, data=habits_info)

				chat_id = report["user_id"]
				reply = get_reply('report').replace('[habit]', habit_info["name"])
				keyboard = get_button('scr_report')
				send_text_message(reply, chat_id, keyboard=keyboard)
			else:
				habits_info = []
				for habit in tied_habits:
					habit_id = habit["h.id"]
					habit_info = db.get_habit_by_id(habit_id)[0]
					habits_info.append(habit_info)
				cache.save_daily_report_info(report["user_id"], one_habit=False, data=habits_info)

				habit_id = tied_habits[0]["h.id"]
				habit_info = db.get_habit_by_id(habit_id)[0]
				chat_id = report["user_id"]
				reply = get_reply('report').replace('[habit]', habit_info["name"])
				keyboard = get_button('scr_report')
				send_text_message(reply, chat_id, keyboard=keyboard)

def send_repetition_reminder():
	habits = db.select_all("habits")
	for habit in habits:
		user_id = habit["user_id"]
		if user_id!=940985788: #Remove this if statement in production
			continue
		reminder_datetime = habit["repetition_reminder_time"]
		if reminder_datetime is None or habit["status"]!="pending":
			continue
		user_now = get_user_time_now(user_id)
		reminder_minutes = reminder_datetime// 60
		user_now_minutes = int(user_now.replace(tzinfo=datetime.timezone.utc).timestamp() // 60)
		
		is_time_to_send = reminder_minutes==user_now_minutes

		if is_time_to_send==False:# Remove ==False in production
			chat_id = user_id
			reply = get_reply('repetition_reminder').replace('[habit]', habit["name"])
			keyboard = get_button('scr_repetition_reminder')
			send_text_message(reply, chat_id, keyboard=keyboard)

			new_data = {
			"habit_id":habit['id'],
			"habit_name": habit['name'].capitalize(),
			"status":habit['status'],
			"aspiration":habit['aspiration'],
			"report_name":None
		}

			cache.save_updating_habit_info(user_id, new_data)

def send_single_notification():
	habits = db.select_all("habits")
	for habit in habits:
		user_id = habit["user_id"]
		if user_id!=940985788: #Remove this if statement in production
			continue
		reminder_datetime = habit["single_notif_time"]
		if reminder_datetime is None:
			continue
		user_now = get_user_time_now(user_id)
		reminder_minutes = reminder_datetime// 60
		user_now_minutes = int(user_now.replace(tzinfo=datetime.timezone.utc).timestamp() // 60)
		
		is_time_to_send = reminder_minutes==user_now_minutes

		if is_time_to_send==False:# Remove ==False in production
			chat_id = user_id
			reply = get_reply('one_time_habit_reminder').replace('[habit]', habit["name"])
			keyboard = get_button('scr_one_time_habit_reminder')
			send_text_message(reply, chat_id, keyboard=keyboard)

			new_data = {
			"habit_id":habit['id'],
			"habit_name": habit['name'].capitalize(),
			"status":habit['status'],
			"aspiration":habit['aspiration'],
			"report_name":None
		}

			cache.save_updating_habit_info(user_id, new_data)

def send_avoid_trigger_reminder():
	habits = db.select_all("habits")
	for habit in habits:
		user_id = habit["user_id"]
		if user_id!=940985788: #Remove this if statement in production
			continue
		reminder_period = habit["avoid_trigger_notif_period"]
		reminder_time = habit["avoid_trigger_notif_time"]
		if reminder_period is None or reminder_time is None:
			continue
		reminder_period = json.loads(reminder_period)
		user_now = get_user_time_now(user_id)
		user_weekday_number = user_now.weekday() + 1
		user_time_hhmm = user_now.strftime("%H:%M")
		is_time_to_send = (user_time_hhmm == reminder_time) and (user_weekday_number in reminder_period)
		if is_time_to_send==False:# Remove ==False in production
			chat_id = user_id
			if habit["avoid_trigger_notif_text"]:
				reply = habit["avoid_trigger_notif_text"]
			else:
				reply = get_reply('avoid_trigger_reminder')
			keyboard = get_button('scr_avoid_trigger_reminder')
			send_text_message(reply, chat_id, keyboard=keyboard)


def send_trigger_reminder():
	habits = db.select_all("habits")
	for habit in habits:
		user_id = habit["user_id"]
		if user_id!=940985788: #Remove this if statement in production
			continue
		reminder_period = habit["trigger_reminder_period"]
		reminder_time = habit["trigger_reminder_time"]
		if reminder_period is None or reminder_time is None:
			continue
		reminder_period = json.loads(reminder_period)
		user_now = get_user_time_now(user_id)
		user_weekday_number = user_now.weekday() + 1
		user_time_hhmm = user_now.strftime("%H:%M")
		is_time_to_send = (user_time_hhmm == reminder_time) and (user_weekday_number in reminder_period)
		if is_time_to_send==False:# Remove ==False in production
			chat_id = user_id
			trigger = habit["trigger_action_desc"]
			habit_name = habit["name"]
			reply = get_reply('trigger_reminder').replace('[trigger]', trigger).replace('[habit]', habit_name)
			keyboard = get_button('scr_trigger_reminder')
			send_text_message(reply, chat_id, keyboard=keyboard)

if __name__=="__main__":
	send_repetition_reminder()