"""One-off importer: load an old SickChill sickchill.db into SickChill Modern.

Display-only and deliberately safe:
  - never imports file locations (location stays NULL) -> no path is ever touched
  - downgrades any WANTED episode to SKIPPED -> the scheduler has nothing to act on
  - marks every imported show paused
  - clears configured providers -> searches return nothing

Usage:
    SCM_DATA_DIR=~/.sickchill-modern python -m scripts.import_sickchill /path/to/sickchill.db

Run with the API server stopped to avoid SQLite write contention.
"""
from __future__ import annotations

import asyncio
import sqlite3
import sys
from datetime import date, datetime

from sqlalchemy import delete

from app.db.session import SessionLocal, init_db
from app.models.episode import Episode, EpisodeStatus
from app.models.history import HistoryAction, HistoryEntry
from app.models.provider import ProviderConfig
from app.models.show import Show, ShowStatus

# SickChill base status code (status % 100) -> our EpisodeStatus.
# WANTED (3) is intentionally mapped to SKIPPED so nothing gets searched.
EP_STATUS = {
    1: EpisodeStatus.unaired,
    2: EpisodeStatus.snatched,
    3: EpisodeStatus.skipped,   # was WANTED, downgraded for safety
    4: EpisodeStatus.downloaded,
    5: EpisodeStatus.skipped,
    6: EpisodeStatus.archived,
    7: EpisodeStatus.ignored,
    9: EpisodeStatus.snatched,
    10: EpisodeStatus.downloaded,  # SUBTITLED
    11: EpisodeStatus.failed,
    12: EpisodeStatus.snatched,
}

HIST_ACTION = {
    2: HistoryAction.snatched,
    4: HistoryAction.downloaded,
    9: HistoryAction.snatched,
    10: HistoryAction.subtitled,
    11: HistoryAction.failed,
    12: HistoryAction.snatched,
}

# SickChill quality bit (status // 100) -> readable label (best effort).
QUALITY_LABEL = {
    1: "SDTV", 2: "SD DVD", 4: "720p HDTV", 8: "RawHD", 16: "1080p HDTV",
    32: "720p WEB-DL", 64: "1080p WEB-DL", 128: "720p BluRay", 256: "1080p BluRay",
    512: "1080p WEB-DL", 1024: "4K", 2048: "4K", 32768: "4K",
}


def quality_label(composite: int) -> str | None:
    return QUALITY_LABEL.get(composite // 100)


def ordinal_to_date(value) -> date | None:
    try:
        v = int(value)
    except (TypeError, ValueError):
        return None
    if v <= 1:
        return None
    try:
        return date.fromordinal(v)
    except (ValueError, OverflowError):
        return None


def parse_hist_date(value) -> datetime | None:
    try:
        return datetime.strptime(str(value), "%Y%m%d%H%M%S")
    except (TypeError, ValueError):
        return None


async def main(old_db_path: str) -> None:
    src = sqlite3.connect(old_db_path)
    src.row_factory = sqlite3.Row
    shows = src.execute("SELECT * FROM tv_shows").fetchall()
    episodes = src.execute("SELECT * FROM tv_episodes").fetchall()
    history = src.execute("SELECT * FROM history").fetchall()
    src.close()

    await init_db()
    async with SessionLocal() as db:
        # Clean slate (display-only import). Providers cleared for safety.
        await db.execute(delete(HistoryEntry))
        await db.execute(delete(Episode))
        await db.execute(delete(Show))
        await db.execute(delete(ProviderConfig))
        await db.commit()

        by_indexer: dict[int, Show] = {}
        for s in shows:
            show = Show(
                tvdb_id=s["indexer_id"] if s["indexer"] == 1 else None,
                name=s["show_name"] or "Unknown",
                network=s["network"],
                imdb_id=s["imdb_id"],
                status=ShowStatus.continuing if (s["status"] or "").lower().startswith("contin") else ShowStatus.ended,
                paused=True,        # safety: imported shows are paused
                location=None,      # safety: never import real file paths
                quality="HD",
                language=s["lang"] or "en",
            )
            db.add(show)
            by_indexer[s["indexer_id"]] = show
        await db.flush()  # assign show ids

        ep_count = 0
        for e in episodes:
            show = by_indexer.get(e["showid"])
            if show is None:
                continue
            base = (e["status"] or 0) % 100
            # Set show_id directly rather than appending to show.episodes: the
            # latter would trigger an async lazy-load of the (selectin) collection.
            db.add(
                Episode(
                    show_id=show.id,
                    season=e["season"],
                    episode=e["episode"],
                    name=e["name"],
                    overview=e["description"],
                    air_date=ordinal_to_date(e["airdate"]),
                    status=EP_STATUS.get(base, EpisodeStatus.skipped),
                    quality=quality_label(e["status"] or 0),
                    release_name=e["release_name"],
                    location=None,  # safety
                )
            )
            ep_count += 1
        await db.commit()

        hist_count = 0
        for h in history:
            base = (h["action"] or 0) % 100
            action = HIST_ACTION.get(base)
            if action is None:
                continue
            show = by_indexer.get(h["showid"])
            entry = HistoryEntry(
                show_id=show.id if show else None,
                action=action,
                provider=h["provider"],
                release_name=h["resource"],
                season=h["season"],
                episode=h["episode"],
                quality=quality_label(h["action"] or 0),
            )
            created = parse_hist_date(h["date"])
            if created is not None:
                entry.created_at = created
            db.add(entry)
            hist_count += 1
        await db.commit()

    print(f"imported {len(by_indexer)} shows, {ep_count} episodes, {hist_count} history entries")
    print("safety: locations NULL, wanted->skipped, shows paused, providers cleared")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python -m scripts.import_sickchill /path/to/sickchill.db")
        raise SystemExit(2)
    asyncio.run(main(sys.argv[1]))
