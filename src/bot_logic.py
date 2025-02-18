import json
import re

from logic import *
from cache_manager import CacheManager
from common import (
	load_json,
	switch_screen, 
	get_button, 
	unix_to_timestamp
	)
from tg_methods import edit_message_reply_markup, delete_message
from config import REPLIES_FILEPATH

# Load cache manager
cache = CacheManager()

# Load JSON data
replies = load_json(REPLIES_FILEPATH)

# Sets of buttons
callback_weekdays = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")

callback_screens_weekdays_and_time = {
	"report":
		[
			("scr_0_5_add_1", "scr_0_5_add_2", "scr_0_5_add_3"),
			("scr_3_4_change_1", "scr_3_4_change_2", "scr_3_4_change_3"),
			("scr_29_add_1", "scr_29_add_2", "scr_29_add_3"),
			("scr_41_1_change_1", "scr_41_1_change_2", "scr_41_1_change_3"),
			("scr_41_add_1", "scr_41_add_2", "scr_41_add_3")
		],
	"habit":
		[
			("scr_3_1_reminder_1", "scr_3_1_reminder_2", "scr_3_1_reminder_3"),
			("scr_22_1", "scr_22_1_1", "scr_22_2"),
			("scr_28", "scr_28_1", "scr_28_2"),
		]
	}

def use_logic(message):
	if button_is_pressed(message):
		message_info = handle_callback_query(message)
		cache.save_previous_message(message_info)
	elif text_message_is_entered(message):
		message_info = handle_text_message(message)
		cache.save_previous_message(message_info)
	else:
		message_info = handle_unknown_message(message)

