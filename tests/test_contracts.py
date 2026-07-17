"""P1 contract tests.

Prove the frozen shared contract imports cleanly, validates, and serializes
deterministically for every teammate. If this file fails, no other role can
trust `contracts/`.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from contracts import (
    CallPort,
    CallResult,
    Evidence,
    EvidencePort,
    MergeResult,
    PaidResult,
    PolicyDecision,
    PolicyPort,
    PullRequest,
    RepoPort,
    RunSpec,
    ServiceMatch,
    ToolManifest,
    ToolRegistryPort,
    ZeroPort,
)
from contracts.events import EventType
from contracts.serde import dumps, loads

# --------------------------------------------------------------------------- #
# Representative valid instances
# --------------------------------------------------------------------------- #

NOW = datetime(2026, 7, 17, 12, 0, 0, tzinfo=timezone.utc)


def _run_spec() -> RunSpec:
    return RunSpec(
        run_id="demo-001",
        goal="book_one_qualified_meeting",
        product="MigrationGuard",
        persona="maya_chen",
        candidates=["alex_rivera", "maya_chen"],
        budget_cents=5000,
        policy_ref="northstar/pitch",
        required_claims=["fact_a", "fact_b"],
    )


def _evidence() -> Evidence:
    return Evidence(
        evidence_id="ev-1",
        run_id="demo-001",
        candidate_id="maya_chen",
        kind="enrichment",
        claim="fact_a",
        value={"statement": "Northstar Systems is hiring backend engineers."},
        source="zero:some_service",
        occurred_at=NOW,
    )


# --------------------------------------------------------------------------- #
# Model construction + defaults
# --------------------------------------------------------------------------- #


def test_run_spec_defaults():
    spec = _run_spec()
    assert spec.max_paid_calls == 2  # frozen default
    assert spec.required_claims == ["fact_a", "fact_b"]


def test_evidence_defaults():
    ev = _evidence()
    assert ev.provenance == {}
    assert ev.policy_decision is None
    assert ev.source_ref is None


def test_all_models_construct():
    PolicyDecision(allowed=False, status_code=403, reason="denied by policy")
    ServiceMatch(service_id="s1", name="Enrich", description="company enrichment")
    PaidResult(
        ok=True,
        service_id="s1",
        result={"statement": "x"},
        receipt={"id": "r1"},
        amount_cents=120,
        raw_artifact_path="runs/demo-001/zero/fact_a_result.json",
    )
    CallResult(
        status="rejected",
        code="REJECTED_MISSING_FACT_B",
        missing_claims=["fact_b"],
        transcript="...",
        transcript_path="runs/demo-001/calls/call_1_transcript.txt",
        receipt={"id": "c1"},
        amount_cents=200,
    )
    PullRequest(number=1, url="https://example/pr/1", branch="agent/fact-b", files=["a"])
    MergeResult(merged=True, merge_sha="abc123")
    ToolManifest(
        name="generated_fact_b_tool",
        capability="fact_b",
        entrypoint="generated_tools.fact_b_tool:run",
        input_schema={"candidate_id": "string"},
        output_claim="fact_b",
        version="1.0.0",
    )


# --------------------------------------------------------------------------- #
# Literal validation is enforced
# --------------------------------------------------------------------------- #


def test_run_spec_rejects_bad_goal():
    with pytest.raises(ValidationError):
        RunSpec(
            run_id="d",
            goal="do_something_else",  # not the allowed literal
            product="p",
            persona="x",
            candidates=[],
            budget_cents=0,
            policy_ref="r",
            required_claims=[],
        )


def test_evidence_rejects_bad_kind():
    with pytest.raises(ValidationError):
        Evidence(
            evidence_id="e",
            run_id="d",
            kind="not_a_kind",
            claim="fact_a",
            value={},
            source="s",
            occurred_at=NOW,
        )


def test_tool_manifest_capability_locked_to_fact_b():
    with pytest.raises(ValidationError):
        ToolManifest(
            name="n",
            capability="fact_a",  # only fact_b is allowed
            entrypoint="m:run",
            input_schema={},
            output_claim="fact_b",
            version="1.0.0",
        )


# --------------------------------------------------------------------------- #
# Deterministic serialization round-trips
# --------------------------------------------------------------------------- #


def test_serde_is_deterministic_and_sorted():
    ev = _evidence()
    text = dumps(ev)
    # sorted keys => "claim" appears before "evidence_id" before "run_id"
    assert text.index('"claim"') < text.index('"evidence_id"') < text.index('"run_id"')
    # datetime serialized as an RFC 3339 string (pydantic emits "Z" for UTC)
    assert "2026-07-17T12:00:00Z" in text
    # stable across calls
    assert dumps(ev) == text


def test_serde_roundtrip_restores_model():
    ev = _evidence()
    restored = Evidence.model_validate(loads(dumps(ev)))
    assert restored == ev


def test_serde_handles_plain_dict_with_datetime():
    text = dumps({"when": NOW, "n": 1})
    assert "2026-07-17T12:00:00+00:00" in text


# --------------------------------------------------------------------------- #
# Ports are runtime-checkable Protocols with the expected method names
# --------------------------------------------------------------------------- #


def test_ports_are_runtime_checkable():
    class _Zero:
        def search(self, capability):
            return []

        def invoke(self, service, payload):
            return None

    class _Policy:
        def authorize(self, action, candidate_id, context):
            return None

    class _Evidence:
        def publish_raw(self, event_type, payload):
            return "cid"

        def wait_for_evidence(self, correlation_id, timeout_seconds=30):
            return None

        def query(self, run_id, *, claim=None, kind=None):
            return []

    class _Call:
        def place_call(self, candidate_id, pitch_text):
            return None

    class _Repo:
        def create_agent_pr(self, files, title, body):
            return None

        def merge(self, pr):
            return None

    class _Registry:
        def reload(self):
            return None

        def find(self, capability):
            return None

    assert isinstance(_Zero(), ZeroPort)
    assert isinstance(_Policy(), PolicyPort)
    assert isinstance(_Evidence(), EvidencePort)
    assert isinstance(_Call(), CallPort)
    assert isinstance(_Repo(), RepoPort)
    assert isinstance(_Registry(), ToolRegistryPort)


def test_incomplete_adapter_fails_protocol_check():
    class _Broken:
        def search(self, capability):
            return []

        # missing invoke()

    assert not isinstance(_Broken(), ZeroPort)


# --------------------------------------------------------------------------- #
# Event vocabulary
# --------------------------------------------------------------------------- #


def test_event_type_values_are_plain_strings():
    assert EventType.MEETING_BOOKED == "meeting_booked"
    assert str(EventType.POLICY_DECISION) == "policy_decision"
    # usable directly as a JSON value
    assert dumps({"type": EventType.CALL_PLACED}) == '{\n  "type": "call_placed"\n}'
