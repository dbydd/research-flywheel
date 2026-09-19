#!/usr/bin/env bash
# formal-research 装配器：模板树 → 本机的可通电 onlyne 集群。自展开执行件。
#
# 用法：
#   scripts/bootstrap.sh --check                      # 只读门禁，零写入
#   scripts/bootstrap.sh --assemble [flags] [--dry-run]
#   scripts/bootstrap.sh --promote [--dry-run]        # .agents/AGENTS.md → 仓根 AGENTS.md
#
# assemble flags：
#   --listen <host:port>      缺省用 spec 现值
#   --provider <name>         重写 11 份模板 settings 的 defaultProvider
#   --model-powerful <id>     档位映射：现 defaultModel 含 powerful 的角色
#   --model-supercheap <id>   档位映射：含 supercheap 的角色
#   --model-weak <id>         含 weak 的角色（一般无；supervisor 位用仓根配置）
#   --vault <绝对路径>        建仓根 obsidian/ 四软链（论文/reports/draft/templates）
#
# 零守护进程：本脚本不起 server / client / tui；结束打印通电动作清单。
# 幂等：每步先判已达状态，达则 SKIP。装配产生的 spec.toml / AGENTS.md diff 属本机装机态。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SPEC=".onlyne/spec.toml"
TPL=".onlyne/templates/formal"
WSD=".onlyne/ws/formal"
KEYS_DIR=".onlyne/keys"
PIN_PLACEHOLDER="sha256/REPLACE_ME_after_server_init"
KEY_PLACEHOLDER="ed25519/AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE="
THIN_TITLE="# 这棵树还没装配 —— 你是 clone 后的第一个会话"
ROLES=(initiation/pi initiation/examiner common/librarian common/scribe theory/speculator theory/theorist experiment/runner review/qa review/referee review/chair archive/planner)

MODE=""; DRY=0; LISTEN=""; VAULT=""; PROVIDER=""; M_POWERFUL=""; M_CHEAP=""; M_WEAK=""
usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; }
while [ $# -gt 0 ]; do
  case "$1" in
    --check) MODE=check ;;
    --assemble) MODE=assemble ;;
    --promote) MODE=promote ;;
    --dry-run) DRY=1 ;;
    --listen) LISTEN="${2:-}"; shift ;;
    --vault) VAULT="${2:-}"; shift ;;
    --provider) PROVIDER="${2:-}"; shift ;;
    --model-powerful) M_POWERFUL="${2:-}"; shift ;;
    --model-supercheap) M_CHEAP="${2:-}"; shift ;;
    --model-weak) M_WEAK="${2:-}"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "bootstrap: 未知参数 $1" >&2; usage; exit 2 ;;
  esac
  shift
done
[ -n "$MODE" ] || { echo "bootstrap: 必须给 --check / --assemble / --promote 之一" >&2; usage; exit 2; }

FAILS=0
ok()   { echo "PASS $1"; }
bad()  { echo "FAIL $1"; FAILS=$((FAILS+1)); }
warn() { echo "WARN $1"; }
skip() { echo "SKIP $1"; }
info() { echo "     $1"; }
act()  { if [ "$DRY" = "1" ]; then echo "DRY  $*"; else "$@"; fi; }

specpy() { python3 - "$SPEC" "$@"; }

# ---------- 只读门禁 ----------
gate_toolchain() {
  local missing=0 b
  for b in onlyne onlyne-server onlyne-client onlyne-gateway onlyne-tui; do
    command -v "$b" >/dev/null || { missing=1; break; }
  done
  if [ "$missing" = "1" ]; then
    bad "五件套不齐（cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui）"
    return
  fi
  local v
  v="$(onlyne version 2>/dev/null || true)"
  if printf '%s' "$v" | python3 -c '
import json,sys
d=json.loads(sys.stdin.read())
p=tuple(int(x) for x in d["onlyne-cli"].split("+")[0].split("-")[0].split("."))
assert d["protocol"]==1 and p>=(1,0,0)
' 2>/dev/null; then
    ok "onlyne 五件套在 PATH，protocol=1，版本 $(printf '%s' "$v" | python3 -c 'import json,sys;print(json.load(sys.stdin)["onlyne-cli"])')（下限 1.0.0，口径追 latest）"
  else
    bad "onlyne 版本不过闸：需 protocol=1 且 ≥1.0.0（${v}）"
  fi
}

