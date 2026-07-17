"""Frozen shared Pydantic models for PitchLoop.

These are copied verbatim (names and semantics) from the global integration
contract (§7). Keep them small and stable. Do not change a field after freeze
without explicit team approval; any change must be additive.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class RunSpec(BaseModel):
    """The specification the agent receives and plans against."""

    run_id: str
    goal: Literal["book_one_qualified_meeting"]
    product: str
    persona: str
    candidates: list[str]
    budget_cents: int
    policy_ref: str
    required_claims: list[Literal["fact_a", "fact_b"]]
    max_paid_calls: int = 2


class Evidence(BaseModel):
    """A single normalized piece of evidence produced during a run.

    ``value`` holds the canonical claim payload; ``provenance`` and the raw
    provider output are preserved separately (see the runtime artifact contract).
    """

    evidence_id: str
    run_id: str
    candidate_id: str | None = None
    kind: Literal["policy", "enrichment", "receipt", "call", "tool", "repo", "meeting"]
    claim: str
    value: dict[str, Any]
    source: str
    source_ref: str | None = None
    occurred_at: datetime
    provenance: dict[str, Any] = Field(default_factory=dict)
    policy_decision: Literal["allow", "deny"] | None = None


class PolicyDecision(BaseModel):
    """Result of a real Pomerium authorization check."""

    allowed: bool
    status_code: int
    reason: str
    audit_ref: str | None = None
    raw_artifact_path: str | None = None


class ServiceMatch(BaseModel):
    """A candidate Zero.xyz service returned by capability search."""

    service_id: str
    name: str
    description: str
    price_cents: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PaidResult(BaseModel):
    """Outcome of a paid Zero.xyz invocation, with receipt and raw artifact."""

    ok: bool
    service_id: str
    result: dict[str, Any]
    receipt: dict[str, Any]
    amount_cents: int
    provider_ref: str | None = None
    raw_artifact_path: str


class CallResult(BaseModel):
    """Outcome of a paid call, driven by the deterministic callee rubric."""

    status: Literal["rejected", "booked", "failed"]
    code: str
    missing_claims: list[str] = Field(default_factory=list)
    transcript: str
    transcript_path: str
    receipt: dict[str, Any]
    amount_cents: int
    provider_ref: str | None = None


class PullRequest(BaseModel):
    """An agent-authored GitHub pull request (created via RepoPort)."""

    number: int
    url: str
    branch: str
    files: list[str]


class MergeResult(BaseModel):
    """Result of merging an agent-authored pull request."""

    merged: bool
    merge_sha: str | None = None
    url: str | None = None


class ToolManifest(BaseModel):
    """Manifest describing a generated tool the registry can load by capability."""

    name: str
    capability: Literal["fact_b"]
    entrypoint: str
    input_schema: dict[str, Any]
    output_claim: Literal["fact_b"]
    version: str
