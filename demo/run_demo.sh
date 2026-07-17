#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python="${PYTHON:-$repo/.venv/bin/python}"
source_dir="$(mktemp -d /tmp/pitchloop-demo.XXXXXX)"
if [[ -n "${PITCHLOOP_RUN_DIR:-}" ]]; then
  if [[ -L "$PITCHLOOP_RUN_DIR" ]]; then
    echo "PITCHLOOP_RUN_DIR must not be a symlink" >&2
    exit 2
  fi
  (umask 077; mkdir -p "$PITCHLOOP_RUN_DIR")
  run_dir="$(cd "$PITCHLOOP_RUN_DIR" && pwd -P)"
else
  mkdir -p "$repo/runs"
  run_dir="$(mktemp -d "$repo/runs/fake-demo.XXXXXX")"
fi
trap 'rm -rf "$source_dir"' EXIT

git -C "$repo" archive --format=tar --output="$source_dir/release.tar" HEAD
tar -xf "$source_dir/release.tar" -C "$source_dir"

cd "$source_dir"
env \
  ZERO_MODE=fake \
  POLICY_MODE=fake \
  CALL_MODE=fake \
  REPO_MODE=fake \
  EVIDENCE_MODE=local \
  AUTHOR_MODE=fake \
  PITCHLOOP_RUN_DIR="$run_dir" \
  PITCHLOOP_OBJECTIVE="${PITCHLOOP_OBJECTIVE:-}" \
  PITCHLOOP_STEP_DELAY_SECONDS="${PITCHLOOP_STEP_DELAY_SECONDS:-0}" \
  CONFORMANCE_COMMAND="$python -m pytest -q conformance/test_generated_tool.py" \
  "$python" -m agent --spec scenario/run_spec.json --run-dir "$run_dir"
"$python" -m demo.show_timeline --run-dir "$run_dir"
echo "Artifacts: $run_dir"