gate_pi() {
  if ! command -v pi >/dev/null; then bad "pi 不在 PATH"; return; fi
  local out
  out="$(pi list 2>/dev/null || true)"
  case "$out" in
    *"npm:pi-onlyne"*) ok "pi 插件 npm:pi-onlyne 在册" ;;
    *) warn "pi 插件缺 npm:pi-onlyne：通电前由 supervisor 跑 pi install npm:pi-onlyne（用户级安装，不属本脚本的写盘动作）" ;;
  esac
}

gate_spec() {
  [ -f "$SPEC" ] || { bad "$SPEC 缺失"; return; }
  if specpy <<'PY'
import sys, tomllib
spec = tomllib.load(open(sys.argv[1], "rb"))
clients = spec.get("client", [])
roles = [c["role"] for c in clients]
if len(roles) != 11 or len(set(roles)) != 11:
    print(f"  role 数 {len(roles)}，应为 11 且不重名"); sys.exit(1)
byname = {c["role"]: c for c in clients}
for c in clients:
    for t in c.get("allowed_targets", []):
        if t == "_supervisor":
            print(f"  {c['role']}: allowed_targets 含 _supervisor（零上行边铁律）"); sys.exit(1)
        if t not in byname:
            print(f"  {c['role']}: target {t} 不在册"); sys.exit(1)
    for s in c.get("allowed_senders", []):
        if s not in byname:
            print(f"  {c['role']}: sender {s} 不在册"); sys.exit(1)
    for r in c.get("relay_required", []):
        if r not in byname:
            print(f"  {c['role']}: relay {r} 不在册"); sys.exit(1)
        elif r not in c.get("allowed_targets", []):
            print(f"  relay 边不闭合：{c['role']}→{r}，但 {c['role']} 的 allowed_targets 缺 {r}"); sys.exit(1)
        elif c["role"] not in byname[r].get("allowed_senders", []):
            print(f"  relay 边不闭合：{c['role']}→{r}，但 {r} 的 allowed_senders 缺 {c['role']}"); sys.exit(1)
PY
  then ok "$SPEC 可 parse：11 role、relay/ACL 双向闭合、_supervisor 零上行"; else bad "$SPEC 结构门禁未过（原因见上行）"; fi
}

gate_templates() {
  [ -d "$TPL" ] || { bad "$TPL 缺失"; return; }
  local missing=0 p
  for p in "${ROLES[@]}"; do
    [ -f "$TPL/$p/AGENTS.md" ] && [ -f "$TPL/$p/.pi/settings.json" ] || { missing=1; break; }
  done
  [ "$missing" = "0" ] && ok "11 份角色模板齐（AGENTS.md + .pi/settings.json）" || bad "角色模板缺件：$TPL/<phase>/<role>"
  local extra
  extra="$(find "$TPL" -mindepth 2 -maxdepth 2 -type d | sed "s|^$TPL/||" | sort | tr '\n' ' ')"
  local want; want="$(printf '%s\n' "${ROLES[@]}" | sort | tr '\n' ' ')"
  [ "$extra" = "$want" ] && ok "模板目录集与脚本角色表一致" || bad "模板目录集与角色表不一致：[$extra] vs [$want]"
}

gate_cert() {
  local pin
  pin="$(specpy <<'PY'
import sys, tomllib
print(tomllib.load(open(sys.argv[1],"rb"))["server"].get("cert_pin",""))
PY
)"
  if [ "$pin" = "$PIN_PLACEHOLDER" ] || [ -z "$pin" ]; then
    bad "cert_pin 仍是占位（跑 scripts/bootstrap.sh --assemble）"
  elif [ ! -f "$KEYS_DIR/server.key" ]; then
    bad "cert_pin 已填但 $KEYS_DIR/server.key 不在盘（证书与 spec 不同机）"
  else
    ok "cert_pin 已回填，server.key 在盘"
  fi
}

gate_keys() {
  local ph
  ph="$(specpy <<'PY'
import sys, tomllib
print(sum(1 for c in tomllib.load(open(sys.argv[1],"rb")).get("client",[]) if c.get("key","").startswith("ed25519/AQEB")))
PY
)"
  if [ "$ph" = "0" ]; then ok "11 个 role key 均为装机产物"; else bad "$ph 个 role key 仍是占位（跑 --assemble）"; fi
}

