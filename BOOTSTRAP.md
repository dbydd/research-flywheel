# BOOTSTRAP —— 模板到主题的装配流程

读者：拿到本模板 clone 的人（或替他干活的 supervisor 会话）。装配 = 把通用骨架填成
一个具体研究主题的飞轮，产出一条 `theme/<slug>` 分支与一套可通电的 onlyne v1 拓扑。
装配期间不起集群、不跑实验；红线是 `.agents/AGENTS.md` 与 `.onlyne/spec.toml` 的结构完整。

## 0. 全景

```mermaid
flowchart TD
  A[clone 模板] --> B[A 定题：THEME 槽×5]
  B --> C[B 拓扑：spec.toml [[client]] 增删 + ACL 边]
  C --> D[C 起草：角色文案/模型三元组/任务书口径]
  D --> E[D 种子：pool/ideas.jsonl ≥1 条硬门字段]
  E --> F[装工具链：onlyne beta + 构建]
  F --> G[promote.sh --dry-run 九检]
  G --> H[人确认 → promote.sh 落分支]
  H --> I[通电：server init/generate/run + clients]
  I --> J[第一发：send --from _supervisor --to entry]
```

## 1. 上下文面（v1 谁读什么）

- `.agents/AGENTS.md` → promote 时复制为 root `AGENTS.md`。pi 沿父目录链把它拼进树内**每个**会话（role ws 在 root 之下），是全局约定的唯一载体。
- `.onlyne/spec.toml` → 拓扑唯一真相。`prose` 字段是 role 身份提示词：welcome 时下发、client 缓存进 `client.db`、pi 插件注入会话。改 prose 后 `onlyne server reload` 生效，旧 receipt 会话拿新 welcome。
- `.onlyne/templates/flywheel/<role>/AGENTS.md` → 该 role 的深规（工作顺序、产物纪律），generate 渲进 ws 后经 pi 链进该 role 每个会话。
- `.onlyne/templates/flywheel/<role>/.pi/settings.json` → 模型三元组（provider/model/thinkingLevel）；generate 会把 `agent_package` 的插件 vendor 进 ws 并改写 settings 指向工作区内副本。
- root `.pi/SYSTEM.md` → supervisor 会话的注入指引（admin 面、空转判定、职责边界）。

## 2. 工具链安装（无发布渠道，源码构建）

crates.io 的 `onlyne` 0.5.x 是旧形态占名，npm 的 `pi-onlyne` ≤0.9.1 是旧协议——都不要装。

```bash
git clone -b v1.0.0-beta.4 https://github.com/dbydd/onlyne && cd onlyne   # 2666ede；beta.3 亦兼容（哨兵方案跨版本）
cargo build --release   # 全新 clone 实测 ~60s
cp target/release/{onlyne,onlyne-server,onlyne-client,onlyne-gateway,onlyne-tui} ~/.cargo/bin/
codesign --force --sign - ~/.cargo/bin/onlyne*   # macOS 必做：复制后的二进制签名失效，直接 exec 收 SIGKILL
onlyne version   # {"onlyne-cli":"1.0.0","protocol":1}；协议不匹配握手报 protocol_version，fail-fast
```

动词面（勘正版，照抄进任何脚本）：瘦入口 `onlyne --server-root <root>` 持有 `send|control|ledger|faults|roles|sessions|watch|history|reload|repair_*`；`onlyne-server` 二进制只有 `init|run|start|stop|status|generate`；`onlyne-client` 持有 `run|start|stop|status|roles|sessions|history|watch`（ws 面用 `--workspace <ws>`）。`onlyne control` 的通用 flag 在子命令前：`onlyne control --server-root R --from _supervisor --task <id> [--reason ...] probe`。send 回执 `{"ok":true,"data":{kind,msg_id,op_id,state,task}}`，task 为 uuid v4、state 取 in_flight|queued。

