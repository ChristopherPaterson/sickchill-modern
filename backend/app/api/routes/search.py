"""Indexer search routes: find shows to add."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/shows")
async def search_shows(q: str, _: CurrentUser):
    """Search the configured indexer for shows matching q."""
    # TODO: call app.indexers to search TVDB/TMDB and return IndexerShow results.
    return {"query": q, "results": []}
