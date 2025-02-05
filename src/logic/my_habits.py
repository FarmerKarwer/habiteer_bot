from datetime import datetime, timedelta
import json
import random

from ._common_imports import *
from ._common_imports import premade_triggers, callback_weekdays
from common import (
	add_report_buttons,
	format_numbered_list,
	parse_numbers,
	numbers_to_weekdays,
	parse_time_from_string,
	validate_marginal_datetime_entry,
	calculate_datetime_margin_from_user_input,
	weekdays_to_numbers,
	)
from common.exceptions import ValueOutOfRangeError

def show_user_habits(user_id, chat_id, message_id):
	user_habits = db.view_habits(user_id)
	no_habits = len(user_habits)==0

	if no_habits:
		reply = replies['3_no_habits']
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_3_no_habits'))
	else:
		all_habits = []
		for item in user_habits:
			if item['status'] in ("tracked", "marked"):
				all_habits.append("🔄"+item['name'].capitalize())
			elif item['status']=="pending":
				all_habits.append("⏳"+item['name'].capitalize())
			elif item['status']=="stopped":
				all_habits.append("⏸️"+item['name'].capitalize())
			else:
				all_habits.append(item['name'].capitalize())

		habit_names_str = format_numbered_list(all_habits, capitalize=False)
		reply = replies['3'].replace('[habits]', habit_names_str)
		keyboard = get_button('scr_3')
		switch_screen(reply, chat_id, message_id, keyboard=keyboard, protect_content=False)

def show_habit_info(text, user_id, chat_id, message_id, message_info):
	habits = db.view_habits(user_id)
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
	try:
		habit_idx = int(text)-1
		habit_id = habits[habit_idx].get("id")
		habit_name = habits[habit_idx].get("name")
		aspiration = habits[habit_idx].get("aspiration")
		status = habits[habit_idx].get("status")
		report_name = None
		if status is None:
			reply = replies['3_1']['not_tracked'].replace('[habit]', habit_name)
			keyboard = get_button('scr_3_1_not_tracked')
		elif status in ("tracked", "pending", "marked"):
			if status=="tracked":
				reply = replies['3_1']['tracked'].replace('[habit]', habit_name)
				keyboard = get_button('scr_3_1_tracked')
			elif status=="pending":
				reply = replies['3_1']['pending'].replace('[habit]', habit_name)
				keyboard = get_button('scr_3_1_pending')
			elif status=="marked":
				reply = replies['3_1']['marked'].replace('[habit]', habit_name)
				keyboard = get_button('scr_3_1_tracked')
			elif status=="stopped":
				reply = replies['3_1']['stopped'].replace('[habit]', habit_name)
				keyboard = get_button('scr_3_1_stopped')

			habit_type = habits[habit_idx].get("type")
			trigger_type = habits[habit_idx].get("trigger_type")

			if status in ("tracked", "marked"):
				report_id = habits[habit_idx].get("report_id")
				if report_id is not None:
					report_name = db.get_report_by_id(report_id)[0].get("name")
					reply = reply.replace('[report]', report_name)
				else:
					report_name = "Не указан"
					reply = reply.replace('[report]', report_name)

			if trigger_type=="notification":
				trigger_time = habits[habit_idx].get("trigger_reminder_time")
				trigger_period = habits[habit_idx].get("trigger_reminder_period")
				trigger_period = json.loads(trigger_period)
				trigger_period = numbers_to_weekdays(trigger_period)
				trigger_period = sorted(trigger_period, key=lambda day: weekdays_order.index(day))
				if tuple(trigger_period) == callback_weekdays:
					trigger_desc = f"Каждый день в {trigger_time}"
				else:
					trigger_period = [weekdays_rus_dict[day] for day in trigger_period]
					trigger_period = ", ".join(trigger_period)
					trigger_desc = f"Каждый {trigger_period} в {trigger_time}"
			elif trigger_type=="behavior":
				trigger_desc = habits[habit_idx].get("trigger_action_desc")

			reply = reply.replace('[trigger]', trigger_desc)
			if habit_type == "regular":
				reply = reply.replace('[type]', "Обычная")
			elif habit_type == "harmful":
				reply = reply.replace('[type]', "Вредная")
			elif habit_type == "one-time":
				reply = reply.replace('[type]', "Одноразовая")

		if aspiration is None or aspiration=="None":
			reply = reply.replace('[aspiration]', '_не указано_')
		else:
			reply = reply.replace('[aspiration]', aspiration)
			keyboard = json.loads(keyboard)
			keyboard['inline_keyboard'][2][0]['text'] = keyboard['inline_keyboard'][2][0]['text'].replace('Добавить', 'Изменить')
			keyboard = json.dumps(keyboard)

		new_data = {
			"habit_id":habit_id,
			"habit_number": habit_idx,
			"habit_name": habit_name.capitalize(),
			"status":status,
			"aspiration":aspiration,
			"report_name":report_name
		}

		cache.save_updating_habit_info(user_id, new_data)
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
	text = str(cache.get_updating_habit_info(user_id, "habit_number")+1)
	show_habit_info(text, user_id, chat_id, message_id, message_info)