gate_workspaces() {
  local n=0 bad_pkgs=0 nokey=0 p
  for p in "${ROLES[@]}"; do
    if [ -d "$WSD/$p/.pi" ]; then n=$((n+1)); else continue; fi
    [ -f "$WSD/$p/.onlyne/keys/role.key" ] || nokey=$((nokey+1))
    python3 - "$WSD/$p/.pi/settings.json" <<'PY' || bad_pkgs=$((bad_pkgs+1))
import json,sys
d=json.load(open(sys.argv[1]))
assert d.get("packages")==["npm:pi-onlyne"], d.get("packages")
PY
  done
  if [ "$n" = "11" ] && [ "$bad_pkgs" = "0" ] && [ "$nokey" = "0" ]; then
    ok "11 份角色工作区在盘（.pi/settings.json + .onlyne/keys/role.key），packages 全为 npm:pi-onlyne"
  else
    bad "角色工作区：渲染 $n/11，packages 不过闸 $bad_pkgs 份，缺 role.key $nokey 份（跑 --assemble）"
  fi
}

gate_backend() {
  if command -v onlyne-client >/dev/null; then
    local out
    out="$(onlyne-client doctor 2>&1 || true)"
    if printf '%s' "$out" | grep -qiE 'herdr|orca|zellij'; then ok "会话后端可探测：$(printf '%s\n' "$out" | tail -1)"; else warn "doctor 未见 herdr/orca/zellij：client run 会退 5（除非点名 ONLYNE_BACKEND=exec）"; fi
  else
    warn "onlyne-client doctor 不可用，跳过后端探测"
  fi
}

gate_port() {
  local addr
  addr="$(specpy <<'PY'
import sys, tomllib
print(tomllib.load(open(sys.argv[1],"rb"))["server"]["listen"])
PY
)"
  local socket=".onlyne/run/s"
  if [ -S "$socket" ] || [ -f ".onlyne/run/socket" ]; then skip "server 已在跑（${addr}），端口占用不判"; return; fi
  if python3 - "$addr" <<'PY'
import socket,sys
h,_,p=sys.argv[1].rpartition(":")
s=socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind((h or "127.0.0.1", int(p))); s.close()
except OSError:
    sys.exit(1)
PY
  then ok "listen $addr 空闲"; else bad "listen $addr 已被占且本树 server 未跑：改 spec 的 [server].listen 再 reload，或腾端口"; fi
}

gate_hygiene() {
  if ! git rev-parse --git-dir >/dev/null 2>&1; then skip "非 git 工作树，跳过文档卫生门禁"; return; fi
  local hits
  hits="$(git grep --untracked -nIE '/Users/|/home/[a-z]|OneDrive|\bdbydd\b|/Applications/|onlyne/harness|~/\.cargo|\bmlx\b|MLX' -- \
      ':!scripts/bootstrap.sh' 2>/dev/null || true)"
  if [ -z "$hits" ]; then ok "文档卫生：跟踪文件零本机路径、零装机者标识、零 mlx 栈字样"; else bad "文档卫生门禁命中："; printf '%s\n' "$hits" | sed 's/^/     /'; fi
}

gate_vault() {
  if [ ! -e obsidian ]; then skip "未接 vault（obsidian/ 不在盘）：vault 条款按约定整段失效"; return; fi
  local d miss=0
  for d in 论文 reports draft templates; do
    [ -e "obsidian/$d" ] || miss=$((miss+1))
  done
  [ "$miss" = "0" ] && ok "vault 四软链齐" || bad "obsidian/ 缺 $miss 个软链（--assemble --vault <路径> 可补）"
}

run_check() {
  echo "== bootstrap check（只读门禁）=="
  gate_toolchain; gate_pi; gate_spec; gate_templates; gate_cert; gate_keys
  gate_workspaces; gate_backend; gate_port; gate_hygiene; gate_vault
  if [ "$FAILS" = "0" ]; then echo "== 门禁全绿：可 --promote，然后通电 =="; else echo "== 门禁 $FAILS 项未过：按各行提示修完重跑 =="; return 1; fi
}

# ---------- 装配 ----------
asm_toolchain() {
  if command -v onlyne >/dev/null && command -v pi >/dev/null; then skip "装具在 PATH（版本闸交给 check）"; return; fi
  bad "装具缺失：先装 onlyne 五件套与 pi（README「前置」节），再重跑"
}

asm_cert() {
  local pin; pin="$(specpy <<'PY'
import sys, tomllib
print(tomllib.load(open(sys.argv[1],"rb"))["server"].get("cert_pin",""))
PY
)"
  if [ "$pin" != "$PIN_PLACEHOLDER" ] && [ -n "$pin" ]; then skip "cert_pin 已回填"; return; fi
  if [ -z "$LISTEN" ]; then LISTEN="$(specpy <<'PY'
