"""Show routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import Message
from app.schemas.episode import EpisodeOut
from app.schemas.show import ShowCreate, ShowListItem, ShowOut, ShowStats, ShowUpdate
from app.services import search_service, show_service

router = APIRouter(prefix="/shows", tags=["shows"])


@router.get("", response_model=list[ShowListItem])
async def list_shows(db: DbSession, _: CurrentUser):
    return await show_service.list_shows_overview(db)


@router.post("", response_model=ShowOut, status_code=status.HTTP_201_CREATED)
async def add_show(payload: ShowCreate, db: DbSession, _: CurrentUser):
    return await show_service.create_show(db, payload)


async def _get_or_404(db, show_id: int):
    show = await show_service.get_show(db, show_id)
    if show is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    return show


@router.get("/{show_id}", response_model=ShowOut)
async def get_show(show_id: int, db: DbSession, _: CurrentUser):
    return await _get_or_404(db, show_id)


@router.patch("/{show_id}", response_model=ShowOut)
async def update_show(show_id: int, payload: ShowUpdate, db: DbSession, _: CurrentUser):
    show = await _get_or_404(db, show_id)
    return await show_service.update_show(db, show, payload)


@router.delete("/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(show_id: int, db: DbSession, _: CurrentUser):
    show = await _get_or_404(db, show_id)
    await show_service.delete_show(db, show)


@router.get("/{show_id}/episodes", response_model=list[EpisodeOut])
async def list_episodes(show_id: int, db: DbSession, _: CurrentUser):
    await _get_or_404(db, show_id)
    return await show_service.list_episodes(db, show_id)


@router.get("/{show_id}/stats", response_model=ShowStats)
async def get_stats(show_id: int, db: DbSession, _: CurrentUser):
    await _get_or_404(db, show_id)
    return await show_service.show_stats(db, show_id)


@router.post("/{show_id}/search-wanted", response_model=Message)
async def search_wanted(show_id: int, db: DbSession, _: CurrentUser):
    """Search and snatch all wanted episodes for this show."""
    await _get_or_404(db, show_id)
    count = await search_service.search_show_wanted(db, show_id)
    return Message(message=f"Snatched {count} wanted episode(s)")
