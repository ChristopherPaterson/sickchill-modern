"""Indexer factory.

Returns the configured metadata indexer, or None if none is configured (so the
app still runs and callers can degrade gracefully). Credentials come from the DB
(UI-editable), falling back to env config. TVDB is the default.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.indexers.base import Indexer, IndexerEpisode, IndexerShow
from app.indexers.tvdb import TVDBIndexer
from app.services.settings_service import get_tvdb_credentials

__all__ = ["Indexer", "IndexerEpisode", "IndexerShow", "get_indexer"]


async def get_indexer(db: AsyncSession) -> Indexer | None:
    creds = await get_tvdb_credentials(db)
    if not creds.api_key:
        return None
    return TVDBIndexer(api_key=creds.api_key, pin=creds.pin, language=creds.language)
