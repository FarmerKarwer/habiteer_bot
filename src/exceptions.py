
# Custom exceptions
class ValueOutOfRangeError(Exception):
	"""Custom exception for values out of range."""
	pass

class ListTooShortError(Exception):
	"""Custom exception for lists with fewer than 5 entries."""
	pass

class ListLengthMismatchError(Exception):
	"""Custom exception for list length mismatch errors."""
	pass
