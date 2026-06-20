"""Newznab/Torznab provider parsing tests (mocked HTTP, no network)."""
from __future__ import annotations

import httpx
import pytest

from app.providers.base import SearchQuery
from app.providers.newznab import NewznabProvider

SAMPLE = {
    "channel": {
        "item": [
            {
                "title": "Test.Show.S01E01.1080p.WEB-DL.x264",
                "link": "http://tracker/download/1.torrent",
                "enclosure": {"@attributes": {"url": "http://tracker/1.torrent", "length": "1500000000"}},
                "attr": [
                    {"@attributes": {"name": "seeders", "value": "120"}},
                    {"@attributes": {"name": "size", "value": "1500000000"}},
                ],
            },
            {
                "title": "Test.Show.S01E01.720p.HDTV.x264",
                "link": "http://tracker/download/2.torrent",
                "attr": [{"@attributes": {"name": "seeders", "value": "2"}}],
            },
        ]
    }
}


def _provider(min_seeders: int = 0) -> NewznabProvider:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=SAMPLE)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return NewznabProvider(
        name="test", url="http://tracker/api", api_key="k",
        is_torrent=True, min_seeders=min_seeders, client=client,
    )


@pytest.fixture
def query() -> SearchQuery:
    return SearchQuery(show_name="Test Show", season=1, episode=1)


async def test_parses_items(query):
    provider = _provider()
    results = await provider.search(query)
    assert len(results) == 2
    first = results[0]
    assert first.title.startswith("Test.Show")
    assert first.download_url == "http://tracker/download/1.torrent"
    assert first.seeders == 120
    assert first.size == 1500000000
    await provider.close()


async def test_min_seeders_filter(query):
    provider = _provider(min_seeders=10)
    results = await provider.search(query)
    # The 2-seeder release is filtered out.
    assert len(results) == 1
    assert results[0].seeders == 120
    await provider.close()
