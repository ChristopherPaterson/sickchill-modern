"""History model: a log of snatch / download / failure events."""
from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class HistoryAction(enum.StrEnum):
    snatched = "snatched"
    downloaded = "downloaded"
    subtitled = "subtitled"
    failed = "failed"


class HistoryEntry(Base, TimestampMixin):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    show_id: Mapped[int | None] = mapped_column(ForeignKey("shows.id", ondelete="SET NULL"), index=True)
    episode_id: Mapped[int | None] = mapped_column(ForeignKey("episodes.id", ondelete="SET NULL"), index=True)

    action: Mapped[HistoryAction] = mapped_column(Enum(HistoryAction), index=True)
    quality: Mapped[str | None] = mapped_column(String(50))
    provider: Mapped[str | None] = mapped_column(String(100))
    release_name: Mapped[str | None] = mapped_column(String(1000))
    season: Mapped[int | None] = mapped_column(Integer)
    episode: Mapped[int | None] = mapped_column(Integer)