def show_choosing_habit_type(user_id, chat_id, message_id):
	habit_name = cache.get_updating_habit_info(user_id, "habit_name")
	reply = replies['21'].replace('[habit]', habit_name)
	keyboard = get_button('scr_21')
	habit_idx = cache.get_updating_habit_info(user_id, "habit_number")
	if habit_idx == "no_number":
		keyboard = json.loads(keyboard)
		del keyboard["inline_keyboard"][3]
		keyboard = json.dumps(keyboard)
	switch_screen(reply, chat_id, message_id, keyboard=keyboard)

def show_is_habit_tiny(user_id, chat_id, message_id):
	habit_name = cache.get_updating_habit_info(user_id, "habit_name")
	reply = replies['8'].replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_8'))

def show_make_habit_tiny(user_id, chat_id, message_id):
	habit_name = cache.get_updating_habit_info(user_id, "habit_name")
	reply = replies['8_1'].replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_8_1'))

def show_reminding_options_after_making_habit_tiny(text, chat_id, message_id, user_id):
	new_habit_name = text
	cache.update_updating_habit_info(user_id, "new_habit_name", new_habit_name)
	switch_screen(replies['22'], chat_id, message_id, keyboard=get_button('scr_22'))

def show_choose_time_for_habit(user_id, chat_id, message_id, scr_name, type=None):
	screen_id = '_'.join(scr_name.split('_')[1:])
	if type=="everyday":
		habit_reminder_time = callback_weekdays
		cache.update_updating_habit_info(user_id, "habit_reminder_time", habit_reminder_time)
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
		habit_reminder_time = tuple(cache.get_button_selection(user_id, "user_selections"))
		cache.update_updating_habit_info(user_id, "habit_reminder_time", habit_reminder_time)

		if habit_reminder_time==callback_weekdays:
			reply = replies[screen_id].replace("[period]", "каждый день")
		else:
			habit_reminder_time = sorted(habit_reminder_time, key=lambda day: weekdays_order.index(day))
			habit_reminder_time_rus = [weekdays_rus_dict[day] for day in habit_reminder_time]
			habit_reminder_time_str_rus = ", ".join(habit_reminder_time_rus)
			reply = replies[screen_id].replace("[period]", habit_reminder_time_str_rus)

	cache.delete_button_selection(user_id)
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
		report_reminder_time = tuple(cache.get_button_selection(user_id, "user_selections"))

		if report_reminder_time==callback_weekdays:
			reply = replies[screen_id].replace("[period]", "каждый день")
		else:
			report_reminder_time = sorted(report_reminder_time, key=lambda day: weekdays_order.index(day))
			report_reminder_time_rus = [weekdays_rus_dict[day] for day in report_reminder_time]
			report_reminder_time_str_rus = ", ".join(report_reminder_time_rus)
			reply = replies[screen_id].replace("[period]", report_reminder_time_str_rus)

	new_data = {
			"report_reminder_period": report_reminder_time,
		}
	if cache.get_report_info(user_id, "report_id") is None:
		cache.save_report_info(user_id, new_data)
	else:
		cache.update_report_info(user_id, "report_reminder_period", report_reminder_time)

	cache.delete_button_selection(user_id)
	switch_screen(reply, chat_id, message_id, keyboard=get_button(scr_name))

def show_premade_triggers(user_id, chat_id, message_id):
	habit_name = cache.get_updating_habit_info(user_id, "habit_name")
	new_habit_name = cache.get_updating_habit_info(user_id, "new_habit_name")
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
	cache.update_updating_habit_info(user_id, "trigger_options", chosen_triggers)
	triggers_str = format_numbered_list(chosen_triggers)
	reply = replies['23_1'].replace('[triggers]', triggers_str)
	reply = reply.replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_23_1'))

