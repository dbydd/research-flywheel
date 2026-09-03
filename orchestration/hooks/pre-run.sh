#!/bin/sh
# pre-run.sh — deterministic integrity and mutable-path gate, POSIX shell + Python stdlib fallback.
# Portability (reversible): every Python invocation prefers python3 then python, with
# sha256sum/shasum as final fallback, so the gate works on macOS (python3) and
# minimal Linux (python). Revert by collapsing python3/python branches to a single
# hard-coded python3 branch; no functional change if python3 is guaranteed.
# Usage: bash orchestration/hooks/pre-run.sh [traces/<run_id>/baseline.json]
# Resolves workspace from script location; works from any cwd.
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
WORKSPACE="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

BASELINE=""
if [ $# -ge 1 ]; then
  BASELINE="$1"
  case "$BASELINE" in
    /*) ;;
    *) BASELINE="$WORKSPACE/$BASELINE" ;;
  esac
else
  # find latest traces/<run_id>/baseline.json
  LATEST=""
  if [ -d "$WORKSPACE/traces" ]; then
    # POSIX: use ls -t if available; fallback to find + sort
    if ls -t "$WORKSPACE/traces" >/dev/null 2>&1; then
      for d in $(ls -t "$WORKSPACE/traces" 2>/dev/null); do
        if [ -f "$WORKSPACE/traces/$d/baseline.json" ]; then
          LATEST="$WORKSPACE/traces/$d/baseline.json"
          break
        fi
      done
    fi
    if [ -z "$LATEST" ]; then
      for f in "$WORKSPACE/traces"/*/baseline.json; do
        [ -f "$f" ] || continue
        LATEST="$f"
        break
      done
    fi
  fi
  BASELINE="$LATEST"
fi

if [ -z "$BASELINE" ] || [ ! -f "$BASELINE" ]; then
  echo "pre-run: no baseline.json found (expected traces/<run_id>/baseline.json)" >&2
  exit 1
fi

TRACE_DIR="$(CDPATH= cd -- "$(dirname "$BASELINE")" && pwd)"
MUTATION="$TRACE_DIR/mutation.json"

# Helpers: compute sha256 via python stdlib (fallback to sha256sum/shasum)
sha256_of_file() {
  _f="$1"
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "import hashlib,sys; print('sha256:'+hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$_f"
  elif command -v python >/dev/null 2>&1; then
    python -c "import hashlib,sys; print('sha256:'+hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$_f"
  elif command -v sha256sum >/dev/null 2>&1; then
    printf "sha256:%s" "$(sha256sum "$_f" | cut -d' ' -f1)"
  elif command -v shasum >/dev/null 2>&1; then
    printf "sha256:%s" "$(shasum -a 256 "$_f" | cut -d' ' -f1)"
  else
    echo "pre-run: no sha256 tool available" >&2
    return 1
  fi
}

# Extract integrity_paths and baseline hashes, mutable_paths from baseline.json or program.md fallback
# Use python for reliable JSON parsing when available
INTEGRITY_LIST=""
BASELINE_HASHES_JSON=""
MUTABLE_LIST=""

if command -v python3 >/dev/null 2>&1; then
  PY_JSON="$(python3 - "$BASELINE" <<'PY'
import json,sys
p=sys.argv[1]
data=json.loads(open(p,encoding='utf-8').read())
profile=data.get('profile',{})
integrity_paths=data.get('integrity_paths') or profile.get('integrity_paths') or ["program.md","evaluation/prepare.py","capabilities/registry.json"]
mutable_paths=profile.get('mutable_paths') or ["experiment/run.py"]
integrity_hashes=data.get('integrity_hashes',{})
# print tab-separated for shell
print(";".join(integrity_paths))
print(json.dumps(integrity_hashes))
print(";".join(mutable_paths))
PY
)"
  INTEGRITY_LIST="$(printf "%s" "$PY_JSON" | sed -n '1p')"
  BASELINE_HASHES_JSON="$(printf "%s" "$PY_JSON" | sed -n '2p')"
  MUTABLE_LIST="$(printf "%s" "$PY_JSON" | sed -n '3p')"
elif command -v python >/dev/null 2>&1; then
  PY_JSON="$(python - "$BASELINE" <<'PY'
import json,sys
p=sys.argv[1]
data=json.loads(open(p,encoding='utf-8').read())
profile=data.get('profile',{})
integrity_paths=data.get('integrity_paths') or profile.get('integrity_paths') or ["program.md","evaluation/prepare.py","capabilities/registry.json"]
mutable_paths=profile.get('mutable_paths') or ["experiment/run.py"]
integrity_hashes=data.get('integrity_hashes',{})
print(";".join(integrity_paths))
print(json.dumps(integrity_hashes))
print(";".join(mutable_paths))
PY
)"
  INTEGRITY_LIST="$(printf "%s" "$PY_JSON" | sed -n '1p')"
  BASELINE_HASHES_JSON="$(printf "%s" "$PY_JSON" | sed -n '2p')"
  MUTABLE_LIST="$(printf "%s" "$PY_JSON" | sed -n '3p')"
