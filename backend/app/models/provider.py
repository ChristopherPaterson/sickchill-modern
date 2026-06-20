"""Search provider configuration.

A row per configured indexer (Newznab usenet or Torznab torrent endpoint, e.g.
from Prowlarr/Jackett). The registry instantiates a provider per enabled row.
"""
from __future__ import annotations

import enum

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ProviderType(enum.StrEnum):
    newznab = "newznab"  # usenet
    torznab = "torznab"  # torrent (Jackett/Prowlarr)


class ProviderConfig(Base, TimestampMixin):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[ProviderType] = mapped_column(default=ProviderType.torznab)
    url: Mapped[str] = mapped_column(String(1000))  # base API url
    api_key: Mapped[str | None] = mapped_column(String(255))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)  # higher tried/weighted first
    min_seeders: Mapped[int] = mapped_column(Integer, default=0)  # torznab only
