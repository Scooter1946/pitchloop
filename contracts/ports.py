"""Frozen shared port Protocols for PitchLoop (§8).

Ports are the seams between roles. Every adapter (fake or live) implements the
matching Protocol so the orchestrator depends only on these interfaces.

The Protocols are marked ``@runtime_checkable`` so tests and the orchestrator
can assert an injected adapter exposes the expected methods. This only checks
method *presence*, not signatures, and does not change the frozen interface.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from contracts.models import (
    CallResult,
    Evidence,
    MergeResult,
    PaidResult,
    PolicyDecision,
    PullRequest,
    ServiceMatch,
)


@runtime_checkable
class ZeroPort(Protocol):
    def search(self, capability: str) -> list[ServiceMatch]: ...

    def invoke(self, service: ServiceMatch, payload: dict[str, Any]) -> PaidResult: ...


@runtime_checkable
class PolicyPort(Protocol):
    def authorize(
        self, action: str, candidate_id: str, context: dict[str, Any]
    ) -> PolicyDecision: ...


@runtime_checkable
class EvidencePort(Protocol):
    def publish_raw(self, event_type: str, payload: dict[str, Any]) -> str: ...

    def wait_for_evidence(
        self, correlation_id: str, timeout_seconds: int = 30
    ) -> Evidence: ...

    def query(
        self, run_id: str, *, claim: str | None = None, kind: str | None = None
    ) -> list[Evidence]: ...


@runtime_checkable
class CallPort(Protocol):
    def place_call(self, candidate_id: str, pitch_text: str) -> CallResult: ...


@runtime_checkable
class RepoPort(Protocol):
    def create_agent_pr(
        self, files: list[str], title: str, body: str
    ) -> PullRequest: ...

    def merge(self, pr: PullRequest) -> MergeResult: ...


@runtime_checkable
class ToolRegistryPort(Protocol):
    def reload(self) -> None: ...

    def find(self, capability: str): ...
