"""Search service: orchestrate providers to find releases for wanted episodes."""
from __future__ import annotations

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.episode import Episode, EpisodeStatus
from app.providers.base import SearchQuery, SearchResult
from app.providers.registry import enabled_providers

logger = logging.getLogger(__name__)


async def search_episode(db: AsyncSession, episode: Episode) -> list[SearchResult]:
    """Search all enabled providers concurrently for one episode."""
    show = await episode.awaitable_attrs.show
    query = SearchQuery(
        show_name=show.name,
        season=episode.season,
        episode=episode.episode,
        quality=show.quality,
    )

    providers = enabled_providers()
    if not providers:
        logger.info("no providers enabled; skipping search for %s S%02dE%02d",
                    show.name, episode.season, episode.episode)
        return []

    results_per_provider = await asyncio.gather(
        *(p.search(query) for p in providers),
        return_exceptions=True,
    )

    results: list[SearchResult] = []
    for provider, outcome in zip(providers, results_per_provider, strict=True):
        if isinstance(outcome, BaseException):
            logger.error("provider %s raised: %s", provider.name, outcome)
            continue
        results.extend(outcome)

    # TODO: rank results (quality, seeders, preferred words) and pick the best.
    return results


async def daily_search(db: AsyncSession) -> int:
    """Find and snatch newly aired wanted episodes. Returns count processed."""
    # TODO: query wanted episodes whose air_date <= today, search, snatch best result,
    # hand off to the download client, and record a HistoryEntry.
    _ = EpisodeStatus  # referenced by the real implementation
    logger.info("daily_search tick (not yet implemented)")
    return 0
