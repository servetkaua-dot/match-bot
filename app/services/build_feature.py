from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.models.feature import MatchFeature


def _to_decimal(value: Any):
    if value is None:
        return None
    return Decimal(str(round(float(value), 2)))


def _to_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_status(event: dict) -> str:
    return (event.get("strStatus") or "").upper()


def _is_finished(event: dict) -> bool:
    status = _parse_status(event)
    if status in {"FT", "AET", "PEN", "AFTER ET", "AFTER PEN."}:
        return True
    return _to_int(event.get("intHomeScore")) is not None and _to_int(event.get("intAwayScore")) is not None


def _result_points_for_team(event: dict, team_name: str) -> int | None:
    home = event.get("strHomeTeam")
    away = event.get("strAwayTeam")
    hs = _to_int(event.get("intHomeScore"))
    as_ = _to_int(event.get("intAwayScore"))
    if hs is None or as_ is None:
        return None
    if team_name == home:
        if hs > as_:
            return 3
        if hs == as_:
            return 1
        return 0
    if team_name == away:
        if as_ > hs:
            return 3
        if hs == as_:
            return 1
        return 0
    return None


def _recent_team_stats(events: list[dict], team_name: str) -> dict:
    finished = [e for e in events if _is_finished(e)]
    finished = finished[:5]
    if not finished:
        return {
            "form_points": None,
            "goals_for_avg": None,
            "goals_against_avg": None,
            "home_ppg": None,
            "away_ppg": None,
        }

    points = 0
    gf = 0
    ga = 0
    home_points = 0
    home_played = 0
    away_points = 0
    away_played = 0

    for event in finished:
        home = event.get("strHomeTeam")
        away = event.get("strAwayTeam")
        hs = _to_int(event.get("intHomeScore")) or 0
        as_ = _to_int(event.get("intAwayScore")) or 0
        p = _result_points_for_team(event, team_name) or 0
        points += p
        if team_name == home:
            gf += hs
            ga += as_
            home_played += 1
            home_points += p
        elif team_name == away:
            gf += as_
            ga += hs
            away_played += 1
            away_points += p

    count = len(finished)
    return {
        "form_points": float(points),
        "goals_for_avg": gf / count if count else None,
        "goals_against_avg": ga / count if count else None,
        "home_ppg": home_points / home_played if home_played else None,
        "away_ppg": away_points / away_played if away_played else None,
    }


def _extract_position(table: list[dict], team_name: str) -> int | None:
    for row in table:
        if (row.get("strTeam") or "").strip().lower() == (team_name or "").strip().lower():
            for key in ("intRank", "intPosition", "intRankPosition"):
                pos = _to_int(row.get(key))
                if pos is not None:
                    return pos
    return None


def _compute_h2h(home_events: list[dict], home_team: str, away_team: str) -> tuple[int | None, int | None, int | None]:
    relevant = []
    for e in home_events:
        teams = {(e.get("strHomeTeam") or "").strip().lower(), (e.get("strAwayTeam") or "").strip().lower()}
        if teams == {home_team.strip().lower(), away_team.strip().lower()} and _is_finished(e):
            relevant.append(e)
        if len(relevant) >= 5:
            break
    if not relevant:
        return None, None, None

    home_wins = draws = away_wins = 0
    for e in relevant:
        hs = _to_int(e.get("intHomeScore")) or 0
        as_ = _to_int(e.get("intAwayScore")) or 0
        eh = e.get("strHomeTeam")
        ea = e.get("strAwayTeam")
        if hs == as_:
            draws += 1
        elif eh == home_team and ea == away_team:
            if hs > as_:
                home_wins += 1
            else:
                away_wins += 1
        elif eh == away_team and ea == home_team:
            if hs > as_:
                away_wins += 1
            else:
                home_wins += 1
    return home_wins, draws, away_wins


def _quality_score(home: dict, away: dict, home_pos: int | None, away_pos: int | None, h2h: tuple[int | None, int | None, int | None]) -> float:
    score = 0.0
    if home_pos is not None:
        score += 10
    if away_pos is not None:
        score += 10
    for info in (home, away):
        if info.get("form_points") is not None:
            score += 15
        if info.get("goals_for_avg") is not None and info.get("goals_against_avg") is not None:
            score += 10
    if home.get("home_ppg") is not None:
        score += 10
    if away.get("away_ppg") is not None:
        score += 10
    if all(v is not None for v in h2h):
        score += 10
    return min(score, 100.0)


async def build_feature_from_fixture(fixture: dict, api_client) -> MatchFeature:
    home_team = fixture.get("strHomeTeam", "Home")
    away_team = fixture.get("strAwayTeam", "Away")
    home_team_id = fixture.get("idHomeTeam")
    away_team_id = fixture.get("idAwayTeam")
    league_id = fixture.get("idLeague")
    season = fixture.get("strSeason")

    home_last = await api_client.get_team_last_events(home_team_id) if home_team_id else []
    away_last = await api_client.get_team_last_events(away_team_id) if away_team_id else []
    table = await api_client.get_league_table(league_id, season) if league_id else []

    home = _recent_team_stats(home_last, home_team)
    away = _recent_team_stats(away_last, away_team)
    home_pos = _extract_position(table, home_team)
    away_pos = _extract_position(table, away_team)
    h2h_home, h2h_draws, h2h_away = _compute_h2h(home_last, home_team, away_team)
    quality = _quality_score(home, away, home_pos, away_pos, (h2h_home, h2h_draws, h2h_away))

    return MatchFeature(
        match_id=0,
        home_form_points=_to_decimal(home.get("form_points")),
        away_form_points=_to_decimal(away.get("form_points")),
        home_table_pos=home_pos,
        away_table_pos=away_pos,
        home_goals_avg=_to_decimal(home.get("goals_for_avg")),
        away_goals_avg=_to_decimal(away.get("goals_for_avg")),
        home_conceded_avg=_to_decimal(home.get("goals_against_avg")),
        away_conceded_avg=_to_decimal(away.get("goals_against_avg")),
        home_home_form=_to_decimal(home.get("home_ppg")),
        away_away_form=_to_decimal(away.get("away_ppg")),
        h2h_home_wins=h2h_home,
        h2h_draws=h2h_draws,
        h2h_away_wins=h2h_away,
        data_quality_score=_to_decimal(quality),
        raw_payload={"home_last": home_last, "away_last": away_last, "table": table},
    )
