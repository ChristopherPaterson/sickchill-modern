"""SABnzbd client tests (mocked HTTP, no network)."""
from __future__ import annotations

import httpx

from app.downloaders.sabnzbd import SABnzbdClient


def _client(handler) -> SABnzbdClient:
    transport = httpx.MockTransport(handler)
    return SABnzbdClient(
        url="http://sab:8080",
        api_key="key",
        category="tv",
        client=httpx.AsyncClient(transport=transport),
    )


async def test_add_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("mode") == "addurl"
        assert request.url.params.get("apikey") == "key"
        assert request.url.params.get("cat") == "tv"
        return httpx.Response(200, json={"status": True, "nzo_ids": ["SABnzbd_nzo_x"]})

    client = _client(handler)
    assert await client.add("http://indexer/release.nzb") is True
    await client.close()


async def test_add_rejected():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": False, "error": "Duplicate"})

    client = _client(handler)
    assert await client.add("http://indexer/release.nzb") is False
    await client.close()


async def test_test_ok():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("mode") == "queue"
        return httpx.Response(200, json={"queue": {"status": "Idle", "slots": []}})

    client = _client(handler)
    ok, msg = await client.test()
    assert ok is True
    assert "SABnzbd" in msg
    await client.close()


async def test_test_bad_key():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": False, "error": "API Key Incorrect"})

    client = _client(handler)
    ok, msg = await client.test()
    assert ok is False
    assert "API Key Incorrect" in msg
    await client.close()