def show_enter_your_trigger(user_id, chat_id, message_id):
	habit_info = cache.get_updating_habit_info(user_id)
	habit_name = habit_info.get("habit_name")
	new_habit_name = habit_info.get("new_habit_name")
	habit_status = habit_info.get("status")
	if new_habit_name:
		habit_name = new_habit_name
	if habit_status not in ("tracked", "marked", "pending", "stopped"):
		reply = replies['23'].replace('[habit]', habit_name)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_23'))
	else:
		reply = replies['3_1_trigger'].replace('[habit]', habit_name)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_3_1_trigger'))

def show_habit_repetition(user_id, chat_id, message_id, callback_data=None, text=None):
	habit_name = cache.get_updating_habit_info(user_id, "habit_name")
	new_habit_name = cache.get_updating_habit_info(user_id, "new_habit_name")
	if new_habit_name:
		habit_name = new_habit_name
	if text:
		chosen_trigger = text
		cache.update_updating_habit_info(user_id, "trigger", chosen_trigger)
	if callback_data and callback_data!="scr_24" and callback_data!="scr_24_resume":
		trigger_options = cache.get_updating_habit_info(user_id, "trigger_options")
		chosen_trigger_idx = int(callback_data.split('_')[-1])-1
		chosen_trigger = trigger_options[chosen_trigger_idx]
		cache.update_updating_habit_info(user_id, "trigger", chosen_trigger)
	if callback_data=="scr_24":
		chosen_trigger = cache.get_updating_habit_info(user_id, "trigger")
	if callback_data=="scr_24_resume":
		habit_id = cache.get_updating_habit_info(user_id, "habit_id")
		chosen_trigger = db.get_habit_by_id(habit_id)[0].get("trigger_action_desc")
		cache.update_updating_habit_info(user_id, "trigger", chosen_trigger)

		reply = replies['24_resume'].replace('[trigger]', chosen_trigger)
		reply = reply.replace('[habit]', habit_name)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_24_resume'))
		return
	reply = replies['24'].replace('[trigger]', chosen_trigger)
	reply = reply.replace('[habit]', habit_name)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_24'))

def show_repetition_reminder_set(user_id, chat_id, message_id, callback_data=None, text=None, timestamp=None, message_info=None):
	time_values = {
		"15min": timedelta(minutes=15),
		"30min": timedelta(minutes=30),
		"1h": timedelta(hours=1),
		"2h": timedelta(hours=2),
		"4h": timedelta(hours=4),
		"8h": timedelta(hours=8),
		"1d": timedelta(days=1),
		"2d": timedelta(days=2)
		}
	if callback_data:
		reminder_margin = callback_data.split('_')[-1]
		reminder_margin = time_values[reminder_margin]
		timestamp_dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
		reminder_time = timestamp_dt+reminder_margin
		
	if text:
		try:
			validate_marginal_datetime_entry(text)
			reminder_time = calculate_datetime_margin_from_user_input(text, timestamp)
		except ValueError:
			previous_screen = cache.get_previous_message(user_id)['callback_data']
			reply="Неверно указан период.\nУкажите в формате: “Через X дн в HH:MM”. Например, если хотите отрепетировать сегодня: “через 0 дн в 21:25”.\n\nПопробуйте еще раз."
			switch_screen(reply, chat_id, message_id, keyboard=get_button(previous_screen))
			message_info["callback_data"]=previous_screen
			return
		except ValueOutOfRangeError:
			previous_screen = cache.get_previous_message(user_id)['callback_data']
			reply="Указанный период меньше текущего времени.\nУкажите в формате: “Через X дн в HH:MM”.\n\nПопробуйте еще раз."
			switch_screen(reply, chat_id, message_id, keyboard=get_button(previous_screen))
			message_info["callback_data"]=previous_screen
			return

	habit_info = cache.get_updating_habit_info(user_id)
	habit_id = habit_info.get('habit_id', None)
	habit_name = habit_info.get('habit_name', None)
	new_habit_name = habit_info.get('new_habit_name', None)
	trigger = habit_info.get('trigger', None)

	habit_type = "regular"
	trigger_type = "behavior"
	if new_habit_name:
		habit_name = new_habit_name
	habit_status="pending"

	data_to_update = {
		"name":f"'{habit_name}'",
		"status":f"'{habit_status}'",
		"last_updated":f"CAST('{timestamp}' AS Timestamp)",
		"type" : f"'{habit_type}'",
		"trigger_type":f"'{trigger_type}'",
		"trigger_action_desc":f"'{trigger}'",
		"repetition_reminder_time":f"CAST('{reminder_time}' AS Datetime)"
	}

	for key in data_to_update.keys():
		db.update_habit(unique_id=habit_id, column=key, value=data_to_update[key])

	reminder_time_str = reminder_time.strftime("%d.%m.%Y %H:%M")
	reply = replies['26_2'].replace('[repetition_reminder_time]', reminder_time_str)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_26_2'))

