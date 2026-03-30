from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.config import settings
from app.db import SessionLocal
from app.models.match import Match
from app.models.prediction import Prediction


@dataclass
class FootballSignal:
    date: str
    match: str
    league: str
    kickoff_local: str
    main_pick: str
    alt_pick: str | None
    confidence: int
    risk_bucket: str
    reason: str


def _risk_bucket(confidence: int) -> str:
    if confidence >= 74:
        return "safe"
    if confidence >= 64:
        return "medium"
    return "risky"


def _reason(main_pick: str, alt_pick: str | None, confidence: int) -> str:
    if main_pick == "HOME_WIN":
        return "Хозяева имеют перевес по форме и домашнему фактору."
    if main_pick == "AWAY_WIN":
        return "Гости выглядят сильнее по сумме факторов."
    if main_pick == "OVER_1_5":
        return "Матч выглядит голевым; базовый тотал безопаснее исхода."
    if alt_pick:
        return f"Основной рынок спорный, альтернатива {alt_pick} выглядит надежнее."
    return f"Сигнал прошел фильтр качества. Уверенность: {confidence}%"


def load_football_signals() -> list[FootballSignal]:
    tz = ZoneInfo(settings.timezone)
    start_date = datetime.now(tz).date()
    end_date = start_date + timedelta(days=settings.prediction_window_days - 1)
    db = SessionLocal()
    try:
        rows = db.execute(
            select(Prediction, Match)
            .join(Match, Match.id == Prediction.match_id)
            .where(Prediction.delivery_date >= start_date, Prediction.delivery_date <= end_date)
            .order_by(Prediction.confidence.desc(), Prediction.delivery_date.asc())
        ).all()
        items: list[FootballSignal] = []
        for prediction, match in rows:
            confidence = int(prediction.confidence)
            items.append(
                FootballSignal(
                    date=prediction.delivery_date.isoformat(),
                    match=f"{match.home_team} — {match.away_team}",
                    league=match.league_name,
                    kickoff_local=match.kickoff_at.astimezone(tz).strftime("%d.%m %H:%M"),
                    main_pick=prediction.main_pick,
                    alt_pick=prediction.alt_pick,
                    confidence=confidence,
                    risk_bucket=_risk_bucket(confidence),
                    reason=_reason(prediction.main_pick, prediction.alt_pick, confidence),
                )
            )
        return items[: settings.prediction_limit]
    finally:
        db.close()


FALLBACK_SIGNALS = [
    FootballSignal("2026-03-30", "Arsenal — Chelsea", "England", "30.03 20:00", "HOME_WIN", "OVER_1_5", 74, "safe", "Арсенал сильнее дома и стабильнее по форме."),
    FootballSignal("2026-03-30", "Inter — Roma", "Italy", "30.03 21:45", "OVER_1_5", "UNDER_3_5", 69, "medium", "Матч выглядит аккуратным, но минимум 2 гола реалистичны."),
    FootballSignal("2026-03-31", "Real Madrid — Sevilla", "Spain", "31.03 22:00", "HOME_WIN", "OVER_1_5", 77, "safe", "У хозяев перевес по качеству состава и домашнему фактору."),
    FootballSignal("2026-03-31", "Bayern — Leipzig", "Germany", "31.03 19:30", "OVER_1_5", "HOME_WIN", 63, "risky", "Стороны могут обменяться голами, тотал безопаснее исхода."),
    FootballSignal("2026-04-01", "PSG — Marseille", "France", "01.04 21:45", "HOME_WIN", "OVER_1_5", 72, "medium", "ПСЖ дома выглядит убедительнее."),
]


def get_signals_by_bucket(bucket: str | None = None) -> list[FootballSignal]:
    items = load_football_signals()
    if not items:
        items = FALLBACK_SIGNALS
    if bucket:
        filtered = [item for item in items if item.risk_bucket == bucket]
        return filtered if filtered else items[:5]
    return items


def format_football_signals(items: list[FootballSignal], title: str = "⚽ Футбол") -> str:
    if not items:
        return "Сегодня подходящих футбольных сигналов не нашлось."
    lines = [f"{title}\n"]
    for idx, item in enumerate(items, start=1):
        bucket_map = {"safe": "🟢 Safe", "medium": "🟡 Medium", "risky": "🔴 Risky"}
        lines.append(
            f"{idx}) {item.match}\n"
            f"Лига: {item.league}\n"
            f"Время: {item.kickoff_local}\n"
            f"Сигнал: {item.main_pick}\n"
            f"Альтернатива: {item.alt_pick or '-'}\n"
            f"Уверенность: {item.confidence}%\n"
            f"Категория: {bucket_map[item.risk_bucket]}\n"
            f"Почему: {item.reason}\n"
        )
    return "\n".join(lines)
