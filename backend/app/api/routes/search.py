"""Indexer search routes: find shows to add."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.deps import CurrentUser
from app.indexers import get_indexer


class ShowSearchResult(BaseModel):
    tvdb_id: int
    name: str
    overview: str | None = None
    network: str | None = None
    poster_url: str | None = None


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/shows", response_model=list[ShowSearchResult])
async def search_shows(q: str, _: CurrentUser):
    """Search the configured indexer for shows matching q."""
    indexer = get_indexer()
    if indexer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No metadata indexer configured. Set SCM_TVDB_API_KEY.",
        )
    try:
        results = await indexer.search(q)
    finally:
        await indexer.close()

    return [
        ShowSearchResult(
            tvdb_id=r.indexer_id,
            name=r.name,
            overview=r.overview,
            network=r.network,
            poster_url=r.poster_url,
        )
        for r in results
    ]
