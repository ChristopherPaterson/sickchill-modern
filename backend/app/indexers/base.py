"""Indexer interface.

An Indexer provides show/episode metadata (TVDB, TMDB, TVMaze). Providers find
releases; indexers describe the shows. Implement lookup() and get_episodes().
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class IndexerEpisode:
    season: int
    episode: int
    name: str | None = None
    overview: str | None = None
    air_date: date | None = None


@dataclass(slots=True)
class IndexerShow:
    indexer_id: int
    name: str
    overview: str | None = None
    network: str | None = None
    poster_url: str | None = None
    imdb_id: str | None = None
    episodes: list[IndexerEpisode] = field(default_factory=list)


class Indexer(abc.ABC):
    name: str = "base"

    @abc.abstractmethod
    async def search(self, term: str) -> list[IndexerShow]:
        """Search for shows by name."""

    @abc.abstractmethod
    async def get_show(self, indexer_id: int) -> IndexerShow | None:
        """Fetch full metadata + episode list for a show."""
