"""Show service: all show/episode business logic lives here, not in route handlers.

This is the clean service layer SickChill never had. Routes call these functions;
the scheduler calls these functions. Logic exists in exactly one place.
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.episode import Episode, EpisodeStatus
from app.models.show import Show
from app.schemas.show import ShowCreate, ShowStats, ShowUpdate


async def list_shows(db: AsyncSession) -> list[Show]:
    result = await db.execute(select(Show).order_by(Show.name))
    return list(result.scalars().all())


async def get_show(db: AsyncSession, show_id: int) -> Show | None:
    return await db.get(Show, show_id)


async def create_show(db: AsyncSession, payload: ShowCreate) -> Show:
    # TODO: fetch metadata + episode list from the configured indexer using
    #   app.indexers, then populate episodes. For now create a bare record.
    show = Show(
        tvdb_id=payload.tvdb_id,
        tmdb_id=payload.tmdb_id,
        name=f"Show {payload.tvdb_id or payload.tmdb_id}",  # placeholder until indexer lookup
        quality=payload.quality,
        language=payload.language,
        location=payload.location,
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
