from sqlalchemy import Integer, String, ForeignKey, Boolean, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id", ondelete="CASCADE"), unique=True)
    match_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    home_goals: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_goals: Mapped[int | None] = mapped_column(Integer, nullable=True)
    main_pick_result: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    alt_pick_result: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    resolved_market: Mapped[str | None] = mapped_column(String(32), nullable=True)
    settled_odds: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    stake: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    profit: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    roi_percent: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
