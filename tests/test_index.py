# test_index.py
import pytest
from unittest.mock import patch, MagicMock

from index import handler, handler_long

# Mock event and context for handler
mock_event_handler = "events/using_command.json"
mock_context_handler = "Sample context"

# Mock response for get_updates used in handler
mock_tg_response = {
    "ok": True,
    "result": [
        {
            "update_id": 325958251,
            "message": {
                "message_id": 28,
                "from": {
                    "id": 940985788,
                    "is_bot": False,
                    "first_name": "Artem",
                    "username": "morisdave",
                    "language_code": "en"
                },
                "chat": {
                    "id": 940985788,
                    "first_name": "Artem",
                    "username": "morisdave",
                    "type": "private"
                },
                "date": 1733228485,
                "text": "5"
            }
        },
        {
            "update_id": 325958255,
            "message": {
                "message_id": 33,
                "from": {
                    "id": 940985788,
                    "is_bot": False,
                    "first_name": "Artem",
                    "username": "morisdave",
                    "language_code": "en"
                },
                "chat": {
                    "id": 940985788,
                    "first_name": "Artem",
                    "username": "morisdave",
                    "type": "private"
                },
                "date": 1733228517,
                "text": "something"
            }
        },
        {
            "update_id": 325958257,
            "message": {
                "message_id": 36,
                "from": {
                    "id": 940985788,
                    "is_bot": False,
                    "first_name": "Artem",
                    "username": "morisdave",
                    "language_code": "en"
                },
                "chat": {
                    "id": 940985788,
                    "first_name": "Artem",
                    "username": "morisdave",
                    "type": "private"
                },
                "date": 1733228544,
                "text": "1. sfgsdfg\n2. sdfgsdfg\n3. sdfgsdfg\n4. sdfgdsfg\n5. sdfhgsdfgfds"
            }
        },
        {
            "update_id": 325958276,
            "callback_query": {
                "id": "4041503185848870858",
                "from": {
                    "id": 940985788,
                    "is_bot": False,
                    "first_name": "Artem",
                    "username": "morisdave",
                    "language_code": "en"
                },
                "message": {
                    "message_id": 54,
                    "from": {
                        "id": 7332437137,
                        "is_bot": True,
                        "first_name": "Habiteer_local",
                        "username": "habiteer_local_bot"
                    },
                    "chat": {
                        "id": 940985788,
                        "first_name": "Artem",
                        "username": "morisdave",
                        "type": "private"
                    },
                    "date": 1733232703,
                    "text": "\u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e.\n\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043e\u0434\u0438\u043d \u0438\u0437 \u043f\u0443\u043d\u043a\u0442\u043e\u0432 \u043d\u0438\u0436\u0435",
                    "reply_markup": {
                        "inline_keyboard": [
                            [{"text": "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043f\u0440\u0438\u0432\u044b\u0447\u043a\u0443", "callback_data": "scr_2"}],
                            [{"text": "\u041c\u043e\u0438 \u043f\u0440\u0438\u0432\u044b\u0447\u043a\u0438", "callback_data": "scr_3"}],
                            [{"text": "\u041f\u043e\u0434\u043e\u0431\u0440\u0430\u0442\u044c \u043f\u0440\u0438\u0432\u044b\u0447\u043a\u0443", "callback_data": "scr_4"}],
                            [{"text": "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", "callback_data": "plug"}],
                            [{"text": "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", "callback_data": "scr_6"}]
                        ]
                    },
                    "has_protected_content": True
                },
                "chat_instance": "8667056629342611601",
                "data": "scr_6"
            }
        }
    ]
}

# -------------------- Tests for handler --------------------

@patch('index.get_updates')
@patch('index.use_logic')
def test_handler(mock_use_logic, mock_get_updates):
    # Setup the mock for get_updates
    mock_get_updates.return_value = mock_tg_response

    # Call the handler function with mocked event and context
    response = handler(mock_event_handler, mock_context_handler)

    # Assertions for get_updates
    mock_get_updates.assert_called_once()

    # Assertions for use_logic
    mock_use_logic.assert_called_once_with(mock_tg_response['result'][-1])

    # Assertions for the handler response
    assert response['statusCode'] == 200
    assert response['body'] == mock_event_handler
    assert response['message'] == mock_tg_response['result'][-1]

# -------------------- Tests for handler_long --------------------

def test_handler_long():
    # Sample event and context for handler_long
    event_long = {"key": "value"}
    context_long = {}

    # Mock responses for get_updates
    mock_updates_first_call = {
        "ok": True,
        "result": [
            {"update_id": 1001, "data": "test data 1"}
        ]
    }

    mock_updates_second_call = KeyboardInterrupt()

    with patch('index.get_updates', side_effect=[mock_updates_first_call, mock_updates_second_call]) as mock_get_updates, \
         patch('index.use_logic') as mock_use_logic, \
         patch('index.time.sleep', return_value=None):

        # Execute the handler_long function
        response = handler_long(event_long, context_long)

        # Assertions for the response
        assert response['statusCode'] == 200
        assert response['body'] == event_long
        assert response['message'] == mock_updates_first_call['result'][-1]

        # Verify that get_updates was called twice
        assert mock_get_updates.call_count == 2

        # Verify that use_logic was called once with the correct update
        mock_use_logic.assert_called_once_with(mock_updates_first_call['result'][-1])

# Alternatively, using a separate test function with more detailed mocking

@patch('index.get_updates')
@patch('index.use_logic')
@patch('index.time.sleep', return_value=None)
def test_handler_long_with_keyboard_interrupt(mock_sleep, mock_use_logic, mock_get_updates):
    # Sample event and context
    event_long = {"key": "value"}
    context_long = {}

    # Define side effects for get_updates
    def get_updates_side_effect(offset=None, timeout=30):
        if not hasattr(get_updates_side_effect, 'call_count'):
            get_updates_side_effect.call_count = 0
        get_updates_side_effect.call_count += 1
        if get_updates_side_effect.call_count == 1:
            return {
                "ok": True,
                "result": [{"update_id": 1001, "data": "test data 1"}]
            }
        elif get_updates_side_effect.call_count == 2:
            raise KeyboardInterrupt

    mock_get_updates.side_effect = get_updates_side_effect

    # Execute the handler_long function
    response = handler_long(event_long, context_long)

    # Assertions for the response
    assert response['statusCode'] == 200
    assert response['body'] == event_long
    assert response['message'] == {"update_id": 1001, "data": "test data 1"}

    # Verify that get_updates was called twice
    assert mock_get_updates.call_count == 2

    # Verify that use_logic was called once with the correct update
    mock_use_logic.assert_called_once_with({"update_id": 1001, "data": "test data 1"})

    # Verify that time.sleep was called once
    mock_sleep.assert_called_once_with(1)

