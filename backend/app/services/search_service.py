"""Search service: orchestrate providers, rank results, snatch the best."""
from __future__ import annotations

import asyncio
import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.downloaders import maybe_download
from app.models.episode import Episode, EpisodeStatus
from app.models.history import HistoryAction, HistoryEntry
from app.models.show import Show
from app.providers.base import SearchQuery, SearchResult
from app.providers.quality import parse_release
from app.providers.registry import enabled_providers

logger = logging.getLogger(__name__)


def _score(result: SearchResult) -> tuple[int, int]:
    """Rank key: higher quality first, then more seeders. Quality parsed from the
    release title if the provider did not supply it."""
    quality = parse_release(result.title).quality
    return (int(quality), result.seeders or 0)


def rank_results(results: list[SearchResult]) -> list[SearchResult]:
    """Best release first."""
    return sorted(results, key=_score, reverse=True)


async def find_results(db: AsyncSession, episode: Episode) -> list[SearchResult]:
    """Search all enabled providers concurrently for one episode, ranked best-first."""
    show = await episode.awaitable_attrs.show
    query = SearchQuery(
        show_name=show.name,
        season=episode.season,
        episode=episode.episode,
        quality=show.quality,
    )

    providers = await enabled_providers(db)
    if not providers:
        logger.info(
            "no providers enabled; skipping search for %s S%02dE%02d",
            show.name, episode.season, episode.episode,
        )
        return []

    try:
        outcomes = await asyncio.gather(
            *(p.search(query) for p in providers),
            return_exceptions=True,
        )
    finally:
        await asyncio.gather(*(p.close() for p in providers), return_exceptions=True)

    results: list[SearchResult] = []
    for provider, outcome in zip(providers, outcomes, strict=True):
        if isinstance(outcome, BaseException):
            logger.error("provider %s raised: %s", provider.name, outcome)
            continue
        results.extend(outcome)

    return rank_results(results)


async def snatch_episode(db: AsyncSession, episode: Episode) -> SearchResult | None:
    """Search, pick the best result, mark the episode snatched and log history.

    Returns the chosen result, or None if nothing was found. The actual handoff
    to a download client is the next engine piece (see TODO).
    """
    results = await find_results(db, episode)
    if not results:
        return None

    best = results[0]
    parsed = parse_release(best.title)

    # Hand off to the download client if downloads are enabled (off by default).
    # None = not attempted, True = sent, False = client rejected it.
    sent = await maybe_download(db, best.download_url)

    episode.status = EpisodeStatus.snatched
    episode.quality = parsed.quality.name
    episode.release_name = best.title
    db.add(
        HistoryEntry(
            show_id=episode.show_id,
            episode_id=episode.id,
            action=HistoryAction.snatched,
            quality=parsed.quality.name,
            provider=best.provider,
            release_name=best.title,
            season=episode.season,
            episode=episode.episode,
        )
    )
    await db.commit()

    logger.info(
        "snatched %s S%02dE%02d: %s (download %s)",
        best.provider, episode.season, episode.episode, best.title,
        {True: "sent", False: "FAILED to send", None: "disabled/not configured"}[sent],
    )
    return best


async def _snatch_all(db: AsyncSession, episodes: list[Episode]) -> int:
    snatched = 0
    for episode in episodes:
        if await snatch_episode(db, episode):
            snatched += 1
    return snatched


async def daily_search(db: AsyncSession) -> int:
    """Find and snatch wanted episodes that have aired. Returns count snatched."""
    today = date.today()
    result = await db.execute(
        select(Episode).where(
            Episode.status == EpisodeStatus.wanted,
            Episode.air_date.is_not(None),
            Episode.air_date <= today,
        )
    )
    wanted = list(result.scalars().all())
    snatched = await _snatch_all(db, wanted)
    logger.info("daily_search: %d/%d aired wanted episodes snatched", snatched, len(wanted))
    return snatched


async def backlog_search(db: AsyncSession) -> int:
    """Search and snatch every wanted episode, regardless of air date."""
    result = await db.execute(select(Episode).where(Episode.status == EpisodeStatus.wanted))
    wanted = list(result.scalars().all())
    snatched = await _snatch_all(db, wanted)
    logger.info("backlog_search: %d/%d wanted episodes snatched", snatched, len(wanted))
    return snatched


async def search_show_wanted(db: AsyncSession, show_id: int) -> int:
    """Search and snatch all wanted episodes for one show."""
    result = await db.execute(
        select(Episode).where(Episode.show_id == show_id, Episode.status == EpisodeStatus.wanted)
    )
    wanted = list(result.scalars().all())
    return await _snatch_all(db, wanted)


async def list_wanted(db: AsyncSession) -> list[tuple[Episode, str]]:
    """Wanted episodes joined with their show name, for the backlog overview."""
    rows = await db.execute(
        select(Episode, Show.name)
        .join(Show, Episode.show_id == Show.id)
        .where(Episode.status == EpisodeStatus.wanted)
        .order_by(Show.name, Episode.season, Episode.episode)
    )
    return [(ep, name) for ep, name in rows.all()]
