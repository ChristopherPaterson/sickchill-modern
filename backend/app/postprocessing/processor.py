"""Post-processing engine: match a downloaded release to a show/episode and file
it into the library (rename + move/copy/hardlink), then update the episode.

Pure helpers (normalise, find_video_file, file ops, release parsing) are kept
separate from DB work so they can be unit-tested with temp dirs and no database.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from guessit import guessit
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.episode import Episode, EpisodeStatus
from app.models.history import HistoryAction, HistoryEntry
from app.models.show import Show
from app.postprocessing.namer import episode_path
from app.providers.quality import parse_release

logger = logging.getLogger(__name__)

VIDEO_EXTS = {".mkv", ".mp4", ".avi", ".m4v", ".mov", ".wmv", ".mpg", ".mpeg", ".ts", ".m2ts"}


@dataclass(slots=True)
class ProcessResult:
    release: str
    status: str  # filed | skipped | no_match | no_file | error
    message: str
    destination: str | None = None


def normalise(name: str) -> str:
    """Normalise a show title for matching: lowercase, alphanumerics only."""
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def find_video_file(directory: Path) -> Path | None:
    """Largest video file under a directory (the actual episode, not samples)."""
    best: Path | None = None
    best_size = -1
    for p in directory.rglob("*"):
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS:
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if size > best_size:
                best, best_size = p, size
    return best


def parse_release_name(name: str) -> tuple[str | None, int | None, int | None]:
    """Extract (title, season, episode) from a release name via guessit."""
    info = guessit(name)
    title = info.get("title")
    season = info.get("season")
    episode = info.get("episode")
    if isinstance(season, list):
        season = season[0] if season else None
    if isinstance(episode, list):
        episode = episode[0] if episode else None
    return title, season, episode


def _do_file_op(src: Path, dest: Path, method: str) -> None:
    """Blocking file operation (run via asyncio.to_thread)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if method == "copy":
        shutil.copy2(src, dest)
    elif method == "hardlink":
        try:
            os.link(src, dest)
        except OSError:
            shutil.copy2(src, dest)  # cross-device: fall back to copy
    else:  # move (default)
        shutil.move(str(src), str(dest))


async def _show_by_title(db: AsyncSession, title: str) -> Show | None:
    shows = (await db.execute(select(Show))).scalars().all()
    return {normalise(s.name): s for s in shows}.get(normalise(title))


async def process_file(
    db: AsyncSession,
    src_file: Path,
    release_title: str,
    library_root: str,
    method: str,
) -> ProcessResult:
    """File one downloaded video into the library and update its episode."""
    title, season, episode = parse_release_name(release_title)
    if not title or season is None or episode is None:
        return ProcessResult(release_title, "no_match", "Could not parse show/season/episode")

    show = await _show_by_title(db, title)
    if show is None:
        return ProcessResult(release_title, "no_match", f"No show matched '{title}'")

    ep = (
        await db.execute(
            select(Episode).where(
                Episode.show_id == show.id,
                Episode.season == season,
                Episode.episode == episode,
            )
        )
    ).scalar_one_or_none()

    dest = episode_path(library_root, show.name, season, episode, ep.name if ep else None, src_file.suffix)
    if await asyncio.to_thread(dest.exists):
        return ProcessResult(release_title, "skipped", f"Already in library: {dest.name}", str(dest))

    try:
        await asyncio.to_thread(_do_file_op, src_file, dest, method)
    except OSError as exc:
        logger.exception("post-processing file op failed for %s", release_title)
        return ProcessResult(release_title, "error", str(exc))

    if ep is not None:
        parsed = parse_release(release_title)
        ep.status = EpisodeStatus.downloaded
        ep.location = str(dest)
        ep.quality = parsed.quality.name
        db.add(
            HistoryEntry(
                show_id=show.id,
                episode_id=ep.id,
                action=HistoryAction.downloaded,
                quality=parsed.quality.name,
                provider="post-processing",
                release_name=release_title,
                season=season,
                episode=episode,
            )
        )
        await db.commit()

    return ProcessResult(release_title, "filed", f"Filed to {dest}", str(dest))


def _scan_videos(path: str) -> list[Path] | None:
    """Blocking directory scan (run via asyncio.to_thread). None = path missing."""
    root = Path(path)
    if not root.exists():
        return None
    return [f for f in sorted(root.rglob("*")) if f.is_file() and f.suffix.lower() in VIDEO_EXTS]


async def process_directory(
    db: AsyncSession, path: str, library_root: str, method: str
) -> list[ProcessResult]:
    """Process every video file under a directory."""
    files = await asyncio.to_thread(_scan_videos, path)
    if files is None:
        return [ProcessResult(path, "error", "Path does not exist")]

    results: list[ProcessResult] = []
    for f in files:
        results.append(await process_file(db, f, f.stem, library_root, method))
    if not results:
        results.append(ProcessResult(path, "no_file", "No video files found"))
    return results
