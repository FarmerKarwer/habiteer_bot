import json
import os
import random
import re
from typing import Any, Callable, Dict, List, Optional

import tg_methods
from database import DatabaseClient
from exceptions import (
	ValueOutOfRangeError,
	ListTooShortError,
	ListLengthMismatchError,
)
from recommender import get_ai_response
from utils import (
	load_json,
	save_to_json,
	update_user_value,
	delete_user_records,
	sum_arrays,
	unix_to_timestamp,
	format_numbered_list,
	extract_numbered_items,
	get_cached_data,
	save_data_to_cache,
	check_all_in_range,
	check_matching_lengths,
	check_minimum_length,
	parse_numbers,
	parse_time_from_string,
	weekdays_to_numbers,
)

# Constants for file paths
REPLIES_FILEPATH = "./strings/replies.json"
BUTTONS_FILEPATH = "./strings/buttons.json"
PREMADE_HABITS_FILEPATH = "./strings/premade_habits.json"
PREMADE_TRIGGERS_FILEPATH = "./strings/triggers.json"

CACHE_FILEPATH = "./cache/callback_history.json"
CACHE_PICKHABIT_FILEPATH = "./cache/picking_habit.json"
CACHE_UPDATEHABIT_FILEPATH = "./cache/updating_habit.json"
CACHE_REPORT = "./cache/creating_report.json"
CACHE_KEY_PHRASE = "./cache/key_phrase.json"
CACHE_BUTTON_SELECTION = "./cache/button_selection.json"

# Load JSON data
replies = load_json(REPLIES_FILEPATH)
premade_habits = load_json(PREMADE_HABITS_FILEPATH)
premade_triggers = load_json(PREMADE_TRIGGERS_FILEPATH)
aspirations = list(premade_habits.keys())

# Sets of buttons
callback_predefined_habits = (
	"hab_1", "hab_2", "hab_3", "hab_4", "hab_5", 
	"hab_6", "hab_7", "hab_8", "hab_9", "hab_10"
)

callback_predefined_triggers = (
	"beh_1", "beh_2", "beh_3", "beh_4", "beh_5", 
	"beh_6", "beh_7", "beh_8", "beh_9", "beh_10"
)

callback_suitability_evaluation = (
	"suitability_1", "suitability_2", "suitability_3", "suitability_4", "suitability_5", 
	"suitability_6", "suitability_7", "suitability_8", "suitability_9", "suitability_10"
)

callback_effectiveness_evaluation = (
	"effectiveness_1", "effectiveness_2", "effectiveness_3", "effectiveness_4", "effectiveness_5", 
	"effectiveness_6", "effectiveness_7", "effectiveness_8", "effectiveness_9", "effectiveness_10"
)

callback_weekdays = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")

db = DatabaseClient()

def use_logic(message):
	if button_is_pressed(message):
		message_info = handle_callback_query(message)
		save_data_to_cache(filepath=CACHE_FILEPATH, data=message_info)
	elif text_message_is_entered(message):
		message_info = handle_text_message(message)
		save_data_to_cache(filepath=CACHE_FILEPATH, data=message_info)
	else:
		message_info = handle_unknown_message(message)

