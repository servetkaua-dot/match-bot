from sqlalchemy import Integer, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class MatchFeature(Base):
    __tablename__ = "match_features"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), unique=True)

    home_form_points: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    away_form_points: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    home_table_pos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_table_pos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_goals_avg: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    away_goals_avg: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    home_conceded_avg: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    away_conceded_avg: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    home_home_form: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    away_away_form: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    h2h_home_wins: Mapped[int | None] = mapped_column(Integer, nullable=True)
    h2h_draws: Mapped[int | None] = mapped_column(Integer, nullable=True)
    h2h_away_wins: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_quality_score: Mapped[float | None] = mapped_column(Numeric(6, 2), default=0)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
