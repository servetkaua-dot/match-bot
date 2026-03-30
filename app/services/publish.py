from app.config import settings
from app.clients.telegram_client import TelegramClient


async def publish_to_telegram(items: list[dict]) -> None:
    if not items:
        await TelegramClient().send_message(
            "Сегодня подходящих прогнозов не нашлось. Попробую снова при следующем запуске."
        )
        return

    lines = [f"Прогнозы на {settings.prediction_window_days} дня:\n"]
    for idx, item in enumerate(items[: settings.prediction_limit], start=1):
        lines.append(
            f"{idx}. {item['date']} | {item['match_title']}\n"
            f"Турнир: {item['league_name']}\n"
            f"Время: {item['kickoff_local']}\n"
            f"Основной прогноз: {item['main_pick']}\n"
            f"Альтернатива: {item['alt_pick']}\n"
            f"Уверенность: {item['confidence']}%\n"
        )
    await TelegramClient().send_message("\n".join(lines))
