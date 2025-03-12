import json
import random
import re
import traceback

from logic import *
from cache_manager import CacheManager
from database import DatabaseClient
from common import (
	load_json,
	switch_screen, 
	get_button, 
	unix_to_timestamp
	)
from tg_methods import edit_message_reply_markup, delete_message, confirm_pre_checkout_query
from config import REPLIES_FILEPATH, REPORT_REPLIES_FILEPATH, REPORT_BUTTONS_FILEPATH

# Load cache manager
cache = CacheManager()
db = DatabaseClient()

# Load JSON data
replies = load_json(REPLIES_FILEPATH)
report_replies = load_json(REPORT_REPLIES_FILEPATH)

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
			("scr_3_1_bad_habit_avoid_trigger_1", "scr_3_1_bad_habit_avoid_trigger_2", "scr_3_1_bad_habit_avoid_trigger_3"),
			("scr_3_1_reminder_1", "scr_3_1_reminder_2", "scr_3_1_reminder_3"),
			("scr_3_5_time_1", "scr_3_5_time_2", "scr_3_5_time_3"),
			("scr_22_1", "scr_22_1_1", "scr_22_2"),
			("scr_28", "scr_28_1", "scr_28_2"),
			("scr_33_1", "scr_33_2", "scr_33_3"),
		],
	"daily_report":[
			("scr_report_keep_skipping_notif_1", "scr_report_keep_skipping_notif_2", "scr_report_keep_skipping_notif_3"),
		]
	}

def use_logic(message):
	try:
		if button_is_pressed(message):
			message_info = handle_callback_query(message)
			cache.save_previous_message(message_info)
		elif text_message_is_entered(message):
			message_info = handle_text_message(message)
			cache.save_previous_message(message_info)
		elif invoice_is_sent(message):
			message_info = handle_invoice(message)
		elif payment_was_successful(message):
			message_info = handle_payment(message)
		else:
			message_info = handle_unknown_message(message)
	except Exception as e:
		print(traceback.format_exc())
		# if 'callback_query' in message:
		# 	chat_id = message['callback_query']['message']['chat']['id']
		# 	message_id = message['callback_query']['message']['message_id']
		# 	unix_timestamp = message['callback_query']['message']['date']
		# else:
		# 	chat_id = message['message']['chat']['id']
		# 	message_id = message['message']['message_id']
		# 	unix_timestamp = message['message']['date']
		# timestamp = unix_to_timestamp(unix_timestamp)
		# switch_screen(replies['general_error'], chat_id, message_id, keyboard=get_button('scr_plug'))
		# db.record_user_action(chat_id, "error", timestamp, metadata="Error")

