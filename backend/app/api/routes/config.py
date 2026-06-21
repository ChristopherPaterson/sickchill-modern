"""App configuration routes (UI-editable settings stored in the DB)."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession
from app.downloaders.sabnzbd import SABnzbdClient
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


class DownloadConfigOut(BaseModel):
    configured: bool
    enabled: bool
    url: str | None
    category: str | None
    # api_key intentionally omitted (secret).


class DownloadConfigIn(BaseModel):
    # Omit a field to leave it unchanged; send "" to clear it.
    url: str | None = None
    api_key: str | None = None
    category: str | None = None
    enabled: bool | None = None


@router.get("/download", response_model=DownloadConfigOut)
async def get_download_config(db: DbSession, _: CurrentUser):
    cfg = await ss.get_download_config(db)
    return DownloadConfigOut(
        configured=cfg.configured,
        enabled=cfg.enabled,
        url=cfg.url,
        category=cfg.category,
    )


@router.put("/download", response_model=Message)
async def set_download_config(payload: DownloadConfigIn, db: DbSession, _: CurrentUser):
    if payload.url is not None:
        await ss.set_setting(db, ss.SAB_URL, payload.url or None)
    if payload.api_key is not None:
        await ss.set_setting(db, ss.SAB_API_KEY, payload.api_key or None)
    if payload.category is not None:
        await ss.set_setting(db, ss.SAB_CATEGORY, payload.category or None)
    if payload.enabled is not None:
        await ss.set_setting(db, ss.DOWNLOAD_ENABLED, "true" if payload.enabled else "false")
    return Message(message="Download client configuration saved")


@router.post("/download/test", response_model=Message)
async def test_download_config(db: DbSession, _: CurrentUser):
    """Test connectivity to the saved SABnzbd config."""
    cfg = await ss.get_download_config(db)
    if not cfg.configured:
        return Message(message="Not configured: set the SABnzbd URL and API key first")
    client = SABnzbdClient(url=cfg.url, api_key=cfg.api_key, category=cfg.category)
    try:
        ok, message = await client.test()
    finally:
        await client.close()
    return Message(message=message if ok else f"Test failed: {message}")
