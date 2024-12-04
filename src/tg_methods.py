import os
import requests
import json

"""
There will be all the methods necessary for Telegram Bot
"""

TG_TOKEN=os.getenv('BOT_TOKEN')
URL = f"https://api.telegram.org/bot{TG_TOKEN}/"


# Sending Messages
def send_text_message(reply, chat_id, disable_notification=None, 
    protect_content=None, reply_parameters=None, keyboard=None):
	data = {
		'text':reply,
		'chat_id':chat_id,
		'parse_mode':'Markdown',
		'disable_notification':disable_notification,
		'protect_content':protect_content,
		'reply_parameters':reply_parameters,
		'reply_markup': keyboard
	}
	url = URL+"sendMessage"
	requests.post(url, data=data)

def delete_message(message_id, chat_id):
	data = {
	'chat_id':chat_id,
	'message_id':message_id
	}
	url = URL+"deleteMessage"
	requests.post(url, data=data)

def answer_callback_query(callback_query_id):
	data = {"callback_query_id": callback_query_id}
	url = URL+"answerCallbackQuery"
	requests.post(url, data=data)

def send_picture():
	pass

# Utils
def get_updates(offset=None, timeout=None):
	url = URL+"getUpdates"
	params = {"offset": offset, "timeout": timeout}
	update_array = requests.get(url, params=params)
	return json.loads(update_array.content)

if __name__ == "__main__":
    print(get_updates())