"""Redact sensitive values before evidence reaches disk."""

from __future__ import annotations

import os
import re
from typing import Any

REDACTED = "***REDACTED***"
_SENSITIVE_KEYS = ("secret", "token", "password", "authorization", "api_key", "wallet", "phone")
_PHONE = re.compile(r"(?<!\d)\+\d{10,15}(?!\d)")


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: REDACTED
            if any(marker in str(key).lower() for marker in _SENSITIVE_KEYS)
            else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        safe = _PHONE.sub(REDACTED, value)
        for key, secret in os.environ.items():
            if (
                len(secret) >= 8
                and any(marker.upper() in key.upper() for marker in _SENSITIVE_KEYS)
            ):
                safe = safe.replace(secret, REDACTED)
        return safe
    return value
