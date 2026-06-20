"""Episode routes: status updates and per-episode search trigger."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.models.episode import Episode
from app.schemas.common import Message
from app.schemas.episode import EpisodeOut, EpisodeStatusUpdate
from app.services import search_service

router = APIRouter(prefix="/episodes", tags=["episodes"])


async def _get_or_404(db, episode_id: int) -> Episode:
    episode = await db.get(Episode, episode_id)
    if episode is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    return episode


@router.patch("/{episode_id}/status", response_model=EpisodeOut)
async def set_status(episode_id: int, payload: EpisodeStatusUpdate, db: DbSession, _: CurrentUser):
    episode = await _get_or_404(db, episode_id)
    episode.status = payload.status
    await db.commit()
    await db.refresh(episode)
    return episode


@router.post("/{episode_id}/search", response_model=Message)
async def search_now(episode_id: int, db: DbSession, _: CurrentUser):
    episode = await _get_or_404(db, episode_id)
    results = await search_service.search_episode(db, episode)
    return Message(message=f"Search complete: {len(results)} result(s) found")
