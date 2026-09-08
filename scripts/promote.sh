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
[ -f .agents/AGENTS.md ] || fail ".agents/AGENTS.md 缺失"
if grep -q "<!-- THEME:" .agents/AGENTS.md; then
  LEFT="$(grep -o "<!-- THEME:[a-z-]*" .agents/AGENTS.md | sort -u | tr '\n' ' ')"
  fail "THEME 槽残留未填: $LEFT"
fi

# --- collect roles (single source of truth) ---------------------------------
[ -d .agents/.schedule ] || fail ".agents/.schedule/ 缺失"
ROLES="$(ls .agents/.schedule/)"
[ -n "$ROLES" ] || fail ".agents/.schedule/ 下至少需要 1 个 role 目录"

# --- check 2: each role template --------------------------------------------
for r in $ROLES; do
  T=".agents/.schedule/$r/template.workspace.jsonc"
  [ -f "$T" ] || fail "$T 缺失"
  python3 - "$T" "$r" <<'PY' || fail "$T 不合法（见上行原因）"
import json,sys
p, want = sys.argv[1], sys.argv[2]
d = json.load(open(p))
assert d.get("name") == want, f"name={d.get('name')!r} 与目录名 {want!r} 不一致"
assert d.get("role"), "role 为空"
m = d.get("model") or {}
assert m.get("provider") and m.get("model") and m.get("effort"), "model.provider/model/effort 需填写"
PY
done

# --- check 3: exactly one entry role -----------------------------------------
STAR_COUNT="$(grep -c "★" .agents/AGENTS.md || true)"
[ "$STAR_COUNT" = "1" ] || fail "角色表 ★ 数=$STAR_COUNT（要求恰好 1）"
ENTRY="$(python3 - <<'PY'
import re
text = open(".agents/AGENTS.md").read()
rows = [l for l in text.splitlines() if l.startswith("|") and "★" in l]
name = rows[0].split("|")[1].strip() if rows else ""
print(name)
PY
)"
[ -n "$ENTRY" ] || fail "entry_role 为空（角色表 ★ 行解析失败）"
[ -d ".agents/.schedule/$ENTRY" ] || fail "entry_role '$ENTRY' 在 .agents/.schedule/ 下无对应目录"

# --- check 4: workspace sync green, zero dangling ------------------------------
SYNC_OUT="$(onlyne-swarm workspace sync 2>&1)" || fail "onlyne-swarm workspace sync 失败: $SYNC_OUT"
DANGLING="$(printf '%s' "$SYNC_OUT" | python3 -c "import json,sys;print(len(json.load(sys.stdin).get('dangling',[])))" 2>/dev/null || echo "?")"
[ "$DANGLING" = "0" ] || fail "workspace sync dangling=$DANGLING（要求 0）"

# --- check 5: role table covers .schedule exactly ------------------------------
TABLE_ROLES="$(python3 - <<'PY'
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
PY
)"
for r in $ROLES; do
  printf '%s' " $TABLE_ROLES " | grep -q " $r " || fail "角色表缺 role '$r'（.schedule/ 有，表里没有）"
done
for t in $TABLE_ROLES; do
  printf '%s' " $ROLES " | grep -q " $t " || fail "角色表多余 role '$t'（表里有，.schedule/ 没有）"
done

# --- check 6: seed ideas -------------------------------------------------------
if [ ! -f pool/ideas.jsonl ]; then
  fail "pool/ideas.jsonl 缺失"
fi
SEED_LINES="$(grep -c . pool/ideas.jsonl || true)"
if [ "$SEED_LINES" = "0" ]; then
  warn "pool/ideas.jsonl 为空（允许 0 条种子，继续）"
else
  python3 - pool/ideas.jsonl <<'PY' || fail "pool/ideas.jsonl schema 不合法（见上行原因）"
import json,sys
req = ["id","origin","question","hypothesis","method","evidence","evaluation","done_when","status"]
for i, line in enumerate(open(sys.argv[1]), 1):
    line = line.strip()
    if not line:
        continue
    d = json.loads(line)
    for k in req:
        assert k in d, f"第{i}行缺字段 {k}"
    assert isinstance(d["evidence"], list) and d["evidence"], f"第{i}行 evidence 须为非空数组"
    assert (d.get("evaluation") or {}).get("objectives"), f"第{i}行 evaluation.objectives 为空"
    assert d.get("done_when"), f"第{i}行 done_when 为空"
PY
fi

