import json
import random
import re

from ._common_imports import *
from ._common_imports import aspirations, premade_habits
from config import CACHE_PICKHABIT_FILEPATH, CACHE_FILEPATH
from common import (
	format_numbered_list,
	parse_numbers,
	sum_arrays,
	check_minimum_length,
	)
from common.exceptions import ListTooShortError
from recommender import get_ai_response
from tg_methods import delete_message
from utils import (
	get_cached_data, 
	save_data_to_cache, 
	update_user_value,
	delete_user_records
	)

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
		delete_message(message_id-1, chat_id)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_11'))
	else:
		print("It is impossible to switch screen because the message does not contain text or callback")

def show_magic_wanding_return_back_to_start(chat_id, message_id, user_id, keyboard_name):
	behavior_options = None
	update_user_value(CACHE_PICKHABIT_FILEPATH, user_id, "behavior_options", behavior_options)
	switch_screen(replies['12'], chat_id, message_id, keyboard=get_button(keyboard_name))

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