版本闸钉 tag `v1.0.0-beta.4`（= 2666ede；beta.2/d0f4e60 因 glob 回归作废禁钉，beta.3/125e351 兼容哨兵方案）。v1 见到 legacy `.onlyne/`
（含旧 state.db 表 / `channels/` / swarm marker）会 exit 2 且零写入——这是特性：旧树先整目录
`mv .onlyne .onlyne.v0-archive/`（迁移前用旧 CLI 把在飞任务记 failed 收官、`sqlite3` 导旧 ledger CSV 进 runs/）。

## 3. 主题要改的面（文件级清单）

| # | 文件 | 改什么 | 生效点 |
|---|---|---|---|
| 1 | `.agents/AGENTS.md` 五个 THEME 槽 | 研究问题/runs 结构/评测契约/角色表/entry | root AGENTS.md（全链） |
| 2 | `.onlyne/spec.toml` [[client]] | role 增删、prose、allowed_*、timeout/intent、max_sessions/reuse | `server reload` |
| 3 | `.onlyne/templates/flywheel/<role>/AGENTS.md` | role 深规 | 该 role ws |
| 4 | `.onlyne/templates/flywheel/<role>/.pi/settings.json` | 模型三元组 | 该 role ws（generate 时并入插件引用） |
| 5 | `pool/ideas.jsonl` | 种子 idea（硬门字段） | scout 消费 |
| 6 | `[server].agent_package` | 本机 onlyne checkout 的 `plugins/onlyne-agent-pi` 绝对路径 | generate vendor 进 `<ws>/.onlyne/agent/onlyne-agent-pi/`（目录名=basename）；模板 `.pi/settings.json` 的 packages 是哨兵字面值 `"__AGENT_PACKAGE_ABS__"`，装配时 `sed -i '' "s\|__AGENT_PACKAGE_ABS__\|$ABS\|g" .onlyne/spec.toml .onlyne/templates/flywheel/*/.pi/settings.json` 同步替换；generate 的 settings 重写只认 spec 字面值==settings 字面值，产物即 `../.onlyne/agent/onlyne-agent-pi`。`{{agent_package}}` 占位符在 settings 渲成无 `../` 形态＝pi 0.85.1 拒载（源码+ARIS 双实证，beta.3@125e351 与 d0573e3 同此）|
| 7 | `[server].cert_pin` / 各 role `key` | `server init` / `client init` 产出回填；未 init 前先播合法长度 32 字节占位（`AWAAAAAAAA...AAA=`），非法 key 会让全量 parse 连 `client init` 都跑不动 | 握手 |
| 8 | `.pi/SYSTEM.md`、`README.md` | 口径微调（一般不动） | supervisor 会话 |

relays 一致性铁律：A 的 `handoff B` 要求 B 条目 `allowed_senders` 含 A，且 A 条目
`allowed_targets` 含 B；`_supervisor` 永不出现在任何 `allowed_targets`（上行零常驻边，
completion 走 origin 自动通道不经 ACL）。promote check 4 机器核这条。

## 4. 通电三门（promote 之后，一次性）

1. **server 活**：`onlyne-server start --root .`（自带 detached+pid）后 `onlyne-server status --root .` 的 `socket_present=true` 是真相（`run` 不写 pid、`status.running` 只认 pid 文件，别拿它判活）。
2. **client 连**：每个启用 role `onlyne roles` 显示 connected；welcome/provisioned 完成（首轮 attach 自动）。
0. **渲染抽检**：`python3 -c "import json;print(json.load(open('<ws>/.pi/settings.json'))['packages'])"` 必须是 `['../.onlyne/agent/onlyne-agent-pi']` 且 `<ws>/.onlyne/agent/onlyne-agent-pi/` 有货（`{{agent_package}}` 占位符形态渲成无 ../ 的 `.onlyne/agent/…`＝pi 0.85.1 拒载，beta.3 与 d0573e3 源码同此，ARIS 真机实证）。
2. **client 连**：每个启用 role `onlyne roles` 显示 connected；welcome/provisioned 完成（首轮 attach 自动）。 得 receipt `state=in_flight`，role 会话里出现任务注入，`onlyne ledger` 有投递与 ack 行。绿了再批量起其余 client。

