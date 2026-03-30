from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    league_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    league_name: Mapped[str] = mapped_column(String(120))
    season: Mapped[int | None] = mapped_column(Integer, nullable=True)
    kickoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    home_team: Mapped[str] = mapped_column(String(120))
    away_team: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(32), default="scheduled")
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