def handle_callback_query(message):

	def handle_default_callback(callback_data):
		screen_id = '_'.join(callback_data.split('_')[1:])
		if screen_id in ("44"):
			show_callback_reply(screen_id, delete_previous=False)
		else:
			show_callback_reply(screen_id)

	def handle_special_callback(special_handlers_dict, transition):
		action = special_handlers_dict.get(transition)
		action()

	def handle_conditional_callback(conditional_handlers_dict, conditional_screens, transition):
		matching_prefix = next((prefix for prefix in conditional_screens if transition.startswith(prefix)), None)
		action = conditional_handlers_dict.get(matching_prefix)
		action()

	def handle_weekdays_and_time_choice(callback_data, callback_screens_weekdays_and_time):
		for type in callback_screens_weekdays_and_time:
			for combination in callback_screens_weekdays_and_time[type]:
				if (callback_data in combination) or (previous_screen in combination) or (previous_screen_button_selection in combination):
					choose_weekdays_and_time(combination[0], combination[1], combination[2], type=type)
					break

	def handle_unknown_callback(callback_data):
		print(callback_data)
		reply = "Error: unknown callback data"
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_plug'))

	def show_callback_reply(screen_id, delete_previous=True):
		switch_screen(replies[screen_id], chat_id, message_id, delete_previous=delete_previous,
						keyboard=get_button(f'scr_{screen_id}'))

	def choose_weekdays_and_time(scr_freq, scr_weekdays, scr_time, type):
		if type=="report":
			if (previous_screen==scr_weekdays or previous_screen_button_selection==scr_weekdays) and callback_data in callback_weekdays:
				show_multiple_selection(user_id, chat_id, message_id, callback_data=callback_data, scr_name=scr_weekdays)
			elif previous_screen==scr_freq and callback_data==scr_time:
				show_choose_time_for_report(user_id, chat_id, message_id, scr_time, type="everyday")
			elif previous_screen==scr_weekdays and callback_data==scr_time:
				show_choose_time_for_report(user_id, chat_id, message_id, scr_time, type="everyday")
			elif previous_screen in callback_weekdays and callback_data==scr_time:
				show_choose_time_for_report(user_id, chat_id, message_id, scr_time, type="selected_days")
		elif type=="habit":
			if (previous_screen==scr_weekdays or previous_screen_button_selection==scr_weekdays) and callback_data in callback_weekdays:
				show_multiple_selection(user_id, chat_id, message_id, callback_data=callback_data, scr_name=scr_weekdays)
			elif previous_screen==scr_freq and callback_data==scr_time:
				show_choose_time_for_habit(user_id, chat_id, message_id, scr_time, type="everyday")
			elif previous_screen==scr_weekdays and callback_data==scr_time:
				show_choose_time_for_habit(user_id, chat_id, message_id, scr_time, type="everyday")
			elif previous_screen in callback_weekdays and callback_data==scr_time:
				show_choose_time_for_habit(user_id, chat_id, message_id, scr_time, type="selected_days")

	# Getting data
	callback_query_id = message['callback_query']['id']
	callback_data = message['callback_query']['data']
	chat_id = message['callback_query']['message']['chat']['id']
	message_id = message['callback_query']['message']['message_id']
	user_id = message['callback_query']['from']['id']
	unix_timestamp = message['callback_query']['message']['date']
	timestamp = unix_to_timestamp(unix_timestamp)

	# Retrieve previous screen info
	previous_screen = cache.get_previous_message(user_id)['callback_data']
	previous_screen_button_selection = cache.get_button_selection(user_id, "previous_screen")
	transition = (previous_screen, callback_data)
	
	# Determine current callback type
	is_previous_screen_in_magic_wanding = bool(re.match(r"^scr_12_proxy_\d+$", previous_screen))
	is_callback_in_screens_weekdays_and_time_report = any(callback_data in sublist or previous_screen_button_selection in sublist for sublist in callback_screens_weekdays_and_time['report']) or callback_data in callback_weekdays
	is_callback_in_screens_weekdays_and_time_habit = any(callback_data in sublist or previous_screen_button_selection in sublist for sublist in callback_screens_weekdays_and_time['habit']) or callback_data in callback_weekdays
	is_callback_in_repetition_reminders = bool(re.match(r"^rep_\w+$", callback_data))
	is_callback_in_reports = bool(re.match(r"^report_\d+$", callback_data))

	# Actual logic
	DEFAULT_CALLBACK_SCREENS = (
		"scr_0_1", "scr_0_11", "scr_0_3", "scr_0_4", "scr_0_42", "scr_0_412",
		"scr_0_5", "scr_0_5_add_1", "scr_0_7", "scr_0_421", "scr_0_422", "scr_0_413", 
		"scr_2", "scr_3_2_proxy", "scr_3_1_trigger_type", "scr_3_1_reminder_1",
		"scr_3_2_proxy_reset", "scr_3_2_proxy_resume", "scr_3_2_forbidden",	"scr_3_4_change_1", 
		"scr_6", "scr_9", "scr_10", "scr_12", "scr_13", "scr_3_3",
		"scr_16", "scr_17", "scr_19", "scr_22", "scr_22_1",
		"scr_review", "scr_25", "scr_26", "scr_26_1", "scr_28", 
		"scr_29_add_1", "scr_30", "scr_31", "scr_32", "scr_33",
		"scr_34", "scr_35", "scr_37", "scr_38", "scr_39",
		"scr_40", "scr_41_add_1", "scr_41_1_conf_deletion", "scr_41_1_change_1", 
		"scr_44", "scr_plug"
		)

	SPECIAL_CALLBACK_HANDLERS = {
		"scr_0_2": lambda: show_onboarding_secret(user_id, chat_id, message_id),
		"scr_0_41": lambda: edit_message_reply_markup(chat_id, message_id, json.loads(get_button('scr_0_41'))),
		"scr_0_4_back": lambda: edit_message_reply_markup(chat_id, message_id, json.loads(get_button('scr_0_4'))),
		"scr_0_414": lambda: edit_message_reply_markup(chat_id, message_id, json.loads(get_button('scr_0_414'))),
		"scr_0_414_back": lambda: edit_message_reply_markup(chat_id, message_id, json.loads(get_button('scr_0_413'))),
		"scr_0_5_add_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_0_5_add_2'),
		"scr_1": lambda: show_main_menu(user_id, chat_id, message_id),
		"scr_3": lambda: show_user_habits(user_id, chat_id, message_id),
		"scr_3_1": lambda: get_back_to_habit(callback_data, user_id, chat_id, message_id, timestamp),
		"scr_3_1_reminder_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_3_1_reminder_2'),
		"scr_3_1_trigger": lambda: show_enter_your_trigger(user_id, chat_id, message_id),
		"scr_3_2": lambda: show_mark_habit_as_completed(user_id, chat_id, message_id, timestamp),
		"scr_3_2_reset": lambda: show_reset_habit_completion(user_id, chat_id, message_id, timestamp),
		"scr_3_2_resume": lambda: show_resume_tracking_habit(user_id, chat_id, message_id, timestamp),
		"scr_3_2_stop_habit": lambda: show_stop_tracking_habit(user_id, chat_id, message_id, timestamp),
		"scr_3_2_finish_habit": lambda: show_finish_tracking_habit(user_id, chat_id, message_id, timestamp),
		"scr_3_4": lambda: show_pick_report_for_habit(user_id, chat_id, message_id, callback_data=callback_data),
		"scr_3_4_change_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_3_4_change_2'),
		"scr_4": lambda: show_aspirations(chat_id, message_id),
		"scr_5": lambda: show_user_stats(user_id, chat_id, message_id),
		"scr_8": lambda: show_is_habit_tiny(user_id, chat_id, message_id),
		"scr_8_1": lambda: show_make_habit_tiny(user_id, chat_id, message_id),
		"scr_11": lambda: show_aspiration_confirmation(chat_id, message_id, user_id, callback_data=callback_data),
		"scr_12_1": lambda: show_ai_recommended_habits(user_id, chat_id, message_id),
		"scr_13": lambda: show_evaluation(callback_data, user_id, chat_id, message_id, type="suitability"),
		"scr_13_change_priorities": lambda: show_evaluation(callback_data, user_id, chat_id, message_id, type="suitability"),
		"scr_14": lambda: show_evaluation(callback_data, user_id, chat_id, message_id, type="effectiveness"),
		"scr_15": lambda: show_proposed_habits(user_id, chat_id, message_id),
		"scr_18": lambda: show_picked_habits(user_id, chat_id, message_id, timestamp),
		"scr_21": lambda: show_choosing_habit_type(user_id, chat_id, message_id),
		"scr_22_1_1": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_22_1_1'),
		"scr_23": lambda: show_enter_your_trigger(user_id, chat_id, message_id),
		"scr_23_1": lambda: show_premade_triggers(user_id, chat_id, message_id),
		"scr_24": lambda: show_habit_repetition(user_id, chat_id, message_id, callback_data=callback_data, text=None),
		"scr_24_resume": lambda: show_habit_repetition(user_id, chat_id, message_id, callback_data=callback_data, text=None),
		"scr_27": lambda: show_set_trigger_notification_confirmation(user_id, chat_id, message_id),
		"scr_28_1": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_28_1'),
		"scr_29": lambda: show_pick_report_for_habit(user_id, chat_id, message_id, callback_data=callback_data),
		"scr_29_add_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_29_add_2'),
		"scr_review_sent": lambda: show_review_sent(user_id, chat_id, message_id, timestamp),
		"scr_41": lambda: show_all_reports_in_settings(user_id, chat_id, message_id),
		"scr_41_1": lambda: show_choose_report(callback_data, user_id, chat_id, message_id),
		"scr_41_1_deleted": lambda: show_report_deleted(user_id, chat_id, message_id),
		"scr_42": lambda: show_delete_all_data_confirmation(user_id, chat_id, message_id),
		"scr_41_add_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_41_add_2'),
		"scr_41_1_change_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_41_1_change_2'),
		"no_scr": lambda: delete_message(message_id, chat_id),
		("scr_12_1", "scr_12"): lambda: show_magic_wanding_return_back_to_start(chat_id, message_id, user_id, 'scr_12'),
		("scr_9", "scr_12"): lambda: switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('9_scr_12')),
		("scr_11", "scr_12"): lambda: switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('scr_12')),
		("scr_12", "scr_9"): lambda: show_getting_back_to_predefined_habits(user_id, chat_id, message_id),
	}
	SPECIAL_CALLBACK_SCREENS = SPECIAL_CALLBACK_HANDLERS.keys()

	CONDITIONAL_CALLBACK_HANDLERS = {
		"scr_12_proxy_": lambda: show_magic_wanding_return_back(callback_data, user_id, chat_id, message_id),
		"hab_": lambda: show_predefined_habits(callback_data, user_id, chat_id, message_id),
		"suitability_": lambda: show_evaluation(callback_data, user_id, chat_id, message_id, type="suitability"),
		"scr_13_proxy_": lambda: show_evaluation(callback_data, user_id, chat_id, message_id, type="suitability"),
		"effectiveness_": lambda: show_evaluation(callback_data, user_id, chat_id, message_id, type="effectiveness"),
		"scr_14_proxy_": lambda: show_evaluation(callback_data, user_id, chat_id, message_id, type="effectiveness"),
		"beh_": lambda: show_habit_repetition(user_id, chat_id, message_id, callback_data=callback_data, text=None),
	}
	CONDITIONAL_CALLBACK_SCREENS = tuple(CONDITIONAL_CALLBACK_HANDLERS.keys())
	
	if callback_data in SPECIAL_CALLBACK_SCREENS:
		handle_special_callback(SPECIAL_CALLBACK_HANDLERS, callback_data)

	elif transition in SPECIAL_CALLBACK_SCREENS:
		handle_special_callback(SPECIAL_CALLBACK_HANDLERS, transition)

	elif callback_data.startswith(CONDITIONAL_CALLBACK_SCREENS):
		handle_conditional_callback(CONDITIONAL_CALLBACK_HANDLERS, CONDITIONAL_CALLBACK_SCREENS, callback_data)

	elif previous_screen=="scr_3_4" and is_callback_in_reports:
		show_report_updated_for_habit(user_id, chat_id, message_id, callback_data=callback_data, text=None, timestamp=timestamp)

	elif is_previous_screen_in_magic_wanding and callback_data=="scr_12":
		show_magic_wanding_return_back_to_start(chat_id, message_id, user_id, 'scr_12')

	elif previous_screen.startswith("hab_") and callback_data == "scr_12":
		show_magic_wanding_return_back_to_start(chat_id, message_id, user_id, '9_scr_12')

	elif previous_screen=="scr_26" and is_callback_in_repetition_reminders:
		show_repetition_reminder_set(user_id, chat_id, message_id, callback_data=callback_data, text=None, timestamp=timestamp, message_info=None)

	elif previous_screen=="scr_29" and is_callback_in_reports:
		show_habit_is_tracked(user_id, chat_id, message_id, callback_data=callback_data, text=None, timestamp=timestamp)

	elif previous_screen=="scr_41" and is_callback_in_reports:
		show_choose_report(callback_data, user_id, chat_id, message_id)

	elif callback_data in DEFAULT_CALLBACK_SCREENS:
		handle_default_callback(callback_data)

	elif is_callback_in_screens_weekdays_and_time_report:
		handle_weekdays_and_time_choice(callback_data, callback_screens_weekdays_and_time)
	elif is_callback_in_screens_weekdays_and_time_habit:
		handle_weekdays_and_time_choice(callback_data, callback_screens_weekdays_and_time)
	else:
		handle_unknown_callback(callback_data)

	# Saving data
	data = {"user_id":user_id,"chat_id":chat_id, "message_id":message_id, "callback_data":callback_data, "text":None}
	return data