else
  # fallback: hardcode reference profile values
  INTEGRITY_LIST="program.md;evaluation/prepare.py;capabilities/registry.json"
  MUTABLE_LIST="experiment/run.py"
  BASELINE_HASHES_JSON="{}"
fi

# Integrity check
INTEGRITY_PASSED=1
for rel in $(printf "%s" "$INTEGRITY_LIST" | tr ';' ' '); do
  [ -n "$rel" ] || continue
  FULL="$WORKSPACE/$rel"
  if [ ! -f "$FULL" ]; then
    echo "pre-run: integrity file missing: $rel" >&2
    INTEGRITY_PASSED=0
    continue
  fi
  CURRENT="$(sha256_of_file "$FULL" 2>/dev/null || echo "sha256:missing")"
  # extract expected hash from baseline JSON via python if possible
  EXPECTED=""
  if command -v python3 >/dev/null 2>&1; then
    EXPECTED="$(python3 - "$BASELINE" "$rel" <<'PY'
import json,sys
baseline=json.loads(open(sys.argv[1],encoding='utf-8').read())
hashes=baseline.get('integrity_hashes',{})
print(hashes.get(sys.argv[2],""))
PY
)"
  elif command -v python >/dev/null 2>&1; then
    EXPECTED="$(python - "$BASELINE" "$rel" <<'PY'
import json,sys
baseline=json.loads(open(sys.argv[1],encoding='utf-8').read())
hashes=baseline.get('integrity_hashes',{})
print(hashes.get(sys.argv[2],""))
PY
)"
  fi
  if [ -n "$EXPECTED" ] && [ "$CURRENT" != "$EXPECTED" ]; then
    echo "pre-run: integrity mismatch: $rel expected $EXPECTED got $CURRENT" >&2
    INTEGRITY_PASSED=0
  fi
done

# Changed paths: prefer recorded mutation/candidate-branch, not whole workspace diff
CHANGED=""
# 1) Prefer existing mutation.json changed_paths (flywheel writes this before pre-run)
if [ -f "$MUTATION" ]; then
  if command -v python3 >/dev/null 2>&1; then
    CHANGED="$(python3 - "$MUTATION" <<'PY'
import json
try:
    data=json.loads(open(sys.argv[1],encoding='utf-8').read())
    print(";".join(data.get("changed_paths",[])))
except:
    print("")
PY
)"
  elif command -v python >/dev/null 2>&1; then
    CHANGED="$(python - "$MUTATION" <<'PY'
import json
try:
    data=json.loads(open(sys.argv[1],encoding='utf-8').read())
    print(";".join(data.get("changed_paths",[])))
except:
    print("")
PY
)"
  fi
fi
# 2) If mutation has no changed_paths, try branch diff vs baseline SHA
if [ -z "$CHANGED" ] && [ -d "$WORKSPACE/.git" ] && command -v git >/dev/null 2>&1; then
  _B_SHA=""
  if command -v python3 >/dev/null 2>&1; then
    _B_SHA="$(python3 - "$BASELINE" <<'PY'
import json
try: print(json.loads(open(sys.argv[1],encoding='utf-8').read()).get("git",{}).get("head",""))
except: print("")
PY
)"
  elif command -v python >/dev/null 2>&1; then
    _B_SHA="$(python - "$BASELINE" <<'PY'
import json
try: print(json.loads(open(sys.argv[1],encoding='utf-8').read()).get("git",{}).get("head",""))
except: print("")
PY
)"
  fi
  _B_NAME=""
  if [ -f "$MUTATION" ] && command -v python3 >/dev/null 2>&1; then
    _B_NAME="$(python3 - "$MUTATION" <<'PY'
import json
try: print(json.loads(open(sys.argv[1],encoding='utf-8').read()).get("branch_name",""))
except: print("")
PY
)"
  elif [ -f "$MUTATION" ] && command -v python >/dev/null 2>&1; then
    _B_NAME="$(python - "$MUTATION" <<'PY'
import json
try: print(json.loads(open(sys.argv[1],encoding='utf-8').read()).get("branch_name",""))
except: print("")
PY
)"
  fi
  if [ -n "$_B_SHA" ] && [ -n "$_B_NAME" ] && git -C "$WORKSPACE" rev-parse --verify "$_B_NAME" >/dev/null 2>&1; then
    _diff="$(git -C "$WORKSPACE" diff --name-only "${_B_SHA}..${_B_NAME}" 2>/dev/null || true)"
    if [ -n "$_diff" ]; then
      CHANGED="$(printf "%s" "$_diff" | tr '\n' ';' | sed 's/;*$//')"
    fi
  fi
fi
# 3) Fallback: candidate dir contents for mutable audit
if [ -z "$CHANGED" ] && [ -d "$TRACE_DIR/candidate" ]; then
  _cand=""
  for mp in $(printf "%s" "$MUTABLE_LIST" | tr ';' ' '); do
    if [ -f "$TRACE_DIR/candidate/$mp" ]; then
      if [ -n "$_cand" ]; then _cand="${_cand};$mp"; else _cand="$mp"; fi
    fi
  done
  if [ -n "$_cand" ]; then CHANGED="$_cand"; fi
