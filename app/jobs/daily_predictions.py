from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.clients.thesportsdb import TheSportsDBClient
from app.config import settings
from app.db import SessionLocal
from app.models.feature import MatchFeature
from app.models.match import Match
from app.models.prediction import Prediction
from app.services.build_feature import build_feature_from_fixture
from app.services.filter_predictions import filter_and_rank_predictions
from app.services.score_matches import score_match

MODEL_VERSION = "thesportsdb_smart_v2"
SOCCER_ONLY = "Soccer"


def _kickoff_local(date_str: str | None, time_str: str | None) -> tuple[datetime, str]:
    date_part = date_str or datetime.now().date().isoformat()
    time_part = (time_str or "12:00:00").split("+")[0].split("Z")[0]
    if len(time_part.split(":")) == 2:
        time_part += ":00"
    naive = datetime.fromisoformat(f"{date_part}T{time_part}")
    utc_dt = naive.replace(tzinfo=ZoneInfo("UTC"))
    local_dt = utc_dt.astimezone(ZoneInfo(settings.timezone))
    return utc_dt, local_dt.strftime("%H:%M")


async def run_daily_predictions() -> list[dict]:
    tz = ZoneInfo(settings.timezone)
    start_date = datetime.now(tz).date()
    client = TheSportsDBClient()

    all_events: list[dict] = []
    seen_ids: set[str] = set()
    for offset in range(settings.prediction_window_days):
        target_date = start_date + timedelta(days=offset)
        day_events = await client.get_events_by_date(target_date.isoformat())
        for item in day_events:
            event_id = str(item.get("idEvent") or "")
            if event_id and event_id not in seen_ids:
                seen_ids.add(event_id)
                all_events.append(item)

    db = SessionLocal()
    scored_matches: list[dict] = []

    try:
        for item in all_events:
            if (item.get("strSport") or "") != SOCCER_ONLY:
                continue
            if not item.get("strHomeTeam") or not item.get("strAwayTeam"):
                continue

            external_id = str(item.get("idEvent"))
            kickoff_at, kickoff_local = _kickoff_local(item.get("dateEvent"), item.get("strTime"))
            delivery_date = kickoff_at.astimezone(tz).date()

            existing_match = db.execute(select(Match).where(Match.external_id == external_id)).scalar_one_or_none()
            if existing_match is None:
                existing_match = Match(
                    external_id=external_id,
                    league_id=int(item.get("idLeague")) if item.get("idLeague") else None,
                    league_name=item.get("strLeague") or "Unknown",
                    season=None,
                    kickoff_at=kickoff_at,
                    home_team=item.get("strHomeTeam") or "Home",
                    away_team=item.get("strAwayTeam") or "Away",
                    status=(item.get("strStatus") or "scheduled")[:32],
                    raw_payload=item,
                )
                db.add(existing_match)
                db.flush()

            existing_feature = db.execute(select(MatchFeature).where(MatchFeature.match_id == existing_match.id)).scalar_one_or_none()
            if existing_feature is None:
                feature = await build_feature_from_fixture(item, client)
                feature.match_id = existing_match.id
                db.add(feature)
                db.flush()
            else:
                feature = existing_feature

            result = score_match(feature)
            scored_matches.append(
                {
                    "match_id": existing_match.id,
                    "delivery_date": delivery_date,
                    "match_title": f"{existing_match.home_team} — {existing_match.away_team}",
                    "league_name": existing_match.league_name,
                    "kickoff_local": kickoff_local,
                    "main_pick": result.main_pick,
                    "alt_pick": result.alt_pick,
                    "confidence": result.confidence,
                    "score_total": result.total_score,
                    "score_breakdown": result.breakdown,
                    "data_quality_score": float(feature.data_quality_score or 0),
                }
            )

        selected = filter_and_rank_predictions(
            scored_matches,
            limit=settings.prediction_limit,
            min_confidence=settings.min_confidence,
            min_data_quality=settings.min_data_quality,
        )

        for item in selected:
            exists = db.execute(
                select(Prediction).where(
                    Prediction.match_id == item["match_id"],
                    Prediction.delivery_date == item["delivery_date"],
                )
            ).scalar_one_or_none()
            if exists is None:
                db.add(
                    Prediction(
                        match_id=item["match_id"],
                        delivery_date=item["delivery_date"],
                        model_version=MODEL_VERSION,
                        main_pick=item["main_pick"],
                        alt_pick=item["alt_pick"],
                        confidence=item["confidence"],
                        score_total=item["score_total"],
                        score_breakdown=item["score_breakdown"],
                        explanation_text="Smart TheSportsDB rule-based prediction",
                        published=False,
                    )
                )

        db.commit()
        print(f"Saved predictions for {settings.prediction_window_days} day window: {len(selected)}")
        return selected
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_daily_predictions())
