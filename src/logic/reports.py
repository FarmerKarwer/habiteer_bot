from config import (
	REPORT_REPLIES_FILEPATH, 
	REPORT_BUTTONS_FILEPATH
	)
import json
import random

from database import DatabaseClient
from cache_manager import CacheManager
from common import (switch_screen, 
					get_button, 
					load_json, 
					calculate_streak, 
					get_days_string, 
					calculate_usual_streak,
					get_consecutive_skipped_days_for_habit
					)

replies = load_json(REPORT_REPLIES_FILEPATH)
db = DatabaseClient()
cache = CacheManager() 

def get_reply(screen_name):
	return random.choice(replies[screen_name])

def show_report_to_do(user_id, chat_id, message_id):
	habit_idx = cache.get_current_habit_idx(user_id)
	habit_name = cache.get_daily_report_info(user_id, habit_idx).get("name", None)
	reply = get_reply("report_next").replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_report', REPORT_BUTTONS_FILEPATH))

def show_report_done(user_id, chat_id, message_id, timestamp):
	habit_idx = cache.get_current_habit_idx(user_id)
	habit_id = cache.get_daily_report_info(user_id, habit_idx).get("id", None)
	habit_name = cache.get_daily_report_info(user_id, habit_idx).get("name", None)
	report_id = db.get_habit_by_id(habit_id)[0].get("report_id", None)
	status = "completed"
	habit_status = "marked"

	db.add_habit_log(user_id, habit_id, status, timestamp)
	
	logs = db.get_habit_logs_for_habit(habit_id, status="completed")
	if report_id:
		period = db.get_report_by_id(report_id)[0]['on_weekdays']
		period = json.loads(period)

		current_streak, max_streak = calculate_streak(logs, timestamp, period).values()
	else:
		current_streak, max_streak = calculate_usual_streak(logs, timestamp).values()

	db.update_habit(habit_id, "status", f"'{habit_status}'")
	db.update_habit(habit_id, "current_streak_days", f"{current_streak}")
	db.update_habit(habit_id, "max_streak_days", f"{max_streak}")

	days_string = get_days_string(current_streak)
	days_string = get_days_string(current_streak)
	
	if cache.is_daily_report_one_habit(user_id) or len(cache.get_daily_report_info(user_id))-(habit_idx+1)==0:
		reply = get_reply("report_done")
		keyboard = get_button("scr_report_done", REPORT_BUTTONS_FILEPATH)
	else:
		reply = get_reply("report_done_to_next")
		keyboard = get_button("scr_report_done_to_next", REPORT_BUTTONS_FILEPATH)
		cache.set_current_habit_idx(user_id, habit_idx+1)
		
	reply = reply.replace('[habit]', habit_name)
	reply = reply.replace('[days]', days_string)
	switch_screen(reply, chat_id, message_id, keyboard=keyboard)		   

def show_report_skipped(user_id, chat_id, message_id, timestamp):
	"""
	Show different buttons depending on the type of trigger (behavior/notification),
	as well as on how many consecutive times the habit was skipped.
	"""
	habit_idx = cache.get_current_habit_idx(user_id)
	habit_id = cache.get_daily_report_info(user_id, habit_idx).get("id", None)
	trigger_type = cache.get_daily_report_info(user_id, habit_idx).get("trigger_type", None)
	report_id = db.get_habit_by_id(habit_id)[0].get("report_id", None)

	logs = db.get_habit_logs_for_habit(habit_id, status="completed")
	started_tracking_at = db.get_habit_logs_for_habit(habit_id, status="started")[0]['timestamp']
	if report_id:
		period = db.get_report_by_id(report_id)[0]['on_weekdays']
		period = json.loads(period)
		consecutive_skipped_days = get_consecutive_skipped_days_for_habit(logs, timestamp, period, started_tracking_at)
	else:
		period = [1,2,3,4,5,6,7]
		consecutive_skipped_days = get_consecutive_skipped_days_for_habit(logs, timestamp, period, started_tracking_at)

	if trigger_type=="behavior":
		if consecutive_skipped_days<=2:
			keyboard = get_button("scr_report_skipped", REPORT_BUTTONS_FILEPATH)
		else:
			keyboard = get_button("scr_report_skipped_2_cons_times", REPORT_BUTTONS_FILEPATH)
	elif trigger_type=="notification":
		if consecutive_skipped_days<=2:
			keyboard = get_button("scr_report_skipped_notif", REPORT_BUTTONS_FILEPATH)
		else:
			keyboard = get_button("scr_report_skipped_notif_2_cons_times", REPORT_BUTTONS_FILEPATH)
	
	switch_screen(get_reply("report_skipped"), chat_id, message_id, keyboard=keyboard)

def show_report_repetition(user_id, chat_id, message_id):
	"""
	Show repetition screen with habit name and trigger description.
	"""

def show_report_change_trigger(user_id, chat_id, message_id):
	"""
	Show enter trigger screen with habit name.
	"""

def show_report_forgetting_repetition(user_id, chat_id, message_id):
	"""
	Show another repetition screen with habit name and trigger description.
	"""

def show_report_enter_trigger(user_id, chat_id, message_id):
	"""
	Show enter trigger screen with habit name.
	"""

def show_report_too_hard(user_id, chat_id, message_id):
	"""
	Show harden habit screen with habit name.
	"""

def show_report_delete_habit_confirmation(user_id, chat_id, message_id):
	"""
	Show deletion confirmation screen with habit name.
	"""

def show_report_habit_deleted(user_id, chat_id, message_id):
	"""
	Show habit deleted screen with habit name.
	"""

def show_report_habit_not_deleted(user_id, chat_id, message_id):
	"""
	Show habit not deleted screen with habit name.
	"""

def show_report_skipped_finish(user_id, chat_id, message_id):
	"""
	Show report is completed with buttons, depending on current habit index.
	If there are multiple habits to evaluate, increment the index by 1.
	"""

def show_report_skipped_finish_refused(user_id, chat_id, message_id):
	"""
	Show report is completed (even though a user did not repeat a habit) with buttons, depending on current habit index.
	If there are multiple habits to evaluate, increment the index by 1.
	"""

def show_report_skipped_notif_finish(user_id, chat_id, message_id):
	"""
	Show report is completed with buttons, depending on current habit index.
	If there are multiple habits to evaluate, increment the index by 1.

	This screen will be shown if a user skipped notification no more than 2 consecutive times.
	"""