# --- check 7: payload/ and research/ --------------------------------------------
PAYLOAD_MISSING=0
[ -d payload ] || PAYLOAD_MISSING=1
if ! ls research/ 2>/dev/null | grep -vq "^\.gitkeep$"; then
  fail "research/ 缺领域锚点文件（除 .gitkeep 外至少一个文件）"
fi

# --- check 8: pi-onlyne version floor -------------------------------------------
python3 - .pi/settings.json <<'PY' || fail ".pi/settings.json 缺 npm:pi-onlyne@^0.8.1 或更高下限（见上行原因）"
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
PY

# --- check 9: binaries -----------------------------------------------------------
for b in onlyne-swarm onlyne orca pi; do
  command -v "$b" >/dev/null || fail "二进制缺失: $b"
done
SWARM_VER="$(onlyne-swarm --version 2>&1 | grep -o "[0-9][0-9.]*" | head -1)"
python3 - "$SWARM_VER" <<'PY' || fail "onlyne-swarm --version=$SWARM_VER（要求 >= 0.5.0）"
import sys
parts = [int(x) for x in sys.argv[1].split(".")]
assert (parts + [0, 0])[:3] >= [0, 5, 0], "version too old"
PY

info "checks: 9/9 通过（entry_role=$ENTRY，roles: $(echo $ROLES | tr '\n' ' ')）"

# --- plan ---------------------------------------------------------------
[ -z "$THEME" ] && THEME="$(basename "$ROOT")"
RETIRE=( ".agents/AGENTS.md" ".agents/skills/flywheel-setup/" "BOOTSTRAP.md" )
info "plan:"
info "  1) git checkout -b theme/$THEME"
info "  2) cp .agents/AGENTS.md AGENTS.md"
info "  3) 写 .onlyne/flywheel.json (stage=live, theme=$THEME, entry_role=$ENTRY)"
if [ "$PAYLOAD_MISSING" = "1" ]; then
  info "  4) 建 payload/ + .gitkeep（模板缺口，本次 commit 含它）"
else
  info "  4) payload/ 已存在，跳过建目录"
fi
info "  5) onlyne-swarm workspace create 生成 .ws/"
info "  6) 删除装配材料: ${RETIRE[*]}"
info "  7) git add -A && commit"
if [ "$DRY_RUN" = "1" ]; then
  info "--dry-run: 零写入，止步于此。"
  exit 0
fi

# --- act ------------------------------------------------------------------
if git show-ref --verify --quiet "refs/heads/theme/$THEME"; then
  if [ "$FORCE_STAGE" = "1" ]; then
    git checkout -q "theme/$THEME" || fail "切到已有分支 theme/$THEME 失败"
  else
    fail "分支 theme/$THEME 已存在（加 --force-stage 允许切到它）"
  fi
else
  git checkout -qb "theme/$THEME" || fail "建分支 theme/$THEME 失败"
fi
cp .agents/AGENTS.md AGENTS.md
TEMPLATE_COMMIT="$(git log --format=%H -1 -- BOOTSTRAP.md .agents/AGENTS.md 2>/dev/null || echo unknown)"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ROLES_JSON="$(printf '%s\n' $ROLES | python3 -c "import json,sys;print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))")"
python3 - "$THEME" "$ENTRY" "$ROLES_JSON" "$TEMPLATE_COMMIT" "$NOW" <<'PY'
import json,sys
theme, entry, roles, commit, now = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]), sys.argv[4], sys.argv[5]
json.dump({"stage":"live","theme":theme,"slug":theme,"template_commit":commit,
           "promoted_at":now,"entry_role":entry,"roles":json.loads(roles)},
          open(".onlyne/flywheel.json","w"), indent=2, ensure_ascii=False)
PY
if [ "$PAYLOAD_MISSING" = "1" ]; then
  mkdir -p payload
  touch payload/.gitkeep
fi
onlyne-swarm workspace create >/dev/null || fail "workspace create 失败"
rm -rf "${RETIRE[@]}"
git add -A
git commit -qm "feat(bootstrap): promote template to theme $THEME"

cat <<EOF
1) 本目录终端执行: onlyne-swarm run            # 起调度器（人执行，脚本不拉常驻进程）
2) 另开终端:      pi                           # 这个会话就是 supervisor
3) 飞轮现在是全 idle：tasks 0 行、runs/ 空、pool 只有种子。
   起 scheduler 等于接上电；它在转还需要再一步：
   给 supervisor 一个研究方向，或直接执行
   onlyne-swarm submit --to $ENTRY --payload payload/first.md
EOF
