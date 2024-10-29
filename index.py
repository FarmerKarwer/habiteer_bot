import tg_methods
import json

replies_filepath = "./strings/replies.json"
buttons_filepath = "./strings/buttons.json"

with open(replies_filepath, "r", encoding="utf-8") as file:
	replies = json.load(file)

with open(buttons_filepath, "r", encoding="utf-8") as file:
	buttons = json.load(file)

def handler(event, context):
	#Change it to json.loads(event['body']) when using it on Yandex Cloud
	message = tg_methods.get_updates()['result'][-1] 
	print(message)

	if 'callback_query' in message.keys():
		callback_data = message['callback_query']['data']
		chat_id = message['callback_query']['message']['chat']['id']
		if callback_data == "menu":
			tg_methods.send_text_message(replies['/menu'], chat_id, protect_content=True, keyboard=json.dumps(buttons['main_menu']))
	elif 'message' in message and 'text' in message['message']:
		chat_id = message['message']['chat']['id']
		text = message['message']['text']
		if text=="/start":
			tg_methods.send_text_message(replies['/start'], chat_id, protect_content=True, keyboard=json.dumps(buttons['start']))
	else:
		chat_id = message['message']['chat']['id']
		send_text('Это и не команда и не отзыв!', chat_id)
	return {
	'statusCode':200,
	'body':event
	}