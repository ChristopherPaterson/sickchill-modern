"""FastAPI application entry point.

Run with: uvicorn app.main:app --reload
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.api.routes import api_router
from app.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal, engine, init_db
from app.scheduler.scheduler import shutdown_scheduler, start_scheduler

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
)
logger = logging.getLogger("app")


async def ensure_default_admin() -> None:
    """Create a default admin on first run if no users exist.

    Username 'admin', password from SCM_ADMIN_PASSWORD env or 'admin' (must be
    changed). Logged loudly so it is not missed.
    """
    from app.models.user import User

    async with SessionLocal() as db:
        existing = (await db.execute(select(User).limit(1))).scalar_one_or_none()
        if existing is not None:
            return
        import os

        password = os.environ.get("SCM_ADMIN_PASSWORD", "admin")
        db.add(User(username="admin", hashed_password=hash_password(password), is_admin=True))
        await db.commit()
        logger.warning(
            "Created default admin user 'admin'. CHANGE THIS PASSWORD via the API/UI immediately."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("%s %s starting", settings.app_name, __version__)
    await init_db()
    await ensure_default_admin()
    start_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler()
        await engine.dispose()
        logger.info("shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/healthz", include_in_schema=False)
async def healthz():
    return {"status": "ok"}


class SPAStaticFiles(StaticFiles):
    """StaticFiles with single-page-app fallback.

    Serves real files (assets, sw.js, manifest) normally, but falls back to
    index.html for client-side routes (e.g. /manage, /show/5) so deep links and
    refreshes work. Paths that look like files (have an extension) still 404.
    """

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404 and "." not in path.rsplit("/", 1)[-1]:
                return await super().get_response("index.html", scope)
            raise


# Serve the built frontend if present, so a single container serves API + UI.
# In dev the SPA runs separately via Vite. API routes are registered above and
# take precedence over this catch-all mount.
_frontend_dist = Path(__file__).resolve().parent.parent / "static"
if _frontend_dist.is_dir():
    app.mount("/", SPAStaticFiles(directory=_frontend_dist, html=True), name="frontend")
