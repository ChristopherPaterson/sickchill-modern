"""Smoke tests: the app boots, health responds, and the auth toggle behaves.

These do not run the lifespan: the health route is pure, and the protected-route
auth check happens before any DB access.
"""
from __future__ import annotations

import httpx
import pytest

from app.config import settings
from app.main import app


@pytest.mark.asyncio
async def test_health():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/system/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "auth_enabled" in body


@pytest.mark.asyncio
async def test_protected_route_requires_token_when_auth_enabled(monkeypatch):
    monkeypatch.setattr(settings, "auth_enabled", True)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/shows")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_open_when_auth_disabled(monkeypatch):
    # With auth disabled the route must not reject for missing credentials.
    monkeypatch.setattr(settings, "auth_enabled", False)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/shows")
    assert resp.status_code != 401
