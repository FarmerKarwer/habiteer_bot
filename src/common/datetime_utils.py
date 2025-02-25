from datetime import datetime, timezone, timedelta
import re

from .exceptions import InvalidTimezoneFormat, TimezoneOutOfRangeError

def unix_to_timestamp(unix_time):
    # Convert the Unix timestamp to a datetime object
    dt = datetime.fromtimestamp(unix_time, tz=timezone.utc)
    
    # Format the datetime object in ISO 8601 format with milliseconds
    formatted_time = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    return formatted_time

def convert_timezone(timezone_str: str) -> str:
    """
    Converts a timezone string in either "UTC±X" or "МСК±X" format to "utc±X" format.
    
    For UTC input, it normalizes the string.
    For МСК input, it converts the timezone to UTC by applying the offset relative to UTC+3.
    
    Examples:
      - "МСК+0" or "мск-0" converts to "utc+3"
      - "МСК-1" converts to "utc+2"
      - "МСК+2" converts to "utc+5"
      - "UTC+4" returns "utc+4"
      - "utc-7" returns "utc-7"
      
    Additionally, the function will enforce valid ranges:
      - For UTC input, the numeric offset must be within the range -12 to +14.
      - For МСК input, the provided offset (taking into account its sign) must be within the allowable values from -1 to 9.
      
    Raises:
      ValueError: If the input string does not match the expected format or if the offset is out of range.
    
    Parameters:
      timezone_str (str): The timezone string to validate and convert.
      
    Returns:
      str: The normalized timezone string in the format "utc±X".
    """
    if not isinstance(timezone_str, str):
        raise ValueError("Invalid input: expected a string.")

    # Regular expression to match either "мск" or "utc" followed by a sign and one or more digits.
    # The regex is case-insensitive.
    pattern = re.compile(r'^(мск|utc)([+-])(\d+)$', re.IGNORECASE)
    match = pattern.match(timezone_str)
    
    if not match:
        raise InvalidTimezoneFormat("Invalid timezone format. Expected formats: 'МСК±X' or 'UTC±X'.")

    prefix = match.group(1).lower()  # either "мск" or "utc" in lowercase
    sign = match.group(2)
    try:
        number = int(match.group(3))
    except ValueError:
        raise InvalidTimezoneFormat("Invalid numeric value in the timezone string.")

    if prefix == "utc":
        # For UTC, determine the full numeric value with sign.
        utc_value = number if sign == "+" else -number
        # Define the acceptable range for UTC offsets.
        if not (-12 <= utc_value <= 14):
            raise TimezoneOutOfRangeError("UTC offset out of allowed range (-12 to +14).")
        return f"utc{sign}{number}"

    # For МСК, validate that the provided offset is within the allowable range of -1 to 9.
    # Calculate the signed offset provided in the string.
    msk_input_offset = number if sign == "+" else -number
    if not (-1 <= msk_input_offset <= 9):
        raise TimezoneOutOfRangeError("МСК offset out of allowed range (-1 to 9).")
    
    # Moscow standard time is UTC+3.
    base_offset = 3
    # Convert МСК to UTC offset.
    utc_offset = base_offset + msk_input_offset

    # Validate the resulting UTC offset as well, ensuring it is within the allowed range for UTC.
    if not (-12 <= utc_offset <= 14):
        raise TimezoneOutOfRangeError("Resulting UTC offset is out of allowed range (-12 to +14).")

    result_sign = "+" if utc_offset >= 0 else "-"
    return f"utc{result_sign}{abs(utc_offset)}"

def parse_time_from_string(input_string):
    """
    Validates and parses time in the format HH:MM from a string.
    The string must contain only the time in this format, otherwise raises a ValueError.

    :param input_string: The input string to validate and parse.
    :return: A string representing time in HH:MM format.
    """
    # Regular expression for matching the exact format HH:MM
    time_pattern = r'^([01]\d|2[0-3]):[0-5]\d$'
    match = re.fullmatch(time_pattern, input_string.strip())
    
    if match:
        return match.group(0)  # Return the matched time
    else:
        raise ValueError("Input string must contain only time in HH:MM format.")

def validate_datetime(s):
    # First check the format length and expected separators.
    if len(s) != 14:
        raise ValueError("Invalid format")
    if s[2] != '.' or s[5] != '.' or s[8] != ' ' or s[11] != ':':
        raise ValueError("Invalid separators")
    
    # Extract components from the string.
    day_str = s[0:2]
    month_str = s[3:5]
    year_str = s[6:8]
    hour_str = s[9:11]
    minute_str = s[12:14]
    
    # Validate that all the components are numeric.
    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit() and hour_str.isdigit() and minute_str.isdigit()):
        raise ValueError("Non-digit components")
    
    day = int(day_str)
    month = int(month_str)
    year = int(year_str)
    hour = int(hour_str)
    minute = int(minute_str)
    
    # Basic range checks.
    if not 1 <= day <= 31:
        raise ValueError("Day out of range")
    if not 1 <= month <= 12:
        raise ValueError("Month out of range")
    if not 0 <= year <= 99:
        raise ValueError("Year out of range")
    if not 0 <= hour <= 23:
        raise ValueError("Hour out of range")
    if not 0 <= minute <= 59:
        raise ValueError("Minute out of range")
    
    # Construct a datetime object.
    # Assuming the two-digit year represents a year from 2000 to 2099.
    input_datetime = datetime(2000 + year, month, day, hour, minute)
    
    # Check if the input datetime is before the current datetime.
    if input_datetime <= datetime.now():
        raise ValueError("Datetime must be in the future")
    
    return input_datetime

