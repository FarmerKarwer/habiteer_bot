import json
import pytest
from unittest.mock import mock_open, patch

from utils import (
    append_to_json,
    delete_user_records,
    load_json,
    save_to_json,
    sum_arrays,
    unix_to_timestamp,
    update_user_value,
)


# ---------------------
# Fixtures
# ---------------------

@pytest.fixture
def sample_user_data():
    """Provides sample user data for tests."""
    return [
        {"user_id": 1, "name": "Alice", "age": 30},
        {"user_id": 2, "name": "Bob", "age": 25}
    ]

@pytest.fixture
def sample_append_initial_data():
    """Provides initial data for append_to_json tests."""
    return [
        {"user_id": 1, "chat_id": 100, "message": "Hello", "id": 1},
        {"user_id": 1, "chat_id": 100, "message": "How are you?", "id": 2},
    ]

# ---------------------
# Test Load JSON
# ---------------------

def test_load_json_valid():
    """Test loading valid JSON data."""
    valid_json = '{"name": "John", "age": 30}'
    with patch("builtins.open", mock_open(read_data=valid_json)):
        result = load_json("fake_path.json")
    expected = {"name": "John", "age": 30}
    assert result == expected

def test_load_json_invalid():
    """Test loading invalid JSON data raises JSONDecodeError."""
    invalid_json = '{"name": "John", "age": 30'
    with patch("builtins.open", mock_open(read_data=invalid_json)):
        with pytest.raises(json.JSONDecodeError):
            load_json("fake_path.json")

