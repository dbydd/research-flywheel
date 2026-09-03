#!/bin/sh
# post-eval.sh — deterministic keep/discard recording, never deletes unrelated files.
# Python via uv-first helper: prefers 'uv run --directory "$WORKSPACE" --frozen python' when uv and uv.lock exist, then python3, then python.
# Usage: bash orchestration/hooks/post-eval.sh [traces/<run_id>/metrics.json or traces/<run_id>]
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
WORKSPACE="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

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

ARG=""
if [ $# -ge 1 ]; then
  ARG="$1"
  case "$ARG" in
    /*) ;;
    *) ARG="$WORKSPACE/$ARG" ;;
  esac
fi

TRACE_DIR=""
if [ -n "$ARG" ]; then
  if [ -d "$ARG" ]; then
    TRACE_DIR="$ARG"
  elif [ -f "$ARG" ]; then
    TRACE_DIR="$(CDPATH= cd -- "$(dirname "$ARG")" && pwd)"
  else
    echo "post-eval: argument not found: $ARG" >&2
    exit 1
  fi
else
  # latest traces/<run_id>/metrics.json
  TRACE_DIR=""
  if [ -d "$WORKSPACE/traces" ] && ls -t "$WORKSPACE/traces" >/dev/null 2>&1; then
    for d in $(ls -t "$WORKSPACE/traces" 2>/dev/null); do
      if [ -f "$WORKSPACE/traces/$d/metrics.json" ]; then
        TRACE_DIR="$WORKSPACE/traces/$d"
        break
      fi
    done
  fi
  if [ -z "$TRACE_DIR" ]; then
    for f in "$WORKSPACE/traces"/*/metrics.json; do
      [ -f "$f" ] || continue
      TRACE_DIR="$(CDPATH= cd -- "$(dirname "$f")" && pwd)"
      break
    done
  fi
fi

if [ -z "$TRACE_DIR" ] || [ ! -d "$TRACE_DIR" ]; then
  echo "post-eval: no trace dir found" >&2
  exit 1
fi

# Resolve run_id from directory name
RUN_ID="$(basename "$TRACE_DIR")"

METRICS="$TRACE_DIR/metrics.json"
VERIFICATION="$TRACE_DIR/verification.json"
MUTATION="$TRACE_DIR/mutation.json"
COST="$TRACE_DIR/cost.json"

if [ ! -f "$METRICS" ]; then
  echo "post-eval: missing $METRICS" >&2
  exit 1
fi

# Compute outcome/keep using python stdlib so result matches native evaluator semantics (uv-first)

OUTCOME=""
KEEP=""
DELTA=""
REASON=""
EVAL_STATE=""
EXEC_STATE=""
REPRO_STATE=""

if run_python -c "import sys" >/dev/null 2>&1; then
  PYOUT="$(run_python - "$METRICS" "$VERIFICATION" <<'PY'
import json, sys
m=json.loads(open(sys.argv[1],encoding='utf-8').read())
v={}
try: v=json.loads(open(sys.argv[2],encoding='utf-8').read())
except: pass
print(json.dumps({
  "outcome": m.get("outcome") or v.get("outcome") or "discard",
  "keep": bool(m.get("keep") if isinstance(m.get("keep"), bool) else v.get("keep") if isinstance(v.get("keep"), bool) else False),
  "delta": m.get("delta", v.get("delta")),
  "reason": m.get("reason",""),
  "evaluation_state": (m.get("evaluation") or {}).get("state") or v.get("evaluation_state") or "",
  "execution_state": (m.get("execution") or {}).get("state") or v.get("execution_state") or "",
  "reproduction_state": v.get("reproduction_state",""),
  "idea_id": m.get("idea_id") or v.get("idea_id") or "",
  "metric_main": m.get("metric_main") or v.get("candidate_metric"),
  "baseline": v.get("baseline_metric"),
}))
PY
)"
  # shell-extract without jq via python
  OUTCOME="$(run_python -c "import json,sys; print(json.loads(open(sys.argv[1]).read())['parsed']['outcome'])" "$PYOUT" 2>/dev/null || run_python -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('outcome','discard'))" "$PYOUT")"
  # simpler: re-parse using python helper
  EVAL_OUT="$(run_python - "$PYOUT" <<'PY'
import json,sys
payload=json.loads(open(sys.argv[1],encoding='utf-8').read()) if sys.argv[1].endswith('.json') else json.loads(sys.argv[1])
# if argv1 was raw json string, parse directly
try:
    data=json.loads(sys.argv[1])
except:
    data=json.loads(open(sys.argv[1],encoding='utf-8').read())
print(data.get("outcome","discard"))
print("1" if data.get("keep") else "0")
print(data.get("reason",""))
PY
)"
  # Fallback structured parse: just re-run a tiny extractor
  OUTCOME="$(run_python - "$METRICS" <<'PY'
