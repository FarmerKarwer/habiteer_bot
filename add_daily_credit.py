"""
This function is used to add daily credit for using AI to the user's account.
"""
from src.database import DatabaseClient

db = DatabaseClient()

def add_daily_credit():
    users = db.select_all("users")
    for user in users:
        user_id = user['id']
        daily_credit = user.get('daily_ai_credits', None)
        if daily_credit is None or daily_credit == 0:
            db.update_user_credits(user_id, 1)

if __name__ == "__main__":
    add_daily_credit()
    print("Daily credit added successfully.")
        