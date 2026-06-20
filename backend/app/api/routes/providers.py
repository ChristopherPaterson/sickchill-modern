"""Search-provider configuration routes (Config > Search Providers)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.provider import ProviderConfig, ProviderType


class ProviderIn(BaseModel):
    name: str
    type: ProviderType = ProviderType.torznab
    url: str
    api_key: str | None = None
    enabled: bool = True
    priority: int = 0
    min_seeders: int = 0


class ProviderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: ProviderType
    url: str
    enabled: bool
    priority: int
    min_seeders: int
    # api_key intentionally omitted from output (secret).


router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("", response_model=list[ProviderOut])
async def list_providers(db: DbSession, _: CurrentUser):
    result = await db.execute(select(ProviderConfig).order_by(ProviderConfig.priority.desc()))
    return list(result.scalars().all())


@router.post("", response_model=ProviderOut, status_code=status.HTTP_201_CREATED)
async def create_provider(payload: ProviderIn, db: DbSession, _: CurrentUser):
    provider = ProviderConfig(**payload.model_dump())
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return provider


@router.patch("/{provider_id}", response_model=ProviderOut)
async def update_provider(provider_id: int, payload: ProviderIn, db: DbSession, _: CurrentUser):
    provider = await db.get(ProviderConfig, provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    for field, value in payload.model_dump().items():
        setattr(provider, field, value)
    await db.commit()
    await db.refresh(provider)
    return provider


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(provider_id: int, db: DbSession, _: CurrentUser):
    provider = await db.get(ProviderConfig, provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    await db.delete(provider)
    await db.commit()
