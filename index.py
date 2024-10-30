import json
import bot_logic
import tg_methods

def handler(event, context):
	#Change it to json.loads(event['body']) when using it on Yandex Cloud
	message = tg_methods.get_updates()['result'][-1] 
	print(message)
	bot_logic.use_logic(message)	
	return {
	'statusCode':200,
	'body':event
	}