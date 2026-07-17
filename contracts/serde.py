"""Stable, readable JSON serialization shared across all roles.

Every artifact written to a run directory should go through :func:`dumps` so the
output is deterministic (sorted keys, fixed indent) and diff-friendly. Datetimes
are emitted as ISO-8601 strings; Pydantic models are dumped in JSON mode.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


def to_jsonable(value: Any) -> Any:
    """Return a JSON-serializable representation of ``value``.

    Pydantic models are converted with ``model_dump(mode="json")`` so nested
    datetimes/enums become strings. Plain dicts/lists/scalars pass through and
    are handled by :func:`dumps`'s encoder.
    """

    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    return value


def _default(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def dumps(value: Any) -> str:
    """Serialize to deterministic, human-readable JSON (sorted keys, 2-space indent)."""

    return json.dumps(
        to_jsonable(value),
        default=_default,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )


def loads(text: str) -> Any:
    """Parse JSON text back into Python objects."""

    return json.loads(text)
