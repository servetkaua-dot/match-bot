from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import settings


@dataclass
class BTCSummary:
    symbol: str
    price: float
    change_percent_24h: float
    high_24h: float
    low_24h: float
    signal: str
    risk_label: str


async def get_btc_summary() -> BTCSummary:
    symbol = settings.btc_symbol
    async with httpx.AsyncClient(timeout=20) as client:
        ticker_resp = await client.get(
            "https://api.binance.com/api/v3/ticker/24hr",
            params={"symbol": symbol},
        )
        ticker_resp.raise_for_status()
        ticker = ticker_resp.json()

    price = float(ticker["lastPrice"])
    change_percent = float(ticker["priceChangePercent"])
    high_24h = float(ticker["highPrice"])
    low_24h = float(ticker["lowPrice"])

    if change_percent >= 2.5:
        signal = "Бычий"
        risk_label = "🟢 Safe"
    elif change_percent >= 0.5:
        signal = "Умеренно бычий"
        risk_label = "🟡 Medium"
    elif change_percent <= -2.5:
        signal = "Медвежий"
        risk_label = "🔴 Risky"
    elif change_percent <= -0.5:
        signal = "Умеренно медвежий"
        risk_label = "🟡 Medium"
    else:
        signal = "Нейтральный"
        risk_label = "🟢 Safe"

    return BTCSummary(
        symbol=symbol,
        price=price,
        change_percent_24h=change_percent,
        high_24h=high_24h,
        low_24h=low_24h,
        signal=signal,
        risk_label=risk_label,
    )


def format_btc_summary(item: BTCSummary) -> str:
    direction = "Рост" if item.change_percent_24h >= 0 else "Падение"
    return (
        f"₿ BTC блок\n\n"
        f"Символ: {item.symbol}\n"
        f"Цена: {item.price:,.2f}\n"
        f"24ч: {direction} {item.change_percent_24h:.2f}%\n"
        f"Диапазон 24ч: {item.low_24h:,.2f} — {item.high_24h:,.2f}\n"
        f"Сигнал: {item.signal}\n"
        f"Категория: {item.risk_label}"
    )