import json,sys
m=json.loads(open(sys.argv[1],encoding='utf-8').read())
print(m.get("outcome","discard"))
PY
)"
  KEEP="$(run_python - "$METRICS" <<'PY'
import json,sys
m=json.loads(open(sys.argv[1],encoding='utf-8').read())
print("true" if m.get("keep") else "false")
PY
)"
  # Normalize
  if [ "$KEEP" = "true" ]; then KEEP_VAL=true; else KEEP_VAL=false; fi
else
  # shell fallback — grep keep
  if grep -q '"keep"[[:space:]]*:[[:space:]]*true' "$METRICS" 2>/dev/null; then
    KEEP_VAL=true
    OUTCOME=keep
  else
    KEEP_VAL=false
    OUTCOME=discard
    # downgrade to execution_error if error.json exists
    if [ -f "$TRACE_DIR/error.json" ]; then OUTCOME=execution_error; fi
  fi
fi

# Re-derive outcome robustly via python single call
if run_python -c "import sys" >/dev/null 2>&1; then
  RESULT_JSON="$(run_python - "$TRACE_DIR" <<'PY'
import json, pathlib, sys
td=pathlib.Path(sys.argv[1])
m=json.loads((td/"metrics.json").read_text(encoding='utf-8'))
v={}
try: v=json.loads((td/"verification.json").read_text(encoding='utf-8'))
except: pass
outcome=m.get("outcome") or ("keep" if m.get("keep") else ("execution_error" if (td/"error.json").exists() else "discard"))
# trust execution_state from verification/metrics for inconclusive classification
eval_state=(m.get("evaluation") or {}).get("state") or v.get("evaluation_state")
exec_state=(m.get("execution") or {}).get("state") or v.get("execution_state")
repro_state=v.get("reproduction_state","")
if (td/"error.json").exists() and outcome!="keep":
    # if metrics says execution failed, keep execution_error
    if exec_state=="failed":
        outcome="execution_error"
    elif eval_state=="failed" and repro_state=="failed":
        outcome="execution_error"
print(json.dumps({"outcome":outcome,"keep":bool(m.get("keep")), "reason": m.get("reason",""), "metric_main": m.get("metric_main"), "baseline": v.get("baseline_metric"), "idea_id": m.get("idea_id") or v.get("idea_id"), "eval_state": eval_state, "exec_state": exec_state, "repro_state": repro_state}))
PY
)"
  OUTCOME="$(printf "%s" "$RESULT_JSON" | run_python -c "import json,sys; print(json.loads(sys.argv[1]).get('outcome','discard'))" "$RESULT_JSON")"
  KEEP_STR="$(printf "%s" "$RESULT_JSON" | run_python -c "import json,sys; print('true' if json.loads(sys.argv[1]).get('keep') else 'false')" "$RESULT_JSON")"
  REASON="$(printf "%s" "$RESULT_JSON" | run_python -c "import json,sys; print(json.loads(sys.argv[1]).get('reason',''))" "$RESULT_JSON")"
else
  REASON=""
fi

# Global traces.jsonl append (dedup by run_id)
TRACES_JSONL="$WORKSPACE/traces.jsonl"
mkdir -p "$(dirname "$TRACES_JSONL")"
touch "$TRACES_JSONL"
if run_python -c "import sys" >/dev/null 2>&1; then
  run_python - "$TRACES_JSONL" "$RESULT_JSON" "$RUN_ID" <<'PY'
import json, pathlib, sys
jl_path=pathlib.Path(sys.argv[1])
payload=json.loads(sys.argv[2])
run_id=sys.argv[3]
existing=set()
if jl_path.exists():
    for line in jl_path.read_text(encoding='utf-8').splitlines():
        try: existing.add(json.loads(line).get("run_id"))
        except: continue
if run_id not in existing:
    import datetime
    ts=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    entry={"ts": ts, "run_id": run_id, "idea_id": payload.get("idea_id"), "event": payload.get("outcome","unknown"), "outcome": payload.get("outcome"), "keep": payload.get("keep"), "metric_main": payload.get("metric_main")}
    with open(jl_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False)+"\n")
PY
else
  if ! grep -q "\"run_id\"[[:space:]]*:[[:space:]]*\"$RUN_ID\"" "$TRACES_JSONL" 2>/dev/null; then
    printf '{"run_id":"%s","outcome":"%s"}\n' "$RUN_ID" "$OUTCOME" >> "$TRACES_JSONL"
  fi
fi

# Archive: keep -> archive/papers/<run_id>, else -> archive/failed.jsonl (dedup)
ARCHIVE_FAILED="$WORKSPACE/archive/failed.jsonl"
mkdir -p "$(dirname "$ARCHIVE_FAILED")"
touch "$ARCHIVE_FAILED"

