"""Episode model."""
from __future__ import annotations

import enum
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.show import Show


class EpisodeStatus(enum.StrEnum):
    unaired = "unaired"
    wanted = "wanted"
    snatched = "snatched"
    downloaded = "downloaded"
    archived = "archived"
    skipped = "skipped"
    ignored = "ignored"
    failed = "failed"


class Episode(Base, TimestampMixin):
    __tablename__ = "episodes"
    __table_args__ = (UniqueConstraint("show_id", "season", "episode", name="uq_show_season_episode"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    show_id: Mapped[int] = mapped_column(ForeignKey("shows.id", ondelete="CASCADE"), index=True)

    season: Mapped[int] = mapped_column(Integer)
    episode: Mapped[int] = mapped_column(Integer)
    name: Mapped[str | None] = mapped_column(String(500))
    overview: Mapped[str | None] = mapped_column(Text)
    air_date: Mapped[date | None] = mapped_column(Date, index=True)

    status: Mapped[EpisodeStatus] = mapped_column(Enum(EpisodeStatus), default=EpisodeStatus.unaired, index=True)
    quality: Mapped[str | None] = mapped_column(String(50))
    location: Mapped[str | None] = mapped_column(String(1000))  # downloaded file path
    release_name: Mapped[str | None] = mapped_column(String(1000))

    show: Mapped[Show] = relationship(back_populates="episodes")
