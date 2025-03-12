import json
import os
import random
import re
from dotenv import load_dotenv
load_dotenv()

from ._common_imports import *
from ._common_imports import callback_weekdays
from common import (
	convert_timezone,
	add_report_buttons,
	numbers_to_weekdays,
	parse_time_from_string,
	weekdays_to_numbers,
	insert_inline_keyboard_row
	)
from common.exceptions import InvalidTimezoneFormat, TimezoneOutOfRangeError
from config import TIMEZONE_DICT
from tg_methods import send_invoice, delete_message

def show_settings_screen(user_id, chat_id, message_id):
	user_credits = db.get_user_property(user_id, "daily_ai_credits")
	donated_sum = db.get_user_property(user_id, "donated_sum")
	if donated_sum is None:
		donated_sum = 0
	if user_credits is None:
		user_credits = 0

	if user_id==940985788:
		reply = replies['6_user'].replace('[credits]', str(user_credits))
		reply = reply.replace('[support_level]', "Основатель").replace('[support_emoji]', "🌟")
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_6'))
		return

	user_level = db.get_user_level(donated_sum)[0]
	level_id = user_level['id']
	level_name = user_level['name']
	level_emoji = user_level['emoji']
	if level_id!=0:
		level_required_donation = user_level['donation_required']

		next_level = db.get_next_user_level(donated_sum)
		if next_level:
			next_level = next_level[0]
			next_level_name = next_level['name']
			next_level_donation = next_level['donation_required']
			remaining_amount = int(next_level_donation - donated_sum)
			progress = (donated_sum - level_required_donation) / (next_level_donation - level_required_donation) * 100
			filled_blocks = int(progress / 10)
			progress_bar = "▓" * filled_blocks + "░" * (10 - filled_blocks)

			reply = replies['6'].replace('[credits]', str(user_credits))
			reply = reply.replace('[support_level]', level_name).replace('[support_emoji]', level_emoji).replace('[level_num]', str(level_id))
			reply = reply.replace('[progress_bar]', progress_bar).replace('[progress]', str(int(progress)))
			reply = reply.replace('[next_level]', next_level_name).replace('[remaining_donations]', str(remaining_amount))
			reply = reply.replace('[total_sum]', str(int(donated_sum)))
		else:
			reply = replies['6_max_level'].replace('[credits]', str(user_credits))
			reply = reply.replace('[support_level]', level_name).replace('[support_emoji]', level_emoji).replace('[level_num]', str(level_id))
			reply = reply.replace('[total_sum]', str(int(donated_sum)))
	else:
		reply = replies['6_user'].replace('[credits]', str(user_credits))
		reply = reply.replace('[support_level]', level_name).replace('[support_emoji]', level_emoji)

	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_6'))

def show_donate_screen(chat_id, message_id, sum):
	donate_replies = {
		100: replies['donate_100'],
		500: replies['donate_500'],
		1000: replies['donate_1000'],
		5000: replies['donate_5000']
	}
	title = "Поддержать проект"
	description = donate_replies[sum]
	payload = "donate"
	provider_token = os.getenv("PAYMENT_PROVIDER_TOKEN")
	currency = "RUB"
	prices = [
		{"label": "Поддержка Habiteer", "amount": sum*100}
	]
	keyboard = get_button('scr_donate_proceed')
	keyboard = json.loads(keyboard)
	payment_row = [{"text": "💳 Поддержать", "pay": True}]
	keyboard = insert_inline_keyboard_row(keyboard, payment_row, position=0)
	send_invoice(chat_id, title, description, payload, provider_token, currency, prices, keyboard=json.dumps(keyboard))
	delete_message(message_id, chat_id)

def show_user_timezone(user_id, chat_id, message_id):
	current_timezone = db.select_user(user_id)[0]['timezone']
	if current_timezone is None:
		current_timezone = "utc+3"
	timezone_name = TIMEZONE_DICT[current_timezone]
	reply = replies['40'].replace('[timezone]', f"{current_timezone.upper()} ({timezone_name})")
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_40'))

