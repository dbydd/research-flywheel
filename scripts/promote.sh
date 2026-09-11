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

# --- collect roles (single source of truth: spec.toml [[client]]) ----------
SPEC=".onlyne/spec.toml"
TOPO="${TOPO:-flywheel}"
TPLDIR=".onlyne/templates/$TOPO"
[ -f "$SPEC" ] || fail "$SPEC MISSING (v1 central truth)"
[ -d "$TPLDIR" ] || fail "$TPLDIR MISSING (role content templates)"
ROLES="$(python3 - "$SPEC" <<'PY_ROLES'
import tomllib, sys
spec = tomllib.load(open(sys.argv[1], "rb"))
print(" ".join(c["role"] for c in spec.get("client", []) if c["role"] != "_supervisor"))
PY_ROLES
)" || fail "spec.toml parse FAILED (python3>=3.11 tomllib)"
[ -n "$ROLES" ] || fail "spec.toml has no [[client]] roles"

# --- check 2: per-role template dir + model triplet -------------------------
for r in $ROLES; do
  A="$TPLDIR/$r/AGENTS.md"; S="$TPLDIR/$r/.pi/settings.json"
  [ -f "$A" ] || fail "$A MISSING"
  [ -f "$S" ] || fail "$S MISSING"
  python3 - "$S" <<'PY_CHECK2' || fail "$S model triplet INCOMPLETE (reason above)"
import json,sys
d = json.load(open(sys.argv[1]))
import os
assert d.get("defaultProvider") and d.get("defaultModel") and d.get("defaultThinkingLevel"), "defaultProvider/defaultModel/defaultThinkingLevel required non-empty"
pkgs = d.get("packages", [])
assert len(pkgs) == 1 and (pkgs[0] == "__AGENT_PACKAGE_ABS__" or os.path.isabs(pkgs[0])), f'packages={[p for p in pkgs]}: need sentinel or absolute literal ({{agent_package}} placeholder renders un-loadable in settings)' 
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
printf '%s' " $ROLES " | grep -q " $ENTRY " || fail "entry_role '$ENTRY' not a spec [[client]] role"

# --- check 4: spec==templates, supervisor admin, relay edges closed ---------
python3 - "$SPEC" "$TPLDIR" <<'PY_SPEC' || fail "spec/templates MISMATCH (reason above)"
import tomllib, sys, os
spec = tomllib.load(open(sys.argv[1], "rb"))
clients = {c["role"]: c for c in spec.get("client", [])}
tpl = {d for d in os.listdir(sys.argv[2]) if os.path.isdir(os.path.join(sys.argv[2], d))}
assert (tpl - {"_supervisor"}) == (set(clients) - {"_supervisor"}), f"templates {sorted(tpl)} vs spec {sorted(clients)}"
sup = clients.get("_supervisor")
assert sup and sup.get("admin") is True, "[[client]] _supervisor with admin=true REQUIRED"
for r, c in clients.items():
    assert c.get("prose"), f"[[client]] {r}: prose EMPTY"
    for x in c.get("allowed_targets", []):
        assert x != "_supervisor", f"{r}: allowed_targets includes _supervisor (uplink must stay zero)"
        tgt = clients.get(x)
        assert tgt is not None, f"{r}: targets unknown role {x}"
        s = tgt.get("allowed_senders", [])
        assert r in s or "*" in s, f"{r}->{x}: {x} lacks the sender edge"
PY_SPEC

# --- check 5: role table matches spec [[client]] exactly -----------------------
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
  printf '%s' " $TABLE_ROLES " | grep -q " $r " || fail "table MISSING role '$r' (spec has it, table lacks it)"
done
for t in $TABLE_ROLES; do
  printf '%s' " $ROLES " | grep -q " $t " || fail "table EXTRA role '$t' (table has it, spec lacks it)"
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

# --- check 8: [server].agent_package resolves to v1 pi plugin ------------------
python3 - "$SPEC" <<'PY_PKG' || fail "agent_package INVALID (reason above)"
import tomllib, sys, os, json
spec = tomllib.load(open(sys.argv[1], "rb"))
pkg = (spec.get("server") or {}).get("agent_package", "")
assert pkg and os.path.isabs(pkg), f"agent_package={pkg!r}: absolute local path required (fill at assembly)"
meta = json.load(open(os.path.join(pkg, "package.json")))
import glob
for s in glob.glob(os.path.join((spec.get("server") or {}).get("template_root", ".onlyne/templates"), "*", "*", ".pi", "settings.json")):
    pk = json.load(open(s)).get("packages", [])
    assert len(pk) == 1 and pk[0] == pkg, f"{s}: packages {pk} not sed-synced with agent_package"
parts = [int(x) for x in meta.get("version", "0").split("-")[0].split(".")]
assert (parts + [0, 0])[:3] >= [1, 0, 0], f"pi plugin version {meta.get('version')} < 1.0.0"
PY_PKG

# --- check 9: v1 toolchain + backend candidates --------------------------------
for b in onlyne onlyne-server onlyne-client pi; do
  command -v "$b" >/dev/null || fail "binary MISSING:: $b (build onlyne @ v1.0.0-beta.3, copy target/release/* into PATH)"
done
V1_VER="$(onlyne version 2>&1 | grep -o "[0-9][0-9.]*" | head -1)"
python3 - "${V1_VER:-0}" <<'PY_VER' || fail "onlyne version=${V1_VER:-none} (want >= 1.0.0)"
import sys
parts = [int(x) for x in sys.argv[1].split(".")]
assert (parts + [0, 0])[:3] >= [1, 0, 0], "version too old (v0 line is legacy protocol; exit 2 on legacy .onlyne/)"
PY_VER
if ! command -v zellij >/dev/null && ! command -v orca >/dev/null; then
  warn "no zellij/orca on PATH: ONLYNE_BACKEND will probe to fake (role sessions need a real backend)"
fi

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
info "  5) runtime power-on stays manual (AGENTS cold-start: server init/generate/run, client run)"
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
           "promoted_at":now,"entry_role":entry,"roles":roles},
          open(".onlyne/flywheel.json","w"), indent=2, ensure_ascii=False)
PY_FLY
if [ "$PAYLOAD_MISSING" = "1" ]; then
  mkdir -p payload
  touch payload/.gitkeep
fi
rm -rf "${RETIRE[@]}"
git add -A
git commit -qm "feat(bootstrap): promote template to theme $THEME"

cat <<EOF
1) run in this dir terminal: onlyne server init --root . --listen <port>, fill spec.toml pins/keys/agent_package,
   onlyne server generate --root ., then onlyne-server run --root .     # power-on, human runs it
2) open another terminal:    pi                                        # this session is the supervisor (_supervisor admin mount)
3) start each role client:   onlyne-client run --workspace .onlyne/ws/$TOPO/<role>
4) flywheel fully idle now:  empty ledger, empty runs/, seeds only in pool.
   power-on is not running; to turn the ring give the supervisor a direction, or run:
   onlyne --server-root . send --from _supervisor --to $ENTRY --file payload/first.md
EOF

