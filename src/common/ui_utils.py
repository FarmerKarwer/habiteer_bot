import json
from typing import Any, Callable, Dict, List, Optional

import tg_methods
from config import BUTTONS_FILEPATH
from database import DatabaseClient
from cache_manager import CacheManager
from .json_utils import load_json

def switch_screen(
    reply: str,
    chat_id: int,
    message_id: int,
    delete_previous: bool = True,
    parse_mode: str = 'Markdown',
    disable_notification: Optional[bool] = None,
    protect_content: bool = True,
    reply_parameters: Optional[Dict[str, Any]] = None,
    keyboard: Optional[str] = None,
) -> None:
    """Sends a message and optionally deletes the previous one."""
    tg_methods.send_text_message(
        reply,
        chat_id,
        parse_mode=parse_mode,
        disable_notification=disable_notification,
        protect_content=protect_content,
        reply_parameters=reply_parameters,
        keyboard=keyboard,
    )
    if delete_previous:
        tg_methods.delete_message(message_id, chat_id)

def get_button(screen_name, buttons_filepath=BUTTONS_FILEPATH):
	"""Retrieves the button configuration for a given screen."""
	buttons = load_json(buttons_filepath)
	return json.dumps(buttons[screen_name])

def select_multiple_days(callback_data, additional_actions, user_id, chat_id, message_id):
	cache = CacheManager()
	user_selections = cache.get_button_selection(user_id, "user_selections")
	previous_screen = cache.get_previous_message(user_id)['callback_data']
	if user_selections is None:
		user_selections = []
		new_data = {"user_id":user_id, "user_selections":json.dumps(user_selections), "previous_screen":previous_screen}
		cache.save_button_selection(new_data)

	if callback_data in user_selections:
		user_selections.remove(callback_data)
	else:
		user_selections.append(callback_data)

	cache.update_button_selection(user_id, {"user_selections":json.dumps(user_selections)})

	days = [
		{"text": "✅ Пн" if "mon" in user_selections else "Пн", "callback_data": "mon"},
		{"text": "✅ Вт" if "tue" in user_selections else "Вт", "callback_data": "tue"},
		{"text": "✅ Ср" if "wed" in user_selections else "Ср", "callback_data": "wed"},
		{"text": "✅ Чт" if "thu" in user_selections else "Чт", "callback_data": "thu"},
	]
	weekend = [
		{"text": "✅ Пт" if "fri" in user_selections else "Пт", "callback_data": "fri"},
		{"text": "✅ Сб" if "sat" in user_selections else "Сб", "callback_data": "sat"},
		{"text": "✅ Вс" if "sun" in user_selections else "Вс", "callback_data": "sun"},
	]
	reply_markup = {
		"inline_keyboard": [days, weekend]+additional_actions
	}
	tg_methods.edit_message_reply_markup(chat_id, message_id, reply_markup)

def add_report_buttons(keyboard_name, user_id):
	db = DatabaseClient()
	keyboard = json.loads(get_button(keyboard_name))
	reports = db.view_reports(user_id)
	if len(reports)==0:
		return None
	else:
		report_names = [report.get('name') for report in reports]
		report_rows = []
		for i in range(0, len(report_names), 3):
			report_rows.append([
				{"text": report, "callback_data": f"report_{index+1}"}
				for index, report in enumerate(report_names[i:i+3], start=i)
			])
		keyboard["inline_keyboard"] = report_rows+keyboard["inline_keyboard"]
		keyboard=json.dumps(keyboard)
		return keyboard

def change_button(keyboard, row, col, changes):
    """
    Modify a specific button in a Telegram inline keyboard and return the updated keyboard as JSON.

    Args:
        keyboard (str or dict): The inline keyboard. Can be a JSON string or a Python dict.
            Expected structure:
            {
                "inline_keyboard": [
                    [ { "text": "...", "callback_data": "..." }, ... ],
                    ...
                ]
            }
        row (int): The row index of the button to modify.
        col (int): The column index (within that row) of the button to modify.
        changes (dict): A dictionary containing the keys and new values you want to update.
            For example: {"text": "Настройка отчетности"} or
                         {"text": "New Text", "callback_data": "new_callback"}

    Returns:
        str: The updated keyboard as a JSON string.

    Raises:
        IndexError: If the specified row or column is out of range.
        ValueError: If the keyboard does not have the expected structure.
    """
    # If the keyboard is provided as a JSON string, convert it to a dict.
    if isinstance(keyboard, str):
        keyboard = json.loads(keyboard)
    
    # Check that the keyboard has the expected structure.
    if "inline_keyboard" not in keyboard:
        raise ValueError("Keyboard does not contain 'inline_keyboard' key")
    
    # Validate row and col
    if row < 0 or row >= len(keyboard["inline_keyboard"]):
        raise IndexError("Row index out of range")
    if col < 0 or col >= len(keyboard["inline_keyboard"][row]):
        raise IndexError("Column index out of range")
    
    # Update the specified button with all the key-value pairs provided in changes.
    button = keyboard["inline_keyboard"][row][col]
    for key, new_value in changes.items():
        if callable(new_value):
            # If new_value is a callable, pass in the current value.
            button[key] = new_value(button.get(key, ""))
        else:
            # Otherwise, assign the value directly.
            button[key] = new_value
    
    # Return the updated keyboard as a JSON string.
    return json.dumps(keyboard, ensure_ascii=False)
