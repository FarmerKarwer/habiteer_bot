from typing import Any, Callable, Dict, List, Optional
from exceptions import (
    ValueOutOfRangeError,
    ListTooShortError,
    ListLengthMismatchError,
)

def sum_arrays(arr1, arr2):
    # Check if arrays have the same length
    if len(arr1) != len(arr2):
        raise ValueError("Arrays must be of the same length")

    # Sum elements at corresponding positions
    return [a + b for a, b in zip(arr1, arr2)]

def format_numbered_list(items: List[str], capitalize: bool = True) -> str:
    """
    Formats a list of strings into a numbered, newline-separated string.

    Args:
        items (List[str]): The list of strings to format.
        capitalize (bool, optional): Whether to capitalize each item. Defaults to True.

    Returns:
        str: A numbered, newline-separated string with each item optionally capitalized.
    """
    if capitalize:
        items = (item.capitalize() for item in items)
    else:
        items = (item for item in items)
    
    return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))

def extract_numbered_items(text: str) -> List[str]:
    """
    Extracts items from a numbered multi-line string.

    Each line should start with a number followed by a period and a space (e.g., "1. Item").

    Args:
        text (str): The input string containing numbered items separated by newlines.

    Returns:
        List[str]: A list of extracted items without their numbering.
    """
    items = []
    for line in text.strip().split('\n'):
        if line:
            match = re.match(r'^\d+\.\s+(.*)', line)
            if match:
                item = match.group(1).strip()
                items.append(item)
            else:
                print("Warning! Lines do not match the expected pattern. Handling is skipped")
                continue
    return items

def parse_numbers(text: str) -> List[int]:
    """Parses numbers and ranges from a given text."""
    numbers = []
    # Split the input by commas
    parts = text.split(',')
    for part in parts:
        part = part.strip()  # Remove any surrounding whitespace
        if '-' in part:
            # Split the range into start and end
            try:
                start, end = part.split('-')
                start, end = int(start), int(end)
                if start > end:
                    raise ValueError(f"Invalid range: {part}")
                # Extend the numbers list with the range
                numbers.extend(range(start, end + 1))
            except ValueError as ve:
                raise ValueError(f"Invalid range format: '{part}'. Error: {ve}")
        else:
            # Convert single number to integer and append
            try:
                number = int(part)
                numbers.append(number)
            except ValueError:
                raise ValueError(f"Invalid number format: '{part}'")
    return numbers

# List conditions
def check_all_in_range(input_list, min=1, max=10):
    # Check if all items are between 1 and 10
    if not all(min <= item <= max for item in input_list):
        raise ValueOutOfRangeError("All items must be between 1 and 10.")

def check_matching_lengths(list1, list2):
    """Checks if two lists have matching lengths."""
    if len(list1) != len(list2):
        raise ListLengthMismatchError("The lengths of the lists do not match.")

def check_minimum_length(input_list, min_length=5):
    """Ensures the list meets the minimum required length."""
    if len(input_list) < min_length:
        raise ListTooShortError(f"The list has fewer than {min_length} entries.")
