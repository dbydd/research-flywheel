#!/usr/bin/env bash
# Promote a configured flywheel clone to a live theme.
#
# Usage: ./scripts/promote.sh [--dry-run] [--theme <slug>] [--force-stage]
#
# Contract: README.md "装配与通电 > 装配". Checks run first; any
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
    *) echo "unknown flag: $1 (usage: promote.sh [--dry-run] [--theme <slug>] [--force-stage])" >&2; exit 1 ;;
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

# --- check 1: role surface carries no assembly or ops content --------------
# Scope is the file set a role session reads through the parent-directory
# chain. README.md, .pi/SYSTEM.md, and scripts/ are the operator and duty
# surface and carry their own rule below.
[ -f .agents/AGENTS.md ] || fail ".agents/AGENTS.md MISSING"
ROLE_SURFACE=( ".agents/AGENTS.md" )
while IFS= read -r f; do ROLE_SURFACE+=( "$f" ); done < <(find .agents/skills .onlyne/templates -type f -name '*.md' 2>/dev/null)
OPS_RE='装配|装机|换机|通电|promote|bootstrap|REPLACE_ME|clone|cargo install|pi install|brew|launchd|workspace rename|onlyne server (init|generate|stop)|/Users/|/home/|codesign'
OPS_HITS="$(grep -nE "$OPS_RE" "${ROLE_SURFACE[@]}" 2>/dev/null || true)"
if [ -n "$OPS_HITS" ]; then
  printf '%s\n' "$OPS_HITS" >&2
  fail "role surface carries assembly or ops content (lines above)"
fi
# The duty canon holds ops verbs by design; it carries no assembly content.
DUTY_HITS="$(grep -nE 'REPLACE_ME|cargo install|pi install|clone|/Users/|/home/|codesign|npm:pi-onlyne' .pi/SYSTEM.md 2>/dev/null || true)"
if [ -n "$DUTY_HITS" ]; then
  printf '%s\n' "$DUTY_HITS" >&2
  fail ".pi/SYSTEM.md carries assembly content (lines above)"
fi
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
keys = ("defaultProvider", "defaultModel", "defaultThinkingLevel")
missing = [k for k in keys if not isinstance(d.get(k), str)]
assert not missing, f"keys absent or not strings: {missing}"
if not all(d[k] for k in keys):
    print(f"{sys.argv[1]}: model triplet empty, the installer fills it (pi falls back to its own default)")
pkgs = d.get("packages", [])
assert pkgs == ["npm:pi-onlyne"], f'packages={pkgs}: published template ships npm:pi-onlyne (supervisor first-run: pi install npm:pi-onlyne)' 
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

# --- check 6: seed ideas (markdown pool) ----------------------------------------
POOL="pool/ideas.md"
if [ ! -f "$POOL" ]; then
  fail "$POOL MISSING"
fi
SEED_N="$(sed -n 's/^## \[[ >x!]\] \([^ ]*\).*/\1/p' "$POOL" | wc -l | tr -d ' ')"
if [ "$SEED_N" = "0" ]; then
  warn "$POOL 无 idea 小节（0 seeds allowed, continuing）"
else
  python3 - "$POOL" <<'PY_SEEDS' || fail "pool/ideas.md schema INVALID (reason above)"
import sys, re, json
txt = open(sys.argv[1], encoding='utf-8').read()
parts = re.split(r'^## \[([ >x!])\] (\S+)[ \t]*$', txt, flags=re.M)
triples = list(zip(parts[1::3], parts[2::3], parts[3::3]))
assert triples, "没有任何 '## [符] id' 小节"
for sym, sid, body in triples:
    assert sym in (' ', '>', 'x', '!'), f"{sid}: 非法状态框 [{sym}]"
    for k in ("origin", "parent_run", "question", "hypothesis", "method", "evidence", "done_when"):
        m = re.search(r'(?:^[-*][ \t]+| \| )' + k + r':[ \t]*(\S.*)$', body, flags=re.M)
        assert m and m.group(1).strip(), f"{sid}: 字段 {k} 缺失或为空"
    assert re.search(r'(?:^[-*][ \t]+| \| )evidence:[ \t]*(?![,\s]$)\S', body, flags=re.M), f"{sid}: evidence 为空"
    ev = re.search(r'(?:^[-*][ \t]+| \| )evaluation:[ \t]*(\{.*\})[ \t]*$', body, flags=re.M)
    assert ev, f"{sid}: evaluation 非单行 JSON"
    obj = json.loads(ev.group(1))
    assert obj.get("objectives"), f"{sid}: evaluation.objectives EMPTY"
    assert obj.get("pass_rule") in ("all", "any"), f"{sid}: pass_rule 缺失或非法"
