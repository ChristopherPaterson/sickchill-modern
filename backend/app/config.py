"""Application configuration loaded from environment / .env.

All settings are overridable via environment variables prefixed with SCM_,
e.g. SCM_SECRET_KEY=... or SCM_DATABASE_URL=...
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SCM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    app_name: str = "SickChill Modern"
    debug: bool = False
    data_dir: Path = Field(default=Path.home() / ".sickchill-modern")

    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    # Database. Defaults to a SQLite file under data_dir if unset.
    database_url: str | None = None

    # Auth. SECRET_KEY must be set in production; a random dev key is generated otherwise.
    secret_key: str = "CHANGE-ME-IN-PRODUCTION"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    jwt_algorithm: str = "HS256"

    # When False (the default), no login is required and every request acts as the
    # admin user. Set SCM_AUTH_ENABLED=true to require login (do this if the app is
    # reachable beyond your trusted network).
    auth_enabled: bool = False

    # CORS. In production set this to your own origin(s).
    cors_origins: list[str] = ["http://localhost:5173"]

    # Scheduler intervals (minutes)
    daily_search_interval: int = 60
    backlog_search_interval: int = 60 * 24
    show_update_interval: int = 60 * 12

    # TheTVDB v4 API. Register a free key at https://thetvdb.com/dashboard/account/apikey
    # The free tier also requires a subscriber PIN; licensed keys do not. Set once
    # via SCM_TVDB_API_KEY / SCM_TVDB_PIN; never entered in the UI.
    tvdb_api_key: str | None = None
    tvdb_pin: str | None = None
    tvdb_language: str = "eng"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return f"sqlite+aiosqlite:///{self.data_dir / 'sickchill-modern.db'}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
