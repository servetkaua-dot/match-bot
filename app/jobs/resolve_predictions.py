from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.clients.thesportsdb import TheSportsDBClient
from app.config import settings
from app.db import SessionLocal
from app.models.match import Match
from app.models.prediction import Prediction
from app.models.prediction_result import PredictionResult
from app.services.evaluate_prediction import evaluate_pick
from app.services.profit_service import calculate_profit


def _to_int(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _finished(event: dict) -> bool:
    status = (event.get("strStatus") or "").upper()
    if status in {"FT", "AET", "PEN", "AFTER ET", "AFTER PEN."}:
        return True
    return _to_int(event.get("intHomeScore")) is not None and _to_int(event.get("intAwayScore")) is not None


async def resolve_predictions() -> None:
    db = SessionLocal()
    client = TheSportsDBClient()
    try:
        rows = db.execute(
            select(Prediction, Match)
            .join(Match, Match.id == Prediction.match_id)
            .outerjoin(PredictionResult, PredictionResult.prediction_id == Prediction.id)
            .where(PredictionResult.id.is_(None))
        ).all()

        resolved = 0
        for prediction, match in rows:
            event = await client.get_event_by_id(match.external_id)
            if not event or not _finished(event):
                continue

            home_goals = _to_int(event.get("intHomeScore"))
            away_goals = _to_int(event.get("intAwayScore"))
            if home_goals is None or away_goals is None:
                continue

            main_result = evaluate_pick(prediction.main_pick, home_goals, away_goals)
            alt_result = evaluate_pick(prediction.alt_pick, home_goals, away_goals)
            profit, roi = calculate_profit(main_result, float(settings.default_stake))

            db.add(
                PredictionResult(
                    prediction_id=prediction.id,
                    match_status=(event.get("strStatus") or "FT")[:32],
                    home_goals=home_goals,
                    away_goals=away_goals,
                    main_pick_result=main_result,
                    alt_pick_result=alt_result,
                    resolved_market=prediction.main_pick,
                    settled_odds=1.90,
                    stake=settings.default_stake,
                    profit=profit,
                    roi_percent=roi,
                    raw_payload=event,
                )
            )
            resolved += 1

        db.commit()
        print(f"Resolved predictions: {resolved}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(resolve_predictions())
