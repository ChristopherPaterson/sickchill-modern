"""Release quality parsing and scoring.

Uses guessit to parse a release title into resolution/source, then maps that to
an ordered quality tier and a numeric score. Ranking in the search service uses
this so the "best" release is chosen consistently.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass

from guessit import guessit


class Quality(enum.IntEnum):
    """Ordered quality tiers (higher = better). IntEnum so they compare directly."""

    UNKNOWN = 0
    SDTV = 1
    SD_DVD = 2
    HDTV_720 = 3
    WEBDL_720 = 4
    BLURAY_720 = 5
    HDTV_1080 = 6
    WEBDL_1080 = 7
    BLURAY_1080 = 8
    UHD_4K = 9


@dataclass(slots=True)
class ParsedRelease:
    quality: Quality
    resolution: str | None
    source: str | None


def _classify(resolution: str | None, source: str | None) -> Quality:
    res = (resolution or "").lower()
    src = (source or "").lower()

    if "2160" in res or "4k" in res:
        return Quality.UHD_4K
    if "1080" in res:
        if "blu" in src:
            return Quality.BLURAY_1080
        if "web" in src:
            return Quality.WEBDL_1080
        return Quality.HDTV_1080
    if "720" in res:
        if "blu" in src:
            return Quality.BLURAY_720
        if "web" in src:
            return Quality.WEBDL_720
        return Quality.HDTV_720
    if "dvd" in src:
        return Quality.SD_DVD
    if res or src:
        return Quality.SDTV
    return Quality.UNKNOWN


def parse_release(title: str) -> ParsedRelease:
    """Parse a release title into a quality tier. Never raises."""
    try:
        info = guessit(title)
        resolution = info.get("screen_size")
        source = info.get("source")
        if isinstance(source, list):
            source = source[0] if source else None
        return ParsedRelease(
            quality=_classify(resolution, str(source) if source else None),
            resolution=str(resolution) if resolution else None,
            source=str(source) if source else None,
        )
    except Exception:
        return ParsedRelease(quality=Quality.UNKNOWN, resolution=None, source=None)
