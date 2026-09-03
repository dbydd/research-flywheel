#!/bin/sh
# reproduce.sh — locate latest keep archive/run and execute its reference reproduction.
# POSIX shell; Python via uv-first helper (uv run --directory "$WORKSPACE" --frozen python when uv and uv.lock exist, then python3, then python).
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
WORKSPACE="$SCRIPT_DIR"

# uv-first python helper — prefers uv when lock exists, falls back to python3/python
run_python() {
  if [ -f "$WORKSPACE/uv.lock" ] && command -v uv >/dev/null 2>&1; then
    uv run --directory "$WORKSPACE" --frozen python "$@"
  elif command -v python3 >/dev/null 2>&1; then
    python3 "$@"
  elif command -v python >/dev/null 2>&1; then
    python "$@"
  else
    return 127
  fi
}

# SAFE_RUN_ID pattern mirrored from orchestration/flywheel.py
# Used for path-traversal protection; validated in helper and in shell.
find_latest_keep() {
  if ! run_python -c "import sys; sys.exit(0)" >/dev/null 2>&1; then
    return 0
  fi
  run_python - "$WORKSPACE" <<'PY'
import json
import math
import os
import re
import sys
from pathlib import Path

ws = Path(sys.argv[1]).resolve()
SAFE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")

def is_safe_name(name: str) -> bool:
    if "/" in name or "\\" in name or ".." in name:
        return False
    if not SAFE.fullmatch(name):
        return False
    return True

def path_is_symlink(p: Path) -> bool:
    try:
        return p.is_symlink()
    except Exception:
        return True

def resolved_inside_workspace(p: Path) -> bool:
    try:
        r = p.resolve()
        ws_s = str(ws)
        rs = str(r)
        return rs == ws_s or rs.startswith(ws_s + os.sep)
    except Exception:
        return False

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def is_finite_number(v) -> bool:
    if isinstance(v, bool):
        return False
    if not isinstance(v, (int, float)):
        return False
    try:
        return math.isfinite(float(v))
    except Exception:
        return False

def is_finite_nonneg(v) -> bool:
    return is_finite_number(v) and float(v) >= 0

def validate_metrics(metrics: dict, rid: str):
    if not isinstance(metrics, dict):
        return False
    if metrics.get("run_id") != rid:
        return False
    idea_id = metrics.get("idea_id")
    if not isinstance(idea_id, str) or not idea_id:
        return False
    if metrics.get("keep") is not True:
        return False
    if metrics.get("outcome") != "keep":
        return False
    execution = metrics.get("execution")
    if not isinstance(execution, dict) or execution.get("state") != "completed":
        return False
    evaluation = metrics.get("evaluation")
    if not isinstance(evaluation, dict) or evaluation.get("state") != "completed":
        return False
    # metric_main must be present with finite value
    metric_main = metrics.get("metric_main")
    if not isinstance(metric_main, dict):
        return False
    v = metric_main.get("value")
    if not is_finite_number(v):
        return False
    # fingerprint and evaluator_hash are validated when present; require evaluator_hash
    fingerprint = metrics.get("fingerprint")
    if not isinstance(fingerprint, dict):
        return False
    device = fingerprint.get("device")
    env = fingerprint.get("environment")
    if not isinstance(device, dict) or not isinstance(env, dict):
        return False
    if not isinstance(device.get("kind"), str) or not device.get("kind"):
        return False
    if not isinstance(device.get("count"), int) or isinstance(device.get("count"), bool):
        return False
    if not isinstance(env.get("python_version"), str) or not env.get("python_version"):
        return False
    if not isinstance(env.get("platform"), str) or not env.get("platform"):
        return False
    if not isinstance(env.get("package_lock_hash"), str):
        return False
    ev_hash = evaluation.get("evaluator_hash")
    if not isinstance(ev_hash, str) or not ev_hash:
        return False
    return True

def validate_verification(verification: dict, metrics: dict, rid: str):
    if not isinstance(verification, dict):
        return False
    if verification.get("run_id") != rid:
        return False
    if verification.get("idea_id") != metrics.get("idea_id"):
        return False
    if verification.get("keep") is not True:
        return False
    if verification.get("execution_state") != "completed":
        return False
    if verification.get("evaluation_state") != "completed":
        return False
    if verification.get("reproduction_state") != "completed":
        return False
    if verification.get("clean_reproduction_passed") is not True:
        return False
    if verification.get("integrity_passed") is not True:
        # integrity must be true for a valid keep
        return False
    # boolean fields must be exact bool
    for f in ("integrity_passed", "clean_reproduction_passed", "keep"):
        if type(verification.get(f)) is not bool:
            return False
    baseline = verification.get("baseline_metric")
    if not isinstance(baseline, dict):
        return False
    if not is_finite_number(baseline.get("value")):
        return False
    candidate = verification.get("candidate_metric")
    if not isinstance(candidate, dict):
        return False
    if not is_finite_number(candidate.get("value")):
        return False
    mv = metrics.get("metric_main", {}).get("value") if isinstance(metrics.get("metric_main"), dict) else None
    cv = candidate.get("value")
    if is_finite_number(mv) and is_finite_number(cv) and float(mv) != float(cv):
        return False
    delta = verification.get("delta")
    if not is_finite_number(delta):
        return False
    epsilon = verification.get("epsilon")
    if not is_finite_nonneg(epsilon):
        return False
    direction = verification.get("direction")
    if direction not in ("lower", "higher"):
        return False
    return True

def validate_cost(cost: dict, metrics: dict, verification: dict, rid: str):
    if not isinstance(cost, dict):
        return False
    if cost.get("run_id") != rid:
        return False
    if cost.get("idea_id") != metrics.get("idea_id"):
        return False
    if cost.get("reproduction_state") != "completed":
        return False
    requested = cost.get("requested")
    actual = cost.get("actual")
    if not isinstance(requested, dict) or not isinstance(actual, dict):
        return False
    if verification is not None and isinstance(verification, dict):
        if verification.get("reproduction_state") != cost.get("reproduction_state"):
            return False
    return True

def validate_terminal_marker(path: Path, rid: str, idea_id: str):
    if path_is_symlink(path):
        return False
    if not resolved_inside_workspace(path):
        return False
    rec = load_json(path)
    if not isinstance(rec, dict):
        return False
    if rec.get("run_id") != rid:
        return False
    if rec.get("idea_id") != idea_id:
        return False
    if rec.get("outcome") != "keep":
        return False
    if rec.get("terminal") is not True:
        return False
    return True

# Gather candidate run_ids from filesystem and from traces.jsonl
rids = set()
bases = [ws / "archive" / "papers", ws / "runs", ws / "traces"]
for base in bases:
    if not base.is_dir():
        continue
    if path_is_symlink(base):
        continue
    if not resolved_inside_workspace(base):
        continue
    try:
        for entry in base.iterdir():
            if not entry.is_dir():
                continue
            if path_is_symlink(entry):
                continue
            if not resolved_inside_workspace(entry):
                continue
            rid = entry.name
            if not is_safe_name(rid):
                continue
            rids.add(rid)
    except Exception:
        continue

jl = ws / "traces.jsonl"
if jl.is_file() and not path_is_symlink(jl) and resolved_inside_workspace(jl):
    try:
        for line in jl.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            rid = o.get("run_id")
            if not isinstance(rid, str):
                continue
            if not is_safe_name(rid):
                continue
            if o.get("keep") is True or o.get("outcome") == "keep":
                rids.add(rid)
    except Exception:
        pass

def is_keep_eligible(rid: str):
    # Canonical evidence directories in priority order: traces, runs, archive/papers
    # Each candidate must alone contain metrics.json, verification.json, cost.json
    canonical_candidates = [ws / "traces" / rid, ws / "runs" / rid, ws / "archive" / "papers" / rid]
    eligible_dir = None
    metrics = None
    verification = None
    cost = None
    for cand in canonical_candidates:
        if not cand.is_dir():
            continue
        if path_is_symlink(cand):
            continue
        if not resolved_inside_workspace(cand):
            continue
        m_p = cand / "metrics.json"
        v_p = cand / "verification.json"
        c_p = cand / "cost.json"
        # All three must exist as regular files, not symlinks, and resolve inside workspace
        missing = False
        for p in (m_p, v_p, c_p):
            if not p.is_file():
                missing = True
                break
            if path_is_symlink(p):
                missing = True
                break
            if not resolved_inside_workspace(p):
                missing = True
                break
        if missing:
            continue
        # Load and validate JSON well-formedness
        m = load_json(m_p)
        v = load_json(v_p)
        c = load_json(c_p)
        if m is None or v is None or c is None:
            continue
        if not isinstance(m, dict) or not isinstance(v, dict) or not isinstance(c, dict):
            continue
        if not validate_metrics(m, rid):
            continue
        if not validate_verification(v, m, rid):
            continue
        if not validate_cost(c, m, v, rid):
            continue
        # Terminal markers: both trace and run directories must exist and carry exact markers
        idea_id = m.get("idea_id")
        trace_marker = ws / "traces" / rid / "terminal.json"
        run_marker = ws / "runs" / rid / "terminal.json"
        # Both markers must exist as files, not symlinks, inside workspace
        markers_ok = True
        for mp in (trace_marker, run_marker):
            if not mp.is_file():
                markers_ok = False
                break
            if path_is_symlink(mp):
                markers_ok = False
                break
            if not resolved_inside_workspace(mp):
                markers_ok = False
                break
            if not validate_terminal_marker(mp, rid, idea_id):
                markers_ok = False
                break
        if not markers_ok:
            continue
        # This candidate is eligible; prefer first (traces before runs)
        eligible_dir = cand
        metrics = m
        verification = v
        cost = c
        break

    if eligible_dir is None:
        return None
    # Use mtime of the canonical evidence directory for recency
    try:
        ts = int(eligible_dir.stat().st_mtime)
    except Exception:
        ts = 0
    return (eligible_dir, ts)

eligible = []
for rid in rids:
    res = is_keep_eligible(rid)
    if res is not None:
        d, ts = res
        eligible.append((ts, rid, d))

if not eligible:
    sys.exit(0)

eligible.sort(key=lambda x: (x[0], x[1]))
best = eligible[-1]
print(str(best[2]))
PY
}

