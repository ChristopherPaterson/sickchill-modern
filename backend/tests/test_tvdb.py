"""TVDB indexer tests using a mocked HTTP transport (no real API key/network)."""
from __future__ import annotations

from datetime import date

import httpx
import pytest

from app.indexers import tvdb as tvdb_mod
from app.indexers.tvdb import BASE_URL, TVDBIndexer


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/v4/login":
        return httpx.Response(200, json={"data": {"token": "test-token"}})
    if path == "/v4/search":
        return httpx.Response(200, json={"data": [
            {"tvdb_id": "12345", "name": "Test Show", "overview": "An overview",
             "network": "HBO", "image_url": "http://img/poster.jpg"},
        ]})
    if path == "/v4/series/12345/extended":
        return httpx.Response(200, json={"data": {
            "name": "Test Show", "overview": "An overview",
            "latestNetwork": {"name": "HBO"}, "image": "http://img/poster.jpg",
            "remoteIds": [{"sourceName": "IMDB", "id": "tt0123456"}],
        }})
    if path == "/v4/series/12345/episodes/default":
        page = request.url.params.get("page")
        if page in (None, "0"):
            return httpx.Response(200, json={
                "data": {"episodes": [
                    {"seasonNumber": 1, "number": 1, "name": "Pilot",
                     "overview": "first", "aired": "2020-01-05"},
                ]},
                "links": {"next": "page2"},
            })
        return httpx.Response(200, json={
            "data": {"episodes": [
                {"seasonNumber": 1, "number": 2, "name": "Second",
                 "overview": "second", "aired": "2020-01-12"},
            ]},
            "links": {"next": None},
        })
    return httpx.Response(404)


@pytest.fixture
def indexer():
    tvdb_mod._token_cache.clear()
    client = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(_handler))
    return TVDBIndexer(api_key="test-key", client=client)


async def test_search_maps_results(indexer):
    results = await indexer.search("test")
    assert len(results) == 1
    show = results[0]
    assert show.indexer_id == 12345
    assert show.name == "Test Show"
    assert show.network == "HBO"
    assert show.poster_url == "http://img/poster.jpg"
    await indexer.close()


async def test_get_show_with_paginated_episodes(indexer):
    show = await indexer.get_show(12345)
    assert show is not None
    assert show.name == "Test Show"
    assert show.imdb_id == "tt0123456"
    # Two pages, one episode each.
    assert len(show.episodes) == 2
    assert show.episodes[0].season == 1
    assert show.episodes[0].episode == 1
    assert show.episodes[0].air_date == date(2020, 1, 5)
    assert show.episodes[1].episode == 2
    await indexer.close()
