from __future__ import annotations

import asyncio
from typing import Any

from app.clients.telegram_client import TelegramClient
from app.config import settings
from app.jobs.daily_predictions import run_daily_predictions
from app.services.btc_service import format_btc_summary, get_btc_summary
from app.services.football_premium import format_football_signals, get_signals_by_bucket
from app.services.stats_service import get_stats_summary
from app.services.telegram_menu import MENU_KEYBOARD, welcome_text

COMMANDS = [
    {"command": "start", "description": "Открыть меню"},
    {"command": "football", "description": "Футбольные сигналы"},
    {"command": "btc", "description": "BTC блок"},
    {"command": "safe", "description": "Надежные сигналы"},
    {"command": "medium", "description": "Средний риск"},
    {"command": "risky", "description": "Рискованные сигналы"},
    {"command": "refresh", "description": "Обновить футбол"},
    {"command": "stats", "description": "Статистика"},
]


def build_stats_text() -> str:
    stats = get_stats_summary()
    return (
        "📊 Статистика\n\n"
        f"Всего прогнозов: {stats.get('total_predictions', 0)}\n"
        f"Решено: {stats.get('resolved_predictions', 0)}\n"
        f"Побед: {stats.get('won_predictions', 0)}\n"
        f"Win rate: {stats.get('win_rate', 0)}%\n"
        f"Profit: {stats.get('profit', 0)}\n"
        f"ROI: {stats.get('roi', 0)}%"
    )


async def handle_text(text: str, tg: TelegramClient, chat_id: int | str) -> None:
    normalized = (text or "").strip().lower()

    if normalized in {"/start", "/menu", "🏠 меню", "меню"}:
        await tg.send_message(welcome_text(), chat_id=chat_id, reply_markup=MENU_KEYBOARD)
        return

    if normalized in {"/football", "⚽ футбол"}:
        await tg.send_message(format_football_signals(get_signals_by_bucket(), "⚽ Футбол"), chat_id=chat_id, reply_markup=MENU_KEYBOARD)
        return

    if normalized in {"/safe", "🟢 safe"}:
        await tg.send_message(format_football_signals(get_signals_by_bucket("safe"), "🟢 Safe сигналы"), chat_id=chat_id, reply_markup=MENU_KEYBOARD)
        return

    if normalized in {"/medium", "🟡 medium"}:
        await tg.send_message(format_football_signals(get_signals_by_bucket("medium"), "🟡 Medium сигналы"), chat_id=chat_id, reply_markup=MENU_KEYBOARD)
        return

    if normalized in {"/risky", "🔴 risky"}:
        await tg.send_message(format_football_signals(get_signals_by_bucket("risky"), "🔴 Risky сигналы"), chat_id=chat_id, reply_markup=MENU_KEYBOARD)
        return

    if normalized in {"/btc", "₿ btc"}:
        btc = await get_btc_summary()
        await tg.send_message(format_btc_summary(btc), chat_id=chat_id, reply_markup=MENU_KEYBOARD)
        return

    if normalized in {"/refresh", "🔄 обновить"}:
        await run_daily_predictions()
        await tg.send_message("Футбольный блок обновлен.", chat_id=chat_id, reply_markup=MENU_KEYBOARD)
        await tg.send_message(format_football_signals(get_signals_by_bucket(), "⚽ Свежие сигналы"), chat_id=chat_id, reply_markup=MENU_KEYBOARD)
        return

    if normalized in {"/stats", "📊 статистика"}:
        await tg.send_message(build_stats_text(), chat_id=chat_id, reply_markup=MENU_KEYBOARD)
        return

    await tg.send_message("Не понял команду. Нажми кнопку внизу 👇", chat_id=chat_id, reply_markup=MENU_KEYBOARD)


async def main() -> None:
    tg = TelegramClient()
    await tg.set_commands(COMMANDS)
    offset: int | None = None
    print("Bot loop started")
    while True:
        try:
            updates = await tg.get_updates(offset=offset, timeout=settings.bot_poll_interval_sec)
            for upd in updates:
                offset = upd["update_id"] + 1
                message: dict[str, Any] | None = upd.get("message")
                if not message:
                    continue
                text = message.get("text") or ""
                chat_id = message["chat"]["id"]
                await handle_text(text, tg, chat_id)
        except Exception as exc:
            print(f"bot_loop error: {exc}")
            await asyncio.sleep(settings.bot_loop_sleep_sec)


if __name__ == "__main__":
    asyncio.run(main())
