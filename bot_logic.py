import tg_methods
import json
from utils import load_json, save_to_json, append_to_json

replies_filepath = "./strings/replies.json"
buttons_filepath = "./strings/buttons.json"
cache_filepath = "./cache/callback_history.json"

replies = load_json(replies_filepath)
buttons = load_json(buttons_filepath)



def use_logic(message):
	if button_is_pressed(message):
		handle_callback_query(message)
	elif text_message_is_entered(message):

		## Getting data
		chat_id = message['message']['chat']['id']
		text = message['message']['text']
		message_id = message['message']['message_id']
		previous_message_id = get_latest_messageid_from_cache(cache_filepath, chat_id)
		print(previous_message_id)
		print(message_id == previous_message_id+1)
		if message_id == previous_message_id+1:
			print('It works!')
		else: 
			handle_text_query(text, chat_id, message_id)
	else:
		chat_id = message['message']['chat']['id']
		tg_methods.send_text_message('Я понимаю только текстовые сообщения и кнопки', chat_id)

def handle_callback_query(message):

	## Getting data
	callback_query_id = message['callback_query']['id']
	callback_data = message['callback_query']['data']
	chat_id = message['callback_query']['message']['chat']['id']
	message_id = message['callback_query']['message']['message_id']

	## Actual logic
	if callback_data == "scr_1":
		tg_methods.send_text_message(replies['1'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_1']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_2":
		tg_methods.send_text_message(replies['2'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_2']))
		tg_methods.delete_message(message_id, chat_id)
		data = {"chat_id":chat_id, "message_id":message_id, "callback_data":callback_data}
		newdata = append_to_json(filepath = cache_filepath, new_data=data)
		save_to_json(filepath = cache_filepath, data = newdata)
	elif callback_data == "scr_3":
		tg_methods.send_text_message(replies['3'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_3']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_4":
		tg_methods.send_text_message(replies['4'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_4']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_5":
		tg_methods.send_text_message(replies['5'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_5']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "scr_6":
		tg_methods.send_text_message(replies['6'], chat_id, protect_content=True, keyboard=json.dumps(buttons['scr_6']))
		tg_methods.delete_message(message_id, chat_id)
	else:
		tg_methods.send_text_message("Error: unknown callback data", chat_id, protect_content=True)

def handle_text_query(text, chat_id, message_id):

	## Actual logic
	if text=="/start":
		tg_methods.send_text_message(replies['/start'], chat_id, protect_content=True, keyboard=json.dumps(buttons['start']))
		tg_methods.delete_message(message_id, chat_id)

def get_latest_messageid_from_cache(filepath, chat_id):
	
	target_chat_id = chat_id

	# Load data from the JSON file
	with open(filepath, "r") as json_file:
	    data = json.load(json_file)

	# Filter the list to get items matching the target chat_id
	filtered_data = [item for item in data if item["chat_id"] == target_chat_id]

	# Get the latest message_id for the specified chat_id
	if filtered_data:
	    latest_message_id = filtered_data[-1]["message_id"]  # Get the last matching entry
	    return latest_message_id
	else:
	    return None

# Checking for conditions

def text_message_is_entered(message):
	return 'message' in message and 'text' in message['message']

def button_is_pressed(message):
	return 'callback_query' in message.keys()