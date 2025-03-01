"""
This cloud function recalculates the streak of all the users each day at 00:00 MSK
"""
import json
from datetime import datetime, timedelta

from src.database import DatabaseClient

db = DatabaseClient()

def recalculate_streak():
    timestamp = datetime.now()
    timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    habits = db.select_all("habits")
    for habit in habits:
        habit_id = habit['id']
        habit_type = habit['type']
        habit_status = habit['status']
        logs = db.get_habit_logs_for_habit(habit_id, status="completed")
        if habit_type == "regular" and habit_status in ['tracked', 'marked']:
            report_id = habit.get('report_id', None)
            if report_id:
                report_info = db.get_report_by_id(report_id)
                if len(report_info) != 0:
                    period = report_info[0]['on_weekdays']
                    period = json.loads(period)

                    if period!=[1,2,3,4,5,6,7]:
                        current_streak, max_streak = calculate_streak(logs, timestamp, period).values()
                        db.update_habit(habit_id, "current_streak_days", f"{current_streak}")
                        db.update_habit(habit_id, "max_streak_days", f"{max_streak}")
                    else:
                        current_streak, max_streak = calculate_usual_streak(logs, timestamp).values()
                        db.update_habit(habit_id, "current_streak_days", f"{current_streak}")
                        db.update_habit(habit_id, "max_streak_days", f"{max_streak}")
            else:
                current_streak, max_streak = calculate_usual_streak(logs, timestamp).values()
                db.update_habit(habit_id, "current_streak_days", f"{current_streak}")
                db.update_habit(habit_id, "max_streak_days", f"{max_streak}")
        elif habit_type == "harmful" and habit_status in ['tracked', 'marked']:
            started_tracking_at = db.get_habit_logs_for_habit(habit_id, status="started")[0].get("timestamp")
            current_streak, max_streak = calculate_streak_for_bad_habit(logs, timestamp, started_tracking_at).values()
            db.update_habit(habit_id, "current_streak_days", f"{current_streak}")
            db.update_habit(habit_id, "max_streak_days", f"{max_streak}")
        else:
            continue

def calculate_streak(habit_logs, timestamp, period):
    """
    Calculates current and maximum streaks based on the provided habit logs, a timestamp,
    and a period (list of weekdays when the habit should be marked).
    
    Parameters:
      - habit_logs: a list of dicts. Each dict must have a 'date' field which is an integer
        representing the number of days since the epoch (1970-01-01).
      - timestamp: a timestamp representing the current time. We assume that if timestamp > 1e12,
        it is given in microseconds.
      - period: list of weekdays (1=Monday, 7=Sunday) on which the habit is scheduled.
    
    Returns:
      A dict: {"current_streak": current_streak, "max_streak": max_streak}.
      
    Behavior:
      - The max streak is the longest run of consecutive scheduled days on which a log exists.
      - The current streak is the run ending with the effective scheduled day (either today if
        today is scheduled, or the most recent scheduled day before today). If that day wasn’t
        logged, the current streak is 0.
    """
    def next_scheduled_date(current_date, period):
        """
        Given a current_date and a list of scheduled weekdays (1=Mon,...,7=Sun),
        returns the next scheduled date after current_date.
        """
        sorted_period = sorted(period)
        w = current_date.isoweekday()  # Monday=1, Sunday=7
        for day in sorted_period:
            if day > w:
                return current_date + timedelta(days=(day - w))
        # If none found, wrap to the next week:
        return current_date + timedelta(days=(7 - w + sorted_period[0]))

    def previous_scheduled_date(current_date, period):
        """
        Given a current_date (assumed to be a scheduled day) and a list of scheduled weekdays,
        returns the previous scheduled date before current_date.
        """
        sorted_period = sorted(period)
        w = current_date.isoweekday()
        candidate = None
        for day in sorted_period:
            if day < w:
                candidate = day  # the last one less than w
        if candidate is not None:
            return current_date - timedelta(days=(w - candidate))
        else:
            # If current_date's weekday is the smallest in period, wrap to previous week.
            candidate = sorted_period[-1]
            return current_date - timedelta(days=(w + (7 - candidate)))

    def effective_scheduled_date(current_date, period):
        """
        Returns the effective scheduled date to consider for the current streak.
        If current_date is scheduled (its weekday is in period), return it;
        otherwise, return the most recent scheduled day.
        """
        if current_date.isoweekday() in period:
            return current_date
        else:
            d = current_date
            # At most, we have to go back 6 days.
            while d.isoweekday() not in period:
                d -= timedelta(days=1)
            return d

    # Convert the provided timestamp to a date.
    current_date = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    
    # Create a set of logged dates (as date objects) for which the habit was marked.
    # Convert the integer 'date' field to a date using the epoch (1970-01-01).
    epoch_date = datetime(1970, 1, 1).date()
    logged_dates = set()
    for log in habit_logs:
        log_date = epoch_date + timedelta(days=log['date'])
        # Only consider logs on scheduled days.
        if log_date.isoweekday() in period:
            logged_dates.add(log_date)
    
    # If there are no logs, both streaks are 0.
    if not logged_dates:
        return {"current_streak": 0, "max_streak": 0}
    
    # ----------------------
    # Compute maximum streak.
    # We assume that consecutive logs are those that fall on the exact scheduled day
    # expected after the previous logged scheduled day.
    sorted_logged = sorted(logged_dates)
    max_streak = 1
    current_run = 1
    prev_date = sorted_logged[0]
    for d in sorted_logged[1:]:
        expected = next_scheduled_date(prev_date, period)
        if d == expected:
            current_run += 1
        else:
            current_run = 1  # reset the run if a scheduled day was missed
        if current_run > max_streak:
            max_streak = current_run
        prev_date = d
    
    # ----------------------
    # Compute current streak.
    # Determine the effective scheduled date (if today is scheduled, use today; else, the most recent scheduled day).
    effective_day = effective_scheduled_date(current_date, period)
    
    # If the effective scheduled day was missed, the current streak is 0.
    if effective_day not in logged_dates:
        current_streak = 0
    else:
        # Walk backwards (using the previous scheduled date) counting consecutive logged days.
        current_streak = 0
        d = effective_day
        while d in logged_dates:
            current_streak += 1
            d = previous_scheduled_date(d, period)
    
    return {"current_streak": current_streak, "max_streak": max_streak}