def handle_callback_query(message):

	# Getting data
	callback_query_id = message['callback_query']['id']
	callback_data = message['callback_query']['data']
	chat_id = message['callback_query']['message']['chat']['id']
	message_id = message['callback_query']['message']['message_id']
	user_id = message['callback_query']['from']['id']
	unix_timestamp = message['callback_query']['message']['date']
	timestamp = unix_to_timestamp(unix_timestamp)

	previous_screen = get_cached_data(CACHE_FILEPATH, user_id, chat_id, property="callback_data")
	previous_screen_button_selection = get_cached_data(CACHE_BUTTON_SELECTION, user_id, chat_id, property="previous_screen") # Fix logging issue
	if previous_screen:
		is_previous_screen_in_magic_wanding = bool(re.match(r"^scr_12_proxy_\d+$", previous_screen))
	is_callback_in_magic_wanding = bool(re.match(r"^scr_12_proxy_\d+$", callback_data))
	is_callback_in_suitability_eval = bool(re.match(r"^scr_13_proxy_\d+$", callback_data))
	is_callback_in_effectiveness_eval = bool(re.match(r"^scr_14_proxy_\d+$", callback_data))

	def show_callback_reply(screen_id, delete_previous=True):
		switch_screen(replies[screen_id], chat_id, message_id, delete_previous=delete_previous,
						keyboard=get_button(f'scr_{screen_id}'))

	# Actual logic
	DEFAULT_CALLBACK_SCREENS = (
		"scr_1", "scr_2", "scr_5", "scr_6",
		"scr_9", "scr_10", "scr_12", "scr_13", "scr_3_3",
		"scr_16", "scr_17", "scr_19", "scr_22", "scr_22_1",
		 "scr_review", "scr_25", "scr_26", "scr_26_1",
		"scr_28", "scr_30", "scr_31", "scr_32", "scr_33",
		"scr_34", "scr_35", "scr_37", "scr_38", "scr_39",
		"scr_40", "scr_41_add_1", "scr_44", "scr_plug"
		)

	SPECIAL_CALLBACK_HANDLERS = {
	"scr_3": lambda: show_user_habits(user_id, chat_id, message_id),
	"scr_3_1": lambda: get_back_to_habit(callback_data, user_id, chat_id, message_id),
	"scr_4": lambda: show_aspirations(chat_id, message_id),
	"scr_8": lambda: show_is_habit_tiny(user_id, chat_id, message_id),
	"scr_8_1": lambda: show_make_habit_tiny(user_id, chat_id, message_id),
	"scr_11": lambda: show_aspiration_confirmation(chat_id, message_id, user_id, callback_data=callback_data),
	"scr_12_1": lambda: show_ai_recommended_habits(user_id, chat_id, message_id),
	"scr_13": lambda: show_evaluation(callback_data, user_id, chat_id, message_id, type="suitability"),
	"scr_14": lambda: show_evaluation(callback_data, user_id, chat_id, message_id, type="effectiveness"),
	"scr_15": lambda: show_proposed_habits(user_id, chat_id, message_id),
	"scr_18": lambda: show_picked_habits(user_id, chat_id, message_id, timestamp),
	"scr_21": lambda: show_choosing_habit_type(user_id, chat_id, message_id),
	"scr_22_1_1": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_22_1_1'),
	"scr_23": lambda: show_enter_your_trigger(user_id, chat_id, message_id),
	"scr_23_1": lambda: show_premade_triggers(user_id, chat_id, message_id),
	"scr_27": lambda: show_set_trigger_notification_confirmation(user_id, chat_id, message_id),
	"scr_28_1": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_28_1'),
	"scr_review_sent": lambda: show_review_sent(user_id, chat_id, message_id, timestamp),
	"scr_41": lambda: show_all_reports_in_settings(user_id, chat_id, message_id),
	"scr_42": lambda: show_delete_all_data_confirmation(user_id, chat_id, message_id),
	"scr_41_add_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_41_add_2'),
	"no_scr": lambda: tg_methods.delete_message(message_id, chat_id)
	}

	SPECIAL_CALLBACK_SCREENS = SPECIAL_CALLBACK_HANDLERS.keys()
	
	if callback_data in SPECIAL_CALLBACK_SCREENS:
		action = SPECIAL_CALLBACK_HANDLERS.get(callback_data)
		action()

	elif callback_data in callback_predefined_habits:
		show_predefined_habits(callback_data, user_id, chat_id, message_id)

	elif is_callback_in_magic_wanding:
		show_magic_wanding_return_back(callback_data, user_id, chat_id, message_id)

	elif callback_data in callback_suitability_evaluation or is_callback_in_suitability_eval:
		show_evaluation(callback_data, user_id, chat_id, message_id, type="suitability")

	elif callback_data in callback_effectiveness_evaluation or is_callback_in_effectiveness_eval:
		show_evaluation(callback_data, user_id, chat_id, message_id, type="effectiveness")

	elif callback_data in callback_predefined_triggers or callback_data=="scr_24":
		show_habit_repetition(user_id, chat_id, message_id, callback_data=callback_data, text=None)

	elif previous_screen is not None and is_previous_screen_in_magic_wanding and callback_data=="scr_12":
		behavior_options = None
		update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "behavior_options", behavior_options)
		switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('scr_12'))

	elif previous_screen in callback_predefined_habits and callback_data == "scr_12":
		behavior_options = None
		update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "behavior_options", behavior_options)
		switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('9_scr_12'))

	elif previous_screen == "scr_12_1" and callback_data == "scr_12":
		behavior_options = None
		update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "behavior_options", behavior_options)
		switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('scr_12'))

	elif previous_screen=="scr_9" and callback_data=="scr_12":
		switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('9_scr_12'))

	elif previous_screen=="scr_11" and callback_data=="scr_12":
		switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('scr_12'))

	elif previous_screen=="scr_16" and callback_data=="scr_13":
		switch_screen(replies['13'], chat_id, message_id, keyboard=get_button('16_scr_13'))

	elif (previous_screen=="scr_22_1_1" or previous_screen_button_selection=="scr_22_1_1") and callback_data in callback_weekdays:
		show_multiple_selection(user_id, chat_id, message_id, callback_data=callback_data, scr_name='scr_22_1_1')
	elif previous_screen=="scr_22_1" and callback_data=="scr_22_2":
		show_choose_time_for_habit(user_id, chat_id, message_id, "scr_22_2", type="everyday")
	elif previous_screen=="scr_22_1_1" and callback_data=="scr_22_2":
		show_choose_time_for_habit(user_id, chat_id, message_id, "scr_22_2", type="everyday")
	elif previous_screen in callback_weekdays and callback_data=="scr_22_2":
		show_choose_time_for_habit(user_id, chat_id, message_id, "scr_22_2", type="selected_days")

	elif (previous_screen=="scr_28_1"or previous_screen_button_selection=="scr_28_1") and callback_data in callback_weekdays:
		show_multiple_selection(user_id, chat_id, message_id, callback_data=callback_data, scr_name='scr_28_1')
	elif previous_screen=="scr_28" and callback_data=="scr_28_2":
		show_choose_time_for_habit(user_id, chat_id, message_id, "scr_28_2", type="everyday")
	elif previous_screen=="scr_28_1" and callback_data=="scr_28_2":
		show_choose_time_for_habit(user_id, chat_id, message_id, "scr_28_2", type="everyday")
	elif previous_screen in callback_weekdays and callback_data=="scr_28_2":
		show_choose_time_for_habit(user_id, chat_id, message_id, "scr_28_2", type="selected_days")

	elif (previous_screen=="scr_41_add_2"or previous_screen_button_selection=="scr_41_add_2") and callback_data in callback_weekdays:
		show_multiple_selection(user_id, chat_id, message_id, callback_data=callback_data, scr_name='scr_41_add_2')
	elif previous_screen=="scr_41_add_1" and callback_data=="scr_41_add_3":
		show_choose_time_for_report(user_id, chat_id, message_id, "scr_41_add_3", type="everyday")
	elif previous_screen=="scr_41_add_2" and callback_data=="scr_41_add_3":
		show_choose_time_for_report(user_id, chat_id, message_id, "scr_41_add_3", type="everyday")
	elif previous_screen in callback_weekdays and callback_data=="scr_41_add_3":
		show_choose_time_for_report(user_id, chat_id, message_id, "scr_41_add_3", type="selected_days")

	elif callback_data in DEFAULT_CALLBACK_SCREENS:
		screen_id = '_'.join(callback_data.split('_')[1:])
		if screen_id in ("44"):
			show_callback_reply(screen_id, delete_previous=False)
		else:
			show_callback_reply(screen_id)

	else:
		print(callback_data)
		tg_methods.send_text_message(f"Error: unknown callback data", chat_id, protect_content=True)

	# Saving data
	data = {"user_id":user_id,"chat_id":chat_id, "message_id":message_id, "callback_data":callback_data, "text":None}
	return data

