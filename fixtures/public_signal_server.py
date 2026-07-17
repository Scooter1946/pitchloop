"""Public fictional company-signal fixture used by generated tools.

Run locally with::

    uvicorn fixtures.public_signal_server:app --host 127.0.0.1 --port 8088
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query


_DATA_PATH = Path(__file__).with_name("public_company_data.json")


@lru_cache(maxsize=1)
def _load_fixture() -> dict[str, Any]:
    """Load and minimally validate the committed fictional public dataset."""

    with _DATA_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    signal = data.get("northstar_systems", {}).get("migration_signal", {})
    required = {"allowed_candidates", "claim", "statement", "source", "published_at"}
    if not required.issubset(signal):
        missing = sorted(required.difference(signal))
        raise RuntimeError(f"fixture is missing required fields: {missing}")
    return data


app = FastAPI(
    title="PitchLoop Public Company Signal Fixture",
    description="Fictional public-company data; contains no private personal data.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    _load_fixture()
    return {"status": "ok"}


@app.get("/companies/northstar_systems/migration-signal")
def migration_signal(
    candidate_id: str = Query(..., min_length=1),
) -> dict[str, str]:
    signal = _load_fixture()["northstar_systems"]["migration_signal"]
    if candidate_id not in signal["allowed_candidates"]:
        raise HTTPException(status_code=404, detail="migration signal not found")
    return {
        "candidate_id": candidate_id,
        "company_id": "northstar_systems",
        "claim": signal["claim"],
        "statement": signal["statement"],
        "source": signal["source"],
        "published_at": signal["published_at"],
    }
