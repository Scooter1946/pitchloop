# Integration checklist

Merge only handoffs marked `READY: yes`, in this order.

## P1 — contracts, agent, Zero

- [ ] Run the command in `handoffs/p1.md`.
- [ ] Run `pytest -q tests/test_contracts.py tests/test_agent_fake_loop.py`.
- [ ] Confirm required Zero and authoring environment names are documented without values.

## P2 — scenario and calls

- [ ] Run the command in `handoffs/p2.md`.
- [ ] Run `pytest -q tests/test_pitch.py tests/test_call_adapter.py conformance/test_generated_tool.py`.
- [ ] Confirm fixture, call, and callee phone environment names are documented without values.

## P3 — policy and repository

- [ ] Run the command in `handoffs/p3.md`.
- [ ] Run `pytest -q tests/test_policy_adapter.py tests/test_repo_adapter.py`.
- [ ] Confirm Pomerium and GitHub environment names are documented without values.

## P4 — evidence and release

- [x] Run `pytest -q tests/test_evidence_adapter.py`.
- [ ] Run `python -m demo.prove_nexla` with live Nexla configuration.
- [ ] Save redacted flow identifiers and lineage proof under `docs/lineage/`.

## Release gate

- [ ] Run `pytest -q`.
- [ ] Run `python -m agent --spec scenario/run_spec.json` with all modes fake.
- [ ] Review `python -m demo.show_timeline` on one screen.
- [ ] Scan tracked files for secrets and phone numbers.

## Current cross-branch blockers

- P1 `step1` is ready and shares the frozen base.
- P2 tests pass in a synthetic overlay, but its published branch has unrelated Git history and its handoff is `READY: no`; replay it onto `86d689f` before merging.
- P3 tests pass in a synthetic overlay, but its handoff is `READY: no`. Before live integration, P3 must accept P1's `exit_code: 0` conformance artifact and the first entry in `evidence_ids`; P1/P3 must also stop overwriting each other's policy and repository proof artifacts.
- The synthetic P1+P2+P3+P4 tree passes 81 tests and reaches `MEETING_BOOKED` in the full fake loop. This is compatibility evidence, not a substitute for clean branch history or sponsor proof.