def handle_text_input(text, chat_id, message_id, user_id, timestamp, message_info):

		previous_screen = get_cached_data(CACHE_FILEPATH, user_id, chat_id, property="callback_data")
		if previous_screen:
			is_previous_screen_in_magic_wanding = bool(re.match(r"^scr_12_proxy_\d+$", previous_screen))
		else:
			is_previous_screen_in_magic_wanding = False

		if previous_screen=='scr_2':
			show_adding_habit(text, user_id, chat_id, message_id, timestamp)

		elif previous_screen=='scr_3':
			show_habit_info(text, user_id, chat_id, message_id, message_info)

		elif previous_screen=='scr_3_3':
			show_change_habit_aspiration(text, chat_id, message_id, user_id, timestamp)

		elif previous_screen=='scr_8_1':
			show_reminding_options_after_making_habit_tiny(text, chat_id, message_id, user_id)

		elif previous_screen in callback_predefined_habits or previous_screen =="scr_9":
			show_picked_predefined_habits(text, chat_id, message_id, user_id, timestamp, message_info)

		elif previous_screen=='scr_10':
			show_aspiration_confirmation(chat_id, message_id, user_id, text=text)
			
		elif previous_screen=='scr_12' or is_previous_screen_in_magic_wanding:
			show_magic_wanding(text, chat_id, message_id, user_id, message_info)

		elif previous_screen=='scr_17': 
			show_magic_wanding(text, chat_id, message_id, user_id, message_info)

		elif previous_screen=='scr_19':
			show_updated_habitname(text, chat_id, message_id, user_id, timestamp)

		elif previous_screen=='scr_23':
			show_habit_repetition(user_id, chat_id, message_id, callback_data=None, text=text)

		elif previous_screen=='scr_26':
			switch_screen(replies['20'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif previous_screen=='scr_28':
			switch_screen(replies['20'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif previous_screen=='scr_31':
			switch_screen(replies['7'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_7'))

		elif previous_screen=='scr_33':
			switch_screen(replies['36'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_36'))
			message_info["callback_data"]="scr_36"
			print(text)
		elif previous_screen=='scr_35':
			switch_screen(replies['36'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_36'))
			message_info["callback_data"]="scr_36"

		elif previous_screen=='scr_36':
			switch_screen(replies['20'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif previous_screen=='scr_37':
			switch_screen(replies['20'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif previous_screen=='scr_38':
			switch_screen(replies['20'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif previous_screen=='scr_40':
			switch_screen(replies['43'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_43'))

		elif previous_screen=='scr_41_add_3':
			show_add_report(text, chat_id, message_id, user_id, timestamp, message_info)

		elif previous_screen=='scr_42':
			show_user_deletion_screen(text, chat_id, message_id, user_id, message_info)

		elif previous_screen=='scr_44':
			show_updated_habits_after_deletion(text, chat_id, message_id, user_id, message_info)

		elif previous_screen=='scr_review':
			show_review_confirmation(text, chat_id, message_id, user_id, message_info)

		elif previous_screen=='scr_42':
			show_delete_all_user_data(text)

def handle_text_message(message):
	"""Handles the text message from the user."""
	# Extract common data
	chat_id = message['message']['chat']['id']
	text = message['message']['text']
	message_id = message['message']['message_id']
	user_id = message['message']['from']['id']
	unix_timestamp = message['message']['date']
	timestamp = unix_to_timestamp(unix_timestamp)

	message_info = {
	"user_id": user_id,
	"chat_id": chat_id,
	"message_id": message_id,
	"callback_data": None,
	"text": text
	}

	tg_methods.delete_message(message_id-1, chat_id)

	if text=="/start":
		switch_screen(replies['start'], chat_id, message_id, keyboard=get_button('start'))
	else:
		handle_text_input(text, chat_id, message_id, user_id, timestamp, message_info)

	return message_info

def handle_unknown_message(message):
	"""Handles messages that are neither text nor button presses."""
	chat_id = message['message']['chat']['id']
	message_id = message['message']['message_id']
	user_id = message['message']['from']['id']

	tg_methods.send_text_message(replies['unknown_message'], chat_id)
	return {
	"user_id": user_id,
	"chat_id": chat_id,
	"message_id": message_id,
	"callback_data": None,
	"text": None
	}


def show_adding_habit(text, user_id, chat_id, message_id, timestamp):
	new_data = {
			"user_id": user_id,
			"chat_id": chat_id,
			"habit_name": text,
			"habit_number":"no_number"
		}
	db.add_habit(habit=text, creation_datetime=timestamp, user_id=user_id)
	save_data_to_cache(CACHE_UPDATEHABIT_FILEPATH, new_data)
	reply = replies['7'].replace("[habit]", text)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_7'))

def show_user_habits(user_id, chat_id, message_id):
	user_habits = db.view_habits(user_id)
	no_habits = len(user_habits)==0

	if no_habits:
		reply = replies['3_no_habits']
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_3_no_habits'))
	else:
		habit_names = [item['name'] for item in user_habits]
		habit_names_str = format_numbered_list(habit_names)
		reply = replies['3'].replace('[habits]', habit_names_str)
		keyboard = get_button('scr_3')
		switch_screen(reply, chat_id, message_id, keyboard=keyboard)

def show_habit_info(text, user_id, chat_id, message_id, message_info):
	habits = db.view_habits(user_id)
	try:
		habit_idx = int(text)-1
		habit_name = habits[habit_idx].get("name")
		aspiration = habits[habit_idx].get("aspiration")
		status = habits[habit_idx].get("status")
		print(habits[habit_idx])
		if status is None:
			reply = replies['3_1']['not_tracked'].replace('[habit]', habit_name)
			keyboard = get_button('scr_3_1_not_tracked')
		elif status=="tracked":
			reply = replies['3_1']['tracked'].replace('[habit]', habit_name)
			keyboard = get_button('scr_3_1_tracked')

		if aspiration is None or aspiration=="None":
			reply = reply.replace('[aspiration]', '_не указано_')
		else:
			reply = reply.replace('[aspiration]', aspiration)
			keyboard = json.loads(keyboard)
			keyboard['inline_keyboard'][2][0]['text'] = keyboard['inline_keyboard'][2][0]['text'].replace('Добавить', 'Изменить')
			keyboard = json.dumps(keyboard)

		new_data = {
			"user_id": user_id,
			"chat_id": chat_id,
			"habit_number": habit_idx,
			"habit_name": habit_name.capitalize(),
			"status":status,
			"aspiration":aspiration
		}

		save_data_to_cache(CACHE_UPDATEHABIT_FILEPATH, new_data)
		switch_screen(reply, chat_id, message_id, keyboard=keyboard)
	except ValueError:
		habit_names = [item['name'] for item in habits]
		habit_names_str = format_numbered_list(habit_names)
		reply = f"Пожалуйста, введите номер привычки, которую вы хотите выбрать числом.\n\nВаши привычки:\n\n{habit_names_str}"
		switch_screen(reply, chat_id, message_id)
		message_info["callback_data"]="scr_3"
	except IndexError:
		habit_names = [item['name'] for item in habits]
		habit_names_str = format_numbered_list(habit_names)
		reply = f"Такой привычки не существует. Попробуйте ещё раз.\n\nВаши привычки:\n\n{habit_names_str}"
		switch_screen(reply, chat_id, message_id)
		message_info["callback_data"]="scr_3"

def get_back_to_habit(callback_data, user_id, chat_id, message_id):
	message_info = None
	text = str(get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_number")+1)
	show_habit_info(text, user_id, chat_id, message_id, message_info)

def show_choosing_habit_type(user_id, chat_id, message_id):
	habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_name")
	reply = replies['21'].replace('[habit]', habit_name)
	keyboard = get_button('scr_21')
	habit_idx = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_number")
	if habit_idx == "no_number":
		keyboard = json.loads(keyboard)
		del keyboard["inline_keyboard"][3]
		keyboard = json.dumps(keyboard)
	switch_screen(reply, chat_id, message_id, keyboard=keyboard)

def show_is_habit_tiny(user_id, chat_id, message_id):
	habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_name")
	reply = replies['8'].replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_8'))

def show_make_habit_tiny(user_id, chat_id, message_id):
	habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_name")
	reply = replies['8_1'].replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_8_1'))

def show_reminding_options_after_making_habit_tiny(text, chat_id, message_id, user_id):
	new_habit_name = text
	update_user_value(CACHE_UPDATEHABIT_FILEPATH, user_id, "new_habit_name", new_habit_name)
	switch_screen(replies['22'], chat_id, message_id, keyboard=get_button('scr_22'))

def show_choose_weekdays(user_id, chat_id, message_id, scr_name):
	screen_id = '_'.join(scr_name.split('_')[1:])
	delete_user_records(CACHE_BUTTON_SELECTION, user_id)
	switch_screen(replies[screen_id], chat_id, message_id, keyboard=get_button(scr_name))

def show_multiple_selection(user_id, chat_id, message_id, callback_data, scr_name):
	additional_actions = json.loads(get_button(scr_name))['inline_keyboard'][2:]
	select_multiple_days(callback_data, additional_actions, user_id, chat_id, message_id)

def show_choose_time_for_habit(user_id, chat_id, message_id, scr_name, type=None):
	screen_id = '_'.join(scr_name.split('_')[1:])
	if type=="everyday":
		habit_reminder_time = callback_weekdays
		update_user_value(CACHE_UPDATEHABIT_FILEPATH, user_id, "habit_reminder_time", habit_reminder_time)
		reply = replies[screen_id].replace("[period]", "каждый день")
	elif type=="selected_days":
		weekdays_rus_dict = {
			"mon":"понедельник",
			"tue":"вторник",
			"wed":"среда",
			"thu":"четверг",
			"fri":"пятница",
			"sat":"суббота",
			"sun":"воскресенье"
		}
		weekdays_order = list(weekdays_rus_dict.keys())
		habit_reminder_time = tuple(get_cached_data(CACHE_BUTTON_SELECTION, user_id, chat_id, property="user_selections"))
		update_user_value(CACHE_UPDATEHABIT_FILEPATH, user_id, "habit_reminder_time", habit_reminder_time)

		if habit_reminder_time==callback_weekdays:
			reply = replies[screen_id].replace("[period]", "каждый день")
		else:
			habit_reminder_time = sorted(habit_reminder_time, key=lambda day: weekdays_order.index(day))
			habit_reminder_time_rus = [weekdays_rus_dict[day] for day in habit_reminder_time]
			habit_reminder_time_str_rus = ", ".join(habit_reminder_time_rus)
			reply = replies[screen_id].replace("[period]", habit_reminder_time_str_rus)

	delete_user_records(CACHE_BUTTON_SELECTION, user_id)
	switch_screen(reply, chat_id, message_id, keyboard=get_button(scr_name))

def show_choose_time_for_report(user_id, chat_id, message_id, scr_name, type=None):
	screen_id = '_'.join(scr_name.split('_')[1:])
	if type=="everyday":
		report_reminder_time = callback_weekdays
		reply = replies[screen_id].replace("[period]", "каждый день")
	elif type=="selected_days":
		weekdays_rus_dict = {
			"mon":"понедельник",
			"tue":"вторник",
			"wed":"среда",
			"thu":"четверг",
			"fri":"пятница",
			"sat":"суббота",
			"sun":"воскресенье"
		}
		weekdays_order = list(weekdays_rus_dict.keys())
		report_reminder_time = tuple(get_cached_data(CACHE_BUTTON_SELECTION, user_id, chat_id, property="user_selections"))

		if report_reminder_time==callback_weekdays:
			reply = replies[screen_id].replace("[period]", "каждый день")
		else:
			report_reminder_time = sorted(report_reminder_time, key=lambda day: weekdays_order.index(day))
			report_reminder_time_rus = [weekdays_rus_dict[day] for day in report_reminder_time]
			report_reminder_time_str_rus = ", ".join(report_reminder_time_rus)
			reply = replies[screen_id].replace("[period]", report_reminder_time_str_rus)

	new_data = {
			"user_id": user_id,
			"chat_id": chat_id,
			"report_reminder_period": report_reminder_time,
		}

	save_data_to_cache(CACHE_REPORT, new_data)

	delete_user_records(CACHE_BUTTON_SELECTION, user_id)
	switch_screen(reply, chat_id, message_id, keyboard=get_button(scr_name))

def show_premade_triggers(user_id, chat_id, message_id):
	habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_name")
	new_habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="new_habit_name")
	if new_habit_name:
		habit_name = new_habit_name

	morning_triggers = random.sample(list(premade_triggers["morning"].values()),4)
	commuting_triggers = random.sample(list(premade_triggers["commuting"].values()),1)
	at_work_triggers = random.sample(list(premade_triggers["at_work"].values()),2)
	break_time_triggers = random.sample(list(premade_triggers["break_time"].values()),1)
	evening_triggers = random.sample(list(premade_triggers["evening"].values()),2)

	chosen_triggers = []
	for trigger_type in [morning_triggers, commuting_triggers, at_work_triggers, break_time_triggers, evening_triggers]:
		for trigger in trigger_type:
			chosen_triggers.append(trigger)
	update_user_value(CACHE_UPDATEHABIT_FILEPATH, user_id, "trigger_options", chosen_triggers)
	triggers_str = format_numbered_list(chosen_triggers)
	reply = replies['23_1'].replace('[triggers]', triggers_str)
	reply = reply.replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_23_1'))

def show_enter_your_trigger(user_id, chat_id, message_id):
	habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_name")
	new_habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="new_habit_name")
	if new_habit_name:
		habit_name = new_habit_name
	reply = replies['23'].replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_23'))

def show_habit_repetition(user_id, chat_id, message_id, callback_data=None, text=None):
	habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_name")
	new_habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="new_habit_name")
	if new_habit_name:
		habit_name = new_habit_name
	if text:
		chosen_trigger = text
		update_user_value(CACHE_UPDATEHABIT_FILEPATH, user_id, "trigger", chosen_trigger)
	if callback_data and callback_data!="scr_24":
		trigger_options = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="trigger_options")
		chosen_trigger_idx = int(callback_data.split('_')[-1])-1
		chosen_trigger = trigger_options[chosen_trigger_idx]
		update_user_value(CACHE_UPDATEHABIT_FILEPATH, user_id, "trigger", chosen_trigger)
	if callback_data=="scr_24":
		chosen_trigger = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="trigger")
	reply = replies['24'].replace('[trigger]', chosen_trigger)
	reply = reply.replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_24'))

def show_set_trigger_notification_confirmation(user_id, chat_id, message_id):
	habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_name")
	new_habit_name = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="new_habit_name")
	trigger = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="trigger")
	if new_habit_name:
		habit_name = new_habit_name
	reply = replies['27'].replace('[trigger]', trigger)
	reply = reply.replace('[habit]', habit_name)

	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_27'))

def show_aspirations(chat_id, message_id):
	aspirations_str = format_numbered_list(aspirations)
	reply = replies['4'].replace("[aspirations]", aspirations_str)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_4'))

def show_predefined_habits(callback_data, user_id, chat_id, message_id):
	"""After clicking on aspiration, this func sends a message to a user with predefined habits"""
	aspiration = get_aspiration_from_callback(callback_data)
	random_habits = get_predefined_habits_for_aspiration(aspiration, size=10)
	random_habits_str = format_numbered_list(random_habits)
	reply = replies['9'].replace("[habits]", random_habits_str)

	new_data = {"user_id":user_id,"chat_id":chat_id, "aspiration":aspiration, "habits":None, "behavior_options":random_habits, "suitability":None, "effectiveness":None}
	save_data_to_cache(CACHE_PICKHABIT_FILEPATH, new_data)

	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_9'))

def show_ai_recommended_habits(user_id, chat_id, message_id):
	aspiration = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property="aspiration")
	habits = get_ai_response(aspiration=aspiration)
	numbered_habits = format_numbered_list(habits.values())
	behavior_options_list = [habit for habit in habits.values()]
	reply = "Возможно, вам подойдут эти варианты:\n\n"+numbered_habits+'\n\n---\n\n'+replies['ai_warn']

	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_12_1'))
	update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "behavior_options", behavior_options_list)

def show_picked_habits(user_id, chat_id, message_id, timestamp):
	habits = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property="habits")
	habits_str = format_numbered_list(habits)
	for habit in habits:
		db.add_habit(habit=habit, creation_datetime=timestamp, user_id=user_id)	
	delete_user_records(CACHE_PICKHABIT_FILEPATH, user_id)
	reply = replies['18']+f"\n\nСохраненные привычки:\n{habits_str}"

	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_18'))

def show_picked_predefined_habits(text, chat_id, message_id, user_id, timestamp, message_info):
	try:
		entered_numbers = parse_numbers(text)
		habit_options = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property="behavior_options")	
		filtered_habits = [i-1 for i in entered_numbers if i < len(habit_options)+1]
		selected_habits = [habit_options[i] for i in filtered_habits]
		filtered_habits_str = format_numbered_list(selected_habits)
		check_minimum_length(selected_habits, min_length=1)
		update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "habits", selected_habits)
		
		aspiration = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property="aspiration")

		# Save to DB
		for habit in selected_habits:
			db.add_habit(habit=habit, creation_datetime=timestamp, user_id=user_id, aspiration=aspiration)
		delete_user_records(CACHE_PICKHABIT_FILEPATH, user_id)

		reply = replies['18']+f"\n\nСохраненные привычки:\n{filtered_habits_str}"
		switch_screen(reply, chat_id, message_id, 
					delete_previous=False, keyboard=get_button('scr_18'))				

	except ValueError:
		reply = "Введенный текст должен содержать числа, введеные через запятую. Возможно, у вас лишние пробелы. Попробуйте ввести еще раз."
		switch_screen(reply, chat_id, message_id, 
					delete_previous=False, keyboard=get_button('scr_9'))
		message_info["callback_data"]="scr_9"

	except IndexError:
		reply = "Введенный текст должен содержать 1-3 привычки, введеные через запятую. Попробуйте ввести еще раз."
		switch_screen(reply, chat_id, message_id, 
					delete_previous=False, keyboard=get_button('scr_9'))
		message_info["callback_data"]="scr_9"

	except ListTooShortError:
		reply = "Введенный текст должен содержать хотя бы одну привычку из списка. Возможно, вы ввели слишком маленькое или большое число. Попробуйте ввести еще раз."
		switch_screen(reply, chat_id, message_id, 
					delete_previous=False, keyboard=get_button('scr_9'))
		message_info["callback_data"]="scr_9"

def show_aspiration_confirmation(chat_id, message_id, user_id, callback_data=None, text=None):
	if callback_data:
		aspiration = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property="aspiration")
		reply = replies['11'].replace("[aspiration]", aspiration)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_11'))
	elif text:
		new_data = {"user_id":user_id,"chat_id":chat_id, "aspiration":text, 
					"habits":None, "behavior_options":None, "suitability":None, 
					"effectiveness":None}
		save_data_to_cache(CACHE_PICKHABIT_FILEPATH, new_data)

		reply = replies['11'].replace("[aspiration]", text)
		tg_methods.delete_message(message_id-1, chat_id)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_11'))
	else:
		print("It is impossible to switch screen because the message does not contain text or callback")

def show_magic_wanding(text, chat_id, message_id, user_id, message_info):
	# TO-DO After returning back to a screen, I should remove the old behaviours
	behavior_options = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property="behavior_options")
	if behavior_options is None:
		behaviors = [text]
		behaviors_str = format_numbered_list(behaviors)
		update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "behavior_options", behaviors)
		main_message = replies['12_proxy']['main_message'].replace('[behaviors]', behaviors_str)
		praise = random.choice(replies['12_proxy']['praises'])
		reply = main_message + praise
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_12_proxy_1'))
		message_info["callback_data"]="scr_12_proxy_1"

	else:
		entered_options_cnt = len(behavior_options)+1
		print(entered_options_cnt)
		if entered_options_cnt<5:
			behavior_options.append(text)
			behaviors_str = format_numbered_list(behavior_options)
			update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "behavior_options", behavior_options)
			main_message = replies['12_proxy']['main_message'].replace('[behaviors]', behaviors_str)
			praise = random.choice(replies['12_proxy']['praises'])
			reply = main_message + praise
			keyboard = json.loads(get_button('scr_12_proxy_5_less'))
			keyboard["inline_keyboard"][0][0]["callback_data"] = keyboard["inline_keyboard"][0][0]["callback_data"].replace("[n]", str(entered_options_cnt-1))
			keyboard = json.dumps(keyboard)
			switch_screen(reply, chat_id, message_id, keyboard=keyboard)
			message_info["callback_data"]=f"scr_12_proxy_{entered_options_cnt}"

		elif entered_options_cnt==5:
			behavior_options.append(text)
			behaviors_str = format_numbered_list(behavior_options)
			update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "behavior_options", behavior_options)
			main_message = replies['12_proxy']['main_message'].replace('[behaviors]', behaviors_str)
			praise = replies['12_proxy']['5_options']
			reply = main_message + praise
			keyboard = json.loads(get_button('scr_12_proxy_5_more'))
			keyboard["inline_keyboard"][1][0]["callback_data"] = keyboard["inline_keyboard"][1][0]["callback_data"].replace("[n]", str(entered_options_cnt-1))
			keyboard = json.dumps(keyboard)
			switch_screen(reply, chat_id, message_id, keyboard=keyboard)
			message_info["callback_data"]=f"scr_12_proxy_{entered_options_cnt}"

		elif entered_options_cnt>5:
			behavior_options.append(text)
			behaviors_str = format_numbered_list(behavior_options)
			update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "behavior_options", behavior_options)
			main_message = replies['12_proxy']['main_message'].replace('[behaviors]', behaviors_str)
			praise = random.choice(replies['12_proxy']['praises'])
			reply = main_message + praise
			keyboard = json.loads(get_button('scr_12_proxy_5_more'))
			keyboard["inline_keyboard"][1][0]["callback_data"] = keyboard["inline_keyboard"][1][0]["callback_data"].replace("[n]", str(entered_options_cnt-1))
			keyboard = json.dumps(keyboard)
			switch_screen(reply, chat_id, message_id, keyboard=keyboard)
			message_info["callback_data"]=f"scr_12_proxy_{entered_options_cnt}"

		else:
			reply = "Что-то пошло не так"
			switch_screen(reply, chat_id, message_id)

