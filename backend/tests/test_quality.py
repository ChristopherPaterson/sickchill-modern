"""Quality parsing and result ranking tests."""
from __future__ import annotations

from app.providers.base import SearchResult
from app.providers.quality import Quality, parse_release
from app.services.search_service import rank_results


def test_parse_resolution_and_source():
    assert parse_release("Some.Show.S01E01.1080p.WEB-DL.x264").quality == Quality.WEBDL_1080
    assert parse_release("Some.Show.S01E01.720p.HDTV.x264").quality == Quality.HDTV_720
    assert parse_release("Some.Show.S01E01.2160p.WEB.x265").quality == Quality.UHD_4K
    assert parse_release("Some.Show.S01E01.1080p.BluRay.x264").quality == Quality.BLURAY_1080


def test_parse_unknown_is_lowest():
    assert parse_release("just a title with no quality markers").quality == Quality.UNKNOWN


def test_rank_prefers_higher_quality_then_seeders():
    results = [
        SearchResult(title="Show.S01E01.720p.HDTV.x264", download_url="a", provider="p", seeders=100),
        SearchResult(title="Show.S01E01.1080p.WEB-DL.x264", download_url="b", provider="p", seeders=5),
        SearchResult(title="Show.S01E01.1080p.WEB-DL.x264", download_url="c", provider="p", seeders=50),
    ]
    ranked = rank_results(results)
    # Best two are the 1080p WEB-DLs, the one with more seeders first.
    assert ranked[0].download_url == "c"
    assert ranked[1].download_url == "b"
    assert ranked[2].download_url == "a"
