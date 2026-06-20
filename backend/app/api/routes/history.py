"""History routes."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.history import HistoryAction, HistoryEntry


class HistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    show_id: int | None
    action: HistoryAction
    provider: str | None
    release_name: str | None
    season: int | None
    episode: int | None


router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[HistoryOut])
async def list_history(db: DbSession, _: CurrentUser, limit: int = 100):
    result = await db.execute(select(HistoryEntry).order_by(HistoryEntry.created_at.desc()).limit(limit))
    return list(result.scalars().all())
