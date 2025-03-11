import os
import requests
import json

"""
There will be all the methods necessary for Telegram Bot
"""

TG_TOKEN=os.getenv('BOT_TOKEN')
URL = f"https://api.telegram.org/bot{TG_TOKEN}/"


# Sending Messages
def send_text_message(reply, chat_id, parse_mode='Markdown', disable_notification=None, 
    protect_content=None, reply_parameters=None, keyboard=None):
	data = {
		'text':reply,
		'chat_id':chat_id,
		'parse_mode':parse_mode,
		'disable_notification':disable_notification,
		'protect_content':protect_content,
		'reply_parameters':reply_parameters,
		'reply_markup': keyboard
	}
	url = URL+"sendMessage"
	response = requests.post(url, data=data)

def delete_message(message_id, chat_id):
	data = {
	'chat_id':chat_id,
	'message_id':message_id
	}
	url = URL+"deleteMessage"
	requests.post(url, data=data)

def answer_callback_query(callback_query_id):
	data = {"callback_query_id": callback_query_id}
	url = URL+"answerCallbackQuery"
	requests.post(url, data=data)

def send_picture():
	pass

def edit_message_reply_markup(chat_id, message_id, reply_markup):
	"""
	Edits the inline keyboard of a specific message.
	"""
	url = URL+"editMessageReplyMarkup"

	# Payload for the API request
	payload = {
		"chat_id": chat_id,
		"message_id": message_id,
		"reply_markup": json.dumps(reply_markup)
	}

	# Send the request
	response = requests.post(url, data=payload)

def send_invoice(chat_id, title, description, payload, provider_token, currency, prices, start_parameter=None,
                 provider_data=None, photo_url=None, photo_size=None, photo_width=None, photo_height=None,
                 need_name=None, need_phone_number=None, need_email=None, need_shipping_address=None, 
                 send_email_to_provider=None, is_flexible=None, keyboard=None):
    
    data = {
        'chat_id': chat_id,
        'title': title,
        'description': description,
        'payload': payload,
        'provider_token': provider_token,
        'currency': currency,
        'prices': json.dumps(prices),
        'start_parameter': start_parameter,
        'provider_data': provider_data,
        'photo_url': photo_url,
        'photo_size': photo_size,
        'photo_width': photo_width,
        'photo_height': photo_height,
        'need_name': need_name,
        'need_phone_number': need_phone_number,
        'need_email': need_email,
        'need_shipping_address': need_shipping_address,
        'send_email_to_provider': send_email_to_provider,
        'is_flexible': is_flexible,
		"reply_markup": keyboard
    }

    # Filtering out any None values
    data = {key: value for key, value in data.items() if value is not None}
    url = URL + "sendInvoice"
    response = requests.post(url, data=data)
    return response.json()

def confirm_pre_checkout_query(pre_checkout_query_id):
    """Confirms the payment request so the transaction can proceed."""
    url = URL + "answerPreCheckoutQuery"
    data = {"pre_checkout_query_id": pre_checkout_query_id, "ok": True}
    response = requests.post(url, data=data)
    return response.json()

# Utils
def get_updates(offset=None, timeout=None):
	url = URL+"getUpdates"
	params = {"offset": offset, "timeout": timeout}
	update_array = requests.get(url, params=params)
	return update_array.json()

if __name__ == "__main__":
    print(get_updates())
