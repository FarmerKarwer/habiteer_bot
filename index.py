import tg_methods


def handler(event, context):
	message = tg_methods.get_updates() #Change it to json.loads(event['body']) when using it on Yandex Cloud
	print(message)
	return {
	'statusCode':200,
	'body':event
	}