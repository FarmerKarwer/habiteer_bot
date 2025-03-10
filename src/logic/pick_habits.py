import json
from datetime import datetime
import random
import re

from ._common_imports import *
from ._common_imports import aspirations, premade_habits
from common import (
	format_numbered_list,
	parse_numbers,
	sum_arrays,
	check_minimum_length,
	change_button,
	)
from common.exceptions import ListTooShortError, ValueOutOfRangeError
from recommender import get_ai_response
from tg_methods import delete_message

def show_aspirations(chat_id, message_id):
	aspirations_str = format_numbered_list(aspirations)
	reply = replies['4'].replace("[aspirations]", aspirations_str)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_4'))

def show_predefined_habits(callback_data, user_id, chat_id, message_id, unix_timestamp):
	"""After clicking on aspiration, this func sends a message to a user with predefined habits"""
	aspiration = get_aspiration_from_callback(callback_data)
	random_habits = get_predefined_habits_for_aspiration(aspiration, unix_timestamp, size=10)
	random_habits_str = format_numbered_list(random_habits)
	reply = replies['9'].replace("[habits]", random_habits_str)

	new_data = {"user_id":user_id,"chat_id":chat_id, "aspiration":aspiration, 
	"habits":None, "behavior_options":json.dumps(random_habits), 
	"suitability":None, "effectiveness":None}
	cache.save_picking_habit_info(new_data)

	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_9'))

def show_getting_back_to_predefined_habits(user_id, chat_id, message_id):
	aspiration = cache.get_picking_habit_info(user_id)['aspiration']
	random_habits = get_predefined_habits_for_aspiration(aspiration, size=10)
	random_habits_str = format_numbered_list(random_habits)
	reply = replies['9'].replace("[habits]", random_habits_str)
	cache.update_picking_habit_info(user_id, {"behavior_options":json.dumps(random_habits)})

	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_9'))

def show_ai_recommended_habits(user_id, chat_id, message_id):
	user_credits = db.get_user_property(user_id, "daily_ai_credits")
	if user_credits is None:
		user_credits = 0
	if user_credits<1:
		reply = replies['12_1_no_credits']
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_12_1_no_credits'))
	else:
		user_credits -= 1
		db.update_user_credits(user_id, user_credits)
		aspiration = cache.get_picking_habit_info(user_id)['aspiration']
		habits = get_ai_response(aspiration=aspiration)
		numbered_habits = format_numbered_list(habits.values())
		behavior_options_list = [habit for habit in habits.values()]
		reply = replies['12_1'].replace('[behaviors]', numbered_habits)

		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_12_1'))
		cache.update_picking_habit_info(user_id, {"behavior_options":json.dumps(behavior_options_list)})

def show_magic_wanding_from_ai_recommended_habits(user_id, chat_id, message_id, text, message_info):
	try:
		behavior_options = cache.get_picking_habit_info(user_id)['behavior_options']
		behavior_options = json.loads(behavior_options)
		numbered_habits = format_numbered_list(behavior_options)
		entered_numbers = parse_numbers(text)
		if len(entered_numbers)>len(behavior_options):
			raise IndexError
		if len(entered_numbers)==1:
			if entered_numbers[0]==0:
				raise ValueOutOfRangeError
		selected_habits = [behavior_options[i-1] for i in entered_numbers]
		cache.update_picking_habit_info(user_id, {"behavior_options":json.dumps(selected_habits)})
		show_magic_wanding(text=None, chat_id=chat_id, message_id=message_id, user_id=user_id, message_info=message_info)
	except ValueError:
		reply = replies['12_1_errors']['incorrect_format'].replace("[behaviors]", numbered_habits)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_12_1'))
		message_info["callback_data"]="scr_12_1"
	except IndexError:
		reply = replies['12_1_errors']['incorrect_range'].replace("[behaviors]", numbered_habits)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_12_1'))
		message_info["callback_data"]="scr_12_1"
	except ValueOutOfRangeError:
		reply = replies['12_1_errors']['zero_number'].replace("[behaviors]", numbered_habits)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_12_1'))
		message_info["callback_data"]="scr_12_1"

def show_picked_habits(user_id, chat_id, message_id, timestamp):
	habits = cache.get_picking_habit_info(user_id)['habits']
	habits = json.loads(habits)
	habits_str = format_numbered_list(habits)
	for habit in habits:
		db.add_habit(habit=habit, creation_datetime=timestamp, user_id=user_id)	
	cache.delete_picking_habit_info(user_id)
	reply = replies['18'].replace('[habits]', habits_str)

	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_18'))

