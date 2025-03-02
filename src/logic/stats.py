from ._common_imports import *
from common import format_numbered_list

def show_user_stats(user_id, chat_id, message_id):
	accomplished_habits = db.view_finished_habits(user_id)
	no_habits = len(accomplished_habits)==0

	if no_habits:
		reply = replies['5_no_habits']
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_5_no_habits'))
	else:
		accomplished_habit_names = [item['name'] for item in accomplished_habits]
		accomplished_habit_names_str = format_numbered_list(accomplished_habit_names, capitalize=True)
		reply = replies['5'].replace("[finished_habits]", accomplished_habit_names_str)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_5'))

def show_return_habit_back(text, user_id, chat_id, message_id, timestamp, message_info):
	accomplished_habits = db.view_finished_habits(user_id)
	if len(accomplished_habits)==0:
		return
	try:
		habit_idx = int(text)-1
		if habit_idx<0:
			raise IndexError
		habit_id = accomplished_habits[habit_idx].get("id")
		habit_name = accomplished_habits[habit_idx].get("name")
		db.update_habit(habit_id, "status", f"'tracked'")
		db.add_habit_log(user_id, habit_id, "returned", timestamp)
		reply = replies['5_habit_returned'].replace("[habit]", habit_name)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_5_habit_returned'))
	except ValueError:
		habit_names = [item['name'] for item in accomplished_habits]
		habit_names_str = format_numbered_list(habit_names)
		reply = replies['5_errors']['incorrect_format'].replace("[habits]", habit_names_str)
		switch_screen(reply, chat_id, message_id)
		message_info["callback_data"]="scr_5"
	except IndexError:
		habit_names = [item['name'] for item in accomplished_habits]
		habit_names_str = format_numbered_list(habit_names)
		reply = replies['5_errors']['incorrect_format'].replace("[habits]", habit_names_str)
		switch_screen(reply, chat_id, message_id)
		message_info["callback_data"]="scr_5"
