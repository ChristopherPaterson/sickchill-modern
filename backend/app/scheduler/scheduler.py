"""Background scheduler using APScheduler's asyncio scheduler.

Replaces SickChill's hand-rolled threading.Scheduler. Jobs run on the same event
loop as the API, so they share the async DB engine and session factory safely.
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.scheduler import jobs

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    scheduler.add_job(
        jobs.daily_search_job,
        "interval",
        minutes=settings.daily_search_interval,
        id="daily_search",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.add_job(
        jobs.backlog_search_job,
        "interval",
        minutes=settings.backlog_search_interval,
        id="backlog_search",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.add_job(
        jobs.show_update_job,
        "interval",
        minutes=settings.show_update_interval,
        id="show_update",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.add_job(
        jobs.post_process_job,
        "interval",
        minutes=settings.post_process_interval,
        id="post_process",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.start()
    logger.info("scheduler started with %d jobs", len(scheduler.get_jobs()))


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
