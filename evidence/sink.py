"""FastAPI destination for canonical evidence emitted by Nexla."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import ValidationError

from contracts.models import Evidence
from evidence.store import EvidenceStore


def create_app(store: EvidenceStore | None = None) -> FastAPI:
    evidence_store = store if store is not None else EvidenceStore()
    app = FastAPI(title="PitchLoop evidence sink")

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "records": len(evidence_store)}

    @app.post("/ingest/evidence")
    def ingest(payload: dict[str, Any]) -> dict[str, Any]:
        body = dict(payload)
        provenance = dict(body.get("provenance") or {})
        correlation_id = body.pop("correlation_id", None) or provenance.get(
            "correlation_id"
        )
        if not correlation_id:
            raise HTTPException(422, "correlation_id is required")
        provenance["correlation_id"] = str(correlation_id)
        body["provenance"] = provenance
        try:
            evidence = Evidence.model_validate(body)
            stored, created = evidence_store.append(evidence)
        except ValidationError as exc:
            raise HTTPException(422, exc.errors()) from exc
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc
        return {"created": created, "evidence": stored.model_dump(mode="json")}

    @app.get("/evidence/{evidence_id}", response_model=Evidence)
    def get_evidence(evidence_id: str) -> Evidence:
        evidence = evidence_store.get(evidence_id)
        if not evidence:
            raise HTTPException(404, "evidence not found")
        return evidence

    @app.get("/evidence", response_model=list[Evidence])
    def query_evidence(
        run_id: str = Query(...),
        claim: str | None = None,
        kind: str | None = None,
    ) -> list[Evidence]:
        return evidence_store.query(run_id, claim=claim, kind=kind)

    @app.get("/correlations/{correlation_id}", response_model=Evidence)
    def get_correlation(correlation_id: str) -> Evidence:
        evidence = evidence_store.by_correlation(correlation_id)
        if not evidence:
            raise HTTPException(404, "correlation not found")
        return evidence

    return app


app = create_app()