def show_picked_predefined_habits(text, chat_id, message_id, user_id, timestamp, message_info):
	try:	
		habit_options = cache.get_picking_habit_info(user_id)['behavior_options']
		habit_options = json.loads(habit_options)
		entered_numbers = parse_numbers(text)
		filtered_habits = [i-1 for i in entered_numbers if i < len(habit_options)+1]
		selected_habits = [habit_options[i] for i in filtered_habits]
		filtered_habits_str = format_numbered_list(selected_habits)
		check_minimum_length(selected_habits, min_length=1)
		cache.update_picking_habit_info(user_id, {"habits":json.dumps(selected_habits)})

		aspiration = cache.get_picking_habit_info(user_id)['aspiration']

		# Save to DB
		for habit in selected_habits:
			db.add_habit(habit=habit, creation_datetime=timestamp, user_id=user_id, aspiration=aspiration)
		cache.delete_picking_habit_info(user_id)

		reply = replies['18'].replace('[habits]', filtered_habits_str)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_18'))				

	except ValueError:
		reply = replies['9_errors']['incorrect_format'].replace("[habits]", format_numbered_list(habit_options))
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_9'))
		message_info["callback_data"]="scr_9"

	except IndexError:
		reply = replies['9_errors']['index_error'].replace("[habits]", format_numbered_list(habit_options))
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_9'))
		message_info["callback_data"]="scr_9"

	except ListTooShortError:
		reply = replies['9_errors']['incorrect_range'].replace("[habits]", format_numbered_list(habit_options))
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_9'))
		message_info["callback_data"]="scr_9"

	except Exception as e:
		reply = replies['general_error']
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_plug'))

def show_aspiration_confirmation(chat_id, message_id, user_id, callback_data=None, text=None):
	if callback_data:
		aspiration = cache.get_picking_habit_info(user_id)['aspiration']
		reply = replies['11'].replace("[aspiration]", aspiration)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_11'))
	elif text:
		new_data = {"user_id":user_id,"chat_id":chat_id, "aspiration":text, 
					"habits":None, "behavior_options":None, "suitability":None, 
					"effectiveness":None}
		cache.save_picking_habit_info(new_data)

		reply = replies['11'].replace("[aspiration]", text)
		delete_message(message_id-1, chat_id)
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_11'))

def show_magic_wanding_start(user_id, chat_id, message_id):
	previous_screen = cache.get_previous_message(user_id).get("callback_data", None)
	if previous_screen and (previous_screen.startswith("hab_") or previous_screen=="scr_9"):
		show_magic_wanding_return_back_to_start(chat_id, message_id, user_id, '9_scr_12')
		return
	elif previous_screen and previous_screen == "scr_12_proxy_1":
		show_magic_wanding_return_back_to_start(chat_id, message_id, user_id, 'scr_12')
		return
	else:
		keyboard = get_button('scr_12')
	aspiration = cache.get_picking_habit_info(user_id)['aspiration']
	reply = replies['12'].replace("[aspiration]", aspiration)
	switch_screen(reply, chat_id, message_id, keyboard=keyboard)

def show_magic_wanding_return_back_to_start(chat_id, message_id, user_id, keyboard_name):
	behavior_options = None
	cache.update_picking_habit_info(user_id, {"behavior_options":behavior_options})
	aspiration = cache.get_picking_habit_info(user_id)['aspiration']
	reply = replies['12'].replace("[aspiration]", aspiration)
	switch_screen(reply, chat_id, message_id, keyboard=get_button(keyboard_name))

