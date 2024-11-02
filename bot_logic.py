import tg_methods
import json
import os
from utils import *
from recommender import get_ai_response
import random
import re
from database import add_habit, generate_unique_uuid

replies_filepath = "./strings/replies.json"
buttons_filepath = "./strings/buttons.json"
premade_habits_filepath = "./strings/premade_habits.json"
cache_filepath = "./cache/callback_history.json"
cache_pickhabit_filepath = "./cache/picking_habit.json"

replies = load_json(replies_filepath)
buttons = load_json(buttons_filepath)
premade_habits = load_json(premade_habits_filepath)
aspirations = list(premade_habits.keys())

def use_logic(message):
	if button_is_pressed(message):
		message_info = handle_callback_query(message)
	elif text_message_is_entered(message):

		## Getting data
		chat_id = message['message']['chat']['id']
		text = message['message']['text']
		message_id = message['message']['message_id']
		user_id = message['message']['from']['id']
		unix_timestamp = message['message']['date']
		timestamp = unix_to_timestamp(unix_timestamp)

		message_info = {"user_id":user_id,"chat_id":chat_id, "message_id":message_id, "callback_data":None, "text":text}

		handle_text_input(text, chat_id, message_id, user_id, timestamp, message_info)
	else:
		chat_id = message['message']['chat']['id']
		message_id = message['message']['message_id']
		user_id = message['message']['from']['id']

		tg_methods.send_text_message('Я понимаю только текстовые сообщения и кнопки', chat_id)
		message_info = {"user_id":user_id,"chat_id":chat_id, "message_id":message_id, "callback_data":None, "text":None}
	newdata = append_to_json(filepath = cache_filepath, new_data = message_info)
	save_to_json(filepath = cache_filepath, new_data = newdata)

