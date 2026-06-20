"""Indexer factory.

Returns the configured metadata indexer, or None if none is configured (so the
app still runs and callers can degrade gracefully). TVDB is the default.
"""
from __future__ import annotations

from app.config import settings
from app.indexers.base import Indexer, IndexerEpisode, IndexerShow
from app.indexers.tvdb import TVDBIndexer

__all__ = ["Indexer", "IndexerEpisode", "IndexerShow", "get_indexer"]


def get_indexer() -> Indexer | None:
    if settings.tvdb_api_key:
        return TVDBIndexer()
    return None
