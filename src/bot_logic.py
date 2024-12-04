import json
import os
import random
import re
from typing import Any, Callable, Dict, List, Optional

import tg_methods
from database import (
	add_habit,
	delete_habit,
	delete_user_data,
	generate_unique_uuid,
	update_habit,
	view_habits,
)
from recommender import get_ai_response
from utils import *

# Constants for file paths
REPLIES_FILEPATH = "./strings/replies.json"
BUTTONS_FILEPATH = "./strings/buttons.json"
PREMADE_HABITS_FILEPATH = "./strings/premade_habits.json"

cache_filepath = "./cache/callback_history.json"
cache_pickhabit_filepath = "./cache/picking_habit.json"
cache_updatehabit_filepath = "./cache/updating_habit.json"

# Load JSON data
replies = load_json(REPLIES_FILEPATH)
premade_habits = load_json(PREMADE_HABITS_FILEPATH)
aspirations = list(premade_habits.keys())


def use_logic(message):
	if button_is_pressed(message):
		message_info = handle_callback_query(message)
	elif text_message_is_entered(message):

		# Getting data
		chat_id = message['message']['chat']['id']
		text = message['message']['text']
		message_id = message['message']['message_id']
		user_id = message['message']['from']['id']
		unix_timestamp = message['message']['date']
		timestamp = unix_to_timestamp(unix_timestamp)

		message_info = {"user_id": user_id, "chat_id": chat_id, 
						"message_id": message_id, "callback_data": None, 
						"text": text}

		handle_text_input(text, chat_id, message_id, user_id, timestamp, message_info)
	else:
		
		# Getting data
		chat_id = message['message']['chat']['id']
		message_id = message['message']['message_id']
		user_id = message['message']['from']['id']

		tg_methods.send_text_message('Я понимаю только текстовые сообщения и кнопки', chat_id)
		message_info = {"user_id": user_id,"chat_id": chat_id, 
						"message_id": message_id, "callback_data": None, 
						"text": None}
	
	newdata = append_to_json(filepath=cache_filepath, new_data=message_info)
	save_to_json(filepath=cache_filepath, new_data=newdata)


