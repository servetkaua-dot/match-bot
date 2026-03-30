from __future__ import annotations

MENU_KEYBOARD = {
    "keyboard": [
        [{"text": "⚽ Футбол"}, {"text": "₿ BTC"}],
        [{"text": "🟢 Safe"}, {"text": "🟡 Medium"}, {"text": "🔴 Risky"}],
        [{"text": "🔄 Обновить"}, {"text": "📊 Статистика"}],
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False,
}


def welcome_text() -> str:
    return (
        "Премиум-бот готов.\n\n"
        "Кнопки:\n"
        "⚽ Футбол — топ футбольные сигналы\n"
        "₿ BTC — блок по Bitcoin\n"
        "🟢 Safe / 🟡 Medium / 🔴 Risky — разделение по риску\n"
        "🔄 Обновить — пересобрать футбол и показать свежие сигналы\n"
        "📊 Статистика — краткая сводка"
    )
