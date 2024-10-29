import os
import requests
import json

"""
There will be all the methods necessary for Telegram Bot
"""

TG_TOKEN=os.getenv('BOT_TOKEN')
URL = f"https://api.telegram.org/bot{TG_TOKEN}/"

# Sending Messages
def send_text_message(reply, chat_id, disable_notification=None, protect_content=None, reply_parameters=None, keyboard=None):
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

def send_picture():
	pass

def delete_message(message_id, chat_id):
	data = {
	'chat_id':chat_id,
	'message_id':message_id
	}
	url = URL+"deleteMessage"
	requests.post(url, data=data)

# Utils
def get_updates():
	url = URL+"getUpdates"
	update_array = requests.get(url)
	return json.loads(update_array.content)

if __name__ == "__main__":
    print(get_updates())


def get_ai_response(habit): 
	'''
	Пример вызова:

		import tg_methods

		habit = 'Лучше справляться со стрессом'
		response = tg_methods.get_ai_response(habit) 
		print(response)

	'''

	api_token = os.getenv('API_TOKEN')

	url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

	russian_text = f"В моей жизни появилось стремление: {habit}. Предложи 5 привычек, чтобы достичь этой цели, они должны быть короткие, без лишнего текста, в инфинитиве." + "Ответ должен быть в формате json {'habit1': '', 'habit2': '', 'habit3': '', 'habit4': '', 'habit5': ''}"

	payload = {
		"messages": [
			{
				"text": russian_text,
				"role": "user"
			}
		],
		"completionOptions": {
			"temperature": 0.3,
			"maxTokens": 1000
		},
		"modelUri": "gpt://b1gn0kf4hjuuqk9lr9nu/yandexgpt-lite/rc"
	}

	headers = {
		"Content-Type": "application/json; charset=utf-8",
		"Authorization": f"Api-Key {api_token}",
		"Accept": "*/*"
	}

	try:
		response = requests.post(
			url=url,
			headers=headers,
			data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
		)
		
		print(f"Status Code: {response.status_code}")
		
		if response.status_code == 200:
			try:
				result = json.loads(response.text)
				textres = result['result']['alternatives'][0]['message']['text']
				json_string = textres.split('```')[1].strip()
				habits = json.loads(json_string)

				''' 
				Внутри habits 5 привычек, их можно вытащить как показано ниже и отправить пользователю в сообщения.

				habit1 = habits['habit1']
				habit2 = habits['habit2']
				habit3 = habits['habit3']
				habit4 = habits['habit4']
				habit5 = habits['habit5']

				'''
				return habits

			except json.JSONDecodeError:
				return response.text
		else:
			return response.text

	except Exception as e:
		return f"Error occurred: {str(e)}"


