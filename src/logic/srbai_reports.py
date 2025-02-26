from config import (
	REPORT_REPLIES_FILEPATH, 
	REPORT_BUTTONS_FILEPATH
	)
import json
import random

from database import DatabaseClient
from cache_manager import CacheManager
from common import (switch_screen, 
					get_button, 
					load_json)

replies = load_json(REPORT_REPLIES_FILEPATH)
db = DatabaseClient()
cache = CacheManager() 

def get_reply(screen_name):
	return random.choice(replies[screen_name])

def show_srbai_report(user_id, chat_id, message_id):
    pass

def show_srbai_tomorrow(user_id, chat_id, message_id, timestamp):
	pass

def show_srbai_in_a_month(user_id, chat_id, message_id, timestamp):
    pass

def show_srbai_question_1(user_id, chat_id, message_id):
	pass

def show_srbai_question_2(user_id, chat_id, message_id):
	pass

def show_srbai_question_3(user_id, chat_id, message_id):
	pass

def show_srbai_question_4(user_id, chat_id, message_id):
    pass

def show_srbai_result(user_id, chat_id, message_id, timestamp):
    pass

def show_srbai_habit_changed(user_id, chat_id, message_id, timestamp, text):
    pass