"""Shared FastAPI dependencies: DB session and current-user auth."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.user import User

# auto_error=False so a missing token does not 401 before our handler runs
# (needed for the auth-disabled mode below).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_session)]


async def _admin_user(db: AsyncSession) -> User:
    """The user used when auth is disabled: the first (admin) user, or a stand-in."""
    user = (await db.execute(select(User).order_by(User.id).limit(1))).scalar_one_or_none()
    return user or User(id=0, username="admin", is_admin=True, is_active=True, hashed_password="")


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    # No-login mode: every request acts as the admin user.
    if not settings.auth_enabled:
        return await _admin_user(db)

    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exc
    username = decode_access_token(token)
    if username is None:
        raise credentials_exc

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exc
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
