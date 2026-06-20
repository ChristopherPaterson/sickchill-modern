"""Provider registry: build provider instances from the DB configuration."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider import ProviderConfig, ProviderType
from app.providers.base import Provider
from app.providers.newznab import NewznabProvider


def _build(cfg: ProviderConfig) -> Provider:
    return NewznabProvider(
        name=cfg.name,
        url=cfg.url,
        api_key=cfg.api_key,
        is_torrent=cfg.type == ProviderType.torznab,
        min_seeders=cfg.min_seeders,
    )


async def enabled_providers(db: AsyncSession) -> list[Provider]:
    """Instantiate every enabled provider, highest priority first."""
    result = await db.execute(
        select(ProviderConfig)
        .where(ProviderConfig.enabled.is_(True))
        .order_by(ProviderConfig.priority.desc())
    )
    return [_build(cfg) for cfg in result.scalars().all()]