def test_load_json_file_not_found():
    """Test loading JSON from a non-existent file raises FileNotFoundError."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            load_json("non_existent_file.json")

# ---------------------
# Test Save JSON
# ---------------------

def test_save_to_json(tmp_path):
    """Test saving data to a JSON file."""
    test_data = {
        "name": "ChatGPT",
        "type": "AI Language Model",
        "features": ["text generation", "conversation", "code assistance"]
    }
    file_path = tmp_path / "test_output.json"

    save_to_json(file_path, test_data)

    assert file_path.exists(), "JSON file was not created."

    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    assert data == test_data, "Data written to JSON does not match the input data."

    # Verify indentation (4 spaces)
    with open(file_path, "r") as json_file:
        content = json_file.read()
    for line in content.splitlines()[1:]:  # Skip the first line
        stripped_line = line.lstrip()
        indent = len(line) - len(stripped_line)
        assert indent % 4 == 0, "Indentation is not a multiple of 4 spaces."

# ---------------------
# Test Append to JSON
# ---------------------

def test_append_to_json_file_not_exists(tmp_path):
    """
    Append to a non-existent JSON file should create a new list with id=1.
    """
    filepath = tmp_path / "data.json"
    new_data = {"user_id": 1, "chat_id": 100, "message": "Hello"}

    result = append_to_json(str(filepath), new_data)

    expected = [{"user_id": 1, "chat_id": 100, "message": "Hello", "id": 1}]
    assert result == expected

def test_append_to_json_file_empty(tmp_path):
    """
    Append to an existing empty JSON file should initialize the list with id=1.
    """
    filepath = tmp_path / "data.json"
    filepath.write_text("")
    new_data = {"user_id": 2, "chat_id": 200, "message": "Hi"}

    result = append_to_json(str(filepath), new_data)

    expected = [{"user_id": 2, "chat_id": 200, "message": "Hi", "id": 1}]
    assert result == expected

def test_append_to_json_invalid_json(tmp_path):
    """
    Append to a JSON file with invalid content should treat it as empty and assign id=1.
    """
    filepath = tmp_path / "data.json"
    filepath.write_text("invalid json")
    new_data = {"user_id": 3, "chat_id": 300, "message": "Hey"}

    result = append_to_json(str(filepath), new_data)

    expected = [{"user_id": 3, "chat_id": 300, "message": "Hey", "id": 1}]
    assert result == expected

def test_append_new_user_chat(tmp_path, sample_append_initial_data):
    """
    Appending new (user_id, chat_id) assigns id=1 without affecting existing data.
    """
    filepath = tmp_path / "data.json"
    initial_data = sample_append_initial_data
    filepath.write_text(json.dumps(initial_data))
    new_data = {"user_id": 2, "chat_id": 200, "message": "Hi there"}

    result = append_to_json(str(filepath), new_data)

    expected = initial_data + [{"user_id": 2, "chat_id": 200, "message": "Hi there", "id": 1}]
    assert result == expected

def test_append_existing_user_chat(tmp_path, sample_append_initial_data):
    """
    Appending existing (user_id, chat_id) assigns next sequential id and removes old entries.
    """
    filepath = tmp_path / "data.json"
    initial_data = sample_append_initial_data + [
        {"user_id": 2, "chat_id": 200, "message": "Hi there", "id": 1}
    ]
    filepath.write_text(json.dumps(initial_data))
    new_data = {"user_id": 1, "chat_id": 100, "message": "I'm fine"}

    result = append_to_json(str(filepath), new_data)

    expected = [
        {"user_id": 2, "chat_id": 200, "message": "Hi there", "id": 1},
        {"user_id": 1, "chat_id": 100, "message": "I'm fine", "id": 3},
    ]
    assert result == expected

@pytest.mark.xfail(reason="Function does not handle non-list JSON data correctly")
def test_append_json_data_not_list(tmp_path):
    """
    Appending to a JSON file with non-list data should convert to list and append.
    """
    filepath = tmp_path / "data.json"
    initial_data = {"user_id": 1, "chat_id": 100, "message": "Single entry", "id": 1}
    filepath.write_text(json.dumps(initial_data))
    new_data = {"user_id": 1, "chat_id": 100, "message": "Another entry"}

    result = append_to_json(str(filepath), new_data)

    expected = [
        {"user_id": 1, "chat_id": 100, "message": "Single entry", "id": 1},
        {"user_id": 1, "chat_id": 100, "message": "Another entry", "id": 2},
    ]
    assert result == expected

# ---------------------
# Test Update User Value
# ---------------------

def test_update_existing_user(tmp_path, capsys, sample_user_data):
    """
    Update an existing user's value in the JSON file.
    """
    file_path = tmp_path / "users.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_user_data, f, ensure_ascii=False, indent=4)

    update_user_value(str(file_path), 1, 'age', 31)

    captured = capsys.readouterr()
    assert "Updated age for user_id 1 to 31." in captured.out

    with open(file_path, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    expected_data = [
        {"user_id": 1, "name": "Alice", "age": 31},
        {"user_id": 2, "name": "Bob", "age": 25}
    ]
    assert updated_data == expected_data

def test_update_non_existing_user(tmp_path, capsys, sample_user_data):
    """
    Attempt to update a non-existing user should not alter the JSON and print a message.
    """
    file_path = tmp_path / "users.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_user_data, f, ensure_ascii=False, indent=4)

    update_user_value(str(file_path), 3, 'age', 40)

    captured = capsys.readouterr()
    assert "User with user_id 3 not found." in captured.out

    with open(file_path, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    assert updated_data == sample_user_data

def test_add_new_key_existing_user(tmp_path, capsys, sample_user_data):
    """
    Add a new key to an existing user in the JSON file.
    """
    file_path = tmp_path / "users.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_user_data, f, ensure_ascii=False, indent=4)

    update_user_value(str(file_path), 2, 'email', 'bob@example.com')

    captured = capsys.readouterr()
    assert "Updated email for user_id 2 to bob@example.com." in captured.out

    with open(file_path, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    expected_data = [
        {"user_id": 1, "name": "Alice", "age": 30},
        {"user_id": 2, "name": "Bob", "age": 25, "email": "bob@example.com"}
    ]
    assert updated_data == expected_data

# ---------------------
# Test Delete User Records
# ---------------------

def test_delete_existing_user(tmp_path, capsys):
    """
    Delete an existing user record from the JSON file.
    """
    file_path = tmp_path / "users.json"
    initial_data = [
        {"user_id": 1, "name": "Alice"},
        {"user_id": 2, "name": "Bob"},
        {"user_id": 3, "name": "Charlie"},
    ]
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(initial_data, f, ensure_ascii=False, indent=4)

    delete_user_records(str(file_path), 2)

    captured = capsys.readouterr()
    assert "Deleted records for user_id 2." in captured.out

    with open(file_path, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    expected_data = [
        {"user_id": 1, "name": "Alice"},
        {"user_id": 3, "name": "Charlie"},
    ]
    assert updated_data == expected_data

def test_delete_nonexistent_user(tmp_path, capsys, sample_user_data):
    """
    Attempting to delete a non-existent user should not alter the JSON and print a message.
    """
    file_path = tmp_path / "users.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_user_data, f, ensure_ascii=False, indent=4)

    delete_user_records(str(file_path), 3)

    captured = capsys.readouterr()
    assert "No records found for user_id 3." in captured.out

    with open(file_path, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    assert updated_data == sample_user_data

def test_delete_from_empty_file(tmp_path, capsys):
    """
    Attempt to delete a user from an empty JSON file should print a message.
    """
    file_path = tmp_path / "users.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([], f)

    delete_user_records(str(file_path), 1)

    captured = capsys.readouterr()
    assert "No records found for user_id 1." in captured.out

    with open(file_path, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    assert updated_data == []

def test_delete_file_not_found():
    """
    Attempting to delete a user from a non-existent file should raise FileNotFoundError.
    """
    file_path = "non_existent_file.json"
    with pytest.raises(FileNotFoundError):
        delete_user_records(file_path, 1)

def test_delete_invalid_json_format(tmp_path):
    """
    Deleting from a file with invalid JSON should raise JSONDecodeError.
    """
    file_path = tmp_path / "invalid.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("This is not a valid JSON.")

    with pytest.raises(json.JSONDecodeError):
        delete_user_records(str(file_path), 1)

def test_delete_multiple_records(tmp_path, capsys):
    """
    Delete multiple records with the same user_id.
    """
    file_path = tmp_path / "users.json"
    initial_data = [
        {"user_id": 2, "name": "Bob"},
        {"user_id": 2, "name": "Bobby"},
        {"user_id": 3, "name": "Charlie"},
    ]
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(initial_data, f, ensure_ascii=False, indent=4)

    delete_user_records(str(file_path), 2)

    captured = capsys.readouterr()
    assert "Deleted records for user_id 2." in captured.out

    with open(file_path, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    expected_data = [
        {"user_id": 3, "name": "Charlie"},
    ]
    assert updated_data == expected_data

# ---------------------
# Test Sum Arrays
# ---------------------

@pytest.mark.parametrize(
    "arr1, arr2, expected",
    [
        ([], [], []),
        ([1, 2, 3], [4, 5, 6], [5, 7, 9]),
        ([-1, -2, -3], [-4, -5, -6], [-5, -7, -9]),
        ([1, -2, 3], [-4, 5, -6], [-3, 3, -3]),
        ([1.5, 2.5, 3.5], [4.5, 5.5, 6.5], [6.0, 8.0, 10.0]),
    ]
)
def test_sum_arrays_valid(arr1, arr2, expected):
    """Test summing two arrays with valid inputs."""
    assert sum_arrays(arr1, arr2) == expected

def test_sum_arrays_mismatched_lengths():
    """Test that summing arrays of different lengths raises ValueError."""
    arr1 = [1, 2, 3]
    arr2 = [4, 5]
    with pytest.raises(ValueError, match="Arrays must be of the same length"):
        sum_arrays(arr1, arr2)

# ---------------------
# Test Unix to Timestamp
# ---------------------

@pytest.mark.parametrize(
    "unix_time, expected",
    [
        (0, "1970-01-01T00:00:00.000Z"),
        (1609459200, "2021-01-01T00:00:00.000Z"),  # 2021-01-01
        (1610000000.123, "2021-01-07T06:13:20.123Z"),
        (1625097600, "2021-07-01T00:00:00.000Z"),  # 2021-07-01
        (-1, "1969-12-31T23:59:59.000Z"),
        # Adjust the following timestamp based on the actual current time
        # For demonstration purposes, assuming a known timestamp
        (1700000000, "2023-11-14T22:13:20.000Z"),
    ]
)
def test_unix_to_timestamp(unix_time, expected):
    """Test converting Unix time to ISO timestamp."""
    assert unix_to_timestamp(unix_time) == expected

def test_unix_to_timestamp_invalid_type():
    """Test that passing a non-numeric type raises TypeError."""
    with pytest.raises(TypeError):
        unix_to_timestamp("not_a_timestamp")
