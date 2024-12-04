import json
from bot_logic import use_logic
from tg_methods import get_updates
import time

def handler(event, context):
	#Change it to json.loads(event['body']) when using it on Yandex Cloud
	message = get_updates()['result'][-1] 
	use_logic(message)	
	return {
	'statusCode':200,
	'body':event,
	'message':message
	}

def handler_long(event, context):
	print("Long polling has started...")
	print("Press Ctrl + C to exit")

	last_update_id = None
	offset = None
	#print(f"Last_id: {last_update_id}")
	running = True

	while running:
		if last_update_id:
			offset = last_update_id+1

		updates = get_updates(offset = offset, timeout=30)

		if updates["ok"]:
			update = updates['result'][-1]
			#print(f"New id: {update["update_id"]}")
			if (last_update_id is None) or (update["update_id"] == last_update_id + 1):
				last_update_id = update["update_id"]
				#print(f"Last_id is changed to {last_update_id}")
				#print(update)
				use_logic(update)

		time.sleep(1)
	return {
	'statusCode':200, 
	'body':event,
	'message':update
	}
