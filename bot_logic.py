import tg_methods
import json

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

replies_filepath = "./strings/replies.json"
buttons_filepath = "./strings/buttons.json"

replies = load_json(replies_filepath)
buttons = load_json(buttons_filepath)

def use_logic(message):
	if button_is_pressed(message):
		handle_callback_query(message)
	elif text_message_is_entered(message):
		handle_text_query(message)
	else:
		chat_id = message['message']['chat']['id']
		tg_methods.send_text_message('Я понимаю только текстовые сообщения и кнопки', chat_id)

def handle_callback_query(message):
	callback_query_id = message['callback_query']['id']
	callback_data = message['callback_query']['data']
	chat_id = message['callback_query']['message']['chat']['id']
	message_id = message['callback_query']['message']['message_id']
	if callback_data == "menu":
		tg_methods.send_text_message(replies['1'], chat_id, protect_content=True, keyboard=json.dumps(buttons['main_menu']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "add_habit":
		tg_methods.send_text_message(replies['2'], chat_id, protect_content=True, keyboard=json.dumps(buttons['add_habit']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "view_habits":
		tg_methods.send_text_message(replies['3'], chat_id, protect_content=True, keyboard=json.dumps(buttons['view_habits']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "pick_habit":
		tg_methods.send_text_message(replies['4'], chat_id, protect_content=True, keyboard=json.dumps(buttons['pick_habit']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "stats":
		tg_methods.send_text_message(replies['5'], chat_id, protect_content=True, keyboard=json.dumps(buttons['stats']))
		tg_methods.delete_message(message_id, chat_id)
	elif callback_data == "settings":
		tg_methods.send_text_message(replies['6'], chat_id, protect_content=True, keyboard=json.dumps(buttons['settings']))
		tg_methods.delete_message(message_id, chat_id)
	else:
		tg_methods.send_text_message("Error: unknown callback data", chat_id, protect_content=True)

def handle_text_query(message):
	chat_id = message['message']['chat']['id']
	text = message['message']['text']
	message_id = message['message']['message_id']
	if text=="/start":
		tg_methods.send_text_message(replies['/start'], chat_id, protect_content=True, keyboard=json.dumps(buttons['start']))
		tg_methods.delete_message(message_id, chat_id)


# Checking for conditions

def text_message_is_entered(message):
	return 'message' in message and 'text' in message['message']

def button_is_pressed(message):
	return 'callback_query' in message.keys()