def show_magic_wanding_return_back(callback_data, user_id, chat_id, message_id):
	# Updating behavior options to allow changing an option
	behavior_options = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property="behavior_options")
	previous_callback = get_cached_data(CACHE_FILEPATH, user_id, chat_id, property="callback_data")
	if not previous_callback in ("scr_13","scr_13_proxy_1"):	
		behavior_options.pop()
	behaviors_str = format_numbered_list(behavior_options)
	update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "behavior_options", behavior_options)
	# Updating message
	main_message = replies['12_proxy']['main_message'].replace('[behaviors]', behaviors_str)
	praise = random.choice(replies['12_proxy']['praises'])
	reply = main_message + praise
	if len(behavior_options)>=5:
		keyboard = json.loads(get_button('scr_12_proxy_5_more'))	
		keyboard["inline_keyboard"][1][0]["callback_data"] = keyboard["inline_keyboard"][1][0]["callback_data"].replace("[n]", str(len(behavior_options)))
		keyboard = json.dumps(keyboard)
	elif len(behavior_options)==1:
		keyboard = get_button('scr_12_proxy_1')
	elif 1<len(behavior_options)<5:
		keyboard = json.loads(get_button('scr_12_proxy_5_less'))
		keyboard["inline_keyboard"][0][0]["callback_data"] = keyboard["inline_keyboard"][0][0]["callback_data"].replace("[n]", str(len(behavior_options)))
		keyboard = json.dumps(keyboard)
	switch_screen(reply, chat_id, message_id, keyboard=keyboard)

