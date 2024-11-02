import random
import tg_methods
import json
from utils import *

def get_motivational_message(chat_id):
    stop_list_filepath="strings/stop_list.json"
    stop_list=load_json(stop_list_filepath)
    if chat_id not in stop_list:
        motivation_messages_filepath = "./strings/motivational_messages.json"
        motivation_messages = load_json(motivation_messages_filepath)['messages']
        tg_methods.send_text_message(random.choice(motivation_messages),chat_id)

def stop_command(chat_id):
    stop_list_filepath="strings/stop_list.json"
    stop_list=load_json(stop_list_filepath)
    if chat_id not in stop_list:
        newdata=append_to_json(stop_list_filepath,chat_id)
        save_to_json(stop_list_filepath, newdata)

        tg_methods.send_text_message('Вы успешно отписались от получения мотивирующих сообщений', chat_id)