LATEST="$(find_latest_keep)"

if [ -z "$LATEST" ]; then
  echo "reproduce.sh: no keep archive/run found — run a flywheel keep first (no traces with keep=true present)" >&2
  exit 2
fi

if [ ! -d "$LATEST" ]; then
  echo "reproduce.sh: no keep archive/run found — run a flywheel keep first (no traces with keep=true present)" >&2
  exit 2
fi

# Reject symlinked evidence directory and paths outside workspace
if [ -L "$LATEST" ]; then
  echo "reproduce.sh: evidence directory is a symlink: $LATEST" >&2
  exit 2
fi
# Resolve and ensure inside workspace
if run_python -c "import sys; sys.exit(0)" >/dev/null 2>&1; then
  if ! run_python - "$LATEST" "$WORKSPACE" <<'PY' 2>/dev/null
import sys
from pathlib import Path
p = Path(sys.argv[1]).resolve()
ws = Path(sys.argv[2]).resolve()
import os
rs = str(p)
wss = str(ws)
if not (rs == wss or rs.startswith(wss + os.sep)):
    sys.exit(1)
PY
  then
    echo "reproduce.sh: evidence directory outside workspace: $LATEST" >&2
    exit 2
  fi
fi

# Path-traversal guard on selected run id
RUN_ID="$(basename "$LATEST")"
case "$RUN_ID" in
  *"/"* | *"\\"* | *".."* | "")
    echo "reproduce.sh: invalid run_id (path traversal): $RUN_ID" >&2
    exit 2
    ;;
