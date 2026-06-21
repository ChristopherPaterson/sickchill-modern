"""Download-client interface.

A DownloadClient receives a release (an NZB URL for usenet, a torrent/magnet for
torrents) and hands it to the user's downloader. Implementations must never raise
on network errors: log and return a falsey result.
"""
from __future__ import annotations

import abc

import httpx


class DownloadClient(abc.ABC):
    name: str = "base"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(timeout=30)
        self._owns_client = client is None

    @abc.abstractmethod
    async def add(self, download_url: str, category: str | None = None) -> bool:
        """Send a release to the downloader. Returns True on success."""

    @abc.abstractmethod
    async def test(self) -> tuple[bool, str]:
        """Check connectivity/credentials. Returns (ok, message)."""

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()
