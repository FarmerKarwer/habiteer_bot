import pytest
from unittest.mock import patch, MagicMock, Mock
import json

from tg_methods import get_updates

mock_tg_response = {"ok":True,"result":[{"update_id":325958251,
"message":{"message_id":28,"from":{"id":940985788,"is_bot":False,"first_name":"Artem","username":"morisdave","language_code":"en"},"chat":{"id":940985788,"first_name":"Artem","username":"morisdave","type":"private"},"date":1733228485,"text":"5"}},{"update_id":325958255,
"message":{"message_id":33,"from":{"id":940985788,"is_bot":False,"first_name":"Artem","username":"morisdave","language_code":"en"},"chat":{"id":940985788,"first_name":"Artem","username":"morisdave","type":"private"},"date":1733228517,"text":"something"}},{"update_id":325958257,
"message":{"message_id":36,"from":{"id":940985788,"is_bot":False,"first_name":"Artem","username":"morisdave","language_code":"en"},"chat":{"id":940985788,"first_name":"Artem","username":"morisdave","type":"private"},"date":1733228544,"text":"1. sfgsdfg\n2. sdfgsdfg\n3. sdfgsdfg\n4. sdfgdsfg\n5. sdfhgsdfgfds"}},{"update_id":325958276,
"callback_query":{"id":"4041503185848870858","from":{"id":940985788,"is_bot":False,"first_name":"Artem","username":"morisdave","language_code":"en"},"message":{"message_id":54,"from":{"id":7332437137,"is_bot":True,"first_name":"Habiteer_local","username":"habiteer_local_bot"},"chat":{"id":940985788,"first_name":"Artem","username":"morisdave","type":"private"},"date":1733232703,"text":"\u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e.\n\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043e\u0434\u0438\u043d \u0438\u0437 \u043f\u0443\u043d\u043a\u0442\u043e\u0432 \u043d\u0438\u0436\u0435","reply_markup":{"inline_keyboard":[[{"text":"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043f\u0440\u0438\u0432\u044b\u0447\u043a\u0443","callback_data":"scr_2"}],[{"text":"\u041c\u043e\u0438 \u043f\u0440\u0438\u0432\u044b\u0447\u043a\u0438","callback_data":"scr_3"}],[{"text":"\u041f\u043e\u0434\u043e\u0431\u0440\u0430\u0442\u044c \u043f\u0440\u0438\u0432\u044b\u0447\u043a\u0443","callback_data":"scr_4"}],[{"text":"\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430","callback_data":"plug"}],[{"text":"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438","callback_data":"scr_6"}]]},"has_protected_content":True},"chat_instance":"8667056629342611601","data":"scr_6"}}]}

mock_URL = f"https://api.telegram.org/botTG_TOKEN/"

@patch('requests.get')
def test_get_updates(mock_get):
	# Create a mock response object
	mock_response = Mock()
	# Dump to json string (feedback from get comes as json)
	mock_response.content = json.dumps(mock_tg_response)
	mock_response.status_code = 200

	URL = mock_URL

	mock_get.return_value = mock_response

	# Call the get_updates function
	response = get_updates()

	assert response == mock_tg_response
