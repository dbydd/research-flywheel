#!/bin/sh
# reproduce.sh — locate latest keep archive/run and execute its recorded reference command or fail clearly.
# POSIX shell; Python stdlib only.
# Portability note (reversible): interpreter resolution prefers python3 then python
# so the script works on macOS (python3), Debian/Ubuntu minimal images (python),
# and containers with either binary. Revert by replacing $PY with literal python3
# if a fixed interpreter is desired. All recorded reference commands below use $PY.
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
WORKSPACE="$SCRIPT_DIR"

# Portability: resolve one Python interpreter for this script. Platforms differ
# (macOS ships python3, some Linux distros ship only python); prefer python3,
# fall back to python, and reuse the resolved value everywhere below so the
# recorded reference command and every inline parse use the same interpreter.
# Reversible: remove this block and replace $PY with python3 to restore pinned behaviour.
PY=""
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
fi

find_latest_keep() {
  # Search archive/papers/<run_id>, runs/<run_id>, traces/<run_id> in recency order
  BEST=""
  BEST_TS=0
  # Candidate sources: papers dirs and run dirs with mtime
  for base in "$WORKSPACE/archive/papers" "$WORKSPACE/runs" "$WORKSPACE/traces"; do
    [ -d "$base" ] || continue
    for d in "$base"/*; do
      [ -d "$d" ] || continue
      rid="$(basename "$d")"
      # only consider dirs that have metrics indicating keep or archive marker
      keep_marker=0
      if [ -f "$d/metrics.json" ] && grep -q '"keep"[[:space:]]*:[[:space:]]*true' "$d/metrics.json" 2>/dev/null; then
        keep_marker=1
      elif [ -f "$d/archive.json" ] && grep -q '"outcome"[[:space:]]*:[[:space:]]*"keep"' "$d/archive.json" 2>/dev/null; then
        keep_marker=1
      elif [ "$base" = "$WORKSPACE/archive/papers" ]; then
        keep_marker=1
      fi
      if [ "$keep_marker" -ne 1 ]; then
        continue
      fi
      # use mtime as recency; fallback to lexical sort
      mt=0
      if [ -n "$PY" ]; then
        mt="$("$PY" - "$d" <<'PY'
import os, sys
print(int(os.path.getmtime(sys.argv[1])))
PY
)"
      elif command -v stat >/dev/null 2>&1; then
        mt="$(stat -c %Y "$d" 2>/dev/null || stat -f %m "$d" 2>/dev/null || echo 0)"
      fi
      if [ -z "$mt" ]; then mt=0; fi
      # numeric compare
      if [ "$mt" -gt "$BEST_TS" ] 2>/dev/null; then
        BEST_TS="$mt"
        BEST="$d"
      else
        # fallback lexical newer wins if timestamps equal
        if [ -z "$BEST" ]; then BEST="$d"; fi
      fi
    done
  done
  printf "%s" "$BEST"
}

LATEST="$(find_latest_keep)"

if [ -z "$LATEST" ]; then
  # Also try traces.jsonl for latest keep event
  if [ -f "$WORKSPACE/traces.jsonl" ] && [ -n "$PY" ]; then
    LATEST2="$("$PY" - "$WORKSPACE/traces.jsonl" "$WORKSPACE" <<'PY'
import json, pathlib, sys
jl=pathlib.Path(sys.argv[1])
ws=pathlib.Path(sys.argv[2])
best=None
best_ts=""
for line in jl.read_text(encoding='utf-8').splitlines():
    try:
        o=json.loads(line)
        if o.get("keep") and o.get("run_id"):
            ts=o.get("ts","")
            if best is None or ts>best_ts:
                best=o["run_id"]; best_ts=ts
    except: continue
if best:
    for c in [ws/"archive"/"papers"/best, ws/"runs"/best, ws/"traces"/best]:
        if c.exists():
            print(c); break
    else:
        print(ws/"traces"/best)
PY
)"
    LATEST="$LATEST2"
  fi
fi

if [ -z "$LATEST" ] || [ ! -d "$LATEST" ]; then
  echo "reproduce.sh: no keep archive/run found — run a flywheel keep first (no traces with keep=true present)" >&2
  exit 2
fi

# Resolve canonical trace dir for the run
RUN_ID="$(basename "$LATEST")"
if [ -d "$WORKSPACE/traces/$RUN_ID" ]; then
  TRACE_DIR="$WORKSPACE/traces/$RUN_ID"
elif [ -d "$WORKSPACE/runs/$RUN_ID" ]; then
  TRACE_DIR="$WORKSPACE/runs/$RUN_ID"
else
  TRACE_DIR="$LATEST"
fi

echo "reproduce.sh: latest keep is $RUN_ID ($LATEST)" >&2

# Try recorded reference command sources: tool-call.json, verification, metrics, then default evaluator command
CMD=""
if [ -f "$TRACE_DIR/tool-call.json" ] && [ -n "$PY" ]; then
  CMD="$("$PY" - "$TRACE_DIR/tool-call.json" <<'PY'
import json, sys
data=json.loads(open(sys.argv[1],encoding='utf-8').read())
# look for calls array with reference command or use default
for c in data.get("calls",[]):
    if isinstance(c, dict) and c.get("command"):
        print(c["command"]); break
PY
)"
elif [ -f "$WORKSPACE/traces/$RUN_ID/tool-call.json" ] && [ -n "$PY" ]; then
  CMD="$("$PY" - "$WORKSPACE/traces/$RUN_ID/tool-call.json" <<'PY'
import json,sys
data=json.loads(open(sys.argv[1],encoding='utf-8').read())
for c in data.get("calls",[]):
    if isinstance(c, dict) and c.get("command"):
        print(c["command"]); break
PY
)"
fi

# Default reference reproduction command: re-execute experiment via evaluation/prepare evaluator path
if [ -z "$CMD" ]; then
  # Reversible portability: use resolved $PY so the recorded command matches the host interpreter.
  # If PY is empty (no python found), leave CMD empty and let the missing-command exit handle it.
  if [ -n "$PY" ]; then
    CMD="$PY -c \"from pathlib import Path; from experiment.run import main; print(main({'run_id': '$RUN_ID','trace_dir': 'traces/$RUN_ID/repro'}))\""
  else
    CMD=""
  fi
fi

# Also support explicit command file if flywheel wrote it
for cand in "$TRACE_DIR/command.txt" "$TRACE_DIR/reproduce-command.txt" "$TRACE_DIR/tool-call.json"; do
  if [ -f "$cand" ] && head -n1 "$cand" | grep -qE 'python|bash|make' 2>/dev/null; then
    CMD="$(head -n1 "$cand")"
    break
  fi
done

if [ -z "$CMD" ]; then
  echo "reproduce.sh: no recorded reference command for $RUN_ID — traces present but tool-call/command missing" >&2
  exit 3
fi

echo "reproduce.sh: executing: $CMD" >&2
# Execute in workspace root
cd "$WORKSPACE"
# Use sh -c so quoted python -c works; capture result
if sh -c "$CMD"; then
  echo "reproduce.sh: reproduction succeeded for $RUN_ID" >&2
  exit 0
else
  echo "reproduce.sh: reproduction failed for $RUN_ID (command exited non-zero)" >&2
  exit 1
fi
