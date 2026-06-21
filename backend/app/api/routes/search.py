"""Indexer search routes: find shows to add."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession
from app.indexers import get_indexer
from app.schemas.common import Message
from app.services import search_service


class ShowSearchResult(BaseModel):
    tvdb_id: int
    name: str
    overview: str | None = None
    network: str | None = None
    poster_url: str | None = None


class BacklogItem(BaseModel):
    episode_id: int
    show_id: int
    show_name: str
    season: int
    episode: int
    name: str | None
    air_date: date | None


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/backlog", response_model=list[BacklogItem])
async def list_backlog(db: DbSession, _: CurrentUser):
    """All wanted episodes awaiting a successful search."""
    return [
        BacklogItem(
            episode_id=ep.id,
            show_id=ep.show_id,
            show_name=show_name,
            season=ep.season,
            episode=ep.episode,
            name=ep.name,
            air_date=ep.air_date,
        )
        for ep, show_name in await search_service.list_wanted(db)
    ]


@router.post("/backlog", response_model=Message)
async def run_backlog(db: DbSession, _: CurrentUser):
    """Search and snatch every wanted episode now."""
    count = await search_service.backlog_search(db)
    return Message(message=f"Backlog search complete: {count} episode(s) snatched")


@router.get("/shows", response_model=list[ShowSearchResult])
async def search_shows(q: str, db: DbSession, _: CurrentUser):
    """Search the configured indexer for shows matching q."""
    indexer = await get_indexer(db)
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
