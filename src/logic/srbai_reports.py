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
					load_json)

replies = load_json(REPORT_REPLIES_FILEPATH)
db = DatabaseClient()
cache = CacheManager() 

def get_reply(screen_name):
	return random.choice(replies[screen_name])

def show_srbai_report(user_id, chat_id, message_id):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	habit_name = cache.get_srbai_report_info(user_id, habit_idx).get("name", None)
	if habit_idx==0:
		reply = get_reply("srbai_report").replace('[habit]', habit_name)
	else:
		reply = get_reply("srbai_report_next").replace('[habit]', habit_name)
	
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_srbai_report', REPORT_BUTTONS_FILEPATH))

def show_srbai_tomorrow(user_id, chat_id, message_id, timestamp):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	habit_id = cache.get_srbai_report_info(user_id, habit_idx).get("id")
	keyboard = get_ending_keyboard(habit_idx, user_id, "scr_srbai_tomorrow")
	
	db.add_habit_log(user_id, habit_id, "srbai_reschedule_1d", timestamp)
	switch_screen(get_reply("srbai_tomorrow"), chat_id, message_id, keyboard=keyboard)

def show_srbai_in_a_month(user_id, chat_id, message_id, timestamp):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	habit_id = cache.get_srbai_report_info(user_id, habit_idx).get("id")
	keyboard = get_ending_keyboard(habit_idx, user_id, "scr_srbai_month_later")
	
	db.add_habit_log(user_id, habit_id, "srbai_reschedule_1m", timestamp)
	switch_screen(get_reply("srbai_month_later"), chat_id, message_id, keyboard=keyboard)

def show_srbai_question_1(user_id, chat_id, message_id):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	habit_name = cache.get_srbai_report_info(user_id, habit_idx).get("name", None)
	
    # Check if the habit was already evaluated
	srbai_list = cache.get_srbai_report_info(user_id, habit_idx).get("srbai", None)
	if srbai_list is None:
		cache.update_srbai_report_info(user_id, habit_idx, "srbai", [])
	elif len(srbai_list)>0:
		srbai_list.pop()
		cache.update_srbai_report_info(user_id, habit_idx, "srbai", srbai_list)
	
	reply = get_reply("srbai_report_1").replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_srbai_report_1', REPORT_BUTTONS_FILEPATH))

def show_srbai_question_2(user_id, chat_id, message_id, callback_data):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	habit_name = cache.get_srbai_report_info(user_id, habit_idx).get("name", None)
	if callback_data == "scr_srbai_report_2":
		srbai_list = cache.get_srbai_report_info(user_id, habit_idx).get("srbai")
		srbai_list.pop()
		cache.update_srbai_report_info(user_id, habit_idx, "srbai", srbai_list)
	else:
		srbai = int(callback_data.split("_")[-1])
		srbai_list = cache.get_srbai_report_info(user_id, habit_idx).get("srbai")
		srbai_list.append(srbai)
		cache.update_srbai_report_info(user_id, habit_idx, "srbai", srbai_list)
	
	reply = get_reply("srbai_report_2").replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_srbai_report_2', REPORT_BUTTONS_FILEPATH))

def show_srbai_question_3(user_id, chat_id, message_id, callback_data):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	habit_name = cache.get_srbai_report_info(user_id, habit_idx).get("name", None)
	if callback_data == "scr_srbai_report_3":
		srbai_list = cache.get_srbai_report_info(user_id, habit_idx).get("srbai")
		srbai_list.pop()
		cache.update_srbai_report_info(user_id, habit_idx, "srbai", srbai_list)
	else:
		srbai = int(callback_data.split("_")[-1])
		srbai_list = cache.get_srbai_report_info(user_id, habit_idx).get("srbai")
		srbai_list.append(srbai)
		cache.update_srbai_report_info(user_id, habit_idx, "srbai", srbai_list)
	
	reply = get_reply("srbai_report_3").replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_srbai_report_3', REPORT_BUTTONS_FILEPATH))

