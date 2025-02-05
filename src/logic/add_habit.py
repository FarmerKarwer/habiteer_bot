from ._common_imports import *

def show_adding_habit(text, user_id, chat_id, message_id, timestamp):
	new_data = {
			"habit_name": text,
			"habit_number":"no_number"
		}
	db.add_habit(habit=text, creation_datetime=timestamp, user_id=user_id)
	cache.save_updating_habit_info(user_id, new_data)
	reply = replies['7'].replace("[habit]", text)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_7'))