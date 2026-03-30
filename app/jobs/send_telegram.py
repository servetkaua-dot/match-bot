from __future__ import annotations

import asyncio

from app.clients.telegram_client import TelegramClient
from app.services.football_premium import format_football_signals, get_signals_by_bucket
from app.services.telegram_menu import MENU_KEYBOARD


async def send_today_predictions() -> None:
    items = get_signals_by_bucket()
    text = format_football_signals(items, title="⚽ Футбольный блок")
    await TelegramClient().send_message(text, reply_markup=MENU_KEYBOARD)
    print(f"Sent to Telegram: {len(items)}")


if __name__ == "__main__":
    asyncio.run(send_today_predictions())