def calculate_usual_streak(habit_logs, timestamp):
    if habit_logs is None:
        return {"current_streak": 0, "max_streak": 0}
    
    epoch_date = datetime(1970, 1, 1).date()
    today = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    yesterday = today - timedelta(days=1)
    
    # Sort logs by date and filter out future dates
    sorted_logs = sorted(habit_logs, key=lambda x: x["date"])
    filtered_logs = []
    for log in sorted_logs:
        log_date = epoch_date + timedelta(days=log["date"])
        if log_date <= today:
            filtered_logs.append(log)
    
    current_streak = 0
    max_streak = 0
    prev_date = None
    
    for log in filtered_logs:
        current_date = log["date"]
        
        if prev_date is None:
            current_streak = 1
        elif current_date == prev_date + 1:
            current_streak += 1
        else:
            current_streak = 1  # Reset streak if not consecutive
        
        max_streak = max(max_streak, current_streak)
        prev_date = current_date
    
    # Check if the last log's date is today or yesterday
    if filtered_logs:
        last_log_date = epoch_date + timedelta(days=filtered_logs[-1]["date"])
        if last_log_date not in [today, yesterday]:
            current_streak = 0
    else:
        current_streak = 0
    
    return {"current_streak": current_streak, "max_streak": max_streak}

def _ts_to_dt(ts: float) -> datetime:
    """
    Convert a timestamp to a datetime object.
    If the timestamp appears to be in microseconds, convert by dividing by 1e6.
    Otherwise, assume seconds.
    """
    # Use threshold: if greater than 1e11 assume microseconds.
    if ts > 1e11:
        return datetime.fromtimestamp(ts / 1e6)
    else:
        return datetime.fromtimestamp(ts)

def calculate_streak_for_bad_habit(habit_logs, timestamp, creation_datetime):
    """
    Calculate the current and max streak for a bad habit.

    Parameters:
      - habit_logs: list of dicts each containing a 'date' field representing the number of days since Unix epoch.
                    For example: [{'date': 20127}, {'date': 20126}]
      - timestamp: current timestamp representing "now"
      - creation_datetime: a timestamp (in seconds or microseconds) when the habit was created

    Returns:
      dict with keys "current_streak" and "max_streak"
      
    Streak logic:
      - Days are computed in UTC.
      - Days run from creation_date up to (but not including) the current day (derived from the timestamp).
      - A day is counted as a streak day if no log for that day has a status "completed".
      - If a "completed" log is present on a day, the streak resets on that day.
      - Additionally, if the current day (based on the input timestamp) has a "completed" record (with a log time not later than the provided timestamp), the current streak is 0.
    """
    # Convert input timestamp to a datetime and get its date.
    epoch_date = datetime(1970, 1, 1).date()
    current_date = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    
    # Parse creation_datetime (strip trailing 'Z' if present)
    dt_creation = _ts_to_dt(creation_datetime)
    creation_date = dt_creation.date()
    
    # If the habit was created today or creation_date is after current_date, streak is 0.
    if creation_date >= current_date:
        return {"current_streak": 0, "max_streak": 0}
    
    # Build a set of dates on which habit was marked as completed.
    # For dates before the current_date, any "completed" log resets the streak.
    completed_days = set()
    # Flag indicating if current_date is completed as of dt_current.
    current_date_completed = False
    
    for log in habit_logs:
        log_date = epoch_date + timedelta(days=log.get("date", 0))
        # Only consider logs that occur between creation_date and current_date (or on current_date for special treatment).
        if creation_date <= log_date < current_date:
            completed_days.add(log_date)

    # Also check if the current date is a completion day.
    current_date_completed = (current_date in 
                              {epoch_date + timedelta(days=log.get("date", 0)) for log in habit_logs})

    # Iterate day by day from the creation_date (inclusive) to the day before current_date.
    current_running = 0
    max_running = 0
    day = creation_date
    while day < current_date:
        if day in completed_days:
            current_running = 0  # streak resets on a completed day
        else:
            current_running += 1
            if current_running > max_running:
                max_running = current_running
        day += timedelta(days=1)
    
    # If the current day has a completion record (up to the given timestamp) then current streak resets, otherwise current streak is the streak built from full days.
    current_streak = 0 if current_date_completed else current_running

    return {"current_streak": current_streak, "max_streak": max_running}
    
if __name__ == "__main__":
    recalculate_streak()