def handle_callback_query(message):

	# Getting data
	callback_query_id = message['callback_query']['id']
	callback_data = message['callback_query']['data']
	chat_id = message['callback_query']['message']['chat']['id']
	message_id = message['callback_query']['message']['message_id']
	user_id = message['callback_query']['from']['id']
	unix_timestamp = message['callback_query']['message']['date']
	timestamp = unix_to_timestamp(unix_timestamp)


	## Actual logic
	if callback_data == "scr_1":
		switch_screen(replies['1'], chat_id, message_id, keyboard=get_button('scr_1'))

	elif callback_data == "scr_2":
		switch_screen(replies['2'], chat_id, message_id, keyboard=get_button('scr_2'))

	elif callback_data == "scr_3":
		user_habits = view_habits(user_id)
		no_habits = len(user_habits)==0

		if no_habits:
			reply = replies['3_no_habits']
			switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_3_no_habits'))
		else:
			habit_names = [item['name'] for item in user_habits]
			habit_names_str = format_numbered_list(habit_names)
			reply = replies['3'].replace('[habits]', habit_names_str)
			switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_3'))

	elif callback_data == "scr_3_1":
		switch_screen(replies['3.1'], chat_id, message_id, keyboard=get_button('scr_3_1'))

	elif callback_data == "scr_4":
		aspirations_str = format_numbered_list(aspirations)
		reply = replies['4'].replace("[aspirations]", aspirations_str)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_4'))

	elif callback_data in ("hab_1", "hab_2", "hab_3", "hab_4", "hab_5", "hab_6", "hab_7", "hab_8", "hab_9", "hab_10"):
		aspiration_idx = int(callback_data.split('_')[-1])-1
		aspiration = aspirations[aspiration_idx]
		habits = list(premade_habits[aspiration])
		random_habits = random.sample(habits, k=10)
		random_habits_str = format_numbered_list(random_habits)
		reply = replies['9'].replace("[habits]", random_habits_str)

		new_data = {"user_id":user_id,"chat_id":chat_id, "aspiration":aspiration, "habits":None, "behavior_options":random_habits, "suitability":None, "effectiveness":None}
		new_data = append_to_json(filepath = cache_pickhabit_filepath, new_data=new_data)
		save_to_json(cache_pickhabit_filepath, new_data)

		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_9'))

	elif callback_data == "scr_5":
		switch_screen(replies['5'], chat_id, message_id, keyboard=get_button('scr_5'))

	elif callback_data == "scr_6":
		switch_screen(replies['6'], chat_id, message_id, keyboard=get_button('scr_6'))

	elif callback_data == "scr_8":
		switch_screen(replies['8'], chat_id, message_id, 
						delete_previous=False, keyboard=get_button('scr_8'))

	elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")in ("hab_1", "hab_2", "hab_3", "hab_4", "hab_5", "hab_6", "hab_7", "hab_8", "hab_9", "hab_10") and callback_data=="scr_12":
		switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('9_scr_12'))

	elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=="scr_9" and callback_data=="scr_12":
		switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('9_scr_12'))

	elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=="scr_11" and callback_data=="scr_12":
		switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('scr_12'))

	elif callback_data == "scr_9":
		switch_screen(replies['9'], chat_id, message_id, keyboard=get_button('scr_9'))

	elif callback_data == "scr_10":
		switch_screen(replies['10'], chat_id, message_id, keyboard=get_button('scr_10'))

	elif callback_data == "scr_11":
		aspiration = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="aspiration")
		reply = replies['11'].replace("[aspiration]", aspiration)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_11'))

	elif callback_data == "scr_12":
		switch_screen(replies['12'], chat_id, message_id, keyboard=get_button('scr_12'))

	elif callback_data == "scr_12_1":
		aspiration = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="aspiration")
		habits = get_ai_response(aspiration=aspiration)
		numbered_habits = format_numbered_list(habits.values())
		behavior_options_list = [habit for habit in habits.values()]
		reply = "Возможно, вам подойдут эти варианты:\n\n"+numbered_habits+'\n\n---\n\n'+replies['ai_warn']

		switch_screen(reply, chat_id, message_id, delete_previous=False, keyboard=get_button('scr_12_1'))
		update_user_value(cache_pickhabit_filepath, user_id, "behavior_options", behavior_options_list)

	elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=="scr_16" and callback_data=="scr_13":
		switch_screen(replies['13'], chat_id, message_id, keyboard=get_button('16_scr_13'))

	elif callback_data == "scr_13":
		switch_screen(replies['13'], chat_id, message_id, 
						delete_previous=False, keyboard=get_button('scr_13'))

	elif callback_data == "scr_15":
		switch_screen(replies['15'], chat_id, message_id, keyboard=get_button('scr_15'))

	elif callback_data == "scr_16": 
		switch_screen(replies['16'], chat_id, message_id, keyboard=get_button('scr_16'))

	elif callback_data == "scr_17": 
		switch_screen(replies['17'], chat_id, message_id, keyboard=get_button('scr_17'))

	elif callback_data == "scr_18": 
		habits = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="habits")
		habits_str = format_numbered_list(habits)
		for habit in habits:
			unique_id = generate_unique_uuid()
			add_habit(habit=habit, creation_datetime=timestamp, user_id=user_id, unique_id=unique_id)	
		delete_user_records(cache_pickhabit_filepath, user_id)
		reply = replies['18']+f"\n\nСохраненные привычки:\n{habits_str}"

		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_18'))

	elif callback_data == "scr_19":
		switch_screen(replies['19'], chat_id, message_id, keyboard=get_button('scr_19'))

	elif callback_data == "scr_21":
		switch_screen(replies['21'], chat_id, message_id, 
						delete_previous=False, keyboard=get_button('scr_21'))
	
	elif callback_data == "scr_22": 
		switch_screen(replies['22'], chat_id, message_id, keyboard=get_button('scr_22'))

	elif callback_data == "scr_23_1":
		switch_screen(replies['23.1'], chat_id, message_id, keyboard=get_button('scr_23_1')) 

	elif callback_data == "scr_23": 
		switch_screen(replies['23'], chat_id, message_id, keyboard=get_button('scr_23'))

	elif callback_data == "scr_25": 
		switch_screen(replies['25'], chat_id, message_id, keyboard=get_button('scr_25'))

	elif callback_data == "scr_26": 
		switch_screen(replies['26'], chat_id, message_id, keyboard=get_button('scr_26'))

	elif callback_data == "scr_27": 
		switch_screen(replies['27'], chat_id, message_id, keyboard=get_button('scr_27'))

	elif callback_data == "scr_28": 
		switch_screen(replies['28'], chat_id, message_id, keyboard=get_button('scr_28'))

	elif callback_data == "scr_30": 
		switch_screen(replies['30'], chat_id, message_id, keyboard=get_button('scr_30'))

	elif callback_data == "scr_31": 
		switch_screen(replies['31'], chat_id, message_id, keyboard=get_button('scr_31'))

	elif callback_data == "scr_32": 
		switch_screen(replies['32'], chat_id, message_id, keyboard=get_button('scr_32'))

	elif callback_data == "scr_33": 
		switch_screen(replies['33'], chat_id, message_id, keyboard=get_button('scr_33'))

	elif callback_data == "scr_34": 
		switch_screen(replies['34'], chat_id, message_id, keyboard=get_button('scr_34'))

	elif callback_data == "scr_35": 
		switch_screen(replies['35'], chat_id, message_id, keyboard=get_button('scr_35'))

	elif callback_data == "scr_37": 
		switch_screen(replies['37'], chat_id, message_id, keyboard=get_button('scr_37'))

	elif callback_data == "scr_38": 
		switch_screen(replies['38'], chat_id, message_id, keyboard=get_button('scr_38'))

	elif callback_data == "scr_39": 
		switch_screen(replies['39'], chat_id, message_id, keyboard=get_button('scr_39'))

	elif callback_data == "scr_40": 
		switch_screen(replies['40'], chat_id, message_id, keyboard=get_button('scr_40'))

	elif callback_data == "scr_41": 
		switch_screen(replies['41'], chat_id, message_id, keyboard=get_button('scr_41'))

	elif callback_data == "scr_42": 
		switch_screen(replies['42'], chat_id, message_id, keyboard=get_button('scr_42'))

	elif callback_data == "scr_44": 
		switch_screen(replies['44'], chat_id, message_id, delete_previous=False,
						keyboard=get_button('scr_44'))
	
	elif callback_data == "plug": 
		switch_screen(replies['plug'], chat_id, message_id, keyboard=get_button('plug'))

	else:
		tg_methods.send_text_message("Error: unknown callback data", chat_id, protect_content=True)

	# Saving data
	data = {"user_id":user_id,"chat_id":chat_id, "message_id":message_id, "callback_data":callback_data, "text":None}
	return data

