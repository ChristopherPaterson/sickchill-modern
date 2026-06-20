"""Provider interface.

A Provider searches an indexer/tracker for releases of an episode. This is the
single most maintenance-heavy area of any app like this, so it is deliberately a
small, well-defined contract: implement search() and return SearchResult objects.

Implementations should log failures (never silently swallow them, which was
SickChill's biggest invisible-failure bug) and be defensive about upstream HTML
changes.
"""
from __future__ import annotations

import abc
import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SearchResult:
    title: str
    download_url: str
    provider: str
    seeders: int | None = None
    leechers: int | None = None
    size: int | None = None  # bytes
    quality: str | None = None


@dataclass(slots=True)
class SearchQuery:
    show_name: str
    season: int
    episode: int
    quality: str | None = None


class Provider(abc.ABC):
    """Base class for all search providers."""

    name: str = "base"
    enabled: bool = False
    is_public: bool = True

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30, follow_redirects=True)
        return self._client

    @abc.abstractmethod
    async def search(self, query: SearchQuery) -> list[SearchResult]:
        """Search the provider for the given episode. Must not raise on upstream
        errors: log and return an empty list instead."""
        raise NotImplementedError

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
