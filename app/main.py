from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from sqlalchemy import select

from app.config import settings
from app.db import SessionLocal
from app.models.match import Match
from app.models.prediction import Prediction
from app.scheduler import scheduler, start_scheduler
from app.services.stats_service import get_stats_summary
from app.jobs.resolve_predictions import resolve_predictions


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.scheduler_enabled:
        start_scheduler()
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)


app = FastAPI(title="Match Predictor Simple", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/predictions/tomorrow")
async def predictions_tomorrow() -> dict:
    target_date = (datetime.now(ZoneInfo(settings.timezone)) + timedelta(days=1)).date()
    db = SessionLocal()
    try:
        rows = db.execute(
            select(Prediction, Match)
            .join(Match, Match.id == Prediction.match_id)
            .where(Prediction.delivery_date == target_date)
            .order_by(Prediction.confidence.desc())
        ).all()
        items = []
        for prediction, match in rows:
            items.append(
                {
                    "match": f"{match.home_team} vs {match.away_team}",
                    "league": match.league_name,
                    "kickoff": match.kickoff_at.astimezone(ZoneInfo(settings.timezone)).isoformat(),
                    "main_pick": prediction.main_pick,
                    "alt_pick": prediction.alt_pick,
                    "confidence": prediction.confidence,
                }
            )
        return {"items": items}
    finally:
        db.close()


@app.get("/stats/summary")
async def stats_summary() -> dict:
    return get_stats_summary()


@app.post("/stats/resolve")
async def resolve_stats() -> dict:
    await resolve_predictions()
    return {"status": "ok"}