def show_magic_wanding(text, chat_id, message_id, user_id, message_info):
	ai_credits = db.get_user_property(user_id, "daily_ai_credits")
	behavior_options = cache.get_picking_habit_info(user_id).get('behavior_options', None)
	aspiration = cache.get_picking_habit_info(user_id)['aspiration']
	if behavior_options is None:
		behaviors = [text]
		behaviors_str = format_numbered_list(behaviors)
		cache.update_picking_habit_info(user_id, {"behavior_options":json.dumps(behaviors)})
		main_message = replies['12_proxy']['main_message'].replace('[behaviors]', behaviors_str).replace("[aspiration]", aspiration)
		main_message = main_message.replace("[n]", "1")
		praise = random.choice(replies['12_proxy']['praises'])
		reply = main_message + praise
		switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_12_proxy_1'))
		message_info["callback_data"]="scr_12_proxy_1"

	else:
		behavior_options = json.loads(behavior_options)
		if text is not None:
			entered_options_cnt = len(behavior_options)+1
		else:
			entered_options_cnt = len(behavior_options)
		if entered_options_cnt<5:
			if text is not None:
				behavior_options.append(text)
			behaviors_str = format_numbered_list(behavior_options)
			cache.update_picking_habit_info(user_id, {"behavior_options": json.dumps(behavior_options)})
			main_message = replies['12_proxy']['main_message'].replace('[behaviors]', behaviors_str).replace("[aspiration]", aspiration)
			main_message = main_message.replace("[n]", str(entered_options_cnt))
			praise = random.choice(replies['12_proxy']['praises'])
			reply = main_message + praise
			keyboard = change_button(get_button('scr_12_proxy_5_less'), 0, 0, {"callback_data":lambda old: old.replace("[n]", str(entered_options_cnt-1))})
			switch_screen(reply, chat_id, message_id, keyboard=keyboard)
			message_info["callback_data"]=f"scr_12_proxy_{entered_options_cnt}"

		elif entered_options_cnt==5:
			if text is not None:
				behavior_options.append(text)
			behaviors_str = format_numbered_list(behavior_options)
			cache.update_picking_habit_info(user_id, {"behavior_options": json.dumps(behavior_options)})
			main_message = replies['12_proxy']['main_message'].replace('[behaviors]', behaviors_str).replace("[aspiration]", aspiration)
			main_message = main_message.replace("[n]", str(entered_options_cnt))
			praise = replies['12_proxy']['5_options']
			reply = main_message + praise
			if ai_credits is not None and ai_credits <3 and text is not None:
				reply = reply + replies['12_proxy']['5_options_tease']
			keyboard = change_button(get_button('scr_12_proxy_5_more'), 1, 0, {"callback_data":lambda old: old.replace("[n]", str(entered_options_cnt-1))})
			switch_screen(reply, chat_id, message_id, keyboard=keyboard)
			message_info["callback_data"]=f"scr_12_proxy_{entered_options_cnt}"

		elif entered_options_cnt>5:
			if text is not None:
				behavior_options.append(text)
			behaviors_str = format_numbered_list(behavior_options)
			cache.update_picking_habit_info(user_id, {"behavior_options": json.dumps(behavior_options)})
			main_message = replies['12_proxy']['main_message_5_more'].replace('[behaviors]', behaviors_str).replace("[aspiration]", aspiration)
			praise = random.choice(replies['12_proxy']['praises'])
			reply = main_message + praise
			if ai_credits is not None and ai_credits <3 and text is not None:
				if random.random() <= 0.1:
					ai_credits+=1
					db.update_user_credits(user_id, ai_credits)
					reply = main_message+replies['12_proxy']['bonus'].replace("[credits]", str(ai_credits))

			keyboard = change_button(get_button('scr_12_proxy_5_more'), 1, 0, {"callback_data":lambda old: old.replace("[n]", str(entered_options_cnt-1))})
			switch_screen(reply, chat_id, message_id, keyboard=keyboard)
			message_info["callback_data"]=f"scr_12_proxy_{entered_options_cnt}"

		else:
			reply = "Что-то пошло не так\n\nSomething went wrong"
			switch_screen(reply, chat_id, message_id)

