"""Library path naming for post-processing.

Builds the destination path for a downloaded episode, e.g.
    <root>/<Show>/Season 01/<Show> - S01E02 - <Episode Name>.mkv
"""
from __future__ import annotations

import re
from pathlib import Path

# Characters not allowed in file/dir names on common filesystems.
_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize(name: str) -> str:
    """Make a string safe for use as a path component."""
    cleaned = _ILLEGAL.sub("", name or "").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.rstrip(". ")  # trailing dots/spaces are invalid on Windows
    return cleaned or "Unknown"


def episode_path(
    library_root: str | Path,
    show_name: str,
    season: int,
    episode: int,
    episode_name: str | None,
    ext: str,
) -> Path:
    """Compute the destination path for one episode file."""
    root = Path(library_root)
    show = sanitize(show_name)
    base = f"{show} - S{season:02d}E{episode:02d}"
    if episode_name:
        base += f" - {sanitize(episode_name)}"
    ext = ext if ext.startswith(".") else f".{ext}"
    return root / show / f"Season {season:02d}" / f"{base}{ext}"