def change_user_timezone(user_id, chat_id, message_id, callback_data=None, text=None, message_info=None):
	if text:
		try:
			timezone = convert_timezone(text)
			db.update_user_timezone(user_id, timezone)
		except InvalidTimezoneFormat:
			switch_screen(replies['timezone_errors']['invalid_format'], chat_id, message_id, keyboard=get_button('scr_40_1'))
			message_info['callback_data']="scr_40_1"
			return
		except TimezoneOutOfRangeError:
			switch_screen(replies['timezone_errors']['out_of_range'], chat_id, message_id, keyboard=get_button('scr_40_1'))
			message_info['callback_data']="scr_40_1"
			return
	elif callback_data:
		db.update_user_timezone(user_id, callback_data)

	switch_screen(replies['40_changed'], chat_id, message_id, keyboard=get_button('scr_40_changed'))

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
		report_period = cache.get_report_info(user_id, "report_reminder_period")
		report_period = weekdays_to_numbers(report_period)
		report_time = text
		db.add_report(user_id, timestamp, report_period, report_time)
		switch_screen(replies['41_added'], chat_id, message_id, keyboard=get_button('scr_41_added'))
		cache.delete_report_info(user_id)
	except ValueError:
		reply=replies["incorrect_time_error"]
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
		report_num = cache.get_report_info(user_id, "report_name")
		report_num = report_num.split(" ")[-1]
	else:
		report_num = callback_data.split("_")[-1]
	report = db.get_report(user_id, report_num)[0]
	report_info = {"report_id":report.get("id"), 
					"report_name":report.get("name"), 
					"report_period":report.get("on_weekdays"),
					"report_time":report.get("on_time")}

	if callback_data != "scr_41_1":
		cache.save_report_info(user_id, report_info)

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
	report_id = cache.get_report_info(user_id, "report_id")
	linked_habits = db.get_user_habits_linked_to_report(report_id)

	for habit in linked_habits:
		habit_id = habit['h.id']
		db.update_habit_with_null(habit_id, "report_id")

	db.delete_report(report_id)
	switch_screen(replies['41_1_deleted'], chat_id, message_id, keyboard=get_button('scr_41_1_deleted'))

def show_report_changed(text, user_id, chat_id, message_id, timestamp, message_info):
	try:
		parse_time_from_string(text)
		report_id = cache.get_report_info(user_id, "report_id")
		report_reminder_period = cache.get_report_info(user_id, "report_reminder_period")
		report_reminder_period = weekdays_to_numbers(report_reminder_period)
		report_reminder_time = text
		db.update_report(report_id, 'on_weekdays', f"'{report_reminder_period}'")
		db.update_report(report_id, 'on_time', f"'{report_reminder_time}'")
		db.update_report(report_id, 'updated_at', f"CAST('{timestamp}' AS Timestamp)")

		switch_screen(replies['41_1_changed'], chat_id, message_id, keyboard=get_button('scr_41_1_changed'))
	except ValueError:
		reply=replies["incorrect_time_error"]
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_41_1_change_3'))
		message_info["callback_data"]="scr_41_1_change_3"

def show_review_confirmation(text, chat_id, message_id, user_id, message_info):
	reply = replies['review_confirmation'].replace('[review]', text)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_review_confirmation'))

def show_review_sent(user_id, chat_id, message_id, timestamp):
	review = cache.get_previous_message(user_id)['text']
	db.send_review(user_id, review, timestamp)
	switch_screen(replies['review_sent'], chat_id, message_id, keyboard=get_button('scr_review_sent'))

def show_delete_all_data_confirmation(user_id, chat_id, message_id):
	random_num = random.randint(1000000, 9999999)
	reply = replies['42'].replace('[random_num]', str(random_num))
	key_phrase = re.search(r"_([^_]+)_", reply).group(1)
	cache.save_key_phrase(user_id, key_phrase)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_42'))

def show_user_deletion_screen(text, chat_id, message_id, user_id, message_info):
	key_phrase = cache.get_key_phrase(user_id)
	if text == key_phrase:
		cache.delete_key_phrase(user_id)
		db.delete_user_data(user_id)
		switch_screen(replies['account_deleted'], chat_id, message_id, keyboard=get_button('scr_account_deleted'))
	else:
		reply = replies['42_error']
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_plug'))
