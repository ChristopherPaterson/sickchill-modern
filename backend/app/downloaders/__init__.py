"""Download-client factory and opt-in send helper."""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.downloaders.base import DownloadClient
from app.downloaders.sabnzbd import SABnzbdClient
from app.services.settings_service import get_download_config

__all__ = ["DownloadClient", "get_download_client", "maybe_download"]

logger = logging.getLogger(__name__)


async def get_download_client(db: AsyncSession) -> DownloadClient | None:
    """Build the configured download client, or None if not configured."""
    cfg = await get_download_config(db)
    if not cfg.configured:
        return None
    return SABnzbdClient(url=cfg.url, api_key=cfg.api_key, category=cfg.category)


async def maybe_download(db: AsyncSession, download_url: str) -> bool | None:
    """Send a release to the download client only if downloads are enabled AND a
    client is configured. Returns:
        True  -> sent successfully
        False -> attempted but the client rejected/failed
        None  -> not attempted (downloads disabled or no client configured)
    Downloads are OFF by default, so this is a no-op until explicitly enabled.
    """
    cfg = await get_download_config(db)
    if not cfg.enabled or not cfg.configured:
        return None
    client = SABnzbdClient(url=cfg.url, api_key=cfg.api_key, category=cfg.category)
    try:
        ok = await client.add(download_url)
    finally:
        await client.close()
    return ok
