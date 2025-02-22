"""
This module provides functionality to send reminders to users.
"""
import json
import random
from src.tg_methods import send_text_message
from src.config import REPORT_REPLIES_FILEPATH, REPORT_BUTTONS_FILEPATH

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

replies = load_json(REPORT_REPLIES_FILEPATH)

def get_button(screen_name, buttons_filepath=REPORT_BUTTONS_FILEPATH):
	"""Retrieves the button configuration for a given screen."""
	buttons = load_json(buttons_filepath)
	return json.dumps(buttons[screen_name])

def get_reply(screen_name):
	return random.choice(replies[screen_name])


def send_daily_report():
	chat_id = 940985788
	reply = get_reply('report').replace('[habit]', "тестовая привычка")
	send_text_message(reply, chat_id, keyboard=get_button('scr_report'))

def send_srbai_report():
	chat_id = 940985788
	reply = get_reply('srbai_report').replace('[habit]', "тестовая привычка")
	send_text_message(reply, chat_id, keyboard=get_button('scr_srbai_report'))

if __name__=="__main__":
	send_srbai_report()