def show_set_trigger_notification_confirmation(user_id, chat_id, message_id):
	habit_info = cache.get_updating_habit_info(user_id)
	habit_name = habit_info['habit_name']
	new_habit_name = habit_info['new_habit_name']
	trigger = habit_info['trigger']
	if new_habit_name:
		habit_name = new_habit_name
	reply = replies['27'].replace('[trigger]', trigger)
	reply = reply.replace('[habit]', habit_name)

	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_27'))

def show_pick_report_for_habit(user_id, chat_id, message_id, callback_data=None, text=None, message_info=None):
	habit_status = cache.get_updating_habit_info(user_id, "status")
	user_reports = db.view_reports(user_id)
	no_reports = len(user_reports)==0
	main_message = replies['29']['main_message']

	if text:
		try:
			parse_time_from_string(text)
			notification_time = text
			cache.update_updating_habit_info(user_id, "trigger_reminder_time", notification_time)
			message_info['callback_data'] = 'scr_29'
		except ValueError:
			previous_screen = cache.get_previous_message(user_id)['callback_data']
			reply="Неверно указано время.\nВремя должно быть указано в формате HH:MM. Например: 21:45.\n\nПопробуйте еще раз."
			switch_screen(reply, chat_id, message_id, keyboard=get_button(previous_screen))
			message_info["callback_data"]=previous_screen
			return
	
	if no_reports:
		additional_message = replies['29']['no_report']
	else:
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
		additional_message = replies['29']['reports_exist']
		report_strs = {}
		for report in user_reports:
			report_name = report.get("name")
			report_time = report.get("on_time")
			report_period = json.loads(report.get("on_weekdays"))
			report_period = numbers_to_weekdays(report_period)
			report_period = sorted(report_period, key=lambda day: weekdays_order.index(day))
			if tuple(report_period) == callback_weekdays:
				report_period_str_rus = "каждый день"+f" в {report_time}"
			else:
				report_period_rus = [weekdays_rus_dict[day] for day in report_period]
				report_period_str_rus = ", ".join(report_period_rus)
				report_period_str_rus = report_period_str_rus+f" в {report_time}"
			report_strs.update({report_name:report_period_str_rus})
		formatted_schedule = '\n'.join([f"*{report}*: _{time}_" for report, time in report_strs.items()])
		additional_message = additional_message.replace('[reports]', formatted_schedule)

	reply = main_message+additional_message
	if habit_status not in ("tracked", "marked", "stopped"):
		keyboard = add_report_buttons('scr_29', user_id)
	else:
		report_name = cache.get_updating_habit_info(user_id, "report_name")
		reply = f"*Текущий отчет*: _{report_name}_\n\n"+reply
		keyboard = add_report_buttons('scr_3_4', user_id)
	switch_screen(reply, chat_id, message_id, keyboard=keyboard)

def show_habit_is_tracked(user_id, chat_id, message_id, callback_data=None, text=None, timestamp=None, message_info=None):
	if text:
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

			trigger_reminder_time = cache.get_updating_habit_info(user_id, "trigger_reminder_time")
		except ValueError:
			reply="Неверно указано время.\nВремя должно быть указано в формате HH:MM. Например: 21:45.\n\nПопробуйте еще раз."
			switch_screen(reply, chat_id, message_id, keyboard=get_button(previous_screen))
			message_info["callback_data"]=previous_screen
			return
	if callback_data:
		report_num = callback_data.split("_")[-1]
		report = db.get_report(user_id, report_num)[0]
		report_id = report.get("id")

	habit_info = cache.get_updating_habit_info(user_id)
	habit_id = habit_info.get("habit_id", None)
	habit_name = habit_info.get("habit_name", None)
	new_habit_name = habit_info.get("new_habit_name", None)
	trigger = habit_info.get("trigger", None)
	trigger_reminder_period = habit_info.get("habit_reminder_time", None)
	trigger_reminder_time = habit_info.get("trigger_reminder_time", None)

	if new_habit_name:
		habit_name = new_habit_name
	if trigger:
		trigger_type="behavior"
	else:
		trigger_type="notification"
	habit_type = "regular"
	habit_status="tracked"
	if trigger_reminder_period:
		trigger_reminder_period = weekdays_to_numbers(trigger_reminder_period)

	data_to_update = {
		"name":f"'{habit_name}'",
		"status":f"'{habit_status}'",
		"last_updated":f"CAST('{timestamp}' AS Timestamp)",
		"type" : f"'{habit_type}'",
		"trigger_type":f"'{trigger_type}'",
		"trigger_action_desc":f"'{trigger}'",
		"trigger_reminder_period":f"'{trigger_reminder_period}'",
		"trigger_reminder_time":f"'{trigger_reminder_time}'",
		"report_id":f"{report_id}"
	}

	for key in data_to_update.keys():
		db.update_habit(unique_id=habit_id, column=key, value=data_to_update[key])

	switch_screen(replies['20'], chat_id, message_id, keyboard=get_button('scr_20'))


