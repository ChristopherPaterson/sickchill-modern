"""Provider registry. Discover and instantiate enabled providers."""
from __future__ import annotations

from app.providers.base import Provider
from app.providers.example import ExampleProvider

# Register provider classes here as you implement them.
_PROVIDER_CLASSES: list[type[Provider]] = [
    ExampleProvider,
]


def all_providers() -> list[Provider]:
    return [cls() for cls in _PROVIDER_CLASSES]


def enabled_providers() -> list[Provider]:
    # TODO: read enabled state from the Setting table rather than the class default.
    return [p for p in all_providers() if p.enabled]