def handle_callback_query(message):

	## Getting data
	callback_query_id = message['callback_query']['id']
	callback_data = message['callback_query']['data']
	chat_id = message['callback_query']['message']['chat']['id']
	message_id = message['callback_query']['message']['message_id']
	user_id = message['callback_query']['from']['id']
	unix_timestamp = message['callback_query']['message']['date']
	timestamp = unix_to_timestamp(unix_timestamp)

	print(get_cached_data(cache_filepath, user_id, chat_id, property="callback_data"))

	## Actual logic
	if callback_data == "scr_1":
		tg_methods.send_text_message(replies['1'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_1']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_2":
		tg_methods.send_text_message(replies['2'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_2']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_3":
		tg_methods.send_text_message(replies['3'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_3']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_3_1":
		tg_methods.send_text_message(replies['3.1'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_3_1']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_4":
		aspirations_str = "\n".join([f"{i+1}. {aspiration.capitalize()}" for i, aspiration in enumerate(aspirations)])
		reply = replies['4'].replace("[aspirations]", aspirations_str)
		tg_methods.send_text_message(reply, chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_4']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data in ("hab_1", "hab_2", "hab_3", "hab_4", "hab_5", "hab_6", "hab_7", "hab_8", "hab_9", "hab_10"):
		aspiration_idx = int(callback_data.split('_')[-1])-1
		aspiration = aspirations[aspiration_idx]
		habits = list(premade_habits[aspiration])
		random_habits = random.sample(habits, k=10)
		random_habits_str = "\n".join([f"{i+1}. {habit.capitalize()}" for i, habit in enumerate(random_habits)])
		reply = replies['9'].replace("[habits]", random_habits_str)

		new_data = {"user_id":user_id,"chat_id":chat_id, "aspiration":aspiration, "habits":None, "behavior_options":random_habits, "suitability":None, "effectiveness":None}
		new_data = append_to_json(filepath = cache_pickhabit_filepath, new_data=new_data)
		save_to_json(cache_pickhabit_filepath, new_data)

		tg_methods.send_text_message(reply, chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_9']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_5":
		tg_methods.send_text_message(replies['5'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_5']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_6":
		tg_methods.send_text_message(replies['6'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_6']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_8":
		tg_methods.send_text_message(replies['8'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_8']))
		tg_methods.delete_message(message_id, chat_id)
	elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")in ("hab_1", "hab_2", "hab_3", "hab_4", "hab_5", "hab_6", "hab_7", "hab_8", "hab_9", "hab_10") and callback_data=="scr_12":
		tg_methods.send_text_message(replies['12'], chat_id, protect_content=True, keyboard=json.dumps(buttons['9_scr_12']))
		tg_methods.delete_message(message_id, chat_id)
	elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=="scr_9" and callback_data=="scr_12":
		tg_methods.send_text_message(replies['12'], chat_id, protect_content=True, keyboard=json.dumps(buttons['9_scr_12']))
		tg_methods.delete_message(message_id, chat_id)
	elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=="scr_11" and callback_data=="scr_12":
		tg_methods.send_text_message(replies['12'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_12']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_9":
		tg_methods.send_text_message(replies['9'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_9']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_10":
		tg_methods.send_text_message(replies['10'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_10']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_11":
		aspiration = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="aspiration")
		reply = replies['11'].replace("[aspiration]", aspiration)
		tg_methods.send_text_message(reply, chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_11']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_12":
		tg_methods.send_text_message(replies['12'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_12']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_12_1":
		aspiration = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="aspiration")
		habits = get_ai_response(aspiration=aspiration)
		numbered_habits = "\n".join([f"{i+1}. {habit}" for i, habit in enumerate(habits.values())])
		behavior_options_list = [habit for habit in habits.values()]
		tg_methods.send_text_message("Возможно, вам подойдут эти варианты:\n\n"+numbered_habits+'\n\n---\n\n'+replies['ai_warn'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_12_1']))
		update_user_value(cache_pickhabit_filepath, user_id, "behavior_options", behavior_options_list)
	elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=="scr_16" and callback_data=="scr_13":
		tg_methods.send_text_message(replies['13'], chat_id, protect_content=True, keyboard=json.dumps(buttons['16_scr_13']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_13":
		tg_methods.send_text_message(replies['13'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
	elif callback_data == "scr_15":
		tg_methods.send_text_message(replies['15'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_15']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_16": 
		tg_methods.send_text_message(replies['16'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_16']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_17": 
		tg_methods.send_text_message(replies['17'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_17']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_18": 
		habits = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="habits")
		habits_str = "\n".join([f"{i+1}. {habit.capitalize()}" for i, habit in enumerate(habits)])
		for habit in habits:
			unique_id = generate_unique_uuid()
			add_habit(habit=habit, creation_datetime=timestamp, user_id=user_id, unique_id=unique_id)	
		delete_user_records(cache_pickhabit_filepath, user_id)
		tg_methods.send_text_message(replies['18']+f"\n\nСохраненные привычки:\n{habits_str}", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_18']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_19": 
		tg_methods.send_text_message(replies['19'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_19']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_21": 
		tg_methods.send_text_message(replies['21'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_21']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_22": 
		tg_methods.send_text_message(replies['22'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_22']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_23_1": 
		tg_methods.send_text_message(replies['23.1'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_23_1']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_23": 
		tg_methods.send_text_message(replies['23'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_23']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_25": 
		tg_methods.send_text_message(replies['25'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_25']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_26": 
		tg_methods.send_text_message(replies['26'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_26']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_27": 
		tg_methods.send_text_message(replies['27'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_27']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_28": 
		tg_methods.send_text_message(replies['28'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_28']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_30": 
		tg_methods.send_text_message(replies['30'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_30']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_31": 
		tg_methods.send_text_message(replies['31'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_31']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_32": 
		tg_methods.send_text_message(replies['32'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_32']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_33": 
		tg_methods.send_text_message(replies['33'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_33']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_34": 
		tg_methods.send_text_message(replies['34'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_34']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_35": 
		tg_methods.send_text_message(replies['35'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_35']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_37": 
		tg_methods.send_text_message(replies['37'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_37']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_38": 
		tg_methods.send_text_message(replies['38'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_38']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_39": 
		tg_methods.send_text_message(replies['39'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_39']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_40": 
		tg_methods.send_text_message(replies['40'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_40']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_41": 
		tg_methods.send_text_message(replies['41'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_41']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_42": 
		tg_methods.send_text_message(replies['42'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_42']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_44": 
		tg_methods.send_text_message(replies['44'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_44']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "plug": 
		tg_methods.send_text_message(replies['plug'], chat_id, protect_content=True, keyboard=json.dumps(buttons['plug']))
		tg_methods.delete_message(message_id, chat_id)
	else:
		tg_methods.send_text_message("Error: unknown callback data", chat_id, protect_content=True)

	## Saving data
	data = {"user_id":user_id,"chat_id":chat_id, "message_id":message_id, "callback_data":callback_data, "text":None}
	return data

def handle_text_query(text, chat_id, message_id, user_id):

	## Actual logic
	if text=="/start":
		tg_methods.send_text_message(replies['/start'], chat_id, protect_content=True, keyboard=json.dumps(buttons['start']))
		tg_methods.delete_message(message_id, chat_id)

	## Saving data
	data = {"user_id":user_id,"chat_id":chat_id, "message_id":message_id, "callback_data":None, "text":text}
	return data

def handle_text_input(text, chat_id, message_id, user_id, timestamp, message_info):
	### Possible problems when a user types command '/start'
		if get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_2':
			add_habit(habit=text, creation_datetime=timestamp, user_id=user_id)
			tg_methods.send_text_message(replies['7'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_7']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_3_1':
			tg_methods.send_text_message(replies['21'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_21']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_8':
			tg_methods.send_text_message(replies['8.1'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_8_1']))
			print(text)
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
				filtered_habits_str = "\n".join([f"{i+1}. {habit.capitalize()}" for i, habit in enumerate(selected_habits)])
				check_minimum_length(selected_habits, min_length=1)
				update_user_value(cache_pickhabit_filepath, user_id, "habits", selected_habits)
				### Save to DB
				for habit in selected_habits:
					unique_id = generate_unique_uuid()
					add_habit(habit=habit, creation_datetime=timestamp, user_id=user_id, unique_id=unique_id)
				delete_user_records(cache_pickhabit_filepath, user_id)
				tg_methods.send_text_message(replies['18']+f"\n\nСохраненные привычки:\n{filtered_habits_str}", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_18']))
			except ValueError:
				tg_methods.send_text_message("Введенный текст должен содержать числа, введеные через запятую. Возможно, у вас лишние пробелы. Попробуйте ввести еще раз.", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_9']))
				message_info["callback_data"]="scr_9"
			except IndexError:
				tg_methods.send_text_message("Введенный текст должен содержать 1-3 привычки, введеные через запятую. Попробуйте ввести еще раз.", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_9']))
				message_info["callback_data"]="scr_9"
			except ListTooShortError:
				tg_methods.send_text_message("Введенный текст должен содержать хотя бы одну привычку из списка. Возможно, вы ввели слишком маленькое или большое число. Попробуйте ввести еще раз.", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_9']))
				message_info["callback_data"]="scr_9"
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_10':
			new_data = {"user_id":user_id,"chat_id":chat_id, "aspiration":text, "habits":None, "behavior_options":None, "suitability":None, "effectiveness":None}
			new_data = append_to_json(filepath = cache_pickhabit_filepath, new_data=new_data)
			save_to_json(cache_pickhabit_filepath, new_data)
			reply = replies['11'].replace("[aspiration]", text)
			tg_methods.send_text_message(reply, chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_11']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_12':
			try:
				behaviors = [line.split('. ')[1] for line in text.strip().split('\n') if line]
				check_minimum_length(behaviors)
				update_user_value(cache_pickhabit_filepath, user_id, "behavior_options", behaviors)
				tg_methods.send_text_message(replies['13'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_13"
			except IndexError:
				tg_methods.send_text_message("Данные были введены некорректно.\n\nПожалуйста, введите в формате:\n 1. <поведение1>\n 2. <поведение2>\n...", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_12"
			except ListTooShortError:
				tg_methods.send_text_message("Вариантов поведения должно быть, как минимум, 5.\n\nПожалуйста, введите в формате:\n 1. <поведение1>\n 2. <поведение2>\n...", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_12"
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_13':
			try:
				suitability_ratings = [int(line.split('. ')[1]) for line in text.strip().split('\n')]
				check_all_in_range(suitability_ratings)
				behaviors = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="behavior_options")
				check_matching_lengths(suitability_ratings, behaviors)
				update_user_value(cache_pickhabit_filepath, user_id, "suitability", suitability_ratings)
				tg_methods.send_text_message(replies['14'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_14']))
				message_info["callback_data"]="scr_14"
			except ValueError:
				tg_methods.send_text_message("Оценки должны быть числовыми, от 1 до 10.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_13"
			except ValueOutOfRangeError:
				tg_methods.send_text_message("Оценки должны быть от 1 до 10.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_13"
			except ListLengthMismatchError:
				tg_methods.send_text_message("Оценок должно быть столько же, сколько и вариантов поведения.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_13"
			except IndexError:
				tg_methods.send_text_message("Данные были введены некорректно.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_13"
			print(text)
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
				top_habits_str = "\n".join([f"{i+1}. {habit}" for i, habit in enumerate(top_habits)])

				reply = replies['15'].replace("[habits]", top_habits_str)
				update_user_value(cache_pickhabit_filepath, user_id, "habits", top_habits)
				tg_methods.send_text_message(reply, chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_15']))
				message_info["callback_data"]="scr_14"
			except ValueError:
				tg_methods.send_text_message("Оценки должны быть числовыми, от 1 до 10.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_14"
			except ValueOutOfRangeError:
				tg_methods.send_text_message("Оценки должны быть от 1 до 10.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_14"
			except ListLengthMismatchError:
				tg_methods.send_text_message("Оценок должно быть столько же, сколько и вариантов поведения.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_14"
			except IndexError:
				tg_methods.send_text_message("Данные были введены некорректно.\n\nПожалуйста, введите в формате:\n1. <оценка числом от 1 до 10>\n2. <оценка числом от 1 до 10>\n", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_14"
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_17': 
			try:
				behaviours = get_cached_data(cache_pickhabit_filepath, user_id, chat_id, property="behavior_options")
				new_behaviors = [line.split('. ')[1] for line in text.strip().split('\n') if line]
				behaviours.extend(new_behaviors)
				update_user_value(cache_pickhabit_filepath, user_id, "behavior_options", behaviours)
				tg_methods.send_text_message(replies['13'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_13"
			except IndexError:
				tg_methods.send_text_message("Данные были введены некорректно.\n\nПожалуйста, введите в формате:\n 1. <поведение1>\n 2. <поведение2>\n...", chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
				message_info["callback_data"]="scr_17"
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_19':
			tg_methods.send_text_message(replies['20'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_20']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_23':
			tg_methods.send_text_message(replies['24'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_24']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_26':
			tg_methods.send_text_message(replies['20'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_20']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_28':
			tg_methods.send_text_message(replies['20'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_20']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_31':
			tg_methods.send_text_message(replies['7'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_7']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_33':
			tg_methods.send_text_message(replies['36'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_36']))
			message_info["callback_data"]="scr_36"
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_35':
			tg_methods.send_text_message(replies['36'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_36']))
			message_info["callback_data"]="scr_36"
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_36':
			tg_methods.send_text_message(replies['20'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_20']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_37':
			tg_methods.send_text_message(replies['20'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_20']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_38':
			tg_methods.send_text_message(replies['20'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_20']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_40':
			tg_methods.send_text_message(replies['43'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_43']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_41':
			tg_methods.send_text_message(replies['43'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_43']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_42':
			tg_methods.send_text_message(replies['/start'], chat_id, protect_content=True, keyboard=json.dumps(buttons['start']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_44':
			tg_methods.send_text_message(replies['45'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_45']))
			print(text)
		else:
			handle_text_query(text, chat_id, message_id, user_id)

def get_latest_messageid_from_cache(filepath, chat_id):
	
	target_chat_id = chat_id

	# Load data from the JSON file
	with open(filepath, "r") as json_file:
		try:
			data = json.load(json_file)
		except json.JSONDecodeError:
			data = {}

	# Filter the list to get items matching the target chat_id
	filtered_data = [item for item in data if item["chat_id"] == target_chat_id]

	# Get the latest message_id for the specified chat_id
	if filtered_data:
	    latest_message_id = filtered_data[-1]["message_id"]  # Get the last matching entry
	    return latest_message_id
	else:
	    return None

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

# Checking for conditions

def text_message_is_entered(message):
	return 'message' in message and 'text' in message['message']

def button_is_pressed(message):
	return 'callback_query' in message.keys()

class ValueOutOfRangeError(Exception):
    """Custom exception for values out of range."""
    pass

def check_all_in_range(input_list, min=1, max=10):
    # Check if all items are between 1 and 10
    if not all(min <= item <= max for item in input_list):
        raise ValueOutOfRangeError("All items must be between 1 and 10.")

class ListLengthMismatchError(Exception):
    """Custom exception for list length mismatch errors."""
    pass

def check_matching_lengths(list1, list2):
    if len(list1) != len(list2):
        raise ListLengthMismatchError("The lengths of the lists do not match.")

class ListTooShortError(Exception):
    """Custom exception for lists with fewer than 5 entries."""
    pass

def check_minimum_length(input_list, min_length=5):
    if len(input_list) < min_length:
        raise ListTooShortError(f"The list has fewer than {min_length} entries.")