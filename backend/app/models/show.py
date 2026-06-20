"""Show model: a tracked TV series."""
from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.episode import Episode


class ShowStatus(enum.StrEnum):
    continuing = "continuing"
    ended = "ended"
    paused = "paused"
    unknown = "unknown"


class Show(Base, TimestampMixin):
    __tablename__ = "shows"

    id: Mapped[int] = mapped_column(primary_key=True)

    # External identifiers
    tvdb_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    tmdb_id: Mapped[int | None] = mapped_column(Integer, index=True)
    imdb_id: Mapped[str | None] = mapped_column(String(20), index=True)

    name: Mapped[str] = mapped_column(String(500), index=True)
    overview: Mapped[str | None] = mapped_column(Text)
    network: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[ShowStatus] = mapped_column(Enum(ShowStatus), default=ShowStatus.unknown)

    # Local management
    location: Mapped[str | None] = mapped_column(String(1000))  # path on disk
    quality: Mapped[str] = mapped_column(String(50), default="HD")  # quality profile name
    paused: Mapped[bool] = mapped_column(default=False)
    language: Mapped[str] = mapped_column(String(10), default="en")
    poster_url: Mapped[str | None] = mapped_column(String(1000))

    episodes: Mapped[list[Episode]] = relationship(
        back_populates="show",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
