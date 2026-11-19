#!/bin/sh
# Verifier entry for CS-XX-001.  Harbor mounts this directory at /tests after
# the agent has finished and runs this script as root.  The reward is 1 when
# every unit test listed in ut_index.json passes on /workspace/repo, else 0.
set -eu
mkdir -p /logs/verifier
cd /tests || exit 1
rm -f /logs/verifier/reward.txt
python3 -B /tests/score.py --repo /workspace/repo --out /logs/verifier/result.json --log-dir /logs/verifier > /logs/verifier/score.stdout 2> /logs/verifier/score.stderr
python3 -B - <<'PY'
import json
try:
    document = json.load(open("/logs/verifier/result.json", encoding="utf-8"))
    reward = int(document.get("score", 0)) if document.get("valid") else None
except Exception:
    reward = None
if reward is None:
    # The scorer itself did not produce a usable result: leave no reward so
    # that the trial is reported as a verifier error, not as a model failure.
    raise SystemExit(1)
open("/logs/verifier/reward.txt", "w").write("%d\n" % reward)
PY
