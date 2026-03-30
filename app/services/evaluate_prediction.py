def evaluate_pick(pick: str | None, home_goals: int, away_goals: int) -> bool | None:
    if not pick:
        return None
    total_goals = home_goals + away_goals
    if pick == "HOME_WIN":
        return home_goals > away_goals
    if pick == "AWAY_WIN":
        return away_goals > home_goals
    if pick == "DRAW":
        return home_goals == away_goals
    if pick == "OVER_1_5":
        return total_goals > 1
    if pick == "UNDER_3_5":
        return total_goals < 4
    return None
