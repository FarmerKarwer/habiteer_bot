from config import (
	REPLIES_FILEPATH, 
	PREMADE_HABITS_FILEPATH, 
	PREMADE_TRIGGERS_FILEPATH
	)
from common import switch_screen, get_button
from database import DatabaseClient
from cache_manager import CacheManager
from utils import load_json

replies = load_json(REPLIES_FILEPATH)
premade_habits = load_json(PREMADE_HABITS_FILEPATH)
premade_triggers = load_json(PREMADE_TRIGGERS_FILEPATH)
aspirations = list(premade_habits.keys())
db = DatabaseClient()
cache = CacheManager()
callback_weekdays = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")

__all__ = ["switch_screen", "get_button", "replies", "db", "cache"]