def show_evaluation(callback_data, user_id, chat_id, message_id, type):
	if type=="suitability":
		pattern = r"^scr_13_proxy_\d+$"
		back_to_first_scr = "scr_13_proxy_1"
		scr_number = '13'
		scr_next = '14'
		prev_keyboard_name = 'scr_12'
		keyboard_name = 'scr_13'
		next_keyboard_name = 'scr_14'
	elif type=="effectiveness":
		pattern = r"^scr_14_proxy_\d+$"
		back_to_first_scr = "scr_14_proxy_1"
		scr_number = '14'
		scr_next = '15'
		prev_keyboard_name = 'scr_13'
		keyboard_name = 'scr_14'
		next_keyboard_name = 'scr_15'


	behavior_options = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property="behavior_options")
	ratings = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property=type)
	is_callback_in_type_eval = bool(re.match(pattern, callback_data))

	if is_callback_in_type_eval and callback_data not in back_to_first_scr:
		ratings.pop()
		update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, type, ratings)

	elif callback_data in back_to_first_scr:
		ratings = None
		update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, type, ratings)

	if ratings is None:
		behavior_idx = 0
		cur_progress = 1
		if type in callback_data:
			grade = int(callback_data.split('_')[-1])
			update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, type, [grade])
			behavior_idx = 1
			cur_progress = 2
		behavior_str = behavior_options[behavior_idx].capitalize()
		first_message = replies[scr_number]['first_message']
		progress = f"({cur_progress}/{len(behavior_options)})"
		main_message = replies[scr_number]['main_message'].replace('[progress]', progress)
		main_message = main_message.replace('[behavior]', behavior_str)
		reply = first_message+main_message
		keyboard = json.loads(get_button(keyboard_name))
		# TO-DO: probably replace when getting AI feedback
		keyboard["inline_keyboard"][2][0]["callback_data"] = keyboard["inline_keyboard"][2][0]["callback_data"].replace("[n]", str(len(behavior_options)))
		keyboard = json.dumps(keyboard)

		if type in callback_data:
			reply = main_message
			keyboard = json.loads(get_button(keyboard_name))
			keyboard["inline_keyboard"][2][0]["callback_data"] = keyboard["inline_keyboard"][2][0]["callback_data"].replace("[n]", "1")
			keyboard["inline_keyboard"][2][0]["callback_data"] = keyboard["inline_keyboard"][2][0]["callback_data"].replace(prev_keyboard_name, keyboard_name)
			keyboard = json.dumps(keyboard)
		switch_screen(reply, chat_id, message_id, keyboard=keyboard)

	elif len(ratings)<=len(behavior_options):
		# Updating grade list
		if not is_callback_in_type_eval:
			grade = int(callback_data.split('_')[-1])
			ratings.append(grade)
			update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, type, ratings)
		if len(ratings)==len(behavior_options):
			if type=="suitability":
				update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "effectiveness", None)
				show_evaluation(callback_data, user_id, chat_id, message_id, type="effectiveness")
			elif type=="effectiveness":
				suitability_ratings = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property="suitability")
				effectiveness_ratings = ratings
				habit_grades = sum_arrays(suitability_ratings, effectiveness_ratings)
				top_habits = [habit for _, habit in sorted(zip(habit_grades, behavior_options), reverse=True)[:3]]
				top_habits_str = format_numbered_list(top_habits)

				reply = replies[scr_next].replace("[habits]", top_habits_str)
				update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "habits", top_habits)
				switch_screen(reply, chat_id, message_id, keyboard=get_button(next_keyboard_name))
			return

		# Sending text message
		behavior_str = behavior_options[len(ratings)].capitalize()
		progress = f"({len(ratings)+1}/{len(behavior_options)})"
		main_message = replies[scr_number]['main_message'].replace('[progress]', progress)
		main_message = main_message.replace('[behavior]', behavior_str)
		keyboard = json.loads(get_button(keyboard_name))
		keyboard["inline_keyboard"][2][0]["callback_data"] = keyboard["inline_keyboard"][2][0]["callback_data"].replace("[n]", str(len(ratings)))
		keyboard["inline_keyboard"][2][0]["callback_data"] = keyboard["inline_keyboard"][2][0]["callback_data"].replace(prev_keyboard_name, keyboard_name)
		keyboard = json.dumps(keyboard)
		switch_screen(main_message, chat_id, message_id, keyboard=keyboard)