def handle_text_query(text, chat_id, message_id, user_id):

	# Actual logic
	if text=="/start":
		switch_screen(replies['start'], chat_id, message_id, keyboard=get_button('start'))

	## Saving data
	data = {"user_id":user_id,"chat_id":chat_id, "message_id":message_id, "callback_data":None, "text":text}
	return data

def handle_text_input(text, chat_id, message_id, user_id, timestamp, message_info):
		# ATTENTION! Possible problems when a user types command '/start'
		if get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_2':
			add_habit(habit=text, creation_datetime=timestamp, user_id=user_id)
			switch_screen(replies['7'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_7'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_3_1':
			switch_screen(replies['21'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_21'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_8':
			habits = view_habits(user_id)
			try:
				habit_idx = int(text)-1
				habit_name = habits[habit_idx].get("name")
				new_data = {"user_id":user_id,"chat_id":chat_id, "habit_number":habit_idx, "habit_name":habit_name}
				new_data = append_to_json(filepath = cache_updatehabit_filepath, new_data=new_data)
				save_to_json(cache_updatehabit_filepath, new_data)
				reply = replies['8.1']+f"\n\nВы выбрали привычку: {habit_name}"

				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_8_1'))

			except ValueError:
				reply = "Пожалуйста, введите номер привычки, которую вы хотите изменить числом."
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_8'))
				message_info["callback_data"]="scr_8"
			except IndexError:
				reply = "Такой привычки не существует. Попробуйте ещё раз."
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_8'))
				message_info["callback_data"]="scr_8"

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data") in ("hab_1", "hab_2", "hab_3", "hab_4", "hab_5", "hab_6", "hab_7", "hab_8", "hab_9", "hab_10") or get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=="scr_9":
			try:
				pattern = r"\b\d{1,2}\b"
				if ", " in text:
					entered_numbers = [int(num) for num in text.split(', ')]
				elif "," in text:
					entered_numbers = [int(num) for num in text.split(',')]
				elif re.findall(pattern, text):
					entered_numbers = [int(text)]
				else:
					raise IndexError
				habit_options = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="behavior_options")	
				filtered_habits = [i-1 for i in entered_numbers if i < len(habit_options)+1]
				selected_habits = [habit_options[i] for i in filtered_habits]
				filtered_habits_str = format_numbered_list(selected_habits)
				check_minimum_length(selected_habits, min_length=1)
				update_user_value(cache_pickhabit_filepath, user_id, "habits", selected_habits)
				
				### Save to DB
				for habit in selected_habits:
					unique_id = generate_unique_uuid()
					add_habit(habit=habit, creation_datetime=timestamp, user_id=user_id, unique_id=unique_id)
				delete_user_records(cache_pickhabit_filepath, user_id)

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

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_10':
			new_data = {"user_id":user_id,"chat_id":chat_id, "aspiration":text, 
						"habits":None, "behavior_options":None, "suitability":None, 
						"effectiveness":None}
			new_data = append_to_json(filepath = cache_pickhabit_filepath, new_data=new_data)
			save_to_json(cache_pickhabit_filepath, new_data)
			reply = replies['11'].replace("[aspiration]", text)
			switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_11'))
			
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_12':
			try:
				behaviors = [line.split('. ')[1] for line in text.strip().split('\n') if line]
				check_minimum_length(behaviors)
				update_user_value(cache_pickhabit_filepath, user_id, "behavior_options", behaviors)
				
				switch_screen(replies['13'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_13"

			except IndexError:
				reply = "Данные были введены некорректно.\n\nПожалуйста, введите в формате:\n 1. <поведение1>\n 2. <поведение2>\n..."
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_12"

			except ListTooShortError:
				reply = "Вариантов поведения должно быть, как минимум, 5.\n\nПожалуйста, введите в формате:\n 1. <поведение1>\n 2. <поведение2>\n..."
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_12"

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_13':
			try:
				suitability_ratings = [int(line.split('. ')[1]) for line in text.strip().split('\n')]
				check_all_in_range(suitability_ratings)
				behaviors = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="behavior_options")
				check_matching_lengths(suitability_ratings, behaviors)
				update_user_value(cache_pickhabit_filepath, user_id, "suitability", suitability_ratings)
				
				switch_screen(replies['14'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_14'))
				message_info["callback_data"]="scr_14"

			except ValueError:
				reply = "Оценки должны быть числовыми, от 1 до 10.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n"
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_13"

			except ValueOutOfRangeError:
				reply = "Оценки должны быть от 1 до 10.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n"
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_13"
			except ListLengthMismatchError:
				reply = "Оценок должно быть столько же, сколько и вариантов поведения.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n"
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_13"
			except IndexError:
				reply = "Данные были введены некорректно.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n"
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_13"

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_14':
			try:
				effectiveness_ratings = [int(line.split('. ')[1]) for line in text.strip().split('\n')]
				check_all_in_range(effectiveness_ratings)
				behaviors = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="behavior_options")
				check_matching_lengths(effectiveness_ratings, behaviors)
				update_user_value(cache_pickhabit_filepath, user_id, "effectiveness", effectiveness_ratings)
				suitability_ratings = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="suitability")
				
				habit_grades = sum_arrays(suitability_ratings, effectiveness_ratings)
				top_habits = [habit for _, habit in sorted(zip(habit_grades, behaviors), reverse=True)[:3]]
				top_habits_str = format_numbered_list(top_habits)

				reply = replies['15'].replace("[habits]", top_habits_str)
				update_user_value(cache_pickhabit_filepath, user_id, "habits", top_habits)
				
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_15'))
				message_info["callback_data"]="scr_14"

			except ValueError:
				reply = "Оценки должны быть числовыми, от 1 до 10.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n"
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_14"

			except ValueOutOfRangeError:
				reply = "Оценки должны быть от 1 до 10.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n"
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_14"

			except ListLengthMismatchError:
				reply = "Оценок должно быть столько же, сколько и вариантов поведения.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n"
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_14"

			except IndexError:
				reply = "Данные были введены некорректно.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n"
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_14"

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_17': 
			try:
				behaviours = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="behavior_options")
				new_behaviors = [line.split('. ')[1] for line in text.strip().split('\n') if line]
				behaviours.extend(new_behaviors)
				update_user_value(cache_pickhabit_filepath, user_id, "behavior_options", behaviours)
				
				switch_screen(replies['13'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_13"

			except IndexError:
				reply = "Данные были введены некорректно.\n\nПожалуйста, введите в формате:\n 1. <поведение1>\n 2. <поведение2>\n..."
				switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_13'))
				message_info["callback_data"]="scr_17"

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_19':
			new_name = text
			habit_idx = get_cached_data(cache_updatehabit_filepath, user_id, chat_id, property="habit_number")
			unique_id = view_habits(user_id)[habit_idx].get("id")
			update_habit(unique_id, "name", f"'{new_name}'")
			update_habit(unique_id, "last_updated", f"CAST('{timestamp}'AS Timestamp)")
			updated_habits = view_habits(user_id)
			habit_names = [item['name'] for item in updated_habits]
			habit_names_str = format_numbered_list(habit_names)
			reply = replies['20'].replace("[updated_habits]", habit_names_str)
			switch_screen(reply, chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_23':
			switch_screen(replies['24'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_24'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_26':
			switch_screen(replies['20'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_28':
			switch_screen(replies['20'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_31':
			switch_screen(replies['7'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_7'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_33':
			switch_screen(replies['36'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_36'))
			message_info["callback_data"]="scr_36"
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_35':
			switch_screen(replies['36'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_36'))
			message_info["callback_data"]="scr_36"

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_36':
			switch_screen(replies['20'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_37':
			switch_screen(replies['20'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_38':
			switch_screen(replies['20'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_20'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_40':
			switch_screen(replies['43'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_43'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_41':
			switch_screen(replies['43'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('scr_43'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_42':
			switch_screen(replies['start'], chat_id, message_id, 
							delete_previous=False, keyboard=get_button('start'))

		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_44':
			try:
				pattern = r"\b\d{1,2}\b"
				if ", " in text:
					entered_numbers = [int(num) for num in text.split(', ')]
				elif "," in text:
					entered_numbers = [int(num) for num in text.split(',')]
				elif re.findall(pattern, text):
					entered_numbers = [int(text)]
				else:
					raise IndexError
				user_habits = view_habits(user_id)
				for idx in entered_numbers:
					unique_id = user_habits[idx-1].get("id")
					delete_habit(unique_id)
				updated_user_habits = view_habits(user_id)

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

			except IndexError:
				reply = "Введенный текст должен содержать привычки, введеные через запятую. Попробуйте ввести еще раз."
				switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_44'))
				message_info["callback_data"]="scr_44"
		else:
			handle_text_query(text, chat_id, message_id, user_id)


def switch_screen(
    reply: str,
    chat_id: int,
    message_id: int,
    delete_previous: bool = True,
    disable_notification: Optional[bool] = None,
    protect_content: bool = True,
    reply_parameters: Optional[Dict[str, Any]] = None,
    keyboard: Optional[str] = None,
) -> None:
    """Sends a message and optionally deletes the previous one."""
    tg_methods.send_text_message(
        reply,
        chat_id,
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


# Getting cache data

def get_cached_data(filepath, user_id, chat_id, property):
	# Check if file exists and read data if so
	if os.path.exists(filepath):
		with open(filepath, "r", encoding="utf-8") as json_file:
			try:
				data = json.load(json_file)
			except json.JSONDecodeError:
				print("Error: JSON file is empty or corrupted.")
				return None
	else:
		print("Error: File does not exist.")
		return None

	# Find the entry that matches the specified user_id and chat_id
	for entry in data:
		if entry.get("user_id") == user_id and entry.get("chat_id") == chat_id:
			return entry.get(property)

	# Return None if no matching entry is found
	print("No matching entry found for the given user_id and chat_id.")
	return None

# Saving to cache

def save_data_to_cache(filepath, data):
	new_data = append_to_json(filepath=filepath, new_data=data)
	save_to_json(filepath=cache_filepath, new_data=new_data)
	print(f"Data have been saved successfully to {filepath}")


# Checking for conditions

def text_message_is_entered(message):
	return 'message' in message and 'text' in message['message']

def button_is_pressed(message):
	return 'callback_query' in message.keys()

def check_all_in_range(input_list, min=1, max=10):
	# Check if all items are between 1 and 10
	if not all(min <= item <= max for item in input_list):
		raise ValueOutOfRangeError("All items must be between 1 and 10.")

def check_matching_lengths(list1, list2):
	"""Checks if two lists have matching lengths."""
	if len(list1) != len(list2):
		raise ListLengthMismatchError("The lengths of the lists do not match.")

def check_minimum_length(input_list, min_length=5):
	"""Ensures the list meets the minimum required length."""
	if len(input_list) < min_length:
		raise ListTooShortError(f"The list has fewer than {min_length} entries.")

# Other useful functions
def format_numbered_list(items: List[str], capitalize: bool = True) -> str:
    """
    Formats a list of strings into a numbered, newline-separated string.

    Args:
        items (List[str]): The list of strings to format.
        capitalize (bool, optional): Whether to capitalize each item. Defaults to True.

    Returns:
        str: A numbered, newline-separated string with each item optionally capitalized.
    """
    if capitalize:
        items = (item.capitalize() for item in items)
    else:
        items = (item for item in items)
    
    return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))

# Custom exceptions
class ValueOutOfRangeError(Exception):
	"""Custom exception for values out of range."""
	pass

class ListTooShortError(Exception):
	"""Custom exception for lists with fewer than 5 entries."""
	pass

class ListLengthMismatchError(Exception):
	"""Custom exception for list length mismatch errors."""
	pass