import sys, tomllib
print(tomllib.load(open(sys.argv[1],"rb"))["server"]["listen"])
PY
)"; fi
  echo "装配 1/6 证书：onlyne-server init --root . --listen ${LISTEN}（spec.toml 暂移，init 见 spec 即拒）"
  if [ "$DRY" = "1" ]; then echo "DRY  mv $SPEC → 临时 → init → 还原 → 替换 cert_pin"; return; fi
  local out
  cp "$SPEC" "$SPEC.pre-bootstrap" || die "$0: 暂移前存不下改前备份，拒绝改动拓扑真相"
  trap 'cp "$SPEC.pre-bootstrap" "$SPEC" 2>/dev/null; rm -f "$SPEC.pre-assemble"' EXIT
  mv "$SPEC" "$SPEC.pre-assemble"
  if ! out="$(onlyne-server init --root . --listen "$LISTEN" 2>/dev/null)"; then
    mv "$SPEC.pre-assemble" "$SPEC"; bad "onlyne-server init 失败：$out"; return
  fi
  local newpin; newpin="$(printf '%s\n' "$out" | tail -1)"
  mv "$SPEC.pre-assemble" "$SPEC"
  python3 - "$SPEC" "$newpin" <<'PY'
import re, sys
p, pin = sys.argv[1], sys.argv[2]
text = open(p, encoding="utf-8").read()
new, n = re.subn(r'(?m)^cert_pin = "[^"]*"$', f'cert_pin = "{pin}"', text, count=1)
if n != 1:
    sys.exit("cert_pin 行未找到")
open(p, "w", encoding="utf-8").write(new)
PY
  trap - EXIT
  ok "cert_pin 回填 = $newpin"
}

verify_spec_or_restore() {
  # 装配写 spec 的门禁：parse 通、11 role 齐，否则还原改前备份后退出（防最小模板覆盖丢拓扑）
  if python3 - "$SPEC" <<'PY'
import sys, tomllib
d = tomllib.load(open(sys.argv[1], "rb"))
roles = [c.get("role") for c in d.get("client", [])]
sys.exit(0 if len(roles) == 11 and len(set(roles)) == 11 and "cert_pin" in d.get("server", {}) else 1)
PY
  then
    rm -f "$SPEC.pre-bootstrap"
    ok "spec 改后复检通过（parse + 11 role + cert_pin），改前备份已清"
  else
    cp "$SPEC.pre-bootstrap" "$SPEC" && rm -f "$SPEC.pre-bootstrap"
    die "$0: 装配中途 spec 结构受损，已还原改前备份；请报告 onlyne 版本与报错原文"
  fi
}

