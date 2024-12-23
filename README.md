## Инструкция: как загрузить бота в Yandex Cloud (не протестирована)
### Шаг 1: Поместить все файлы из папки `cache` в Object Storage

### Шаг 2: Загрузить файлы в ZIP-архив
Список файлов и папок в корневой директории:
- [ ] Все файлы из папки src (не саму папку)
- [ ] strings
- [ ] `requirements.txt`

### Шаг 3: Загрузить архив в облачную функцию методом "ZIP-архив"
- [ ] Прикрепить ZIP-архив
- [ ] Указать точку входа: `index.handler`

### Шаг 4: Изменить `index.py`
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

### Шаг 5: Изменить способ подключения к базе данных Yandex
- [ ] Открыть `database.py`
- [ ] Убрать эти строки: 
```
YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')

IAM = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', json={
    'yandexPassportOauthToken': YANDEX_TOKEN
}).json()
```
- [ ] Вместо `credentials=ydb.credentials.AccessTokenCredentials(f'Bearer {IAM['iamToken']}')` вставить `ydb.iam.MetadataUrlCredentials()`

### Шаг 6: Изменить импорты в `bot_logic.py`
- [ ] В константах путей файлов для кэша (CACHE_...) убрать `./cache/`
- [ ] Убрать из `from utils import (...)`: `update_user_value`, `get_cached_data`, `delete_user_records`, `save_data_to_cache`
- [ ] Эти же функции импортировать из `utils_yandex.py`

### Шаг 6_5: Создать webhook (если еще нет)
- [ ] Создать webhook по [этой инструкции](https://yandex.cloud/ru/docs/tutorials/serverless/telegram-bot-serverless#function-bind-bot), отправив POST-запрос

### Шаг 7: Убедиться, что все работает
- [ ] В ответе функции должен быть `"statusCode": 200`
- [ ] В сам бот должно прийти сообщение "Главное меню"
