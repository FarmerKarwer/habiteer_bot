## Инструкция: как загрузить бота в Yandex Cloud (не протестирована)
### Шаг 1: Создать папки
Названия папок:
- [ ] `cache`
- [ ] `strings`

### Шаг 2: Загрузить файлы
Список файлов в корневой директории:
- [ ] `index.py`
- [ ] `bot_logic.py`
- [ ] `database.py`
- [ ] `recommender.py`
- [ ] `tg_methods.py`
- [ ] `utils.py`
- [ ] `requirements.txt`

В папку `cache` подгрузить файлы:
- [ ] `callback_history.json`
- [ ] `picking_habit.json`
- [ ] `updating_habit.json`

В папку `strings` подгрузить файлы:
- [ ] `buttons.json`
- [ ] `motivational_messages.json`
- [ ] `premade_habits.json`
- [ ] `replies.json`
- [ ] `triggers.json`

### Шаг 3: Создать webhook
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
