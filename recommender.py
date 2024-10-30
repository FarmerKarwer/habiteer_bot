import os
import requests
import json

def get_ai_response(aspiration): 
	'''
	Пример вызова:

		import recommender

		aspiration = 'Лучше справляться со стрессом'
		response = recommender.get_ai_response(aspiration) 
		print(response)

	'''

	api_token = os.getenv('API_TOKEN')

	url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

	russian_text = f"В моей жизни появилось стремление: {aspiration}. Предложи 5 привычек, чтобы достичь этой цели. Привычки должны быть: 1) в инфинитиве, 2) конкретным поведением - то, что можно сделать 'здесь и сейчас', 3) максимально простыми. Например: “Выпить стакан воды”, “Отжаться от пола 2 раза”, “Закрыть занавески”, “Позвонить маме”, “Скушать яблоко”." + "Ответ должен быть в формате json {'habit1': '', 'habit2': '', 'habit3': '', 'habit4': '', 'habit5': ''}"

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


if __name__ == "__main__":
    print(get_ai_response("Лучше питаться"))