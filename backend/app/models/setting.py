"""Setting model: a simple key/value store for runtime configuration.

Static/bootstrap config lives in app/config.py (env-driven). This table holds
user-editable settings changed at runtime via the UI (provider toggles, paths,
notification config, etc.).
"""
from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Setting(Base, TimestampMixin):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(200), primary_key=True)
    value: Mapped[str | None] = mapped_column(Text)