def validate_marginal_datetime_entry(user_input):
    """
    Validates if the user input matches the format:
    'Через X дн в HH:MM'
    Example: 'через 0 дн в 21:25'
    Negative values are NOT allowed.
    
    Args:
        user_input (str): The user input to validate.
    
    Returns:
        bool: True if the input matches the format, False otherwise.
    """
    # Define the regex pattern for validation
    pattern = r"(?i)^через (\d{1,2}) дн в ([01]\d|2[0-3]):([0-5]\d)$"
    
    # Check if the input matches the pattern
    if re.match(pattern, user_input):
        return True
    else:
        raise ValueError("Input string must match 'Через X дн в HH:MM' format.")

def calculate_datetime_margin_from_user_input(user_input, timestamp, user_timezone_offset=3):
    """
    Calculate a timestamp based on the input format 'Через X дн в HH:MM'.
    
    Args:
        user_input (str): User input, e.g., 'Через 1 дн в 14:30'.
    
    Returns:
        datetime: Future timestamp based on the input.
    """
    # Define the regex to extract values
    pattern = r"^через (\d+) дн в ([01]?\d|2[0-3]):([0-5]\d)$"
    match = re.match(pattern, user_input, re.IGNORECASE)

    if not match:
        raise ValueError("Invalid input format. Please use 'Через X дн в HH:MM'.")

    # Extract values from input
    days = int(match.group(1))
    hours = int(match.group(2))
    minutes = int(match.group(3))

    # Get the current timestamp
    current_time = timestamp
    current_time = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%S.%fZ")

    user_local_time = current_time + timedelta(hours=user_timezone_offset)

    # Calculate the future timestamp
    future_date = current_time + timedelta(days=days)
    precise_time = future_date.replace(hour=hours, minute=minutes, second=0)

    if precise_time<=user_local_time:
        raise ValueOutOfRangeError

    target_utc_time = precise_time - timedelta(hours=user_timezone_offset)

    return target_utc_time

def weekdays_to_numbers(weekdays, start_from_sunday=False):
    # Define the mapping
    if start_from_sunday:
        weekday_map = {'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6}
    else:  # ISO 8601 standard
        weekday_map = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6, 'sun': 7}
    
    # Convert the list of weekdays to corresponding numbers
    return [weekday_map[day.lower()] for day in weekdays if day.lower() in weekday_map]

def numbers_to_weekdays(numbers, start_from_sunday=False):
    # Define the mapping
    if start_from_sunday:
        number_map = {0: 'sun', 1: 'mon', 2: 'tue', 3: 'wed', 4: 'thu', 5: 'fri', 6: 'sat'}
    else:  # ISO 8601 standard
        number_map = {1: 'mon', 2: 'tue', 3: 'wed', 4: 'thu', 5: 'fri', 6: 'sat', 7: 'sun'}
    
    # Convert the list of numbers to corresponding weekdays
    return [number_map[num] for num in numbers if num in number_map]

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

def get_days_string(days, lang='ru'):
    if lang == 'ru':
        mod_100 = days % 100
        if 11 <= mod_100 <= 14:
            word = 'дней'
        else:
            mod_10 = days % 10
            if mod_10 == 1:
                word = 'день'
            elif 2 <= mod_10 <= 4:
                word = 'дня'
            else:
                word = 'дней'
    else:  # English
        word = 'day' if days == 1 else 'days'
    
    return f"{days} {word}"

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

from datetime import datetime, timedelta, date

from datetime import datetime, timedelta

def get_consecutive_skipped_days_for_habit(habit_logs, timestamp, period, started_tracking_at):
    """
    Returns the number of consecutive scheduled days (per the given period) that the user skipped.
    
    Parameters:
      - habit_logs: list of dicts, each with a 'date' key representing the number of days since Jan 1, 1970.
      - timestamp: ISO 8601 timestamp string (e.g., "2025-02-24T16:26:36.000Z")
      - period: list of weekdays (Monday=1, ..., Sunday=7) on which the habit is expected.
      - started_tracking_at: timestamp in microseconds since the Unix epoch indicating when tracking began.
    
    Note:
      This function counts only complete days. That is, it considers scheduled days strictly before
      the date part of the provided timestamp. For example, if today is Wednesday, only days up to Tuesday
      are evaluated.
    """
    # Convert provided timestamp to a datetime object.
    ts = timestamp.replace("Z", "+00:00")
    current_dt = datetime.fromisoformat(ts)
    current_date = current_dt.date()
    
    # Convert started_tracking_at (microseconds) to a date.
    start_dt = datetime.utcfromtimestamp(started_tracking_at / 1e6)
    start_date = start_dt.date()
    
    # Build a set of dates (as datetime.date) when the habit was logged.
    epoch = datetime(1970, 1, 1).date()
    logged_dates = {epoch + timedelta(days=log['date']) for log in habit_logs}
    
    # Helper: checks if a given date is a scheduled day.
    # Note: Python's weekday() returns 0 for Monday, so we add 1.
    def is_scheduled(d):
        return (d.weekday() + 1) in period
    
    # For consistency with the examples, we count only days before the current date.
    # Find the most recent scheduled day strictly before current_date.
    d = current_date - timedelta(days=1)
    last_scheduled = None
    while d >= start_date:
        if is_scheduled(d):
            last_scheduled = d
            break
        d -= timedelta(days=1)
    
    if last_scheduled is None:
        return 0  # No scheduled day exists in the period before current_date.
    
    # Count consecutive skipped scheduled days by iterating backward.
    streak = 0
    current_day = last_scheduled
    while current_day >= start_date:
        if is_scheduled(current_day):
            if current_day not in logged_dates:
                streak += 1
            else:
                break  # A completed day breaks the consecutive skip streak.
        current_day -= timedelta(days=1)
    
    return streak

