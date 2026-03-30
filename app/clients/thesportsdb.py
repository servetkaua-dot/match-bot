from __future__ import annotations

import httpx
from app.config import settings


class TheSportsDBClient:
    def __init__(self) -> None:
        self.base_url = settings.thesportsdb_base_url.rstrip("/")
        self.api_key = settings.thesportsdb_api_key or "123"

    async def _get(self, endpoint: str, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{self.base_url}/{self.api_key}/{endpoint}", params=params)
            response.raise_for_status()
            try:
                return response.json()
            except Exception:
                return {}

    async def get_events_by_date(self, date_str: str) -> list[dict]:
        data = await self._get("eventsday.php", {"d": date_str, "s": "Soccer"})
        return data.get("events") or []

    async def get_event_by_id(self, event_id: str | int) -> dict | None:
        data = await self._get("lookupevent.php", {"id": event_id})
        events = data.get("events") or []
        return events[0] if events else None

    async def get_team_last_events(self, team_id: str | int) -> list[dict]:
        data = await self._get("eventslast.php", {"id": team_id})
        return data.get("results") or []

    async def get_league_table(self, league_id: str | int, season: str | None = None) -> list[dict]:
        params = {"l": league_id}
        if season:
            params["s"] = season
        data = await self._get("lookuptable.php", params)
        return data.get("table") or []
