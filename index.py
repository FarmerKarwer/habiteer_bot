import tg_methods


def handler(event, context):
	message = tg_methods.get_updates()['result'][0] #Change it to json.loads(event['body']) when using it on Yandex Cloud
	print(message)
	chat_id = message['message']['chat']['id']
	text = message['message']['text']
	print(chat_id, text)
	return {
	'statusCode':200,
	'body':event
	}