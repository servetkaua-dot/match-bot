from sqlalchemy import text
from app.db import SessionLocal



def get_stats_summary() -> dict:
    db = SessionLocal()
    try:
        total_predictions = db.execute(text("SELECT COUNT(*) FROM predictions")).scalar() or 0
        row = db.execute(text("""
            SELECT COUNT(*) AS resolved_predictions,
                   SUM(CASE WHEN main_pick_result = 1 THEN 1 ELSE 0 END) AS won_predictions,
                   COALESCE(SUM(stake), 0) AS turnover,
                   COALESCE(SUM(profit), 0) AS profit
            FROM prediction_results
        """)).mappings().first()
        resolved_predictions = row["resolved_predictions"] or 0
        won_predictions = row["won_predictions"] or 0
        turnover = float(row["turnover"] or 0)
        profit = float(row["profit"] or 0)
        win_rate = round((won_predictions / resolved_predictions) * 100, 2) if resolved_predictions else 0.0
        roi = round((profit / turnover) * 100, 2) if turnover else 0.0
        return {
            "total_predictions": total_predictions,
            "resolved_predictions": resolved_predictions,
            "won_predictions": won_predictions,
            "win_rate": win_rate,
            "turnover": round(turnover, 2),
            "profit": round(profit, 2),
            "roi": roi,
        }
    finally:
        db.close()
