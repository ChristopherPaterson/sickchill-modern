"""App configuration routes (UI-editable settings stored in the DB)."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import Message
from app.services import settings_service as ss

router = APIRouter(prefix="/config", tags=["config"])


class IndexerConfigOut(BaseModel):
    configured: bool
    has_pin: bool
    language: str


class IndexerConfigIn(BaseModel):
    # Omit a field to leave it unchanged; send "" to clear it.
    api_key: str | None = None
    pin: str | None = None
    language: str | None = None


@router.get("/indexer", response_model=IndexerConfigOut)
async def get_indexer_config(db: DbSession, _: CurrentUser):
    """Report indexer config status. Never returns the API key itself."""
    creds = await ss.get_tvdb_credentials(db)
    return IndexerConfigOut(
        configured=bool(creds.api_key),
        has_pin=bool(creds.pin),
        language=creds.language,
    )


@router.put("/indexer", response_model=Message)
async def set_indexer_config(payload: IndexerConfigIn, db: DbSession, _: CurrentUser):
    if payload.api_key is not None:
        await ss.set_setting(db, ss.TVDB_API_KEY, payload.api_key or None)
    if payload.pin is not None:
        await ss.set_setting(db, ss.TVDB_PIN, payload.pin or None)
    if payload.language is not None:
        await ss.set_setting(db, ss.TVDB_LANGUAGE, payload.language or None)
    return Message(message="Indexer configuration saved")