if [ "$OUTCOME" = "keep" ]; then
  PAPER_DIR="$WORKSPACE/archive/papers/$RUN_ID"
  mkdir -p "$PAPER_DIR"
  # preserve report if exists; otherwise copy trace report
  if [ -f "$TRACE_DIR/report.md" ]; then
    cp "$TRACE_DIR/report.md" "$PAPER_DIR/paper.md" 2>/dev/null || true
  elif [ -f "$WORKSPACE/reports/report.md" ]; then
    cp "$WORKSPACE/reports/report.md" "$PAPER_DIR/paper.md" 2>/dev/null || true
  else
    printf "# Paper %s\n\n%s\n" "$RUN_ID" "$REASON" > "$PAPER_DIR/paper.md"
  fi
  if [ -f "$METRICS" ]; then
    cp "$METRICS" "$PAPER_DIR/metrics.json" 2>/dev/null || true
  fi
  # keep trace record
  if run_python -c "import sys" >/dev/null 2>&1; then
    run_python - "$TRACE_DIR" "$PAPER_DIR" <<'PY'
import json, pathlib, sys, datetime
td=pathlib.Path(sys.argv[1])
pd=pathlib.Path(sys.argv[2])
(pd/"archive.json").write_text(json.dumps({"run_id": td.name, "outcome": "keep", "archived_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}, indent=2)+"\n", encoding='utf-8')
PY
  fi
  echo "post-eval: archived keep $RUN_ID -> archive/papers/$RUN_ID (preserving all other archives)" >&2
else
  # discard/inconclusive/execution_error -> failed.jsonl
  if run_python -c "import sys" >/dev/null 2>&1; then
    run_python - "$ARCHIVE_FAILED" "$RESULT_JSON" "$RUN_ID" <<'PY'
import json, pathlib, sys, datetime
fp=pathlib.Path(sys.argv[1])
payload=json.loads(sys.argv[2])
run_id=sys.argv[3]
existing=set()
if fp.exists():
    for line in fp.read_text(encoding='utf-8').splitlines():
        try: existing.add(json.loads(line).get("run_id"))
        except: continue
if run_id not in existing:
    entry={"run_id": run_id, "idea_id": payload.get("idea_id"), "outcome": payload.get("outcome","discard"), "reason": payload.get("reason",""), "metric_main": payload.get("metric_main"), "baseline": payload.get("baseline"), "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "evidence": f"traces/{run_id}/metrics.json"}
    open(fp,"a",encoding="utf-8").write(json.dumps(entry, ensure_ascii=False)+"\n")
PY
  else
    if ! grep -q "\"run_id\"[[:space:]]*:[[:space:]]*\"$RUN_ID\"" "$ARCHIVE_FAILED" 2>/dev/null; then
      printf '{"run_id":"%s","outcome":"%s","ts":"post-eval"}\n' "$RUN_ID" "$OUTCOME" >> "$ARCHIVE_FAILED"
    fi
  fi
  echo "post-eval: recorded $OUTCOME $RUN_ID -> archive/failed.jsonl (no unrelated files deleted)" >&2
fi

# Safe cleanup: only remove candidate worktree/dir for this run_id, never whole trees
CANDIDATE_DIR="$TRACE_DIR/candidate"
if [ -d "$CANDIDATE_DIR" ] && [ "$OUTCOME" != "keep" ]; then
  # Only remove the per-run candidate, and only if branch cleanup is requested via env var
  # Default: keep candidate for audit; do not delete automatically — assignment says without deleting unrelated files
  # So we do NOT delete retained traces/runs/reports; just note location
  echo "post-eval: retaining candidate $CANDIDATE_DIR for audit" >&2
fi
# Optional: remove ephemeral git candidate branch for non-keep only when explicitly allowed
if [ "$OUTCOME" != "keep" ] && [ -n "${POST_EVAL_DELETE_BRANCH:-}" ] && [ -d "$WORKSPACE/.git" ] && command -v git >/dev/null 2>&1; then
  BRANCH=""
  if [ -f "$MUTATION" ] && run_python -c "import sys" >/dev/null 2>&1; then
    BRANCH="$(run_python - "$MUTATION" <<'PY'
import json
print(json.loads(open(sys.argv[1],encoding='utf-8').read()).get("branch_name",""))
PY
)"
  fi
  if [ -n "$BRANCH" ]; then
    git -C "$WORKSPACE" branch -D "$BRANCH" >/dev/null 2>&1 || true
    echo "post-eval: deleted non-keep branch $BRANCH (POST_EVAL_DELETE_BRANCH set)" >&2
  fi
fi

# If keep, do not delete candidate; tag handling is done by flywheel. Just exit.
exit 0
