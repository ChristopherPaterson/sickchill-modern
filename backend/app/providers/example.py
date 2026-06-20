"""Example provider showing the contract. Disabled by default.

Copy this file to implement a real provider. The key rules:
  - never raise on a network/parse error; log and return []
  - parse defensively, upstream HTML/JSON changes constantly
"""
from __future__ import annotations

import logging

from app.providers.base import Provider, SearchQuery, SearchResult

logger = logging.getLogger(__name__)


class ExampleProvider(Provider):
    name = "example"
    enabled = False
    is_public = True

    async def search(self, query: SearchQuery) -> list[SearchResult]:
        try:
            # TODO: build the real request for your indexer, e.g.
            #   resp = await self.client.get(url, params=...)
            #   resp.raise_for_status()
            #   parse resp into SearchResult objects
            logger.debug(
                "ExampleProvider.search called for %s S%02dE%02d",
                query.show_name, query.season, query.episode,
            )
            return []
        except Exception:  # noqa: BLE001  defensive: providers must never crash the search loop
            logger.exception("provider %s failed for query %r", self.name, query)
            return []
