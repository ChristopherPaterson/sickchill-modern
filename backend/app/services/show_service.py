"""Show service: all show/episode business logic lives here, not in route handlers.

This is the clean service layer SickChill never had. Routes call these functions;
the scheduler calls these functions. Logic exists in exactly one place.
"""
from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.indexers import get_indexer
from app.indexers.base import IndexerShow
from app.models.episode import Episode, EpisodeStatus
from app.models.show import Show, ShowStatus
from app.schemas.show import ShowCreate, ShowStats, ShowUpdate

logger = logging.getLogger(__name__)


async def list_shows(db: AsyncSession) -> list[Show]:
    result = await db.execute(select(Show).order_by(Show.name))
    return list(result.scalars().all())


async def get_show(db: AsyncSession, show_id: int) -> Show | None:
    return await db.get(Show, show_id)


def _map_status(value: str | None) -> ShowStatus:
    v = (value or "").lower()
    if "continuing" in v or "returning" in v:
        return ShowStatus.continuing
    if "ended" in v:
        return ShowStatus.ended
    return ShowStatus.unknown


async def create_show(db: AsyncSession, payload: ShowCreate) -> Show:
    """Add a show, fetching real metadata + episodes from the indexer.

    Falls back to a bare record if no indexer is configured or the lookup fails,
    so the operation never hard-errors purely due to indexer availability.
    """
    meta: IndexerShow | None = None
    indexer = await get_indexer(db)
    if indexer is not None and payload.tvdb_id is not None:
        try:
            meta = await indexer.get_show(payload.tvdb_id)
        except Exception:
            logger.exception("indexer lookup failed for tvdb_id=%s", payload.tvdb_id)
        finally:
            await indexer.close()

    show = Show(
        tvdb_id=payload.tvdb_id,
        tmdb_id=payload.tmdb_id,
        name=meta.name if meta else f"Show {payload.tvdb_id or payload.tmdb_id}",
        overview=meta.overview if meta else None,
        network=meta.network if meta else None,
        imdb_id=meta.imdb_id if meta else None,
        poster_url=meta.poster_url if meta else None,
        status=_map_status(None),
        quality=payload.quality,
        language=payload.language,
        location=payload.location,
    )

    if meta:
        today = date.today()
        for ep in meta.episodes:
            aired = ep.air_date
            status = EpisodeStatus.unaired if (aired is None or aired > today) else EpisodeStatus.skipped
            show.episodes.append(
                Episode(
                    season=ep.season,
                    episode=ep.episode,
                    name=ep.name,
                    overview=ep.overview,
                    air_date=aired,
                    status=status,
                )
            )

    db.add(show)
    await db.commit()
    await db.refresh(show)
    return show


async def update_show(db: AsyncSession, show: Show, payload: ShowUpdate) -> Show:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(show, field, value)
    await db.commit()
    await db.refresh(show)
    return show


async def delete_show(db: AsyncSession, show: Show) -> None:
    await db.delete(show)
    await db.commit()


async def list_episodes(db: AsyncSession, show_id: int) -> list[Episode]:
    result = await db.execute(
        select(Episode).where(Episode.show_id == show_id).order_by(Episode.season, Episode.episode)
    )
    return list(result.scalars().all())


async def show_stats(db: AsyncSession, show_id: int) -> ShowStats:
    async def count(status: EpisodeStatus | None) -> int:
        stmt = select(func.count()).select_from(Episode).where(Episode.show_id == show_id)
        if status is not None:
            stmt = stmt.where(Episode.status == status)
        return (await db.execute(stmt)).scalar_one()

    return ShowStats(
        total=await count(None),
        downloaded=await count(EpisodeStatus.downloaded),
        wanted=await count(EpisodeStatus.wanted),
        snatched=await count(EpisodeStatus.snatched),
    )
