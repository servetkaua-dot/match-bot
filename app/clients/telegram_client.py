from __future__ import annotations

from typing import Any

import httpx

from app.config import settings


class TelegramClient:
    def __init__(self) -> None:
        if not settings.telegram_bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is empty in .env")
        self.base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}"

    async def send_message(
        self,
        text: str,
        chat_id: str | int | None = None,
        reply_markup: dict[str, Any] | None = None,
        parse_mode: str | None = None,
    ) -> dict[str, Any]:
        target_chat = chat_id or settings.telegram_chat_id
        if not target_chat:
            raise RuntimeError("TELEGRAM_CHAT_ID is empty in .env")
        payload: dict[str, Any] = {"chat_id": target_chat, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        if parse_mode:
            payload["parse_mode"] = parse_mode
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self.base_url}/sendMessage", json=payload)
            response.raise_for_status()
            return response.json()

    async def get_updates(self, offset: int | None = None, timeout: int = 20) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            payload["offset"] = offset
        async with httpx.AsyncClient(timeout=timeout + 10) as client:
            response = await client.get(f"{self.base_url}/getUpdates", params=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("result") or []

    async def answer_callback_query(self, callback_query_id: str, text: str | None = None) -> None:
        payload: dict[str, Any] = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self.base_url}/answerCallbackQuery", json=payload)
            response.raise_for_status()

    async def set_commands(self, commands: list[dict[str, str]]) -> None:
        payload = {"commands": commands}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self.base_url}/setMyCommands", json=payload)
            response.raise_for_status()
