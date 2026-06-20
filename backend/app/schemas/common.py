"""Shared response schemas."""
from __future__ import annotations

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
