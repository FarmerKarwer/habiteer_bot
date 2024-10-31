import tg_methods
import json
import os
from utils import load_json, save_to_json, append_to_json

replies_filepath = "./strings/replies.json"
buttons_filepath = "./strings/buttons.json"
cache_filepath = "./cache/callback_history.json"

replies = load_json(replies_filepath)
buttons = load_json(buttons_filepath)

def use_logic(message):
	if button_is_pressed(message):
		message_info = handle_callback_query(message)
	elif text_message_is_entered(message):

		## Getting data
		chat_id = message['message']['chat']['id']
		text = message['message']['text']
		message_id = message['message']['message_id']
		user_id = message['message']['from']['id']

		message_info = {"user_id":user_id,"chat_id":chat_id, "message_id":message_id, "callback_data":None, "text":text}

		### Possible problems when a user types command '/start'
		if get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_2':
			tg_methods.send_text_message(replies['7'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_7']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_3_1':
			tg_methods.send_text_message(replies['21'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_21']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_8':
			tg_methods.send_text_message(replies['8.1'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_8_1']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")in ("hab_1", "hab_2", "hab_3", "hab_4", "hab_5", "hab_6", "hab_7", "hab_8", "hab_9", "hab_10"):
			tg_methods.send_text_message(replies['18'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_18']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_10':
			tg_methods.send_text_message(replies['11'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_11']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_12':
			tg_methods.send_text_message(replies['13'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
			message_info["callback_data"]="scr_13"
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_13':
			tg_methods.send_text_message(replies['14'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_14']))
			message_info["callback_data"]="scr_14"
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_14':
			tg_methods.send_text_message(replies['15'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_15']))
			print(text)
		elif get_cached_data(cache_filepath, user_id, chat_id, property="callback_data")=='scr_17':
			tg_methods.send_text_message(replies['13'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_13']))
			message_info["callback_data"]="scr_13"
			print(text)
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
		tg_methods.send_text_message(replies['4'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_4']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data in ("hab_1", "hab_2", "hab_3", "hab_4", "hab_5", "hab_6", "hab_7", "hab_8", "hab_9", "hab_10"):
		tg_methods.send_text_message(replies['9'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_9']))
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
	elif callback_data == "scr_10":
		tg_methods.send_text_message(replies['10'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_10']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_12": 
		tg_methods.send_text_message(replies['12'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_12']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_16": 
		tg_methods.send_text_message(replies['16'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_16']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_17": 
		tg_methods.send_text_message(replies['17'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_17']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_18": 
		tg_methods.send_text_message(replies['18'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_18']))
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
		with open(filepath, "r") as json_file:
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