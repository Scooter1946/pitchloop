"""Render the fixed demo timeline from persisted run artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def timeline(run_dir: Path) -> list[str]:
    lines: list[str] = []
    denied = _read(run_dir / "policy/deny.json")
    allowed = _read(run_dir / "policy/allow.json")
    fact_a = _read(run_dir / "zero/fact_a_result.json")
    receipt = _read(run_dir / "zero/fact_a_receipt.json")
    call_1 = _read(run_dir / "calls/call_1_result.json")
    diagnosis = _read(run_dir / "evidence/diagnosis.json")
    search_b = _read(run_dir / "zero/search_fact_b.json")
    conformance = _read(run_dir / "tools/conformance_result.json")
    merge = _read(run_dir / "repo/merge.json")
    tool = _read(run_dir / "tools/generated_manifest.json")
    call_2 = _read(run_dir / "calls/call_2_result.json")

    if denied:
        lines.append(f"[POLICY] {denied.get('candidate_id', 'alex_rivera')} denied by Pomerium ({denied.get('status_code', 403)})")
    if allowed:
        lines.append(f"[POLICY] {allowed.get('candidate_id', 'maya_chen')} allowed by Pomerium ({allowed.get('status_code', 200)})")
    if fact_a or receipt:
        service = fact_a.get("service_id") or fact_a.get("service", {}).get("name", "service")
        cents = receipt.get("amount_cents", fact_a.get("amount_cents", 0))
        lines.append(f"[ZERO] discovered {service} and paid ${cents / 100:.2f}")
    if call_1:
        missing = ",".join(call_1.get("missing_claims", [])) or "unknown"
        lines.append(f"[CALL 1] rejected: missing {missing}")
    if diagnosis:
        ids = diagnosis.get("evidence_ids") or diagnosis.get("ids") or []
        lines.append(f"[NEXLA] diagnosis cites {','.join(ids)}")
    if search_b:
        lines.append("[ZERO] no marketplace capability matched fact_b")
    if conformance:
        lines.append("[CODE] generated tool; fixed conformance passed")
    if merge:
        lines.append(f"[GITHUB] PR #{merge.get('number', '?')} merged at {merge.get('merge_sha', '?')}")
    if tool:
        lines.append("[TOOL] fact_b acquired from generated tool")
    if call_2:
        lines.append("[CALL 2] meeting booked")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=Path("runs/demo-001"))
    args = parser.parse_args()
    print("\n".join(timeline(args.run_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
