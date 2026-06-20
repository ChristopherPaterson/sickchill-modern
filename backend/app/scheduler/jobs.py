"""Scheduled job bodies. Each opens its own DB session and delegates to a service.

Jobs must never let an exception escape: APScheduler would log it, but wrapping
here lets us add context and guarantees one bad tick does not kill future runs.
"""
from __future__ import annotations

import logging

from app.db.session import SessionLocal
from app.services import search_service

logger = logging.getLogger(__name__)


async def daily_search_job() -> None:
    try:
        async with SessionLocal() as db:
            count = await search_service.daily_search(db)
        logger.info("daily_search_job processed %d episodes", count)
    except Exception:
        logger.exception("daily_search_job failed")


async def backlog_search_job() -> None:
    try:
        # TODO: search wanted/missing back-catalogue episodes.
        logger.info("backlog_search_job tick (not yet implemented)")
    except Exception:
        logger.exception("backlog_search_job failed")


async def show_update_job() -> None:
    try:
        # TODO: refresh show + episode metadata from the indexer.
        logger.info("show_update_job tick (not yet implemented)")
    except Exception:
        logger.exception("show_update_job failed")
