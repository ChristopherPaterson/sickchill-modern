"""Show schemas."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.models.show import ShowStatus


class ShowBase(BaseModel):
    name: str
    quality: str = "HD"
    language: str = "en"
    paused: bool = False
    location: str | None = None


class ShowCreate(BaseModel):
    """Add a new show by external id. The backend fetches metadata from the indexer."""

    tvdb_id: int | None = None
    tmdb_id: int | None = None
    quality: str = "HD"
    language: str = "en"
    location: str | None = None


class ShowUpdate(BaseModel):
    quality: str | None = None
    language: str | None = None
    paused: bool | None = None
    location: str | None = None


class ShowOut(ShowBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tvdb_id: int | None
    tmdb_id: int | None
    imdb_id: str | None
    overview: str | None
    network: str | None
    status: ShowStatus
    poster_url: str | None


class ShowStats(BaseModel):
    total: int
    downloaded: int
    wanted: int
    snatched: int