def show_proposed_habits(user_id, chat_id, message_id):
	top_habits = get_cached_data(CACHE_PICKHABIT_FILEPATH, user_id, chat_id, property="habits")
	top_habits_str = format_numbered_list(top_habits)
	reply = replies['15'].replace("[habits]", top_habits_str)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_15'))

# TO-DO: change these two functions to one function
def show_updated_habitname(text, chat_id, message_id, user_id, timestamp):
	new_name = text
	habit_idx = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_number")
	unique_id = db.view_habits(user_id)[habit_idx].get("id")
	db.update_habit(unique_id, "name", f"'{new_name}'")
	db.update_habit(unique_id, "last_updated", f"CAST('{timestamp}'AS Timestamp)")

	switch_screen(replies['3_7'], chat_id, message_id, keyboard=get_button('scr_3_7'))

def show_change_habit_aspiration(text, chat_id, message_id, user_id, timestamp):
	new_aspiration = text
	habit_idx = get_cached_data(CACHE_UPDATEHABIT_FILEPATH, user_id, chat_id, property="habit_number")
	unique_id = db.view_habits(user_id)[habit_idx].get("id")
	db.update_habit(unique_id, "aspiration", f"'{new_aspiration}'")
	db.update_habit(unique_id, "last_updated", f"CAST('{timestamp}'AS Timestamp)")

	switch_screen(replies['3_7'], chat_id, message_id, keyboard=get_button('scr_3_7'))

