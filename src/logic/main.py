import json

from ._common_imports import *
from .onboarding import show_start_onboarding
from common import select_multiple_days

def show_start_screen(user_id, chat_id, message_id, message, timestamp):
	user = db.select_user(user_id)
	no_user = len(user)==0
	if no_user:
		show_start_onboarding(chat_id, message_id)
	else:
		show_main_menu(user_id, chat_id, message_id)

def show_main_menu(user_id, chat_id, message_id):
	cache.clear_cache(user_id)
	switch_screen(replies['1'], chat_id, message_id, keyboard=get_button('scr_1'))

def show_choose_weekdays(user_id, chat_id, message_id, scr_name):
	screen_id = '_'.join(scr_name.split('_')[1:])
	cache.delete_button_selection(user_id)
	switch_screen(replies[screen_id], chat_id, message_id, keyboard=get_button(scr_name))

def show_multiple_selection(user_id, chat_id, message_id, callback_data, scr_name):
	additional_actions = json.loads(get_button(scr_name))['inline_keyboard'][2:]
	select_multiple_days(callback_data, additional_actions, user_id, chat_id, message_id)
