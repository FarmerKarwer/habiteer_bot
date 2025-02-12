from datetime import datetime, timezone, timedelta
import re

def unix_to_timestamp(unix_time):
    # Convert the Unix timestamp to a datetime object
    dt = datetime.fromtimestamp(unix_time, tz=timezone.utc)
    
    # Format the datetime object in ISO 8601 format with milliseconds
    formatted_time = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    return formatted_time

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
