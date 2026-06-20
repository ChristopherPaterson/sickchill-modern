"""Generic Newznab (usenet) / Torznab (torrent) provider.

Both speak the same Newznab API shape, so one implementation covers both. This is
the standard, stable integration point (Prowlarr/Jackett expose Torznab feeds),
which is far more maintainable than scraping individual tracker HTML.

API: GET {url}?t=tvsearch&apikey=KEY&q=...&season=..&ep=..&o=json
Results carry a title, a download link (.torrent / .nzb), and newznab attrs
(size, seeders for torznab).
"""
from __future__ import annotations

import logging

import httpx

from app.providers.base import Provider, SearchQuery, SearchResult

logger = logging.getLogger(__name__)


class NewznabProvider(Provider):
    def __init__(
        self,
        name: str,
        url: str,
        api_key: str | None = None,
        *,
        is_torrent: bool = True,
        min_seeders: int = 0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(client=client)
        self.name = name
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.is_public = not api_key
        self.is_torrent = is_torrent
        self.min_seeders = min_seeders
        self.enabled = True

    def _params(self, query: SearchQuery) -> dict[str, str | int]:
        params: dict[str, str | int] = {
            "t": "tvsearch",
            "q": query.show_name,
            "season": query.season,
            "ep": query.episode,
            "o": "json",
        }
        if self.api_key:
            params["apikey"] = self.api_key
        return params

    @staticmethod
    def _attrs(item: dict) -> dict[str, str]:
        """Flatten newznab attrs (list of {name,value} or @attributes) into a dict."""
        out: dict[str, str] = {}
        raw = item.get("attr") or item.get("torznab:attr") or item.get("newznab:attr") or []
        if isinstance(raw, dict):
            raw = [raw]
        for a in raw:
            attr = a.get("@attributes", a)
            name = attr.get("name")
            if name is not None:
                out[name] = attr.get("value")
        return out

    async def search(self, query: SearchQuery) -> list[SearchResult]:
        try:
            resp = await self.client.get(self.url, params=self._params(query))
            resp.raise_for_status()
            payload = resp.json()
        except (httpx.HTTPError, ValueError):
            logger.exception("provider %s search failed", self.name)
            return []

        # Newznab JSON nests items under channel.item (shapes vary across servers).
        channel = payload.get("channel", payload)
        items = channel.get("item", [])
        if isinstance(items, dict):
            items = [items]

        results: list[SearchResult] = []
        for item in items:
            try:
                attrs = self._attrs(item)
                seeders = int(attrs["seeders"]) if "seeders" in attrs else None
                if self.is_torrent and self.min_seeders and (seeders or 0) < self.min_seeders:
                    continue
                size = None
                if attrs.get("size"):
                    size = int(attrs["size"])
                elif isinstance(item.get("enclosure"), dict):
                    length = item["enclosure"].get("@attributes", {}).get("length")
                    size = int(length) if length else None

                link = item.get("link") or (item.get("enclosure", {}) or {}).get("@attributes", {}).get("url")
                title = item.get("title")
                if not title or not link:
                    continue

                results.append(
                    SearchResult(
                        title=title,
                        download_url=link,
                        provider=self.name,
                        seeders=seeders,
                        size=size,
                    )
                )
            except (KeyError, ValueError, TypeError):
                logger.warning("provider %s: skipped malformed item", self.name, exc_info=True)
                continue

        return results
