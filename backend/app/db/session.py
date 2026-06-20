"""Async SQLAlchemy engine and session management.

A single async engine is created per process. Sessions are provided to request
handlers via the get_db dependency (see app/api/deps.py).
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.resolved_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session, ensuring it is closed afterwards."""
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create tables for first-run / dev. In production use Alembic migrations."""
    from app import models  # noqa: F401  (ensure models are imported/registered)
    from app.db.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
