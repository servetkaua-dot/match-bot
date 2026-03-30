# Match Predictor Premium

## Что добавлено
- меню-кнопки в Telegram
- один бот для футбола и BTC
- разделение футбольных сигналов: Safe / Medium / Risky
- polling loop для команд `/start`, `/football`, `/btc`, `/safe`, `/medium`, `/risky`, `/refresh`, `/stats`
- fallback-футбол, если API не вернул матчи

## Быстрый старт
1. Скопируй `.env.example` в `.env`
2. Заполни `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`
3. Создай и активируй venv
4. Установи зависимости: `pip install -r requirements`
5. Создай БД: `python -m app.init_db`
6. Собери футбол: `python -m app.jobs.daily_predictions`
7. Отправь футбол: `python -m app.jobs.send_telegram`
8. Для интерактивного меню запусти: `python -m app.jobs.bot_loop`

## Кнопки
- ⚽ Футбол
- ₿ BTC
- 🟢 Safe
- 🟡 Medium
- 🔴 Risky
- 🔄 Обновить
- 📊 Статистика