## 5. promote.sh 九检（校验语义）

1 THEME 槽清空；2 每 role 模板目录 + settings 三元组非空；3 `★` 恰好一个且是 spec 在册 role；
4 spec[[client]]==模板目录、_supervisor admin=true、prose 非空、relay 边双向闭合、targets 不含 _supervisor；
5 角色表与 spec 逐名对齐；6 种子 idea 过 schema 硬门；7 payload/ 与 research/ 有实物；
8 agent_package 绝对路径存在且 package.json ≥1.0.0；9 四二进制在 PATH、`onlyne version` ≥1.0.0、zellij/orca 至少一个（探测序 zellij→orca→fake，`ONLYNE_BACKEND` 可钉）。

actions：建 `theme/<slug>` 分支 → root AGENTS.md → `.onlyne/flywheel.json`（stage=live、roles、entry_role）→
退役装配材料（`.agents/AGENTS.md`、`BOOTSTRAP.md`、`.agents/skills/flywheel-setup/`）→ commit。
运行时通电在 AGENTS.md 冷启动节，人执行，脚本不起任何 daemon。

## 6. 装配阶段表

| 阶段 | 决策 | 动的文件 | 完成判据 |
|---|---|---|---|
| A 定题 | 研究什么、什么算进步、禁区 | 五个 THEME 槽 | 槽内注释块全部替换 |
| B 拓扑 | role 增删、边、模型档位、长跑 timeout | spec.toml + templates/ 目录 | check 2/4/5 绿 |
| C 起草 | 术语、runs 结构、稿件口径、★ 选谁 | 槽、role prose/AGENTS、SYSTEM/README | 角色表==spec，★ 恰好一个 |
| D 种子 | 首批 idea | pool/ideas.jsonl | check 6 硬门绿 |
| E 装具 | 工具链、agent_package | §2 全套 + spec [server] | check 8/9 绿 |
| F 落分支 | 复核 dry-run 清单，人确认 | promote.sh | stage=live |
| G 通电+第一发 | 方向给不给、谁投 | server/clients、payload/first.md | §4 三门绿 + ledger 首行 in_flight |

## 7. 装配后退役面（theme 分支上应消失的东西）

| 材料 | 处置 |
|---|---|
| `.agents/AGENTS.md`、`BOOTSTRAP.md`、`.agents/skills/flywheel-setup/` | promote 删除（root AGENTS.md 接班） |
| `.onlyne/spec.toml`、`templates/`、`.agents/skills/onlyne-{supervisor,role}/` | 保留，运行期要读 |
| `.onlyne.v0-archive/`（若从旧树升上来） | 保留为只读历史，gitignore 已挡 |

## 8. 常见坑

- `onlyne-server status` 连不上 = 未通电（不是故障）；通电用 `onlyne-server start`（detached+pid），判活看 `socket_present`。
- note 打给离线 role 得 `recipient_offline` 是语义不是 bug；要排队就发 task。
- 同 `op_id` 换内容重发得 `conflict`；重试原帧重发。
- prose 改完必须 `onlyne reload --server-root .`（原子校验，坏 spec 保旧并记 `fault{spec_reload_failed}`）；先 `--dry-run` 看 spec-diff。
- e2e/验证脚本开头清库或 `onlyne control ... recycle` 收残 session（v1 无自动回收，D12 设计）。
- role 会话默认不带 `-ns`（omp 裁定：模板 skills 三件套靠 pi 发现进会话）。「确定零 skill 的极简 role」装机者自选加回。
- `promote.sh --dry-run` 零写入可反复跑；正式跑需用户逐项确认退役清单（脚本会打印）。
