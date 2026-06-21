"""Runtime settings service.

Reads/writes the Setting key/value table, with fallback to env-driven defaults in
app.config. DB values take precedence so the UI can override env configuration.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings as env_settings
from app.models.setting import Setting

# Setting keys
TVDB_API_KEY = "tvdb_api_key"
TVDB_PIN = "tvdb_pin"
TVDB_LANGUAGE = "tvdb_language"

SAB_URL = "sab_url"
SAB_API_KEY = "sab_api_key"
SAB_CATEGORY = "sab_category"
DOWNLOAD_ENABLED = "download_enabled"

TV_LIBRARY_ROOT = "tv_library_root"
PROCESSING_ENABLED = "processing_enabled"
PROCESSING_METHOD = "processing_method"  # move | copy | hardlink


async def get_setting(db: AsyncSession, key: str) -> str | None:
    row = await db.get(Setting, key)
    return row.value if row else None


async def set_setting(db: AsyncSession, key: str, value: str | None) -> None:
    row = await db.get(Setting, key)
    if row is None:
        db.add(Setting(key=key, value=value))
    else:
        row.value = value
    await db.commit()


@dataclass(slots=True)
class TVDBCredentials:
    api_key: str | None
    pin: str | None
    language: str


async def get_tvdb_credentials(db: AsyncSession) -> TVDBCredentials:
    """DB settings override env config."""
    return TVDBCredentials(
        api_key=await get_setting(db, TVDB_API_KEY) or env_settings.tvdb_api_key,
        pin=await get_setting(db, TVDB_PIN) or env_settings.tvdb_pin,
        language=await get_setting(db, TVDB_LANGUAGE) or env_settings.tvdb_language,
    )


@dataclass(slots=True)
class DownloadConfig:
    enabled: bool
    url: str | None
    api_key: str | None
    category: str | None

    @property
    def configured(self) -> bool:
        return bool(self.url and self.api_key)


async def get_download_config(db: AsyncSession) -> DownloadConfig:
    enabled = (await get_setting(db, DOWNLOAD_ENABLED)) == "true"
    return DownloadConfig(
        enabled=enabled,
        url=await get_setting(db, SAB_URL),
        api_key=await get_setting(db, SAB_API_KEY),
        category=await get_setting(db, SAB_CATEGORY),
    )


@dataclass(slots=True)
class ProcessingConfig:
    enabled: bool
    library_root: str | None
    method: str  # move | copy | hardlink

    @property
    def configured(self) -> bool:
        return bool(self.library_root)


async def get_processing_config(db: AsyncSession) -> ProcessingConfig:
    enabled = (await get_setting(db, PROCESSING_ENABLED)) == "true"
    return ProcessingConfig(
        enabled=enabled,
        library_root=await get_setting(db, TV_LIBRARY_ROOT),
        method=(await get_setting(db, PROCESSING_METHOD)) or "move",
    )
