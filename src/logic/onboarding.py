from ._common_imports import *
from common import (
	convert_timezone,
	parse_time_from_string,
	weekdays_to_numbers,
	)
from common.exceptions import InvalidTimezoneFormat, TimezoneOutOfRangeError

def show_start_onboarding(user_id, chat_id, message_id, message, timestamp):
	if "last_name" in message['message']['from'].keys():
		last_name = f"'{message['message']['from']['last_name']}'"
	else:
		last_name = "NULL"
	if "username" in message['message']['from'].keys():
		username = f"'{message['message']['from']['username']}'"
	else:
		username = "NULL"
	user_data = {
		"id":user_id,
		"username":username,
		"first_name":f"'{message['message']['from']['first_name']}'",
		"language":f"'{message['message']['from']['language_code']}'",
		"last_name":last_name,
		"created_at":f"CAST('{timestamp}' AS Timestamp)"
	}

	db.add_user(user_data['id'], user_data['username'], user_data['first_name'], user_data['last_name'], user_data['language'], user_data['created_at'])
	switch_screen(replies['0'], chat_id, message_id, keyboard=get_button('scr_0'))

def show_onboarding_habit(user_id, chat_id, message_id, callback_data=None, text=None, message_info=None):
	if text:
		try:
			timezone = convert_timezone(text)
			db.update_user_timezone(user_id, timezone)
		except InvalidTimezoneFormat:
			switch_screen(replies['timezone_errors']['invalid_format'], chat_id, message_id, keyboard=get_button('scr_0_timezone_1'))
			message_info['callback_data']="scr_0_timezone_1"
			return
		except TimezoneOutOfRangeError:
			switch_screen(replies['timezone_errors']['out_of_range'], chat_id, message_id, keyboard=get_button('scr_0_timezone_1'))
			message_info['callback_data']="scr_0_timezone_1"
			return
	elif callback_data:
		db.update_user_timezone(user_id, callback_data)

	switch_screen(replies['0_1'], chat_id, message_id, keyboard=get_button('scr_0_1'))

def show_onboarding_secret(user_id, chat_id, message_id):
	habit_id = 0
	habit_name = "Спрашивать себя: «За что я сегодня благодарен(а)?»"
	trigger = "Когда лягу в кровать перед сном"
	status = None
	aspiration = "Чувствовать себя счастливее каждый день😊"
	report_name = None
	new_data = {
			"habit_id":habit_id,
			"habit_name": habit_name.capitalize(),
			"status":status,
			"aspiration":aspiration,
			"report_name":report_name,
			"trigger":trigger
		}

	cache.save_updating_habit_info(user_id, new_data)
	switch_screen(replies['0_2'], chat_id, message_id, keyboard=get_button('scr_0_2'))

def show_onboarding_report_added(user_id, chat_id, message_id, text, timestamp, message_info):
	previous_screen = cache.get_previous_message(user_id)['callback_data']
	try:
		parse_time_from_string(text)
		report_period = cache.get_report_info(user_id, "report_reminder_period")
		report_period = weekdays_to_numbers(report_period)
		report_time = text
		db.add_report(user_id, timestamp, report_period, report_time)
		cache.delete_report_info(user_id)
		user_reports = db.view_reports(user_id)
		report_id = max(item['id'] for item in user_reports)
	except ValueError:
		reply="Неверно указано время.\nВремя должно быть указано в формате HH:MM. Например: 21:45.\n\nПопробуйте еще раз."
		switch_screen(reply, chat_id, message_id, keyboard=get_button(previous_screen))
		message_info["callback_data"]=previous_screen
		return

	habit_info = cache.get_updating_habit_info(user_id)
	habit_name = habit_info.get("habit_name", None)
	trigger_action_desc = habit_info.get("trigger", None)
	aspiration = habit_info.get("aspiration", None)
	habit_type="regular"
	trigger_type="behavior"
	status="tracked"

	db.add_onboarding_habit(habit_name, timestamp, habit_type, trigger_type, trigger_action_desc, user_id, status, aspiration, report_id)

	switch_screen(replies['0_6'], chat_id, message_id, keyboard=get_button('scr_0_6'))