"""Episode schemas."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.episode import EpisodeStatus


class EpisodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    show_id: int
    season: int
    episode: int
    name: str | None
    air_date: date | None
    status: EpisodeStatus
    quality: str | None


class EpisodeStatusUpdate(BaseModel):
    status: EpisodeStatus
