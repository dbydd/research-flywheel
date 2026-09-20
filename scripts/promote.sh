#!/usr/bin/env bash
# Promote a configured gemini clone to a live theme.
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
    --dry-run) DRY_RUN=1 ;;
    --theme) shift; THEME="${1:-}" ;;
    --force-stage) FORCE_STAGE=1 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

fail() { echo "FAIL: $1" >&2; exit 1; }
warn() { echo "WARN: $1"; }
info() { echo "$1"; }

# --- stage gate -------------------------------------------------------------
STAGE="configuring"
if [ -f .onlyne/gemini.json ]; then
  STAGE="$(python3 -c "import json;print(json.load(open('.onlyne/gemini.json')).get('stage','configuring'))" 2>/dev/null || echo configuring)"
fi
if [ "$STAGE" = "live" ]; then
  fail "already live (stage=live in .onlyne/gemini.json); refusing to re-promote"
fi
case "$STAGE" in
  configuring|checking) ;;
  *) fail "unknown stage '$STAGE' in .onlyne/gemini.json" ;;
esac

# --- check 1: role surface carries no assembly or ops content --------------
# Scope is the file set a role session reads through the parent-directory
# chain. README.md, .pi/SYSTEM.md, and scripts/ are the operator and duty
# surface and carry their own rule below.
[ -f .agents/AGENTS.md ] || fail ".agents/AGENTS.md MISSING"
ROLE_SURFACE=( ".agents/AGENTS.md" ".onlyne/AGENTS.md" )
while IFS= read -r f; do ROLE_SURFACE+=( "$f" ); done < <(find .agents/skills .onlyne/templates -type f -name '*.md' 2>/dev/null)
OPS_RE='装配|装机|换机|通电|promote|bootstrap|REPLACE_ME|clone|cargo install|pi install|brew|launchd|workspace rename|onlyne server (init|generate|stop)|/Users/|/home/|codesign'
OPS_HITS="$(grep -nE "$OPS_RE" "${ROLE_SURFACE[@]}" 2>/dev/null || true)"
if [ -n "$OPS_HITS" ]; then
  echo "$OPS_HITS" >&2
  fail "role surface carries assembly/ops content (list above)"
fi
# The duty canon holds ops verbs by design; it carries no assembly content.
DUTY_HITS="$(grep -nE 'REPLACE_ME|cargo install|pi install|clone|/Users/|/home/|codesign|npm:pi-onlyne' .pi/SYSTEM.md 2>/dev/null || true)"
if [ -n "$DUTY_HITS" ]; then
  echo "$DUTY_HITS" >&2
  fail ".pi/SYSTEM.md carries assembly content (list above)"
fi

# --- collect roles (single source of truth: spec.toml [[client]]) ----------
SPEC=".onlyne/spec.toml"
TOPO="${TOPO:-gemini}"
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

# --- check 2: per-role template dir + model triplet filled ------------------
for r in $ROLES; do
  A="$TPLDIR/$r/AGENTS.md"; S="$TPLDIR/$r/.pi/settings.json"
  [ -f "$A" ] || fail "$A MISSING"
  [ -f "$S" ] || fail "$S MISSING"
  python3 - "$S" <<'PY_CHECK2' || fail "$S model triplet INVALID (reason above)"
import json,sys
d = json.load(open(sys.argv[1]))
keys = ("defaultProvider", "defaultModel", "defaultThinkingLevel")
missing = [k for k in keys if not isinstance(d.get(k), str)]
assert not missing, f"keys absent or not strings: {missing}"
empty = [k for k in keys if not d[k]]
assert not empty, f"model triplet empty: {empty} (the gemini template ships concrete models)"
pkgs = d.get("packages", [])
assert pkgs == ["npm:pi-onlyne"], f'packages={pkgs}: role settings ship npm:pi-onlyne'
PY_CHECK2
done

# --- check 3: exactly one entry role -----------------------------------------
STAR_COUNT="$(grep -c '^|.*★' .onlyne/AGENTS.md || true)"
[ "$STAR_COUNT" = "1" ] || fail "star-table rows=$STAR_COUNT (want exactly 1)"
ENTRY="$(python3 - <<'PY_ENTRY'
import re
text = open(".onlyne/AGENTS.md").read()
rows = [l for l in text.splitlines() if l.startswith("|") and "★" in l]
name = rows[0].split("|")[1].strip() if rows else ""
print(name)
PY_ENTRY
)"
[ -n "$ENTRY" ] || fail "entry_role EMPTY (star row parse FAILED)"
printf '%s' " $ROLES " | grep -q " $ENTRY " || fail "entry_role '$ENTRY' not a spec [[client]] role"

# --- check 4: spec==templates, two mutually pointing edges, zero uplink -----
python3 - "$SPEC" "$TPLDIR" <<'PY_SPEC' || fail "spec/templates MISMATCH (reason above)"
import tomllib, sys, os
spec = tomllib.load(open(sys.argv[1], "rb"))
clients = {c["role"]: c for c in spec.get("client", [])}
tpl = {d for d in os.listdir(sys.argv[2]) if os.path.isdir(os.path.join(sys.argv[2], d))}
assert (tpl - {"_supervisor"}) == (set(clients) - {"_supervisor"}), f"templates {sorted(tpl)} vs spec {sorted(clients)}"
sup = clients.get("_supervisor")
assert sup and sup.get("admin") is True, "[[client]] _supervisor with admin=true REQUIRED"
roles = sorted(r for r in clients if r != "_supervisor")
assert len(roles) == 2, f"roles={roles}: the gemini ring is exactly two roles"
for r, c in clients.items():
    assert c.get("prose"), f"[[client]] {r}: prose EMPTY"
    for x in c.get("allowed_targets", []):
        assert x != "_supervisor", f"{r}: allowed_targets includes _supervisor (uplink must stay zero)"
        assert x in clients, f"{r}: targets unknown role {x}"
        s = clients[x].get("allowed_senders", [])
        assert r in s or "*" in s, f"{r}->{x}: {x} lacks the sender edge"
