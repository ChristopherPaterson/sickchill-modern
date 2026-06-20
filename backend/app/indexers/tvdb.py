"""TheTVDB v4 API client.

Implements the Indexer interface against the supported v4 API
(https://api4.thetvdb.com/v4), not the deprecated endpoint SickChill uses.

Auth flow: POST /login with the API key (and PIN for free-tier keys) returns a
bearer token valid ~1 month; we cache it. Defensive throughout: network/parse
errors are logged and surfaced as empty results rather than crashing callers.
"""
from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta

import httpx

from app.config import settings
from app.indexers.base import Indexer, IndexerEpisode, IndexerShow

logger = logging.getLogger(__name__)

BASE_URL = "https://api4.thetvdb.com/v4"
_TOKEN_TTL = timedelta(hours=24)  # token lives ~1 month; refresh well within that

# Module-level token cache, keyed by api_key.
_token_cache: dict[str, tuple[str, datetime]] = {}


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


class TVDBIndexer(Indexer):
    name = "tvdb"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        if not settings.tvdb_api_key:
            raise RuntimeError("TVDB API key not configured (set SCM_TVDB_API_KEY)")
        self.api_key = settings.tvdb_api_key
        self.pin = settings.tvdb_pin
        self._client = client or httpx.AsyncClient(base_url=BASE_URL, timeout=30)
        self._owns_client = client is None

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def _token(self) -> str:
        cached = _token_cache.get(self.api_key)
        if cached and cached[1] > datetime.now(UTC):
            return cached[0]

        payload: dict[str, str] = {"apikey": self.api_key}
        if self.pin:
            payload["pin"] = self.pin
        resp = await self._client.post("/login", json=payload)
        resp.raise_for_status()
        token = resp.json()["data"]["token"]
        _token_cache[self.api_key] = (token, datetime.now(UTC) + _TOKEN_TTL)
        return token

    async def _get(self, path: str, **params) -> dict:
        token = await self._token()
        resp = await self._client.get(path, params=params, headers={"Authorization": f"Bearer {token}"})
        resp.raise_for_status()
        return resp.json()

    async def search(self, term: str) -> list[IndexerShow]:
        try:
            data = await self._get("/search", query=term, type="series", limit=25)
        except (httpx.HTTPError, KeyError):
            logger.exception("TVDB search failed for %r", term)
            return []

        results: list[IndexerShow] = []
        for item in data.get("data", []):
            raw_id = item.get("tvdb_id") or item.get("id")
            if raw_id is None:
                continue
            # Search ids may arrive as "12345" or "series-12345".
            numeric = str(raw_id).removeprefix("series-")
            if not numeric.isdigit():
                continue
            remote_ids = item.get("remote_ids")
            imdb_id = remote_ids.get("IMDB") if isinstance(remote_ids, dict) else None
            results.append(
                IndexerShow(
                    indexer_id=int(numeric),
                    name=item.get("name") or "",
                    overview=item.get("overview"),
                    network=item.get("network"),
                    poster_url=item.get("image_url") or item.get("thumbnail"),
                    imdb_id=imdb_id,
                )
            )
        return results

    async def get_show(self, indexer_id: int) -> IndexerShow | None:
        try:
            extended = await self._get(f"/series/{indexer_id}/extended")
        except (httpx.HTTPError, KeyError):
            logger.exception("TVDB get_show failed for id %s", indexer_id)
            return None

        s = extended.get("data", {})
        imdb_id = None
        for remote in s.get("remoteIds") or []:
            if remote.get("sourceName") == "IMDB":
                imdb_id = remote.get("id")
                break

        show = IndexerShow(
            indexer_id=indexer_id,
            name=s.get("name", ""),
            overview=s.get("overview"),
            network=(s.get("latestNetwork") or {}).get("name"),
            poster_url=s.get("image"),
            imdb_id=imdb_id,
            episodes=await self._episodes(indexer_id),
        )
        return show

    async def _episodes(self, indexer_id: int) -> list[IndexerEpisode]:
        episodes: list[IndexerEpisode] = []
        page = 0
        while True:
            try:
                data = await self._get(f"/series/{indexer_id}/episodes/default", page=page)
            except (httpx.HTTPError, KeyError):
                logger.exception("TVDB episodes fetch failed for id %s page %s", indexer_id, page)
                break

            for ep in data.get("data", {}).get("episodes", []):
                season = ep.get("seasonNumber")
                number = ep.get("number")
                if season is None or number is None:
                    continue
                episodes.append(
                    IndexerEpisode(
                        season=season,
                        episode=number,
                        name=ep.get("name"),
                        overview=ep.get("overview"),
                        air_date=_parse_date(ep.get("aired")),
                    )
                )

            if not (data.get("links") or {}).get("next"):
                break
            page += 1
        return episodes