def show_mark_habit_as_completed(user_id, chat_id, message_id, timestamp):
	habit_id = cache.get(user_id, "habit_id")
	status = "completed"
	habit_status = "marked"

	epoch_date = datetime(1970, 1, 1)
	today = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").date()  # Simulated current date
	yesterday = today - timedelta(days=1)

	print(today, yesterday)

	db.add_habit_log(user_id, habit_id, status, timestamp)

	#Calculating streak
	logs = db.get_habit_logs_for_habit(user_id, habit_id, status="completed")

	if not logs:
		current_streak = 0
		max_streak = 0
	else:
		current_streak = 0
		max_streak = 0
		prev_date = None

		for log in logs:
			current_date = log["date"]

			if prev_date is None or (current_date == (prev_date + 1)):
				current_streak += 1
			prev_date = current_date

		max_streak = max(max_streak, current_streak)

		actual_date = epoch_date + timedelta(days=current_date)
		if logs and actual_date not in [today, yesterday]:
			current_streak = 0

	db.update_habit(habit_id, "status", f"'{habit_status}'")
	print(f"Current Streak: {current_streak}")
	print(f"Max Streak: {max_streak}")

	#switch_screen(replies['3_2'], chat_id, message_id, keyboard=keyboard)

# TO-DO: change these two functions to one function
def show_updated_habitname(text, chat_id, message_id, user_id, timestamp):
	new_name = text
	habit_idx = cache.get_updating_habit_info(user_id, "habit_number")
	unique_id = db.view_habits(user_id)[habit_idx].get("id")
	db.update_habit(unique_id, "name", f"'{new_name}'")
	db.update_habit(unique_id, "last_updated", f"CAST('{timestamp}'AS Timestamp)")

	switch_screen(replies['3_7'], chat_id, message_id, keyboard=get_button('scr_3_7'))

def show_trigger_updated(text, user_id, chat_id, message_id, timestamp):
	updated_trigger = text
	habit_id = cache.get_updating_habit_info(user_id, "habit_id")
	db.update_habit(habit_id, "trigger_action_desc", f"'{updated_trigger}'")
	db.update_habit(habit_id, "last_updated", f"CAST('{timestamp}'AS Timestamp)")
	db.update_habit(habit_id, "trigger_type", "'behavior'")
	db.update_habit(habit_id, "trigger_reminder_period", "NULL")
	db.update_habit(habit_id, "trigger_reminder_time", "NULL")

	switch_screen(replies['3_7'], chat_id, message_id, keyboard=get_button('scr_3_7'))

def show_report_updated_for_habit(user_id, chat_id, message_id, callback_data=None, text=None, timestamp=None, message_info=None):
	if text:
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
	if callback_data:
		report_num = callback_data.split("_")[-1]
		report = db.get_report(user_id, report_num)[0]
		report_id = report.get("id")

	habit_id = cache.get_updating_habit_info(user_id, "habit_id")

	db.update_habit(habit_id, "report_id", report_id)
	db.update_habit(habit_id, "last_updated", f"CAST('{timestamp}'AS Timestamp)")

	switch_screen(replies['3_4_changed'], chat_id, message_id, keyboard=get_button('scr_3_4_changed'))

def show_change_habit_aspiration(text, chat_id, message_id, user_id, timestamp):
	new_aspiration = text
	habit_idx = cache.get_updating_habit_info(user_id, "habit_number")
	unique_id = db.view_habits(user_id)[habit_idx].get("id")
	db.update_habit(unique_id, "aspiration", f"'{new_aspiration}'")
	db.update_habit(unique_id, "last_updated", f"CAST('{timestamp}'AS Timestamp)")

	switch_screen(replies['3_7'], chat_id, message_id, keyboard=get_button('scr_3_7'))

def show_updated_habits_after_deletion(text, chat_id, message_id, user_id, message_info):
	try:
		entered_numbers = parse_numbers(text)
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