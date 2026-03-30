from datetime import date
from sqlalchemy import Integer, String, ForeignKey, Date, Boolean, Numeric, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"))
    delivery_date: Mapped[date] = mapped_column(Date)
    model_version: Mapped[str] = mapped_column(String(32))
    main_pick: Mapped[str] = mapped_column(String(32))
    alt_pick: Mapped[str | None] = mapped_column(String(32), nullable=True)
    confidence: Mapped[int] = mapped_column(Integer)
    score_total: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    score_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    explanation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
