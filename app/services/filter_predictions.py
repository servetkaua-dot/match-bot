def _safe_float(value, default=0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def compute_composite_rank(item: dict) -> float:
    confidence = int(item.get("confidence", 0))
    data_quality = _safe_float(item.get("data_quality_score"), 0)
    score_total = abs(_safe_float(item.get("score_total"), 0))
    return round(confidence * 0.45 + data_quality * 0.35 + score_total * 1.10, 2)


def filter_and_rank_predictions(
    scored_matches: list[dict],
    limit: int = 10,
    min_confidence: int = 58,
    min_data_quality: float = 35.0,
) -> list[dict]:
    approved = []
    fallback = []
    for item in scored_matches:
        item["composite_rank"] = compute_composite_rank(item)
        fallback.append(item)
        if int(item.get("confidence", 0)) < min_confidence:
            continue
        if _safe_float(item.get("data_quality_score"), 0) < min_data_quality:
            continue
        approved.append(item)

    approved.sort(key=lambda x: (x["composite_rank"], x["confidence"]), reverse=True)
    if approved:
        return approved[:limit]

    fallback.sort(key=lambda x: (x["composite_rank"], x["confidence"]), reverse=True)
    return fallback[:limit]