esac
# Also validate against SAFE pattern via Python if available
if run_python -c "import sys; sys.exit(0)" >/dev/null 2>&1; then
  if ! run_python - "$RUN_ID" <<'PY' 2>/dev/null
import re, sys
SAFE=re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
if not SAFE.fullmatch(sys.argv[1]):
    sys.exit(1)
PY
  then
    echo "reproduce.sh: invalid run_id: $RUN_ID" >&2
    exit 2
  fi
fi

if ! run_python -c "import sys; sys.exit(0)" >/dev/null 2>&1; then
  echo "reproduce.sh: no python interpreter found (uv, python3 or python required)" >&2
  exit 2
fi

echo "reproduce.sh: latest keep is $RUN_ID ($LATEST)" >&2

# Execute fixed workspace-local reproduction entrypoint with argv separation.
# No shell interpretation of archive-controlled strings; no sh -c.
cd "$WORKSPACE"
if run_python - "$RUN_ID" "$WORKSPACE" <<'PY'
import sys
from pathlib import Path
import os
import re

run_id = sys.argv[1]
ws = Path(sys.argv[2]).resolve()
SAFE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
if not SAFE.fullmatch(run_id):
    print(f"reproduce.sh: invalid run_id: {run_id}", file=sys.stderr)
    sys.exit(2)

# Ensure workspaced trace_dir resolves inside workspace and is not symlink-escaped
trace_dir = ws / "traces" / run_id / "repro"
try:
    # Create repro dir safely; check parent chain not symlink
    trace_dir.mkdir(parents=True, exist_ok=True)
    resolved = trace_dir.resolve()
    ws_resolved = ws.resolve()
    if not (str(resolved) == str(ws_resolved) or str(resolved).startswith(str(ws_resolved) + os.sep)):
        print(f"reproduce.sh: trace_dir outside workspace: {resolved}", file=sys.stderr)
        sys.exit(2)
    # Reject if trace_dir itself is a symlink
    if trace_dir.is_symlink():
        print(f"reproduce.sh: trace_dir is symlink: {trace_dir}", file=sys.stderr)
        sys.exit(2)
except Exception as e:
    print(f"reproduce.sh: failed to prepare trace_dir: {e}", file=sys.stderr)
    sys.exit(2)

# Import fixed local runner
sys.path.insert(0, str(ws))
try:
    from experiment.run import main
except Exception as e:
    print(f"reproduce.sh: failed to import experiment.run: {e}", file=sys.stderr)
    sys.exit(1)

ctx = {"run_id": run_id, "trace_dir": str(trace_dir)}
try:
    result = main(ctx)
    # Print result for visibility; not used for control flow
    print(result)
    sys.exit(0)
except Exception as e:
    print(f"reproduce.sh: reproduction raised: {e}", file=sys.stderr)
    sys.exit(1)
PY
then
  echo "reproduce.sh: reproduction succeeded for $RUN_ID" >&2
  exit 0
else
  rc=$?
  if [ "$rc" -eq 2 ]; then
    exit 2
  fi
  echo "reproduce.sh: reproduction failed for $RUN_ID (command exited non-zero)" >&2
  exit 1
fi
