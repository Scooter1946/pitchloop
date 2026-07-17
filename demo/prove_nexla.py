"""Send three heterogeneous events through the live Nexla evidence path."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import httpx

from integrations.evidence_client import build_evidence_port


def _wait_for_sink(url: str, timeout: int = 15) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if httpx.get(f"{url.rstrip('/')}/health", timeout=2).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.25)
    raise TimeoutError(f"sink did not become healthy: {url}")


def main() -> int:
    sink_url = os.getenv("NEXLA_SINK_URL", "http://127.0.0.1:8090")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "evidence.sink:app", "--port", "8090"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_sink(sink_url)
        port = build_evidence_port(mode="live")
        now = datetime.now(timezone.utc).isoformat()
        raw_events = [
            (
                "policy.decision",
                {
                    "run": "demo-001",
                    "candidate": "alex_rivera",
                    "http_status": 403,
                    "decision": "deny",
                    "reason": "candidate_not_consented",
                    "audit_ref": "pomerium-live-proof",
                    "observed_at": now,
                },
            ),
            (
                "zero.paid_result",
                {
                    "run_id": "demo-001",
                    "candidate_id": "maya_chen",
                    "service": {"id": "live-service", "name": "Live Zero service"},
                    "charge_cents": 0,
                    "receipt": {"proof": "replace with live receipt"},
                    "output": {"statement": "Live Fact A proof event"},
                    "timestamp": now,
                },
            ),
            (
                "call.completed",
                {
                    "run_id": "demo-001",
                    "candidate_id": "maya_chen",
                    "result_code": "REJECTED_MISSING_FACT_B",
                    "missing": ["fact_b"],
                    "transcript": "Fact A present; Fact B missing.",
                    "provider_ref": "live-call-proof",
                    "amount_cents": 0,
                    "timestamp": now,
                },
            ),
        ]
        evidence = []
        for event_type, payload in raw_events:
            correlation_id = port.publish_raw(event_type, payload)
            evidence.append(port.wait_for_evidence(correlation_id))

        print(f"NEXLA_OK flow={os.environ['NEXLA_FLOW_ID']}")
        for item in evidence:
            suffix = (
                " missing=" + ",".join(item.value.get("missing_claims", []))
                if item.kind == "call"
                else ""
            )
            print(f"EVIDENCE {item.evidence_id} claim={item.claim}{suffix}")
        ids = ",".join(item.evidence_id for item in evidence if item.claim in {"fact_a", "call_outcome"})
        print(f"DIAGNOSIS_INPUT present=fact_a missing=fact_b ids={ids}")
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