def handle_callback_query(message):

	def handle_default_callback(callback_data, mode="general"):
		screen_id = '_'.join(callback_data.split('_')[1:])
		if mode=="general":
			show_callback_reply(screen_id)
		elif mode=="report":
			show_callback_reply_report(screen_id)

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

	def show_callback_reply_report(screen_id, delete_previous=True):
		reply = random.choice(report_replies[screen_id])
		switch_screen(reply, chat_id, message_id, delete_previous=delete_previous,
						keyboard=get_button(f'scr_{screen_id}', buttons_filepath=REPORT_BUTTONS_FILEPATH))

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
		elif type=="daily_report":
			if (previous_screen==scr_weekdays or previous_screen_button_selection==scr_weekdays) and callback_data in callback_weekdays:
				show_multiple_selection_for_daily_report(user_id, chat_id, message_id, callback_data=callback_data, scr_name=scr_weekdays)
			elif previous_screen==scr_freq and callback_data==scr_time:
				show_choose_time_for_habit_report(user_id, chat_id, message_id, scr_time, type="everyday")
			elif previous_screen==scr_weekdays and callback_data==scr_time:
				show_choose_time_for_habit_report(user_id, chat_id, message_id, scr_time, type="everyday")
			elif previous_screen in callback_weekdays and callback_data==scr_time:
				show_choose_time_for_habit_report(user_id, chat_id, message_id, scr_time, type="selected_days")

	# Getting data
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
	is_callback_in_screens_weekdays_and_time_habit_report = any(callback_data in sublist or previous_screen_button_selection in sublist for sublist in callback_screens_weekdays_and_time['daily_report']) or callback_data in callback_weekdays
	is_callback_in_repetition_reminders = bool(re.match(r"^rep_\w+$", callback_data))
	is_callback_in_reports = bool(re.match(r"^report_\d+$", callback_data))

	# Actual logic
	DEFAULT_CALLBACK_SCREENS = (
		"scr_0_timezone", "scr_0_timezone_1", "scr_0_1", "scr_0_1_habit", "scr_0_11", "scr_0_12", 
		"scr_0_3", "scr_0_4", "scr_0_4_explanation", "scr_0_42", 
		"scr_0_5", "scr_0_5_add_1", "scr_0_7", "scr_0_421", "scr_0_422", "scr_0_413", "scr_0_412",
		"scr_2", "scr_3_2_proxy", "scr_3_1_trigger_type", "scr_3_1_reminder_1",
		"scr_3_1_bad_habit_fighting_method", "scr_3_1_bad_habit_avoid_trigger", "scr_3_1_bad_habit_avoid_trigger_1",
		"scr_3_2_proxy_reset", "scr_3_2_bad_habit_proxy_reset", "scr_3_2_proxy_resume", "scr_3_2_one_time_proxy",
		"scr_3_2_one_time_proxy_from_reminder", "scr_3_2_bad_habit_proxy", "scr_3_2_forbidden", "scr_3_4_change_1", 
		"scr_9", "scr_10", "scr_12_help", "scr_13", "scr_3_3", "scr_3_5_time_1", "scr_3_6_proxy", "scr_3_6",
		"scr_16", "scr_17", "scr_19", "scr_22", "scr_22_1", "scr_24_explanation", "scr_24_resume_explanation",
		"scr_review", "scr_25", "scr_26", "scr_26_1", "scr_28", 
		"scr_29_add_1", "scr_32", "scr_33", "scr_33_1", "scr_38", "scr_39", "scr_donate",
		"scr_40_1", "scr_41_add_1", "scr_41_1_conf_deletion", "scr_41_1_change_1", "scr_plug"
		)

	DEFAULT_CALLBACK_SCREENS_REPORTS = (
		"scr_report_skipped", "scr_report_skipped_2_cons_times", "scr_report_skipped_notif",
		"scr_report_keep_skipping_notif", "scr_report_keep_skipping_notif_1",
		"scr_report_skipped_finish", "scr_report_skipped_notif_finish",
		"scr_report_skipped_finish_refused", "scr_srbai_no"
		)

	SPECIAL_CALLBACK_HANDLERS = {
		"scr_report": lambda: show_report_to_do(user_id, chat_id, message_id),
		"scr_report_done": lambda: show_report_done(user_id, chat_id, message_id, timestamp),
		"scr_report_skipped": lambda: show_report_skipped(user_id, chat_id, message_id, timestamp),
		"scr_report_simply_forgot": lambda: show_report_repetition(user_id, chat_id, message_id),
		"scr_report_keep_forgetting": lambda: show_report_change_trigger(user_id, chat_id, message_id),
		"scr_report_keep_skipping_notif_trigger": lambda: show_report_enter_trigger(user_id, chat_id, message_id),
		"scr_report_keep_skipping_notif_2": lambda: show_choose_weekdays_for_daily_report(user_id, chat_id, message_id, scr_name='scr_report_keep_skipping_notif_2'),
		"scr_report_too_hard": lambda: show_report_too_hard(user_id, chat_id, message_id),
		"scr_report_dont_want": lambda: show_report_delete_habit_confirmation(user_id, chat_id, message_id),
		"scr_report_dont_want_yes": lambda: show_report_habit_deleted(user_id, chat_id, message_id),
		"scr_report_dont_want_no": lambda: show_report_habit_not_deleted(user_id, chat_id, message_id),
		"scr_report_skipped_notif_finish": lambda: show_report_skipped_finish(user_id, chat_id, message_id),
		"scr_report_skipped_finish_refused": lambda: show_report_skipped_finish_refused(user_id, chat_id, message_id),
		"scr_report_skipped_finish": lambda: show_report_skipped_finish(user_id, chat_id, message_id),

		"scr_srbai_report": lambda: show_srbai_report(user_id, chat_id, message_id),
		"scr_srbai_tomorrow": lambda: show_srbai_tomorrow(user_id, chat_id, message_id, timestamp),
		"scr_srbai_month_later": lambda: show_srbai_in_a_month(user_id, chat_id, message_id, timestamp),
		"scr_srbai_report_1": lambda: show_srbai_question_1(user_id, chat_id, message_id),
		"scr_srbai_report_2": lambda: show_srbai_question_2(user_id, chat_id, message_id, callback_data),
		"scr_srbai_report_3": lambda: show_srbai_question_3(user_id, chat_id, message_id, callback_data),
		"scr_srbai_report_4": lambda: show_srbai_question_4(user_id, chat_id, message_id, callback_data),
		"scr_srbai_too_hard": lambda: show_srbai_simplify_habit(user_id, chat_id, message_id),
		"scr_srbai_low_no": lambda: show_srbai_habit_refused(user_id, chat_id, message_id),

		"scr_0_2": lambda: show_onboarding_secret(user_id, chat_id, message_id),
		"scr_0_41": lambda: edit_message_reply_markup(chat_id, message_id, json.loads(get_button('scr_0_41'))),
		"scr_0_4_back": lambda: edit_message_reply_markup(chat_id, message_id, json.loads(get_button('scr_0_4'))),
		"scr_0_414": lambda: edit_message_reply_markup(chat_id, message_id, json.loads(get_button('scr_0_414'))),
		"scr_0_414_back": lambda: edit_message_reply_markup(chat_id, message_id, json.loads(get_button('scr_0_413'))),
		"scr_0_5_add_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_0_5_add_2'),
		"scr_1": lambda: show_main_menu(user_id, chat_id, message_id, unix_timestamp),
		"scr_3": lambda: show_user_habits(user_id, chat_id, message_id),
		"scr_3_1": lambda: get_back_to_habit(callback_data, user_id, chat_id, message_id, timestamp),
		"scr_3_1_bad_habit_avoid_trigger_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_3_1_bad_habit_avoid_trigger_2'),
		"scr_3_1_reminder_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_3_1_reminder_2'),
		"scr_3_1_trigger": lambda: show_enter_your_trigger(user_id, chat_id, message_id),
		"scr_3_1_bad_habit_remove_trigger": lambda: show_change_bad_habit_remove_trigger(user_id, chat_id, message_id),
		"scr_3_1_bad_habit_avoid_trigger_finished": lambda: show_change_bad_habit_trigger_avoided(user_id, chat_id, message_id, timestamp),
		"scr_3_1_bad_habit_avoid_trigger_finished_no_notif": lambda: show_change_bad_habit_trigger_avoided(user_id, chat_id, message_id, timestamp, notifications=False),
		"scr_3_1_bad_habit_harden_behavior": lambda: show_change_bad_habit_harden_behavior(user_id, chat_id, message_id),
		"scr_3_2": lambda: show_mark_habit_as_completed(user_id, chat_id, message_id, timestamp),
		"scr_3_2_reset": lambda: show_reset_habit_completion(user_id, chat_id, message_id, timestamp),
		"scr_3_2_bad_habit_reset": lambda: show_reset_bad_habit_completion(user_id, chat_id, message_id, timestamp),
		"scr_3_2_resume": lambda: show_resume_tracking_habit(user_id, chat_id, message_id, timestamp),
		"scr_3_2_stop_habit": lambda: show_stop_tracking_habit(user_id, chat_id, message_id, timestamp),
		"scr_3_2_finish_habit": lambda: show_finish_tracking_habit(user_id, chat_id, message_id, timestamp),
		"scr_3_2_bad_habit_done": lambda: show_bad_habit_done(user_id, chat_id, message_id, timestamp),
		"scr_3_2_one_time_completed": lambda: show_one_time_habit_completed(user_id, chat_id, message_id),
		"scr_3_4": lambda: show_pick_report_for_habit(user_id, chat_id, message_id, callback_data=callback_data),
		"scr_3_4_change_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_3_4_change_2'),
		"scr_3_5_proxy": lambda: show_change_or_delete_trigger_reminder(user_id, chat_id, message_id),
		"scr_3_5_time_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_3_5_time_2'),
		"scr_3_5_turn_off": lambda: show_trigger_reminder_deleted(user_id, chat_id, message_id, timestamp),
		"scr_3_6_no_reminder": lambda: show_one_time_habit_reminder_removed(user_id, chat_id, message_id, timestamp),
		"scr_4": lambda: show_aspirations(chat_id, message_id),
		"scr_5": lambda: show_user_stats(user_id, chat_id, message_id),
		"scr_6": lambda: show_settings_screen(user_id, chat_id, message_id),
		"scr_8": lambda: show_is_habit_tiny(user_id, chat_id, message_id),
		"scr_8_1": lambda: show_make_habit_tiny(user_id, chat_id, message_id),
		"scr_11": lambda: show_aspiration_confirmation(chat_id, message_id, user_id, callback_data=callback_data),
		"scr_12": lambda: show_magic_wanding_start(user_id, chat_id, message_id),
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
		"scr_24_resume_from_reminder": lambda: show_habit_repetition(user_id, chat_id, message_id, callback_data=callback_data, text=None),
		"scr_27": lambda: show_set_trigger_notification_confirmation(user_id, chat_id, message_id),
		"scr_28_1": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_28_1'),
		"scr_29": lambda: show_pick_report_for_habit(user_id, chat_id, message_id, callback_data=callback_data),
		"scr_29_add_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_29_add_2'),
		"scr_30": lambda: show_bad_habit_remove_trigger(user_id, chat_id, message_id),
		"scr_31": lambda: show_bad_habit_enter_new_habit(user_id, chat_id, message_id),
		"scr_31_finished": lambda: show_bad_habit_tracked(user_id, chat_id, message_id, timestamp),
		"scr_33_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_33_2'),
		"scr_33_finished": lambda: show_bad_habit_tracked_with_reminder(user_id, chat_id, message_id, timestamp, text=None),
		"scr_37": lambda: show_hardening_bad_habit(user_id, chat_id, message_id),
		"scr_38_reminder_question": lambda: show_one_time_habit_reminder_question(user_id, chat_id, message_id),
		"scr_38_no_reminder": lambda: show_one_time_habit_created_no_reminder(user_id, chat_id, message_id, timestamp),
		"scr_review_sent": lambda: show_review_sent(user_id, chat_id, message_id, timestamp),
		"scr_donate_100": lambda: show_donate_screen(chat_id, message_id, sum=100),
		"scr_donate_500": lambda: show_donate_screen(chat_id, message_id, sum=500),
		"scr_donate_1000": lambda: show_donate_screen(chat_id, message_id, sum=1000),
		"scr_donate_5000": lambda: show_donate_screen(chat_id, message_id, sum=5000),
		"scr_40": lambda: show_user_timezone(user_id, chat_id, message_id),
		"scr_41": lambda: show_all_reports_in_settings(user_id, chat_id, message_id),
		"scr_41_1": lambda: show_choose_report(callback_data, user_id, chat_id, message_id),
		"scr_41_1_deleted": lambda: show_report_deleted(user_id, chat_id, message_id),
		"scr_42": lambda: show_delete_all_data_confirmation(user_id, chat_id, message_id),
		"scr_41_add_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_41_add_2'),
		"scr_41_1_change_2": lambda: show_choose_weekdays(user_id, chat_id, message_id, scr_name='scr_41_1_change_2'),
		"scr_44": lambda: show_habits_to_delete(user_id, chat_id, message_id),
		"no_scr": lambda: delete_message(message_id, chat_id),
		("scr_12_1", "scr_12"): lambda: show_magic_wanding_return_back_to_start(chat_id, message_id, user_id, 'scr_12'),
		("scr_12", "scr_9"): lambda: show_getting_back_to_predefined_habits(user_id, chat_id, message_id, unix_timestamp),
	}
	SPECIAL_CALLBACK_SCREENS = SPECIAL_CALLBACK_HANDLERS.keys()

	CONDITIONAL_CALLBACK_HANDLERS = {
		"scr_srbai_report_2_": lambda: show_srbai_question_2(user_id, chat_id, message_id, callback_data),
		"scr_srbai_report_3_": lambda: show_srbai_question_3(user_id, chat_id, message_id, callback_data),
		"scr_srbai_report_4_": lambda: show_srbai_question_4(user_id, chat_id, message_id, callback_data),
		"scr_srbai_finish_": lambda: show_srbai_result(user_id, chat_id, message_id, timestamp, callback_data),

		"scr_12_proxy_": lambda: show_magic_wanding_return_back(user_id, chat_id, message_id),
		"hab_": lambda: show_predefined_habits(callback_data, user_id, chat_id, message_id, unix_timestamp),
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

	elif previous_screen=="scr_0_timezone" and callback_data.startswith("utc"):
		show_onboarding_habit(user_id, chat_id, message_id, message, timestamp, callback_data, text=None, message_info=None)

	elif previous_screen=="scr_40" and callback_data.startswith("utc"):
		change_user_timezone(user_id, chat_id, message_id, callback_data, text=None, message_info=None)

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

	elif callback_data in DEFAULT_CALLBACK_SCREENS_REPORTS:
		handle_default_callback(callback_data, mode="report")

	elif is_callback_in_screens_weekdays_and_time_report:
		handle_weekdays_and_time_choice(callback_data, callback_screens_weekdays_and_time)
	elif is_callback_in_screens_weekdays_and_time_habit:
		handle_weekdays_and_time_choice(callback_data, callback_screens_weekdays_and_time)
	elif is_callback_in_screens_weekdays_and_time_habit_report:
		handle_weekdays_and_time_choice(callback_data, callback_screens_weekdays_and_time)
	else:
		handle_unknown_callback(callback_data)

	# Saving data
	data = {"user_id":user_id,"chat_id":chat_id, "message_id":message_id, "callback_data":callback_data, "text":None}
	db.record_user_action(user_id, "button_pressed", timestamp, metadata=callback_data)
	return data

def handle_text_input(text, chat_id, message_id, user_id, timestamp, message_info, message):
	def handle_special_input(special_handlers_dict, transition):
		action = special_handlers_dict.get(transition)
		action()

	def handle_conditional_input(conditional_handlers_dict, conditional_screens, transition):
		matching_prefix = next((prefix for prefix in conditional_screens if transition.startswith(prefix)), None)
		action = conditional_handlers_dict.get(matching_prefix)
		action()

	previous_screen = cache.get_previous_message(user_id)['callback_data']

	SPECIAL_INPUT_HANDLERS = {
		"scr_report_keep_forgetting": lambda: show_report_forgetting_repetition(user_id, chat_id, message_id, text),
		"scr_report_keep_skipping_notif_trigger": lambda: show_report_forgetting_repetition(user_id, chat_id, message_id, text),
		"scr_report_too_hard": lambda: show_report_skipped_finish(user_id, chat_id, message_id, text),
		"scr_report_keep_skipping_notif_3": lambda: show_report_keep_skipping_notif_finish(user_id, chat_id, message_id, text, message_info),

		"scr_srbai_too_hard": lambda: show_srbai_habit_changed(user_id, chat_id, message_id, timestamp, text),

		"scr_0_timezone_1": lambda: show_onboarding_habit(user_id, chat_id, message_id, message, timestamp, callback_data=None, text=text, message_info=message_info),
		"scr_0_5_add_3": lambda: show_onboarding_report_added(user_id, chat_id, message_id, text, timestamp, message_info),
		"scr_2": lambda: show_adding_habit(text, user_id, chat_id, message_id, timestamp),
		"scr_3": lambda: show_habit_info(text, user_id, chat_id, message_id, message_info, timestamp),
		"scr_3_1_bad_habit_remove_trigger": lambda: show_change_bad_habit_trigger_removed(text, user_id, chat_id, message_id, timestamp),
		"scr_3_1_bad_habit_avoid_trigger_3": lambda: show_change_bad_habit_reminder_text_for_trigger(user_id, chat_id, message_id, text, timestamp, message_info),
		"scr_3_1_bad_habit_avoid_trigger_reminder_text": lambda: show_change_bad_habit_trigger_avoided(user_id, chat_id, message_id, timestamp, text),
		"scr_3_1_bad_habit_harden_behavior": lambda: show_change_bad_habit_hardened(text, user_id, chat_id, message_id, timestamp),
		"scr_3_1_trigger": lambda: show_trigger_updated(text, user_id, chat_id, message_id, timestamp),
		"scr_3_1_reminder_3": lambda: show_habit_reminder_updated(text, user_id, chat_id, message_id, timestamp, message_info=message_info),
		"scr_3_3": lambda: show_change_habit_aspiration(text, chat_id, message_id, user_id, timestamp),
		"scr_3_4_change_3": lambda: show_report_updated_for_habit(user_id, chat_id, message_id, text=text, timestamp=timestamp, message_info=message_info),
		"scr_3_5_time_3": lambda: show_trigger_reminder_changed(user_id, chat_id, message_id, text, timestamp, message_info),
		"scr_3_6": lambda: show_one_time_habit_change_reminder(text, user_id, chat_id, message_id, timestamp, message_info),
		"scr_5": lambda: show_return_habit_back(text, user_id, chat_id, message_id, timestamp, message_info),
		"scr_8_1": lambda: show_reminding_options_after_making_habit_tiny(text, chat_id, message_id, user_id),
		"scr_9": lambda: show_picked_predefined_habits(text, chat_id, message_id, user_id, timestamp, message_info),
		"scr_10": lambda: show_aspiration_confirmation(chat_id, message_id, user_id, text=text),
		"scr_12": lambda: show_magic_wanding(text, chat_id, message_id, user_id, message_info),
		"scr_12_1": lambda: show_magic_wanding_from_ai_recommended_habits(user_id, chat_id, message_id, text, message_info),
		"scr_17": lambda: show_magic_wanding(text, chat_id, message_id, user_id, message_info),
		"scr_19": lambda: show_updated_habitname(text, chat_id, message_id, user_id, timestamp),
		"scr_22_2": lambda: show_pick_report_for_habit(user_id, chat_id, message_id, text=text, message_info=message_info),
		"scr_23": lambda: show_habit_repetition(user_id, chat_id, message_id, callback_data=None, text=text),
		"scr_26_1": lambda: show_repetition_reminder_set(user_id, chat_id, message_id, callback_data=None, text=text, timestamp=timestamp, message_info=message_info),
		"scr_28_2": lambda: show_pick_report_for_habit(user_id, chat_id, message_id, text=text, message_info=message_info),
		"scr_29": lambda: show_habit_is_tracked(user_id, chat_id, message_id, callback_data=None, text=text, timestamp=timestamp, message_info=message_info),
		"scr_29_add_3": lambda: show_habit_is_tracked(user_id, chat_id, message_id, callback_data=None, text=text, timestamp=timestamp, message_info=message_info),
		"scr_31": lambda: show_bad_habit_new_habit_created(text, user_id, chat_id, message_id, timestamp),
		"scr_33_3": lambda: show_bad_habit_reminder_text_for_trigger(user_id, chat_id, message_id, text=text, timestamp=timestamp, message_info=message_info),
		"scr_36": lambda: show_bad_habit_tracked_with_reminder(user_id, chat_id, message_id, timestamp, text=text),
		"scr_37": lambda: show_bad_habit_tracked_with_hardening(text, user_id, chat_id, message_id, timestamp),
		"scr_38": lambda: show_one_time_habit_created(text, chat_id, message_id, user_id, timestamp, message_info),
		"scr_40_1": lambda: change_user_timezone(user_id, chat_id, message_id, callback_data=None, text=text, message_info=message_info),
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

	else:
		if previous_screen and previous_screen!="None":
			keyboard = {
				"inline_keyboard": [
					[{"text": "Вернуться назад", "callback_data": previous_screen}]
				]
			}
			switch_screen(replies['unknown_message'], chat_id, message_id, keyboard=json.dumps(keyboard))
		else:
			switch_screen(replies['unknown_message'], chat_id, message_id, keyboard=get_button('scr_plug'))

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
		show_start_screen(user_id, chat_id, message_id, unix_timestamp)
		db.record_user_action(user_id, "pressed_start", timestamp, metadata=text)
	else:
		handle_text_input(text, chat_id, message_id, user_id, timestamp, message_info, message)
		db.record_user_action(user_id, "text_entered", timestamp, metadata=text)

	return message_info

def handle_invoice(message):
	"""Handles the invoice sent to the user."""
	pre_checkout_query_id = message['pre_checkout_query']['id']
	confirm_pre_checkout_query(pre_checkout_query_id)

def handle_payment(message):
	"""Handles the successful payment made by the user."""
	chat_id = message['message']['chat']['id']
	message_id = message['message']['message_id']
	user_id = message['message']['from']['id']
	unix_timestamp = message['message']['date']
	total_amount_rub = message['message']['successful_payment']['total_amount'] // 100
	timestamp = unix_to_timestamp(unix_timestamp)

	replies_for_amount = replies['donate_finish']
	replies_for_amount = replies_for_amount.get(f"{total_amount_rub}")
	reply = random.choice(replies_for_amount)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_donate_finish'))
	delete_message(message_id-1, chat_id)
	
	#Update donating sum
	donated_sum = db.get_user_property(user_id, "donated_sum")
	donated_sum += total_amount_rub
	db.update_user_donated_sum(user_id, int(donated_sum))

	db.record_user_action(user_id, "payment_made", timestamp, metadata=f"{total_amount_rub}RUB")

def handle_unknown_message(message):
	"""Handles messages that are neither text nor button presses."""
	chat_id = message['message']['chat']['id']
	message_id = message['message']['message_id']
	user_id = message['message']['from']['id']

	delete_message(message_id-1, chat_id)
	switch_screen(replies['unknown_message'], chat_id, message_id, keyboard=get_button('scr_unknown_message'))

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

def invoice_is_sent(message):
    return 'pre_checkout_query' in message.keys()

def payment_was_successful(message):
    return 'message' in message and 'successful_payment' in message['message']
