"""Aggregate all v1 routers under a single APIRouter."""
from fastapi import APIRouter

from app.api.routes import auth, config, episodes, history, providers, search, settings, shows, system

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(shows.router)
api_router.include_router(episodes.router)
api_router.include_router(search.router)
api_router.include_router(providers.router)
api_router.include_router(config.router)
api_router.include_router(history.router)
api_router.include_router(settings.router)
api_router.include_router(system.router)