fi

# Normalize empty to ""
if [ -z "$CHANGED" ]; then
  CHANGED=""
fi

# Mutable gate: every changed path must match a mutable pattern (fnmatch support)
MUTABLE_PASSED=1
if [ -n "$CHANGED" ]; then
  for cp in $(printf "%s" "$CHANGED" | tr ';' ' '); do
    [ -n "$cp" ] || continue
    MATCHED=0
    for pat in $(printf "%s" "$MUTABLE_LIST" | tr ';' ' '); do
      [ -n "$pat" ] || continue
      # use python fnmatch when available for glob patterns
      if command -v python3 >/dev/null 2>&1; then
        _m="$(python3 - "$cp" "$pat" <<'PY'
import fnmatch,sys
print("1" if fnmatch.fnmatch(sys.argv[1], sys.argv[2]) or sys.argv[1]==sys.argv[2] else "0")
PY
)"
      elif command -v python >/dev/null 2>&1; then
        _m="$(python - "$cp" "$pat" <<'PY'
import fnmatch,sys
print("1" if fnmatch.fnmatch(sys.argv[1], sys.argv[2]) or sys.argv[1]==sys.argv[2] else "0")
PY
)"
      else
        # fallback: exact match or prefix match for ** patterns
        case "$cp" in
          $pat) _m=1 ;;
          *) _m=0 ;;
        esac
      fi
      if [ "$_m" = "1" ]; then MATCHED=1; break; fi
    done
    if [ "$MATCHED" -ne 1 ]; then
      echo "pre-run: mutable-path violation: $cp not in $MUTABLE_LIST" >&2
      MUTABLE_PASSED=0
    fi
  done
fi

GATE="pass"
if [ "$INTEGRITY_PASSED" -ne 1 ] || [ "$MUTABLE_PASSED" -ne 1 ]; then
  GATE="fail"
fi

# Write mutation.json — merge with existing if present, else create
if command -v python3 >/dev/null 2>&1; then
  python3 - "$BASELINE" "$MUTATION" "$GATE" "$INTEGRITY_PASSED" "$MUTABLE_PASSED" "$CHANGED" <<'PY'
import json, sys
from pathlib import Path
baseline_path, mutation_path, gate, ip, mp, changed = sys.argv[1:7]
baseline=json.loads(Path(baseline_path).read_text(encoding='utf-8'))
existing={}
try:
    existing=json.loads(Path(mutation_path).read_text(encoding='utf-8'))
except: pass
changed_list=[c for c in changed.split(';') if c] if changed else []
existing.update({
    "run_id": baseline.get("run_id"),
    "idea_id": baseline.get("idea_id"),
    "baseline_sha": baseline.get("git",{}).get("head"),
    "integrity_gate": gate,
    "integrity_passed": ip=="1",
    "mutable_gate_passed": mp=="1",
    "changed_paths": changed_list,
})
Path(mutation_path).parent.mkdir(parents=True, exist_ok=True)
import tempfile, os
tmp=Path(str(mutation_path)+".tmp")
tmp.write_text(json.dumps(existing, indent=2)+"\n", encoding='utf-8')
tmp.replace(mutation_path)
print(json.dumps({"mutation": str(mutation_path), "gate": gate}))
PY
elif command -v python >/dev/null 2>&1; then
  python - "$BASELINE" "$MUTATION" "$GATE" "$INTEGRITY_PASSED" "$MUTABLE_PASSED" "$CHANGED" <<'PY'
import json, sys
from pathlib import Path
baseline_path, mutation_path, gate, ip, mp, changed = sys.argv[1:7]
baseline=json.loads(Path(baseline_path).read_text(encoding='utf-8'))
existing={}
try:
    existing=json.loads(Path(mutation_path).read_text(encoding='utf-8'))
except: pass
changed_list=[c for c in changed.split(';') if c] if changed else []
existing.update({
    "run_id": baseline.get("run_id"),
    "idea_id": baseline.get("idea_id"),
    "baseline_sha": baseline.get("git",{}).get("head"),
    "integrity_gate": gate,
    "integrity_passed": ip=="1",
    "mutable_gate_passed": mp=="1",
    "changed_paths": changed_list,
})
Path(mutation_path).parent.mkdir(parents=True, exist_ok=True)
import tempfile, os
tmp=Path(str(mutation_path)+".tmp")
tmp.write_text(json.dumps(existing, indent=2)+"\n", encoding='utf-8')
tmp.replace(mutation_path)
print(json.dumps({"mutation": str(mutation_path), "gate": gate}))
PY
else
  # fallback shell write
  printf '{\n  "integrity_gate": "%s",\n  "integrity_passed": %s,\n  "mutable_gate_passed": %s\n}\n' "$GATE" "$INTEGRITY_PASSED" "$MUTABLE_PASSED" > "$MUTATION.tmp"
  mv "$MUTATION.tmp" "$MUTATION"
fi

echo "pre-run: gate=$GATE trace=$TRACE_DIR" >&2
if [ "$GATE" = "fail" ]; then
  echo "pre-run: gate failed — see $MUTATION" >&2
  exit 2
fi
exit 0