asm_keys() {
  local i=0 p role ws out key
  for p in "${ROLES[@]}"; do
    role="${p##*/}"; i=$((i+1))
    key="$(python3 - "$SPEC" "$role" <<'PY'
import sys, tomllib
d = tomllib.load(open(sys.argv[1], "rb"))
for c in d.get("client", []):
    if c["role"] == sys.argv[2]:
        print(c.get("key", "")); break
PY
)"
    if [ -n "$key" ] && [ "$key" != "$KEY_PLACEHOLDER" ]; then skip "[$i/11] $role key 已在 spec"; continue; fi
    ws="$WSD/$p"
    echo "装配 2/6 密钥 [$i/11] ${role}：onlyne-client init --workspace $ws --role $role"
    if [ "$DRY" = "1" ]; then echo "DRY  init + 回填 key"; continue; fi
    if ! out="$(onlyne-client init --workspace "$ws" --role "$role" --server-root . 2>&1)"; then
      bad "[$i/11] $role client init 失败：$(printf '%s' "$out" | tail -2 | tr '\n' ' ')"; continue
    fi
    key="$(printf '%s\n' "$out" | sed -n 's/.*key = "\([^"]*\)".*/\1/p' | tail -1)"
    if [ -z "$key" ]; then bad "[$i/11] $role init 输出里没有 key 行"; continue; fi
    python3 - "$SPEC" "$role" "$key" <<'PY'
import re, sys
p, role, key = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(p, encoding="utf-8").read()
pat = re.compile(r'(role = "' + re.escape(role) + r'"\s*\nkey = ")[^"]*(")')
new, n = pat.subn(lambda m: m.group(1) + key + m.group(2), text, count=1)
if n != 1:
    sys.exit(f"role {role} 的 key 行未定位")
open(p, "w", encoding="utf-8").write(new)
PY
    ok "[$i/11] $role key 回填"
  done
}

asm_models() {
  if [ -z "$PROVIDER" ] && [ -z "$M_POWERFUL" ] && [ -z "$M_CHEAP" ] && [ -z "$M_WEAK" ]; then
    skip "模型档位：未给 --provider/--model-* flag，保留模板现值"; return
  fi
  echo "装配 3/6 模型档位写入 11 份模板 settings.json"
  local p
  for p in "${ROLES[@]}"; do
    act python3 - "$TPL/$p/.pi/settings.json" "$PROVIDER" "$M_POWERFUL" "$M_CHEAP" "$M_WEAK" <<'PY'
import json, sys
path, provider, mp, mc, mw = sys.argv[1:6]
d = json.load(open(path, encoding="utf-8"))
cur = d.get("defaultModel", "")
if provider:
    d["defaultProvider"] = provider
tgt = mp if "powerful" in cur else (mc if "supercheap" in cur else (mw if "weak" in cur else ""))
if tgt:
    d["defaultModel"] = tgt
d["packages"] = ["npm:pi-onlyne"]
json.dump(d, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(path, "a", encoding="utf-8").write("\n")
PY
  done
  [ "$DRY" = "1" ] || ok "档位写入完成（effort 档未动）"
}

asm_generate() {
  local i=0 p role
  for p in "${ROLES[@]}"; do
    role="${p##*/}"; i=$((i+1))
    echo "装配 4/6 渲染 [$i/11] $p"
    if [ "$DRY" = "1" ]; then echo "DRY  onlyne server generate --root . --template formal/${p} --role ${role} --force"; continue; fi
    # generate 会把该 role 的 [[client]] 行原样打到 stdout，装机日志里不需要，只留 stderr
    if onlyne server generate --root . --template "formal/$p" --role "$role" --force >/dev/null; then
      ok "[$i/11] $p 渲染到 $WSD/$p"
    else
      bad "[$i/11] $p generate 失败（看上一行 stderr）"
    fi
  done
}

asm_vault() {
  if [ -z "$VAULT" ]; then skip "vault：未给 --vault，仓根不建 obsidian/ 软链（约定 vault 节整段失效）"; return; fi
  if [ ! -d "$VAULT" ]; then bad "--vault 路径不存在：$VAULT"; return; fi
  echo "装配 5/6 vault 软链 → $VAULT"
  act mkdir -p obsidian
  local d
  for d in 论文 reports draft templates; do
    if [ ! -d "$VAULT/$d" ]; then warn "vault 缺子目录 ${d}，跳该链"; continue; fi
    act ln -sfn "$VAULT/$d" "obsidian/$d"
  done
  [ "$DRY" = "1" ] || ok "vault 软链就位（obsidian/ 已 gitignore）"
}

run_assemble() {
  if [ "$DRY" = "1" ]; then echo "== bootstrap assemble（dry-run）=="; else echo "== bootstrap assemble =="; fi
  asm_toolchain; asm_cert; asm_keys; asm_models
  [ "$DRY" = "1" ] || verify_spec_or_restore
  asm_generate; asm_vault
  echo "== 装配步骤跑完，接门禁 =="
  if run_check; then
    cat <<'EOF'

下一步（本脚本不起守护进程）：
  1) scripts/bootstrap.sh --promote     # .agents/AGENTS.md → 仓根 AGENTS.md
  2) 可见前台 tab 起 server：onlyne server start --root .
  3) 各一个可见 tab 起 11 个 client：onlyne client run --workspace .onlyne/ws/formal/<phase>/<role>
  4) 第一发：onlyne send --server-root . --from planner --to pi --file payload/first.md
EOF
  fi
}

run_promote() {
  [ -f ".agents/AGENTS.md" ] || { echo "FAIL .agents/AGENTS.md 缺失" >&2; exit 1; }
  if [ "$(head -1 AGENTS.md)" != "$THIN_TITLE" ]; then
    skip "仓根 AGENTS.md 首行不是薄引导标题 = 已提升过（或已被本机改写），零写入"; return
  fi
  echo "promote：cp .agents/AGENTS.md → AGENTS.md"
  act cp .agents/AGENTS.md AGENTS.md
  if [ "$DRY" = "1" ]; then echo "DRY  完成"; return; fi
  ok "公共约定已上位；git status 会显示 AGENTS.md 本机改动（装机态，设计内）"
}

case "$MODE" in
  check) run_check ;;
  assemble) run_assemble ;;
  promote) run_promote ;;
esac