def show_magic_wanding_return_back(user_id, chat_id, message_id):
	aspiration = cache.get_picking_habit_info(user_id)['aspiration']
	# Updating behavior options to allow changing an option
	behavior_options = cache.get_picking_habit_info(user_id).get('behavior_options', None)
	behavior_options = json.loads(behavior_options)
	previous_callback = cache.get_previous_message(user_id).get("callback_data")
	if not previous_callback in ("scr_13","scr_13_proxy_1"):	
		behavior_options.pop()
	behaviors_str = format_numbered_list(behavior_options)
	cache.update_picking_habit_info(user_id, {"behavior_options":json.dumps(behavior_options)})
	# Updating message
	if len(behavior_options)>=5:
		main_message = replies['12_proxy']['main_message_5_more'].replace('[behaviors]', behaviors_str).replace("[aspiration]", aspiration)
		keyboard = change_button(get_button('scr_12_proxy_5_more'), 1, 0, {"callback_data":lambda old: old.replace("[n]", str(len(behavior_options)-1))})
	elif len(behavior_options)==1:
		main_message = replies['12_proxy']['main_message'].replace('[behaviors]', behaviors_str).replace("[aspiration]", aspiration)
		main_message = main_message.replace("[n]", str(len(behavior_options)))
		keyboard = get_button('scr_12_proxy_1')
	elif 1<len(behavior_options)<5:
		main_message = replies['12_proxy']['main_message'].replace('[behaviors]', behaviors_str).replace("[aspiration]", aspiration)
		main_message = main_message.replace("[n]", str(len(behavior_options)))
		keyboard = change_button(get_button('scr_12_proxy_5_less'), 0, 0, {"callback_data":lambda old: old.replace("[n]", str(len(behavior_options)-1))})

	reply = main_message
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

	behavior_options = cache.get_picking_habit_info(user_id).get('behavior_options', None)
	behavior_options = json.loads(behavior_options)
	ratings = cache.get_picking_habit_info(user_id).get(type, None)
	if ratings:
		ratings = json.loads(ratings)
	is_callback_in_type_eval = bool(re.match(pattern, callback_data))

	if is_callback_in_type_eval and callback_data not in back_to_first_scr:
		ratings.pop()
		cache.update_picking_habit_info(user_id, {type:json.dumps(ratings)})

	elif callback_data in (back_to_first_scr, "scr_13_change_priorities"):
		ratings = None
		to_update = {type:ratings}
		if type=="suitability":
			to_update["effectiveness"]=ratings
		cache.update_picking_habit_info(user_id, to_update)

	if ratings is None:
		behavior_idx = 0
		cur_progress = 1
		if type in callback_data:
			grade = int(callback_data.split('_')[-1])
			cache.update_picking_habit_info(user_id, {type:json.dumps([grade])})
			behavior_idx = 1
			cur_progress = 2
		behavior_str = behavior_options[behavior_idx].capitalize()
		first_message = replies[scr_number]['first_message']
		progress = f"({cur_progress}/{len(behavior_options)})"
		main_message = replies[scr_number]['main_message'].replace('[progress]', progress)
		main_message = main_message.replace('[behavior]', behavior_str)
		reply = first_message+main_message
		
		if callback_data=="scr_13_change_priorities":
			keyboard = get_button("16_scr_13")
		else:
			keyboard = get_button(keyboard_name)
		keyboard = change_button(keyboard, 2, 0, {"callback_data":lambda old: old.replace("[n]", str(len(behavior_options)))})

		if type in callback_data:
			reply = main_message
			keyboard = json.loads(get_button(keyboard_name))
			keyboard["inline_keyboard"][2][0]["callback_data"] = keyboard["inline_keyboard"][2][0]["callback_data"].replace("[n]", "1")
			keyboard["inline_keyboard"][2][0]["callback_data"] = keyboard["inline_keyboard"][2][0]["callback_data"].replace(prev_keyboard_name, keyboard_name)
			keyboard = json.dumps(keyboard)
		switch_screen(reply, chat_id, message_id, keyboard=keyboard)

	elif len(ratings)<=len(behavior_options):
		# Updating grade list
		if not is_callback_in_type_eval and callback_data !="scr_13" and not (callback_data.startswith("suitability_") and type=="effectiveness"):
			grade = int(callback_data.split('_')[-1])
			ratings.append(grade)
			cache.update_picking_habit_info(user_id, {type:json.dumps(ratings)})
		if len(ratings)==len(behavior_options):
			if type=="suitability":
				chosen_habits = cache.get_picking_habit_info(user_id).get('habits', None)
				if chosen_habits is None:
					cache.update_picking_habit_info(user_id, {"effectiveness":None})
				show_evaluation(callback_data, user_id, chat_id, message_id, type="effectiveness")
			elif type=="effectiveness":
				suitability_ratings = cache.get_picking_habit_info(user_id)['suitability']
				suitability_ratings = json.loads(suitability_ratings)
				effectiveness_ratings = ratings
				habit_grades = sum_arrays(suitability_ratings, effectiveness_ratings)
				top_habits = [habit for _, habit in sorted(zip(habit_grades, behavior_options), reverse=True)[:3]]
				top_habits_str = format_numbered_list(top_habits)

				reply = replies[scr_next].replace("[habits]", top_habits_str)
				cache.update_picking_habit_info(user_id, {"habits":json.dumps(top_habits)})
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
	top_habits = cache.get_picking_habit_info(user_id)['habits']
	top_habits = json.loads(top_habits)
	top_habits_str = format_numbered_list(top_habits)
	reply = replies['15'].replace("[habits]", top_habits_str)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_15'))

# Other useful functions
def get_aspiration_from_callback(callback_data):
	"""Returns aspiration from button callback"""
	aspiration_idx = int(callback_data.split('_')[-1])-1
	aspiration = aspirations[aspiration_idx]
	return aspiration

def get_predefined_habits_for_aspiration(aspiration, unix_timestamp, size=10):
	"""Returns a list of randomly selected predefined habits."""
	habits = list(premade_habits[aspiration])

	date_obj = datetime.fromtimestamp(unix_timestamp)
	date_int = int(date_obj.strftime("%Y%m%d"))
	random.seed(date_int)

	habits = random.sample(habits, k=size)
	return habits