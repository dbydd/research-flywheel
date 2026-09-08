#!/usr/bin/env bash
# Promote a configured flywheel clone to a live theme.
#
# Usage: ./scripts/promote.sh [--dry-run] [--theme <slug>] [--force-stage]
#
# Contract: BOOTSTRAP.md section 6. Checks (section 6.3) run first; any
# failure exits 1 with the stage unchanged. --dry-run runs checks and prints
# the planned actions with zero writes. Already live refuses to run.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DRY_RUN=0
THEME=""
FORCE_STAGE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --theme) THEME="${2:-}"; shift 2 ;;
    --force-stage) FORCE_STAGE=1; shift ;;
    *) echo "unknown flag: $1 (see BOOTSTRAP.md section 6.1)" >&2; exit 1 ;;
  esac
done

fail() { echo "FAIL: $1" >&2; exit 1; }
warn() { echo "WARN: $1"; }
info() { echo "$1"; }

# --- stage gate -------------------------------------------------------------
STAGE="configuring"
if [ -f .onlyne/flywheel.json ]; then
  STAGE="$(python3 -c "import json;print(json.load(open('.onlyne/flywheel.json')).get('stage','configuring'))" 2>/dev/null || echo configuring)"
fi
if [ "$STAGE" = "live" ]; then
  fail "already live (stage=live in .onlyne/flywheel.json); refusing to re-promote"
fi
case "$STAGE" in
  configuring|checking) ;;
  *) fail "unexpected stage '$STAGE' (expected configuring or checking)" ;;
esac

# --- check 1: THEME slots filled -------------------------------------------
[ -f .agents/AGENTS.md ] || fail ".agents/AGENTS.md MISSING"
if grep -q "<!-- THEME:" .agents/AGENTS.md; then
  LEFT="$(grep -o "<!-- THEME:[a-z-]*" .agents/AGENTS.md | sort -u | tr '\n' ' ')"
  fail "THEME slots REMAIN:: $LEFT"
fi

# --- collect roles (single source of truth) ---------------------------------
[ -d .agents/.schedule ] || fail ".agents/.schedule/ MISSING"
ROLES="$(ls .agents/.schedule/ | tr '\n' ' ')"
[ -n "$ROLES" ] || fail ".agents/.schedule/  needs >=1 role dir"

# --- check 2: each role template --------------------------------------------
for r in $ROLES; do
  T=".agents/.schedule/$r/template.workspace.jsonc"
  [ -f "$T" ] || fail "$T MISSING"
  python3 - "$T" "$r" <<'PY_CHECK2' || fail "$T INVALID (reason above)"
import json,sys
p, want = sys.argv[1], sys.argv[2]
d = json.load(open(p))
assert d.get("name") == want, f"name={d.get('name')!r} vs dirname {want!r} MISMATCH"
assert d.get("role"), "role EMPTY"
m = d.get("model") or {}
assert m.get("provider") and m.get("model") and m.get("effort"), "model.provider/model/effort REQUIRED"
PY_CHECK2
done

# --- check 3: exactly one entry role -----------------------------------------
STAR_COUNT="$(grep -c '^| .* ★' .agents/AGENTS.md || true)"
[ "$STAR_COUNT" = "1" ] || fail "star-table rows=$STAR_COUNT (want exactly 1)"
ENTRY="$(python3 - <<'PY_ENTRY'
import re
text = open(".agents/AGENTS.md").read()
rows = [l for l in text.splitlines() if l.startswith("|") and "★" in l]
name = rows[0].split("|")[1].strip() if rows else ""
print(name)
PY_ENTRY
)"
[ -n "$ENTRY" ] || fail "entry_role EMPTY (star row parse FAILED)"
[ -d ".agents/.schedule/$ENTRY" ] || fail "entry_role '$ENTRY'  has no .schedule dir"

