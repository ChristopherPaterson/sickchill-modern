"""SABnzbd download client.

Uses the SABnzbd JSON API: {url}/api?mode=...&apikey=...&output=json
  - addurl: queue an NZB by URL (what a Newznab result gives us)
  - queue:  used as a credential/connectivity check
"""
from __future__ import annotations

import logging

import httpx

from app.downloaders.base import DownloadClient

logger = logging.getLogger(__name__)


class SABnzbdClient(DownloadClient):
    name = "sabnzbd"

    def __init__(
        self,
        url: str,
        api_key: str,
        category: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(client=client)
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.category = category

    async def _call(self, params: dict[str, str]) -> dict:
        params = {**params, "apikey": self.api_key, "output": "json"}
        resp = await self._client.get(f"{self.url}/api", params=params)
        resp.raise_for_status()
        return resp.json()

    async def add(self, download_url: str, category: str | None = None) -> bool:
        try:
            data = await self._call({
                "mode": "addurl",
                "name": download_url,
                "cat": category or self.category or "",
            })
        except (httpx.HTTPError, ValueError):
            logger.exception("SABnzbd addurl failed")
            return False
        if not data.get("status"):
            logger.error("SABnzbd rejected the NZB: %s", data.get("error", data))
            return False
        return True

    async def history(self) -> list[dict]:
        """Completed downloads (for post-processing). Each item has name, storage
        (the path to the downloaded files), category and status."""
        try:
            data = await self._call({"mode": "history", "limit": "50"})
        except (httpx.HTTPError, ValueError):
            logger.exception("SABnzbd history fetch failed")
            return []
        slots = (data.get("history") or {}).get("slots") or []
        return [s for s in slots if (s.get("status") == "Completed")]

    async def test(self) -> tuple[bool, str]:
        try:
            data = await self._call({"mode": "queue", "limit": "0"})
        except httpx.HTTPError as exc:
            return False, f"Connection failed: {exc}"
        except ValueError:
            return False, "Unexpected (non-JSON) response from SABnzbd"
        if data.get("error"):
            return False, str(data["error"])  # e.g. "API Key Incorrect"
        if "queue" not in data:
            return False, "Unexpected response from SABnzbd"
        return True, "Connected to SABnzbd"
