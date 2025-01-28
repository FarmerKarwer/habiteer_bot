import json

from ._common_imports import *
from .onboarding import show_start_onboarding
from config import (
	CACHE_UPDATEHABIT_FILEPATH,
	CACHE_PICKHABIT_FILEPATH,
	CACHE_REPORT,
	CACHE_BUTTON_SELECTION,
	CACHE_KEY_PHRASE
	)
from common import select_multiple_days
from utils import delete_user_records

def show_start_screen(user_id, chat_id, message_id, message, timestamp):
	user = db.select_user(user_id)
	no_user = len(user)==0
	if no_user:
		show_start_onboarding(user_id, chat_id, message_id, message, timestamp)
	else:
		show_main_menu(user_id, chat_id, message_id)

def show_main_menu(user_id, chat_id, message_id):
	cache_list = [CACHE_REPORT, CACHE_BUTTON_SELECTION, CACHE_PICKHABIT_FILEPATH, CACHE_UPDATEHABIT_FILEPATH, CACHE_KEY_PHRASE]
	for cache in cache_list:
		delete_user_records(cache, user_id)
	switch_screen(replies['1'], chat_id, message_id, keyboard=get_button('scr_1'))

def show_choose_weekdays(user_id, chat_id, message_id, scr_name):
	screen_id = '_'.join(scr_name.split('_')[1:])
	delete_user_records(CACHE_BUTTON_SELECTION, user_id)
	switch_screen(replies[screen_id], chat_id, message_id, keyboard=get_button(scr_name))

def show_multiple_selection(user_id, chat_id, message_id, callback_data, scr_name):
	additional_actions = json.loads(get_button(scr_name))['inline_keyboard'][2:]
	select_multiple_days(callback_data, additional_actions, user_id, chat_id, message_id)
