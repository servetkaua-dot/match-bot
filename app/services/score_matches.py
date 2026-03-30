from dataclasses import dataclass


@dataclass
class ScoreResult:
    main_pick: str
    alt_pick: str
    confidence: int
    total_score: float
    breakdown: dict



def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))



def score_match(feature) -> ScoreResult:
    form_edge = float((feature.home_form_points or 0) - (feature.away_form_points or 0))
    home_away_edge = float((feature.home_home_form or 0) - (feature.away_away_form or 0))
    table_edge = float((feature.away_table_pos or 0) - (feature.home_table_pos or 0)) if feature.home_table_pos and feature.away_table_pos else 0.0
    goals_edge = float((feature.home_goals_avg or 0) - (feature.away_conceded_avg or 0))
    h2h_edge = float((feature.h2h_home_wins or 0) - (feature.h2h_away_wins or 0)) if feature.h2h_home_wins is not None and feature.h2h_away_wins is not None else 0.0

    form_score = _clamp(form_edge * 4, -20, 20)
    home_away_score = _clamp(home_away_edge * 4, -20, 20)
    table_score = _clamp(table_edge * 1.5, -15, 15)
    goals_score = _clamp(goals_edge * 8, -10, 10)
    h2h_score = _clamp(h2h_edge * 3, -10, 10)

    total = form_score + home_away_score + table_score + goals_score + h2h_score

    if total >= 18:
        main_pick = "HOME_WIN"
    elif total <= -18:
        main_pick = "AWAY_WIN"
    else:
        main_pick = "OVER_1_5"

    avg_total_goals = float((feature.home_goals_avg or 0) + (feature.away_goals_avg or 0))
    alt_pick = "OVER_1_5" if avg_total_goals >= 2.2 else "UNDER_3_5"
    confidence = int(_clamp(58 + abs(total) * 0.9 + float(feature.data_quality_score or 0) * 0.15, 55, 82))

    return ScoreResult(
        main_pick=main_pick,
        alt_pick=alt_pick,
        confidence=confidence,
        total_score=round(total, 2),
        breakdown={
            "form": round(form_score, 2),
            "home_away": round(home_away_score, 2),
            "table": round(table_score, 2),
            "goals": round(goals_score, 2),
            "h2h": round(h2h_score, 2),
        },
    )
