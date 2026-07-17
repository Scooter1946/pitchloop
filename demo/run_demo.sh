#!/usr/bin/env bash
set -euo pipefail

python -m agent --spec scenario/run_spec.json
python -m demo.show_timeline --run-dir "${PITCHLOOP_RUN_DIR:-runs/demo-001}"