def handle_text_input(text, chat_id, message_id, user_id, timestamp, message_info):

	def handle_special_input(special_handlers_dict, transition):
		action = special_handlers_dict.get(transition)
		action()

	def handle_conditional_input(conditional_handlers_dict, conditional_screens, transition):
		matching_prefix = next((prefix for prefix in conditional_screens if transition.startswith(prefix)), None)
		action = conditional_handlers_dict.get(matching_prefix)
		action()

	previous_screen = cache.get_previous_message(user_id)['callback_data']

	SPECIAL_INPUT_HANDLERS = {
		"scr_0_5_add_3": lambda: show_onboarding_report_added(user_id, chat_id, message_id, text, timestamp, message_info),
		"scr_2": lambda: show_adding_habit(text, user_id, chat_id, message_id, timestamp),
		"scr_3": lambda: show_habit_info(text, user_id, chat_id, message_id, message_info, timestamp),
		"scr_3_1_trigger": lambda: show_trigger_updated(text, user_id, chat_id, message_id, timestamp),
		"scr_3_1_reminder_3": lambda: show_habit_reminder_updated(text, user_id, chat_id, message_id, timestamp, message_info=message_info),
		"scr_3_3": lambda: show_change_habit_aspiration(text, chat_id, message_id, user_id, timestamp),
		"scr_3_4_change_3": lambda: show_report_updated_for_habit(user_id, chat_id, message_id, text=text, timestamp=timestamp, message_info=message_info),
		"scr_5": lambda: show_return_habit_back(text, user_id, chat_id, message_id, timestamp, message_info),
		"scr_8_1": lambda: show_reminding_options_after_making_habit_tiny(text, chat_id, message_id, user_id),
		"scr_9": lambda: show_picked_predefined_habits(text, chat_id, message_id, user_id, timestamp, message_info),
		"scr_10": lambda: show_aspiration_confirmation(chat_id, message_id, user_id, text=text),
		"scr_12": lambda: show_magic_wanding(text, chat_id, message_id, user_id, message_info),
		"scr_17": lambda: show_magic_wanding(text, chat_id, message_id, user_id, message_info),
		"scr_19": lambda: show_updated_habitname(text, chat_id, message_id, user_id, timestamp),
		"scr_22_2": lambda: show_pick_report_for_habit(user_id, chat_id, message_id, text=text, message_info=message_info),
		"scr_23": lambda: show_habit_repetition(user_id, chat_id, message_id, callback_data=None, text=text),
		"scr_26_1": lambda: show_repetition_reminder_set(user_id, chat_id, message_id, callback_data=None, text=text, timestamp=timestamp, message_info=message_info),
		"scr_28_2": lambda: show_pick_report_for_habit(user_id, chat_id, message_id, text=text, message_info=message_info),
		"scr_29": lambda: show_habit_is_tracked(user_id, chat_id, message_id, callback_data=None, text=text, timestamp=timestamp, message_info=message_info),
		"scr_29_add_3": lambda: show_habit_is_tracked(user_id, chat_id, message_id, callback_data=None, text=text, timestamp=timestamp, message_info=message_info),
		"scr_31": lambda: switch_screen(replies['7'], chat_id, message_id, keyboard=get_button('scr_7')),
		"scr_36": lambda: switch_screen(replies['20'], chat_id, message_id, keyboard=get_button('scr_20')),
		"scr_37": lambda: switch_screen(replies['20'], chat_id, message_id, keyboard=get_button('scr_20')),
		"scr_38": lambda: switch_screen(replies['20'], chat_id, message_id, keyboard=get_button('scr_20')),
		"scr_40": lambda: switch_screen(replies['43'], chat_id, message_id, keyboard=get_button('scr_43')),
		"scr_41_add_3": lambda: show_add_report(text, chat_id, message_id, user_id, timestamp, message_info),
		"scr_41_1_change_3": lambda: show_report_changed(text, user_id, chat_id, message_id, timestamp, message_info),
		"scr_42": lambda: show_user_deletion_screen(text, chat_id, message_id, user_id, message_info),
		"scr_44": lambda: show_updated_habits_after_deletion(text, chat_id, message_id, user_id, message_info),
		"scr_review": lambda: show_review_confirmation(text, chat_id, message_id, user_id, message_info),
	}
	SPECIAL_INPUT_SCREENS = SPECIAL_INPUT_HANDLERS.keys()

	CONDITIONAL_INPUT_HANDLERS = {
		"hab_": lambda: show_picked_predefined_habits(text, chat_id, message_id, user_id, timestamp, message_info),
		"scr_12_proxy_": lambda: show_magic_wanding(text, chat_id, message_id, user_id, message_info),
	}
	CONDITIONAL_INPUT_SCREENS = tuple(CONDITIONAL_INPUT_HANDLERS.keys())

	if previous_screen in SPECIAL_INPUT_SCREENS:
		handle_special_input(SPECIAL_INPUT_HANDLERS, previous_screen)

	elif previous_screen.startswith(CONDITIONAL_INPUT_SCREENS):
		handle_conditional_input(CONDITIONAL_INPUT_HANDLERS, CONDITIONAL_INPUT_SCREENS, previous_screen)

	elif previous_screen=='scr_33':
		switch_screen(replies['36'], chat_id, message_id, 
						delete_previous=False, keyboard=get_button('scr_36'))
		message_info["callback_data"]="scr_36"
		print(text)
	elif previous_screen=='scr_35':
		switch_screen(replies['36'], chat_id, message_id, 
						delete_previous=False, keyboard=get_button('scr_36'))
		message_info["callback_data"]="scr_36"

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
	"callback_data": "None", # I did it with a string specifically to avoid 'NoneType' errors
	"text": text
	}

	delete_message(message_id-1, chat_id)

	if text=="/start":
		show_start_screen(user_id, chat_id, message_id, message, timestamp)
	else:
		handle_text_input(text, chat_id, message_id, user_id, timestamp, message_info)

	return message_info

def handle_unknown_message(message):
	"""Handles messages that are neither text nor button presses."""
	chat_id = message['message']['chat']['id']
	message_id = message['message']['message_id']
	user_id = message['message']['from']['id']

	delete_message(message_id, chat_id)
	return {
	"user_id": user_id,
	"chat_id": chat_id,
	"message_id": message_id,
	"callback_data": None,
	"text": None
	}

# Checking for conditions
def text_message_is_entered(message):
	return 'message' in message and 'text' in message['message']

def button_is_pressed(message):
	return 'callback_query' in message.keys()
