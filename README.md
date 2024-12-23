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

### Шаг 3: Создать webhook (если еще нет)
- [ ] Открыть `index.py`
- [ ] Заменить `message = tg_methods.get_updates()['result'][-1]` на `json.loads(event['body'])`
- [ ] Создать webhook по [этой инструкции](https://yandex.cloud/ru/docs/tutorials/serverless/telegram-bot-serverless#function-bind-bot), отправив POST-запрос

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

## Идеи для To-Do:

- [ ] Добавить "отметить привычку"
- [ ] Добавить: "Совет — постарайтесь придумать такое поведение, которое сможете сделать при любой мотивации"