# --- check 4: workspace sync green, zero dangling ------------------------------
# dangling counts loopback FIFOs that only exist while workspace daemons run.
# promote.sh never starts daemons, so this check spawns the daemon set that
# `run` would start, syncs against live FIFOs, then stops them. Same code
# path as the scheduler (daemon::ensure_all), minus signal handling.
ONLYNE_BIN="${ONLYNE_BIN:-onlyne}" export ONLYNE_BIN
# daemon-backed sync helper is embedded below via a temp file
HELPER="$(mktemp)"
cat > "$HELPER" <<'PY_DAEMONS'
import json, os, subprocess, sys, time
root = os.getcwd()
env = dict(os.environ)
swarm_bin = subprocess.run(["command", "-v", "onlyne-swarm"], capture_output=True, text=True, shell=True).stdout.strip()
onlyne_bin = env.get("ONLYNE_BIN", "onlyne")
tree = json.load(open(".agents/.schedule.json")) if os.path.exists(".agents/.schedule.json") else None
roles = sorted(os.listdir(".agents/.schedule"))
ws_dirs = ["."] + [os.path.join(".ws", r) for r in roles]
procs = []
for ws in ws_dirs:
    sock = os.path.join(ws, ".onlyne/run/s")
    alive = False
    if os.path.exists(sock):
        import socket as _s
        try:
            s = _s.socket(_s.AF_UNIX, _s.SOCK_STREAM)
            s.settimeout(2)
            s.connect(os.path.abspath(sock))
            s.sendall(b'{"id":"ping","op":"ping"}\n')
            alive = b'"ok":true' in s.recv(256)
            s.close()
        except OSError:
            alive = False
    if not alive:
        p = subprocess.Popen([onlyne_bin, "--workspace", os.path.abspath(ws), "run"],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p)
for _ in range(50):
    time.sleep(0.1)
    ready = True
    for ws in ws_dirs:
        if not os.path.exists(os.path.join(ws, ".onlyne/channels/loopback/in")):
            ready = False
            break
    if ready:
        break
r = subprocess.run(["onlyne-swarm", "workspace", "sync"], capture_output=True, text=True)
for p in procs:
    p.terminate()
for p in procs:
    try:
        p.wait(timeout=10)
    except Exception:
        p.kill()
if r.returncode != 0:
    print(r.stdout + r.stderr)
    sys.exit(1)
print(r.stdout)
PY_DAEMONS
SYNC_OUT="$(python3 "$HELPER" "$ROOT" 2>&1)" || { RC=$?; rm -f "$HELPER"; fail "workspace sync FAILED: $SYNC_OUT"; }
rm -f "$HELPER"
DANGLING="$(printf '%s' "$SYNC_OUT" | python3 -c 'import json,sys;print(len(json.load(sys.stdin).get("dangling",[])))' 2>/dev/null || echo "?")"
[ "$DANGLING" = "0" ] || fail "workspace sync dangling not zero"

# --- check 5: role table covers .schedule exactly ------------------------------
TABLE_ROLES="$(python3 - <<'PY_TABLE'
text = open(".agents/AGENTS.md").read()
names = []
for line in text.splitlines():
    if not line.startswith("|"):
        continue
    cells = [c.strip() for c in line.split("|")]
    if len(cells) < 3:
        continue
    first = cells[1]
    if first in ("role", "") or set(first) <= set("-: "):
        continue
    if "---" in first:
        continue
    names.append(first)
print(" ".join(names))
PY_TABLE
)"
for r in $ROLES; do
  printf '%s' " $TABLE_ROLES " | grep -q " $r " || fail "table MISSING role '$r'(.schedule has it, table lacks it)"
done
for t in $TABLE_ROLES; do
  printf '%s' " $ROLES " | grep -q " $t " || fail "table EXTRA role '$t'(table has it, .schedule lacks it)"
done

# --- check 6: seed ideas -------------------------------------------------------
if [ ! -f pool/ideas.jsonl ]; then
  fail "pool/ideas.jsonl MISSING"
fi
SEED_LINES="$(grep -c . pool/ideas.jsonl || true)"
if [ "$SEED_LINES" = "0" ]; then
  warn "pool/ideas.jsonl empty (0 seeds allowed, continuing)"
else
  python3 - pool/ideas.jsonl <<'PY_SEEDS' || fail "pool/ideas.jsonl schema INVALID (reason above)"
import json,sys
req = ["id","origin","question","hypothesis","method","evidence","evaluation","done_when","status"]
for i, line in enumerate(open(sys.argv[1]), 1):
    line = line.strip()
    if not line:
        continue
    d = json.loads(line)
    for k in req:
        assert k in d, f"line {i}:  MISSING field  {k}"
    assert isinstance(d["evidence"], list) and d["evidence"], f"line {i}:  evidence must be non-empty array"
    assert (d.get("evaluation") or {}).get("objectives"), f"line {i}:  evaluation.objectives EMPTY"
    assert d.get("done_when"), f"line {i}:  done_when EMPTY"
PY_SEEDS
fi

# --- check 7: payload/ and research/ --------------------------------------------
PAYLOAD_MISSING=0
[ -d payload ] || PAYLOAD_MISSING=1
if ! ls research/ 2>/dev/null | grep -vq "^\.gitkeep$"; then
  fail "research/ needs a domain file besides .gitkeep"
