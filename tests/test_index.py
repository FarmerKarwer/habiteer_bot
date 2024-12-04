import pytest
from unittest.mock import patch, MagicMock

from index import handler

# Mock event and context
mock_event = "events/using_command.json"
mock_context = "Sample context"

mock_tg_response = {"ok":True,"result":[{"update_id":325958251,
"message":{"message_id":28,"from":{"id":940985788,"is_bot":False,"first_name":"Artem","username":"morisdave","language_code":"en"},"chat":{"id":940985788,"first_name":"Artem","username":"morisdave","type":"private"},"date":1733228485,"text":"5"}},{"update_id":325958255,
"message":{"message_id":33,"from":{"id":940985788,"is_bot":False,"first_name":"Artem","username":"morisdave","language_code":"en"},"chat":{"id":940985788,"first_name":"Artem","username":"morisdave","type":"private"},"date":1733228517,"text":"something"}},{"update_id":325958257,
"message":{"message_id":36,"from":{"id":940985788,"is_bot":False,"first_name":"Artem","username":"morisdave","language_code":"en"},"chat":{"id":940985788,"first_name":"Artem","username":"morisdave","type":"private"},"date":1733228544,"text":"1. sfgsdfg\n2. sdfgsdfg\n3. sdfgsdfg\n4. sdfgdsfg\n5. sdfhgsdfgfds"}},{"update_id":325958276,
"callback_query":{"id":"4041503185848870858","from":{"id":940985788,"is_bot":False,"first_name":"Artem","username":"morisdave","language_code":"en"},"message":{"message_id":54,"from":{"id":7332437137,"is_bot":True,"first_name":"Habiteer_local","username":"habiteer_local_bot"},"chat":{"id":940985788,"first_name":"Artem","username":"morisdave","type":"private"},"date":1733232703,"text":"\u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e.\n\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043e\u0434\u0438\u043d \u0438\u0437 \u043f\u0443\u043d\u043a\u0442\u043e\u0432 \u043d\u0438\u0436\u0435","reply_markup":{"inline_keyboard":[[{"text":"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043f\u0440\u0438\u0432\u044b\u0447\u043a\u0443","callback_data":"scr_2"}],[{"text":"\u041c\u043e\u0438 \u043f\u0440\u0438\u0432\u044b\u0447\u043a\u0438","callback_data":"scr_3"}],[{"text":"\u041f\u043e\u0434\u043e\u0431\u0440\u0430\u0442\u044c \u043f\u0440\u0438\u0432\u044b\u0447\u043a\u0443","callback_data":"scr_4"}],[{"text":"\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430","callback_data":"plug"}],[{"text":"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438","callback_data":"scr_6"}]]},"has_protected_content":True},"chat_instance":"8667056629342611601","data":"scr_6"}}]}

@patch('index.get_updates')
@patch('index.use_logic')
def test_handler(mock_use_logic, mock_get_updates):
    # Setup the mock for tg_methods.get_updates
    mock_get_updates.return_value = mock_tg_response

    # Call the handler function with mocked event and context
    response = handler(mock_event, mock_context)

    # Assertions for tg_methods.get_updates
    mock_get_updates.assert_called_once()
    mock_use_logic.assert_called_once_with(mock_tg_response['result'][-1])

    # Assertions for the handler response
    assert response['statusCode'] == 200
    assert response['body'] == mock_event
    assert response['message'] == mock_tg_response['result'][-1]
