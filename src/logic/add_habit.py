from ._common_imports import *
from config import CACHE_UPDATEHABIT_FILEPATH
from utils import save_data_to_cache

def show_adding_habit(text, user_id, chat_id, message_id, timestamp):
	new_data = {
			"user_id": user_id,
			"chat_id": chat_id,
			"habit_name": text,
			"habit_number":"no_number"
		}
	db.add_habit(habit=text, creation_datetime=timestamp, user_id=user_id)
	save_data_to_cache(CACHE_UPDATEHABIT_FILEPATH, new_data)
	reply = replies['7'].replace("[habit]", text)
	switch_screen(reply, chat_id, message_id, keyboard=get_button('scr_7'))