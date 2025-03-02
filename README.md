## Инструкция: как загрузить бота в Yandex Cloud
### Шаг 1: Загрузить файлы в ZIP-архив
Список файлов и папок в корневой директории:
- [ ] Все файлы из папки `src`
- [ ] `requirements.txt`

### Шаг 2: Загрузить архив в облачную функцию методом "ZIP-архив"
- [ ] Прикрепить ZIP-архив
- [ ] Указать точку входа: `index.handler`

### Шаг 3: Изменить `index.py`
Вот, какой код нужно оставить:

```
import json
from bot_logic import use_logic

def handler(event, context):
	message = json.loads(event['body'])
	use_logic(message)	
	return {
	'statusCode':200,
	'body':event,
	'message':message
	}
```

### Шаг 4: Изменить способ подключения к базе данных Yandex
- [ ] Открыть `database.py`
- [ ] Убрать эти строки: 
```
YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')

IAM = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', json={
    'yandexPassportOauthToken': YANDEX_TOKEN
}).json()
```
- [ ] Вместо `credentials=ydb.credentials.AccessTokenCredentials(f'Bearer {IAM['iamToken']}')` вставить `ydb.iam.MetadataUrlCredentials()`

### Шаг 5: Убрать из requirements.txt `pytest` и `python-dotenv`, убрать `from dotenv import load_dotenv` и `load_dotenv()` из всех файлов

### Шаг 6: Убрать из `config.py` начало пути `src/`, а остальное оставить

### Шаг 7: Убедиться, что все работает
- [ ] В ответе функции должен быть `"statusCode": 200`
- [ ] В сам бот должно прийти сообщение "Главное меню"

### Шаг бонусный: Создать webhook (если еще нет)
- [ ] Создать webhook по [этой инструкции](https://yandex.cloud/ru/docs/tutorials/serverless/telegram-bot-serverless#function-bind-bot), отправив POST-запрос
