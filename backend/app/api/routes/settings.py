"""Runtime settings routes (key/value store)."""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.setting import Setting
from app.schemas.common import Message

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=dict[str, str | None])
async def get_settings(db: DbSession, _: CurrentUser):
    result = await db.execute(select(Setting))
    return {s.key: s.value for s in result.scalars().all()}


@router.put("/{key}", response_model=Message)
async def set_setting(key: str, value: str, db: DbSession, _: CurrentUser):
    setting = await db.get(Setting, key)
    if setting is None:
        setting = Setting(key=key, value=value)
        db.add(setting)
    else:
        setting.value = value
    await db.commit()
    return Message(message=f"{key} updated")
