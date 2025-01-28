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
