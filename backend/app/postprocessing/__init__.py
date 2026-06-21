"""Post-processing orchestration: read config, then file completed downloads.

These wrap the engine (processor.py) with config/credential lookup so both the
API routes and the scheduler job share one code path.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.downloaders.sabnzbd import SABnzbdClient
from app.postprocessing.processor import ProcessResult, find_video_file, process_directory, process_file
from app.services.settings_service import get_download_config, get_processing_config

__all__ = ["ProcessResult", "run_completed_downloads", "run_folder"]

logger = logging.getLogger(__name__)


async def run_folder(db: AsyncSession, path: str) -> list[ProcessResult]:
    """Manually process a folder of downloaded files."""
    cfg = await get_processing_config(db)
    if not cfg.configured:
        return [ProcessResult(path, "error", "No TV library root configured")]
    return await process_directory(db, path, cfg.library_root, cfg.method)


async def run_completed_downloads(db: AsyncSession) -> list[ProcessResult]:
    """File everything SABnzbd has finished downloading."""
    cfg = await get_processing_config(db)
    if not cfg.configured:
        return [ProcessResult("", "error", "No TV library root configured")]

    dl = await get_download_config(db)
    if not dl.configured:
        return [ProcessResult("", "error", "No download client configured")]

    sab = SABnzbdClient(url=dl.url, api_key=dl.api_key, category=dl.category)
    try:
        items = await sab.history()
    finally:
        await sab.close()

    results: list[ProcessResult] = []
    for item in items:
        storage = item.get("storage")
        name = item.get("name") or ""
        if not storage:
            continue
        video = await asyncio.to_thread(find_video_file, Path(storage))
        if video is None:
            results.append(ProcessResult(name, "no_file", f"No video file in {storage}"))
            continue
        results.append(await process_file(db, video, name or video.stem, cfg.library_root, cfg.method))
    return results