fi

# --- check 8: pi-onlyne version floor -------------------------------------------
python3 - .pi/settings.json <<'PY_PKGS' || fail ".pi/settings.json MISSING pi-onlyne floor (reason above)"
import json,sys
d = json.load(open(sys.argv[1]))
pkgs = d.get("packages", [])
ok = any(
    p.startswith("npm:pi-onlyne@") and (
        p.split("@", 2)[-1].lstrip("^~>= ")[:3] >= "0.8"
    )
    for p in pkgs
)
assert ok, f"packages={pkgs}"
PY_PKGS

# --- check 9: binaries -----------------------------------------------------------
for b in onlyne-swarm onlyne orca pi; do
  command -v "$b" >/dev/null || fail "binary MISSING:: $b"
done
SWARM_VER="$(onlyne-swarm --version 2>&1 | grep -o "[0-9][0-9.]*" | head -1)"
python3 - "$SWARM_VER" <<'PY_VER' || fail "onlyne-swarm --version=$SWARM_VER (want >= 0.5.0)"
import sys
parts = [int(x) for x in sys.argv[1].split(".")]
assert (parts + [0, 0])[:3] >= [0, 5, 0], "version too old"
PY_VER

info "checks: 9/9 PASS (entry_role=$ENTRY, roles: $(echo $ROLES | tr '\n' ' '))"

# --- plan ---------------------------------------------------------------
[ -z "$THEME" ] && THEME="$(basename "$ROOT")"
RETIRE=( ".agents/AGENTS.md" ".agents/skills/flywheel-setup/" "BOOTSTRAP.md" )
info "plan:"
info "  1) git checkout -b theme/$THEME"
info "  2) cp .agents/AGENTS.md AGENTS.md"
info "  3) write .onlyne/flywheel.json (stage=live, theme=$THEME, entry_role=$ENTRY)"
if [ "$PAYLOAD_MISSING" = "1" ]; then
  info "  4) create payload/ + .gitkeep (template gap, included in this commit)"
else
  info "  4) payload/ exists, skip mkdir"
fi
info "  5) onlyne-swarm workspace create generates .ws/"
info "  6) remove assembly material: ${RETIRE[*]}"
info "  7) git add -A && commit"
if [ "$DRY_RUN" = "1" ]; then
  info "--dry-run: zero writes, stopping here."
  exit 0
fi

# --- act ------------------------------------------------------------------
if git show-ref --verify --quiet "refs/heads/theme/$THEME"; then
  if [ "$FORCE_STAGE" = "1" ]; then
    git checkout -q "theme/$THEME" || fail "checkout existing branch theme/$THEME FAILED"
  else
    fail "branch theme/$THEME exists (use --force-stage)"
  fi
else
  git checkout -qb "theme/$THEME" || fail "create branch theme/$THEME FAILED"
fi
cp .agents/AGENTS.md AGENTS.md
TEMPLATE_COMMIT="$(git log --format=%H -1 -- BOOTSTRAP.md .agents/AGENTS.md 2>/dev/null || echo unknown)"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ROLES_JSON="$(printf '%s\n' $ROLES | python3 -c "import json,sys;print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))")"
python3 - "$THEME" "$ENTRY" "$ROLES_JSON" "$TEMPLATE_COMMIT" "$NOW" <<'PY_FLY'
import json,sys
theme, entry, roles, commit, now = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]), sys.argv[4], sys.argv[5]
json.dump({"stage":"live","theme":theme,"slug":theme,"template_commit":commit,
           "promoted_at":now,"entry_role":entry,"roles":json.loads(roles)},
          open(".onlyne/flywheel.json","w"), indent=2, ensure_ascii=False)
PY_FLY
if [ "$PAYLOAD_MISSING" = "1" ]; then
  mkdir -p payload
  touch payload/.gitkeep
fi
onlyne-swarm workspace create >/dev/null || fail "workspace create FAILED"
rm -rf "${RETIRE[@]}"
git add -A
git commit -qm "feat(bootstrap): promote template to theme $THEME"

cat <<EOF
1) run in this dir terminal: onlyne-swarm run            # start scheduler (human runs it, script starts no daemon)
2) open another terminal:      pi                           # this session is the supervisor
3) flywheel is now fully idle: 0 tasks, empty runs/, seeds only in pool.
   starting the scheduler is power-on; one more step to turn it:
   give the supervisor a research direction, or run directly
   onlyne-swarm submit --to $ENTRY --payload payload/first.md
EOF
