"""System routes: health and version. Health is public; version requires auth."""
from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.api.deps import CurrentUser
from app.config import settings
from app.schemas.common import HealthResponse

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__, auth_enabled=settings.auth_enabled)


@router.get("/info")
async def info(_: CurrentUser):
    return {"version": __version__}