def show_updated_habits_after_deletion(text, chat_id, message_id, user_id, message_info):
	try:
		entered_numbers = parse_numbers(text)
		print(entered_numbers)
		user_habits = db.view_habits(user_id)
		if len(entered_numbers)>len(user_habits):
			raise IndexError
		if len(entered_numbers)==1:
			if entered_numbers[0]==0:
				raise ValueOutOfRangeError
		for idx in entered_numbers:
			unique_id = user_habits[idx-1].get("id")
			db.delete_habit(unique_id)
		updated_user_habits = db.view_habits(user_id)

		no_habits_left = len(updated_user_habits)==0
		if no_habits_left:
			reply = "У вас пока нет привычек. Создайте новую привычку или давайте их подберем"
			switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_3_no_habits'))

		else:
			habit_names = [item['name'] for item in updated_user_habits]
			habit_names_str = format_numbered_list(habit_names)
			reply = replies['45'].replace('[updated_habits]', habit_names_str)
			if len(entered_numbers)==1:
				reply = reply.replace("[end1]","а")
				reply = reply.replace("[end2]","а")
			else:
				reply = reply.replace("[end1]","и")
				reply = reply.replace("[end2]","ы")
			switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_45'))

	except ValueError:
		reply = "Введенный текст должен содержать привычки, введеные через запятую или через тире. Возможно, неверно указан диапазон. Попробуйте ввести еще раз."
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_44'))
		message_info["callback_data"]="scr_44"
	except IndexError:
		reply = "Неверно указан диапазон. Число запрашиваемых для удаления привычек больше, чем число самих привычек. Попробуйте ввести еще раз."
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_44'))
		message_info["callback_data"]="scr_44"
	except ValueOutOfRangeError:
		reply = "Номер привычки не может быть нулевым. Попробуйте ввести еще раз."
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_44'))
		message_info["callback_data"]="scr_44"