def show_srbai_question_4(user_id, chat_id, message_id, callback_data):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	habit_name = cache.get_srbai_report_info(user_id, habit_idx).get("name", None)
	if callback_data == "scr_srbai_report_4":
		srbai_list = cache.get_srbai_report_info(user_id, habit_idx).get("srbai")
		srbai_list.pop()
		cache.update_srbai_report_info(user_id, habit_idx, "srbai", srbai_list)
	else:
		srbai = int(callback_data.split("_")[-1])
		srbai_list = cache.get_srbai_report_info(user_id, habit_idx).get("srbai")
		srbai_list.append(srbai)
		cache.update_srbai_report_info(user_id, habit_idx, "srbai", srbai_list)
	
	reply = get_reply("srbai_report_4").replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_srbai_report_4', REPORT_BUTTONS_FILEPATH))

def show_srbai_result(user_id, chat_id, message_id, timestamp, callback_data):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	habit_id = cache.get_srbai_report_info(user_id, habit_idx).get("id")
	srbai = int(callback_data.split("_")[-1])
	srbai_list = cache.get_srbai_report_info(user_id, habit_idx).get("srbai")
	srbai_list.append(srbai)
	final_srbai = sum(srbai_list)
	db.save_srbai_info(user_id, habit_id, final_srbai, timestamp)
	if final_srbai>=16:
		keyboard = get_ending_keyboard(habit_idx, user_id, "scr_srbai_high")
		db.update_habit(habit_id, "status", "'finished'")
		db.add_habit_log(user_id, habit_id, "finished", timestamp)
		switch_screen(get_reply("srbai_high"), chat_id, message_id, keyboard=keyboard)
	elif final_srbai>=12 and final_srbai<=15:
		keyboard = get_ending_keyboard(habit_idx, user_id, "scr_srbai_medium")
		db.add_habit_log(user_id, habit_id, "srbai_reschedule_1m", timestamp)
		switch_screen(get_reply("srbai_medium"), chat_id, message_id, keyboard=keyboard)
	else:
		habit_name = cache.get_srbai_report_info(user_id, habit_idx).get("name", None)
		reply = get_reply("srbai_low").replace('[habit]', habit_name)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_srbai_low', REPORT_BUTTONS_FILEPATH))
		
def show_srbai_simplify_habit(user_id, chat_id, message_id):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	habit_name = cache.get_srbai_report_info(user_id, habit_idx).get("name", None)
	reply = get_reply("srbai_too_hard").replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=None)

def show_srbai_habit_changed(user_id, chat_id, message_id, timestamp, text):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	habit_id = cache.get_srbai_report_info(user_id, habit_idx).get("id")
	db.update_habit(habit_id, "name", f"'{text}'")
	keyboard = get_ending_keyboard(habit_idx, user_id, "scr_srbai_too_hard_done")
	reply = get_reply("srbai_too_hard_done").replace('[habit]', text)
	switch_screen(reply, chat_id, message_id, keyboard=keyboard)
	
def show_srbai_habit_refused(user_id, chat_id, message_id):
	habit_idx = cache.get_current_srbai_habit_idx(user_id)
	keyboard = get_ending_keyboard(habit_idx, user_id, "scr_srbai_low_no")
	switch_screen(get_reply("srbai_low_no"), chat_id, message_id, keyboard=keyboard)

def get_ending_keyboard(habit_idx, user_id, screen_name):
	if cache.is_srbai_report_one_habit(user_id) or len(cache.get_srbai_report_info(user_id))-(habit_idx+1)==0:
		keyboard = get_button(screen_name, REPORT_BUTTONS_FILEPATH)
	else:
		keyboard = get_button(screen_name+"_to_next", REPORT_BUTTONS_FILEPATH)
		cache.set_current_srbai_habit_idx(user_id, habit_idx+1)
	return keyboard
