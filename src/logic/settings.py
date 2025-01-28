import json
import random
import re

from ._common_imports import *
from ._common_imports import callback_weekdays
from config import (
	CACHE_KEY_PHRASE,
	CACHE_REPORT,
	CACHE_FILEPATH
	)
from common import (
	add_report_buttons,
	numbers_to_weekdays,
	parse_time_from_string,
	weekdays_to_numbers,
	)
from utils import (
	get_cached_data, 
	save_data_to_cache, 
	delete_user_records
	)

def show_all_reports_in_settings(user_id, chat_id, message_id):
	user_reports = db.view_reports(user_id)
	no_reports = len(user_reports)==0
	main_message = replies['41']['main_message']
	keyboard = get_button('scr_41')
	if no_reports:
		additional_message = replies['41']['no_report']
	else:
		additional_message = replies['41']['reports_exist']
		keyboard = add_report_buttons('scr_41', user_id)

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

def show_choose_report(callback_data, user_id, chat_id, message_id):
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
	if callback_data == "scr_41_1":
		report_num = get_cached_data(CACHE_REPORT, user_id, chat_id, property="report_name")
		report_num = report_num.split(" ")[-1]
	else:
		report_num = callback_data.split("_")[-1]
	report = db.get_report(user_id, report_num)[0]
	report_info = {"user_id": user_id,
					"chat_id":chat_id,
					"report_id":report.get("id"), 
					"report_name":report.get("name"), 
					"report_period":report.get("on_weekdays"),
					"report_time":report.get("on_time")}

	if callback_data != "scr_41_1":
		save_data_to_cache(CACHE_REPORT, report_info)

	reply = replies['41_1'].replace("[report_name]", report_info["report_name"])
	report_period = json.loads(report_info["report_period"])
	report_period = numbers_to_weekdays(report_period)
	report_period = sorted(report_period, key=lambda day: weekdays_order.index(day))
	if tuple(report_period) == callback_weekdays:
		report_period_str_rus = "каждый день"+f" в {report_info["report_time"]}"
		reply = reply.replace("[report_period]", report_period_str_rus)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_41_1'))
		return
	report_period_rus = [weekdays_rus_dict[day] for day in report_period]
	report_period_str_rus = ", ".join(report_period_rus)
	report_period_str_rus = report_period_str_rus+f" в {report_info["report_time"]}"
	reply = reply.replace("[report_period]", report_period_str_rus)

	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_41_1'))

def show_report_deleted(user_id, chat_id, message_id):
	report_id = get_cached_data(CACHE_REPORT, user_id, chat_id, property="report_id")
	linked_habits = db.get_user_habits_linked_to_report(report_id)

	for habit in linked_habits:
		habit_id = habit['h.id']
		db.update_habit_with_null(habit_id, "report_id")

	db.delete_report(report_id)
	switch_screen(replies['41_1_deleted'], chat_id, message_id, keyboard=get_button('scr_41_1_deleted'))

def show_report_changed(text, user_id, chat_id, message_id, timestamp, message_info):
	try:
		parse_time_from_string(text)
		report_id = get_cached_data(CACHE_REPORT, user_id, chat_id, property="report_id")
		report_reminder_period = get_cached_data(CACHE_REPORT, user_id, chat_id, property="report_reminder_period")
		report_reminder_period = weekdays_to_numbers(report_reminder_period)
		report_reminder_time = text
		db.update_report(report_id, 'on_weekdays', f"'{report_reminder_period}'")
		db.update_report(report_id, 'on_time', f"'{report_reminder_time}'")
		db.update_report(report_id, 'updated_at', f"CAST('{timestamp}' AS Timestamp)")

		switch_screen(replies['41_1_changed'], chat_id, message_id, keyboard=get_button('scr_41_1_changed'))
	except ValueError:
		reply="Неверно указано время.\nВремя должно быть указано в формате HH:MM. Например: 21:45.\n\nПопробуйте еще раз."
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_41_1_change_3'))
		message_info["callback_data"]="scr_41_1_change_3"

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