def show_all_reports_in_settings(user_id, chat_id, message_id):
	user_reports = db.view_reports(user_id)
	no_reports = len(user_reports)==0
	main_message = replies['41']['main_message']
	keyboard = get_button('scr_41')
	if no_reports:
		additional_message = replies['41']['no_report']
	else:
		additional_message = replies['41']['reports_exist']

	reply = main_message+additional_message
	switch_screen(reply, chat_id, message_id, keyboard=keyboard)

def show_add_report(text, chat_id, message_id, user_id, timestamp, message_info):
	try:
		parse_time_from_string(text)
		report_period = get_cached_data(CACHE_REPORT, user_id, chat_id, property="report_reminder_period")
		report_period = weekdays_to_numbers(report_period)
		report_time = text
		db.add_report(user_id, timestamp, report_period, report_time)
		switch_screen(replies['41_added'], chat_id, message_id, keyboard=get_button('scr_41_added'))
		delete_user_records(CACHE_REPORT, user_id)
	except ValueError:
		reply="Неверно указано время.\nВремя должно быть указано в формате HH:MM. Например: 21:45.\n\nПопробуйте еще раз."
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_41_add_3'))
		message_info["callback_data"]="scr_41_add_3"

def show_review_confirmation(text, chat_id, message_id, user_id, message_info):
	reply = replies['review_confirmation'].replace('[review]', text)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_review_confirmation'))

def show_review_sent(user_id, chat_id, message_id, timestamp):
	review = get_cached_data(CACHE_FILEPATH, user_id, chat_id, property="text")
	db.send_review(user_id, review, timestamp)
	switch_screen(replies['review_sent'], chat_id, message_id, keyboard=get_button('scr_review_sent'))

def show_delete_all_data_confirmation(user_id, chat_id, message_id):
	random_num = random.randint(1000000, 9999999)
	reply = replies['42'].replace('[random_num]', str(random_num))
	key_phrase = re.search(r"_([^_]+)_", reply).group(1)
	data = {"user_id":user_id, "chat_id":chat_id, "key_phrase":key_phrase}
	save_data_to_cache(CACHE_KEY_PHRASE, data)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_42'))

def show_user_deletion_screen(text, chat_id, message_id, user_id, message_info):
	key_phrase = get_cached_data(CACHE_KEY_PHRASE, user_id, chat_id, "key_phrase")
	if text == key_phrase:
		delete_user_records(CACHE_KEY_PHRASE, user_id)
		db.delete_user_data(user_id)
		switch_screen(replies['account_deleted'], chat_id, message_id, keyboard=get_button('scr_account_deleted'))
	else:
		reply = "*Кодовая фраза введена неверно.*\nУдаление данных не завершено. Если вы передумаете, мы всегда будем рады, что вы остались."
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_plug'))

def switch_screen(
    reply: str,
    chat_id: int,
    message_id: int,
    delete_previous: bool = True,
    parse_mode: str = 'Markdown',
    disable_notification: Optional[bool] = None,
    protect_content: bool = True,
    reply_parameters: Optional[Dict[str, Any]] = None,
    keyboard: Optional[str] = None,
) -> None:
    """Sends a message and optionally deletes the previous one."""
    tg_methods.send_text_message(
        reply,
        chat_id,
        parse_mode=parse_mode,
        disable_notification=disable_notification,
        protect_content=protect_content,
        reply_parameters=reply_parameters,
        keyboard=keyboard,
    )
    if delete_previous:
        tg_methods.delete_message(message_id, chat_id)

def get_button(screen_name, buttons_filepath=BUTTONS_FILEPATH):
	"""Retrieves the button configuration for a given screen."""
	buttons = load_json(buttons_filepath)
	return json.dumps(buttons[screen_name])

def select_multiple_days(callback_data, additional_actions, user_id, chat_id, message_id):

	user_selections = get_cached_data(CACHE_BUTTON_SELECTION, user_id, chat_id, "user_selections")
	previous_screen = get_cached_data(CACHE_FILEPATH, user_id, chat_id, "callback_data")
	if user_selections is None:
		user_selections = []
		new_data = {"user_id":user_id, "chat_id": chat_id, "user_selections":user_selections, "previous_screen":previous_screen}
		save_data_to_cache(CACHE_BUTTON_SELECTION, new_data)

	if callback_data in user_selections:
		user_selections.remove(callback_data)
	else:
		user_selections.append(callback_data)

	update_user_value(CACHE_BUTTON_SELECTION, user_id, "user_selections", user_selections)

	days = [
		{"text": "✅ Пн" if "mon" in user_selections else "Пн", "callback_data": "mon"},
		{"text": "✅ Вт" if "tue" in user_selections else "Вт", "callback_data": "tue"},
		{"text": "✅ Ср" if "wed" in user_selections else "Ср", "callback_data": "wed"},
		{"text": "✅ Чт" if "thu" in user_selections else "Чт", "callback_data": "thu"},
	]
	weekend = [
		{"text": "✅ Пт" if "fri" in user_selections else "Пт", "callback_data": "fri"},
		{"text": "✅ Сб" if "sat" in user_selections else "Сб", "callback_data": "sat"},
		{"text": "✅ Вс" if "sun" in user_selections else "Вс", "callback_data": "sun"},
	]
	reply_markup = {
		"inline_keyboard": [days, weekend]+additional_actions
	}
	tg_methods.edit_message_reply_markup(chat_id, message_id, reply_markup)


# Checking for conditions
def text_message_is_entered(message):
	return 'message' in message and 'text' in message['message']

def button_is_pressed(message):
	return 'callback_query' in message.keys()

# Other useful functions
def get_aspiration_from_callback(callback_data):
	"""Returns aspiration from button callback"""
	aspiration_idx = int(callback_data.split('_')[-1])-1
	aspiration = aspirations[aspiration_idx]
	return aspiration

def get_predefined_habits_for_aspiration(aspiration, size=10):
	"""Returns a list of randomly selected predefined habits."""
	habits = list(premade_habits[aspiration])
	habits = random.sample(habits, k=size)
	return habits
