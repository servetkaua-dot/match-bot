def calculate_profit(won: bool | None, stake: float) -> tuple[float | None, float | None]:
    if won is None:
        return None, None
    profit = stake * 0.9 if won else -stake
    roi = (profit / stake) * 100.0 if stake else None
    return round(profit, 2), round(roi, 2) if roi is not None else None