a, b = roles
for src, dst in ((a, b), (b, a)):
    t = clients[src].get("allowed_targets", [])
    assert t == [dst], f"{src}: allowed_targets {t} want exactly ['{dst}'] (two mutually pointing edges)"
    s = set(clients[src].get("allowed_senders", []))
    assert s == {dst, "_supervisor"}, f"{src}: allowed_senders {sorted(s)} want ['{dst}', '_supervisor']"
PY_SPEC

# --- check 5: role table matches spec [[client]] exactly -----------------------
TABLE_ROLES="$(python3 - <<'PY_TABLE'
text = open(".onlyne/AGENTS.md").read().splitlines()
names, inside = [], False
for line in text:
    if line.startswith("## "):
        inside = line.strip().startswith("## 角色表")
        continue
    if not inside or not line.startswith("|"):
        continue
    cells = [c.strip() for c in line.split("|")]
    if len(cells) < 3:
        continue
    first = cells[1]
    if first in ("role", "") or "---" in first:
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

# --- check 6: record surface (three layers, first task book, product root) ---
[ -f .onlyne/AGENTS.md ] || fail ".onlyne/AGENTS.md MISSING (role behavior canon)"
[ -f .agents/AGENTS.md ] || fail ".agents/AGENTS.md MISSING (shared objective record)"
[ -f payload/first.md ] || fail "payload/first.md MISSING (first injection task book)"
[ -d runs ] || fail "runs/ MISSING (product root: one directory per task)"
python3 - <<'PY_RECORDS' || fail "record surface INCOMPLETE (reason above)"
import re
def missing_sections(path, names):
    txt = open(path, encoding="utf-8").read()
    return [n for n in names if not re.search(r"^#{0,6}\s*" + re.escape(n) + r"\s*(?:[：:]|$)", txt, flags=re.M)]
for path, names in (
    (".agents/AGENTS.md", ("主线", "支线", "索引")),
    ("payload/first.md", ("目标", "输入", "期望产物", "下一跳建议")),
):
    miss = missing_sections(path, names)
    assert not miss, f"{path}: missing sections {miss}"
PY_RECORDS

# --- check 7: note discipline (mechanical parts) -----------------------------
python3 - "$SPEC" <<'PY_DISC' || fail "note discipline VIOLATED (reason above)"
import glob, re, sys, tomllib
spec = tomllib.load(open(sys.argv[1], "rb"))
root = (spec.get("server") or {}).get("template_root", ".onlyne/templates")
paths = [".agents/AGENTS.md", ".onlyne/AGENTS.md", ".onlyne/spec.toml", ".pi/SYSTEM.md", "README.md", "payload/first.md"]
paths += sorted(glob.glob(".agents/skills/**/*.md", recursive=True))
paths += sorted(glob.glob(root + "/**/*.md", recursive=True))
label = re.compile(r"\b[A-Z]{1,4}-?\d+\b")
stamp = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b")
for p in paths:
    txt = open(p, encoding="utf-8").read()
    hits = sorted(set(label.findall(txt)))
    assert not hits, f"{p}: letter+digit labels banned, write the title instead: {hits}"
    st = sorted(set(stamp.findall(txt)))
    if st:
        print(f"WARN: {p}: date-like strings, records carry no timestamps: {st}")
PY_DISC

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
if pi list 2>/dev/null | grep -q "npm:pi-onlyne"; then
  info "pi plugin npm:pi-onlyne present"
else
  warn "pi plugin npm:pi-onlyne not installed here: the role client loads it at runtime, so run \`pi install npm:pi-onlyne\` before starting the ring"
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
info "  3) write .onlyne/gemini.json (stage=live, theme=$THEME, entry_role=$ENTRY)"
info "  4) remove assembly material: ${RETIRE[*]}"
info "  5) git add -A && commit"
info "  6) runtime power-on stays manual (README: 装配与通电 > 通电)"
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
          open(".onlyne/gemini.json","w"), indent=2, ensure_ascii=False)
PY_FLY
rm -rf "${RETIRE[@]}"
git add -A
git commit -qm "feat(promote): promote template to theme $THEME"

cat <<EOF
promoted to theme/$THEME. Power-on is manual and is not running yet.
Full procedure: README.md "装配与通电".
1) toolchain (once, latest): cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui
   && pi install npm:pi-onlyne
2) server:   onlyne-server init --root . --listen 127.0.0.1:7812
   then copy .onlyne/spec.toml + templates back, fill cert_pin from the init output
   onlyne-server generate --root .   # prints one [[client]] row per role: paste each key back
   onlyne-server start --root .
3) supervisor: open pi in this directory (the _supervisor admin mount)
4) roles:    onlyne client run --workspace .onlyne/ws/$TOPO/<role>    # one visible tab per role
5) gemini is idle: empty ledger, empty runs/. To turn the ring:
   onlyne --server-root . send --from _supervisor --to $ENTRY --file payload/first.md
EOF