PY_SEEDS
fi

# --- check 7: payload/ and research/ --------------------------------------------
PAYLOAD_MISSING=0
[ -d payload ] || PAYLOAD_MISSING=1
if ! ls research/ 2>/dev/null | grep -vq "^\.gitkeep$"; then
  fail "research/ needs a domain file besides .gitkeep"
fi

# --- check 8: npm:pi-onlyne in every role settings; agent_package empty ------
python3 - "$SPEC" <<'PY_PKG' || fail "pi-onlyne settings INVALID (reason above)"
import tomllib, sys, glob, json
spec = tomllib.load(open(sys.argv[1], "rb"))
pkg = (spec.get("server") or {}).get("agent_package", "")
assert pkg == "", f"agent_package={pkg!r}: published template keeps this empty; plugin is npm:pi-onlyne in each role .pi/settings.json"
root = (spec.get("server") or {}).get("template_root", ".onlyne/templates")
found = 0
for s in glob.glob(root + "/*/*/.pi/settings.json"):
    found += 1
    pk = json.load(open(s)).get("packages", [])
    assert pk == ["npm:pi-onlyne"], f"{s}: packages {pk} want ['npm:pi-onlyne']"
assert found >= 1, f"no role .pi/settings.json under {root}"
PY_PKG
if ! pi list 2>/dev/null | grep -q "npm:pi-onlyne"; then
  fail "pi-onlyne MISSING: supervisor first-run is \`pi install npm:pi-onlyne\` (latest)"
fi

# --- check 9: v1 toolchain + backend candidates --------------------------------
for b in onlyne onlyne-server onlyne-client pi; do
  command -v "$b" >/dev/null || fail "binary MISSING:: $b (cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui)"
done
V1_VER="$(onlyne version 2>&1 | grep -o "[0-9][0-9.]*" | head -1)"
python3 - "${V1_VER:-0}" <<'PY_VER' || fail "onlyne version=${V1_VER:-none} below 1.0.0 floor (track latest: cargo install --force the five onlyne crates)"
import sys
parts = [int(x) for x in sys.argv[1].split(".")]
assert (parts + [0, 0])[:3] >= [1, 0, 0], "below the 1.0.0 floor (v0 line is legacy protocol; exit 2 on legacy .onlyne/); install latest"
PY_VER
if ! command -v herdr >/dev/null && ! command -v zellij >/dev/null && ! command -v orca >/dev/null; then
  warn "no herdr/zellij/orca on PATH: auto probe empty, onlyne-client run exits 5 unless ONLYNE_BACKEND=exec or fake"
fi

info "checks: 9/9 PASS (entry_role=$ENTRY, roles: $(echo $ROLES | tr '\n' ' '))"

# --- plan ---------------------------------------------------------------
[ -z "$THEME" ] && THEME="$(basename "$ROOT")"
RETIRE=( ".agents/AGENTS.md" )
info "plan:"
info "  1) git checkout -b theme/$THEME"
info "  2) cp .agents/AGENTS.md AGENTS.md"
info "  3) write .onlyne/flywheel.json (stage=live, theme=$THEME, entry_role=$ENTRY)"
if [ "$PAYLOAD_MISSING" = "1" ]; then
  info "  4) create payload/ + .gitkeep (template gap, included in this commit)"
else
  info "  4) payload/ exists, skip mkdir"
fi
info "  5) runtime power-on stays manual (README: 装配与通电 > 通电)"
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
TEMPLATE_COMMIT="$(git log --format=%H -1 -- .agents/AGENTS.md README.md 2>/dev/null || echo unknown)"
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
promoted to theme/$THEME. Power-on is manual and is not running yet.
Full procedure: README.md "装配与通电".
1) toolchain (once, latest): cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui
   && pi install npm:pi-onlyne
2) server:   onlyne server init --root . --listen <port>   # then fill spec.toml cert_pin and per-role keys
   onlyne server generate --root . && onlyne server start --root .
3) supervisor: open pi in this directory (the _supervisor admin mount)
4) roles:    onlyne client run --workspace .onlyne/ws/$TOPO/<role>    # one visible tab per role
5) flywheel is idle: empty ledger, empty runs/, seeds only in pool. To turn the ring:
   onlyne --server-root . send --from _supervisor --to $ENTRY --file payload/first.md
EOF

