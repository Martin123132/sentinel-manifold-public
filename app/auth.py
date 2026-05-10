"""API-key authentication helpers for Sentinel Manifold."""

from __future__ import annotations

import hmac
import os
from typing import Mapping


API_KEY_ENV = "SENTINEL_API_KEY"
PUBLIC_DEMO_ENV = "SENTINEL_PUBLIC_DEMO"
TRUE_VALUES = {"1", "true", "yes", "on"}


def configured_api_key() -> str:
    """Return the configured API key, or an empty string when auth is disabled."""

    return os.environ.get(API_KEY_ENV, "").strip()


def auth_required() -> bool:
    """Whether protected API routes require an API key."""

    return bool(configured_api_key())


def public_demo_enabled() -> bool:
    """Whether unauthenticated public sandbox routes are enabled."""

    return os.environ.get(PUBLIC_DEMO_ENV, "").strip().lower() in TRUE_VALUES


def is_admin_authorized(headers: Mapping[str, str]) -> bool:
    """Whether the request supplies the configured admin API key."""

    expected = configured_api_key()
    if not expected:
        return False

    supplied = _extract_supplied_key(headers)
    return bool(supplied) and hmac.compare_digest(supplied, expected)


def is_authorized(headers: Mapping[str, str]) -> bool:
    """Check Authorization: Bearer or X-API-Key headers."""

    expected = configured_api_key()
    if not expected:
        return True

    return is_admin_authorized(headers)


def _extract_supplied_key(headers: Mapping[str, str]) -> str:
    authorization = headers.get("Authorization", "").strip()
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return headers.get("X-API-Key", "").strip()

