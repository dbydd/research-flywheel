# Research Flywheel v3 — onlyne v1 公共约定（约定骨架）

本文件位于 server-root，pi 沿父目录链拼进树内每个 role 会话的上下文。
workspace = role = 记忆+设定+历史文件；session = 该 role 手头的一件工作，一跳即结。
一切信息落文件，一切结论可回溯到 runs/、papers/ 与 `onlyne ledger/history` 的 task 行。

<!-- THEME:research-question
装配时替换本注释块，填入：
- 本主题研究什么问题（一到三句，具体到可判断某轮实验是否推进了它）。
- 什么算进步：主度量、次度量、各自的判定阈值。
- 算力与时间预算、禁区（不做的事、不碰的数据集/模型）。
-->

## 工作模型（射后不理）

每个 session 的生命周期：恢复上下文 → 工作 → 激发下游（handoff，可选若干）→ `onlyne_complete` 交活退出。
session 对下游零等待。投递即返回一行 receipt JSON，后续全在 ledger 与 client intent 里走。
下游成果经文件与 ledger 呈现，接力任务唤醒合适的单位继续。

## 目录

- `.onlyne/spec.toml`：拓扑唯一真相（[server] + 每 role 一个 [[client]]：prose、ACL、timeout、intent）。未知键直接拒启动（`spec.toml:<行号>`）；运行期零配置 API，改动落这份文件再 `onlyne server reload`。
- `.onlyne/templates/flywheel/<role>/`：role 内容模板（AGENTS.md 深规、`.pi/settings.json` 模型位）。`onlyne server generate` 渲染出 ws，产物零绝对路径、整目录可 mv。
- `.onlyne/`（其余）：v1 运行时（state.db、run/s、keys、ws、logs）。除 spec.toml 与 templates/ 外不入 git。legacy 布局会被 v1 以 exit 2 拒绝并零写入，旧树退役时整目录改名 `.onlyne.v0-archive/`。
- `pool/ideas.jsonl`：idea 池（唯一队列，一行一条，见下 schema）。scout 追加并自取消费；supervisor 不碰队列。
- `runs/<run-id>/`：一轮 idea 的全部过程件。`idea.json` 快照、`derivation.md`、`lean/`、`measured/`、`verdict.md`。
- `papers/`：成稿（`<run-id>.md`）与 `figs/<run-id>/`（绘图脚本、成图、mermaid/tikz 源，图随稿件走，critic 追溯锚点单一）。figure 制作归 writer 兼职，无独立画图 role。
- `research/`：证据。`frontier-notes.md` 是联网检索记录（URL+单行结论，追加式）。
- `experiment/`：领域代码。`evaluation/`：评测器。
- `payload/`：注入给 entry role 的任务书落这里（`payload/first.md` 及后续）。
- `.onlyne/flywheel.json`（主题状态 stage/theme/roles/entry_role，运行态不入 git）与 `.onlyne/` 同层，v1 对未知文件无动作。

路径约定：本文件与一切任务书里的路径都相对 server-root。role session 的 cwd 在其 ws 目录；读写知识文件用任务书里的 root 相对路径，发现文件不存在先 `pwd` 确认站位。内容按引用交接：text 里给文件路径，接收方读文件；工作区字节从不上总线。

<!-- THEME:runs-layout
装配时替换本注释块，填入本主题对 runs/<run-id>/ 的目录结构与文件命名增补约定。
默认结构（idea.json/derivation.md/lean/measured/verdict.md）保持不变，主题专属产物列出落点。
-->

<!-- THEME:evaluation-contract
装配时替换本注释块，填入本主题的评测契约：
- objectives：指标、评测器、方向、epsilon、基线来源。
- constraints：check 项与描述（数据泄漏、随机种子、时间预算等）。
- pass_rule：all 还是 any。
idea 的 `evaluation` 字段必须能按本节直接填写，缺项的 idea 不进池。
-->

## onlyne 工具（v1 pi 插件在 role 会话提供）

- `onlyne_send {to, text, kind}`：激发新任务族（kind:"task"），或给在飞任务追加 note（kind:"note"，默认）。note 不建 session、目标离线即 `recipient_offline`。to 必须在本 role 的 `allowed_targets` 里，否则 `acl_denied`（行都不落）。
- `onlyne_complete {outcome, text}`：交活结项，`outcome: done|failed`（`cancelled` 走 CLI `onlyne complete --outcome cancelled`）。text 原样进 ledger `out_head`：单行、200 字符封顶，是唯一的上行通道——整句答案放这里，写不下就指产物路径。同一 task 第二次 complete 被拒，只喊一次。
- CLI 同面（shell 里跑）：`onlyne handoff --to <role> --task <id> --text "..."`＝转派新任务并记 `parent_task`+hop+1 血缘；`onlyne send`＝新任务族；`onlyne reply --to <envelope-id>`；`onlyne control recycle|probe|snapshot|cancel --task <id>`。
- 接力一律 handoff：ledger 顺 `parent_task` 链可查出整条科研链路，追溯成本为零。
- 失败交活：handoff/complete 的 text 首行写 `> hop-failed: <环节> <一句话>` 且 `outcome=failed`；产物与现场照写。
- 重试纪律：同一 `op_id` 换内容重发得 `conflict`；重试必须原帧重发。断线期照常干活：outgoing receipt 落 intent，重连按序补投。
- role 会话查现场：`onlyne who`、`onlyne watch --follow`（ws 内自动解析本地 socket）、pi 内 `/onlyne` 命令看连接与 task 统计。

## 任务书四段（send/handoff 的 text）

```text
目标：<一句话，做完算什么>
输入：<必须读的文件路径，runs/ 与 research/ 为准>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<完成后 handoff 谁、干什么；没有就写 无>
```

输入路径必须真实存在。接收方 session 是全新上下文，任务书里没写的路径它找不到。

## idea schema（pool/ideas.jsonl 一行一条 JSON）

字段：`id`、`origin`(user_seed|derived)、`parent_run`、`question`、`hypothesis`、`method`、`evidence`（非空路径数组，含 research/frontier-notes.md）、`evaluation`、`done_when`、`status`(queued|running|keep|failed)。

`evaluation`: `{objectives:[{metric,evaluator,direction,epsilon,baseline}], constraints:[{check,description}], pass_rule:"all"|"any"}`。evidence 为空、objectives 为空、done_when 为空 → 不进池。

## 角色表（叙述视图；拓扑真相在 spec.toml）

role 增删以 `.onlyne/spec.toml` 的 [[client]] 为准，本表与 `allowed_targets` 逐行对齐（promote 脚本核对一致性）。
`entry` 列标出第一发的注入对象，全表恰好一个 `★`；`model` 列与该 role 模板 `.pi/settings.json` 一致。

<!-- THEME:role-table
装配时替换本注释块为 markdown 表，列：

| role | 职责 | 上游 | 下游 | entry | model |
|---|---|---|---|---|---|

每行对应 spec.toml 一个 [[client]] 与 .onlyne/templates/flywheel/ 一个目录；`★` 全表恰好一个。
-->

<!-- THEME:entry-role
装配时替换为起始 role 的名字（与上表 `★` 行同名）。
本名字同时是 `onlyne send --to <这里>` 的参数。
-->

## 飞轮宏观流（接力闭环，从 spec.toml 边推导）

1. scout：产出入池后自取一条 queued idea，固化 `runs/<run-id>/idea.json`（status 改 running），`handoff model` 建模任务；supervisor 不进环。
2. 每个 role：完成后按 spec.toml 自己条目的 `allowed_targets` `handoff` 接力任务书，然后 `onlyne_complete {outcome:"done"}` 交活退出。
3. 产物未齐的跳：`onlyne_complete {outcome:"cancelled", text:"等待条件说明"}` 体面交回（或静默终止由 idle 回收兜底），等接力唤醒，不写无依据产物。
4. 闭环回到 scout：终局 verdict 由标出 accept/reject 流向的 role 自归档（keep 留 papers/、pool 改 keep；failed 记 verdict.md、改 failed），提取下一条 idea 入池（origin=derived），`handoff scout` 开新一轮。
5. 回执自动回 origin（离线也排队）：role 的 `allowed_targets` 从不含 `_supervisor`，上行零常驻边。

环路全在 role 之间自转，人通过 supervisor 或 TUI 观察现场。自激发有账：ledger 每跳一行，`onlyne ledger --task <id>` 顺链可查。终结靠人 `onlyne control cancel --task <id>` 或 TUI。

## 冷启动与第一发

装配完成的瞬间，工作区处于这些事实下：

- `stage=live`，`theme/<slug>` 分支已建，装配材料已消失。
- v1 运行时未起：`onlyne server status` 无 socket；`ws/` 未生成；spec.toml 的 REPLACE_ME 未替换。
- `tasks` 空，`runs/` 空，`papers/` 空，`pool/ideas.jsonl` 只有种子或空。
- 飞轮是反应式的：没有入站任务就什么都不会发生。`onlyne server start` 属于通电，第一发属于开跑。

通电顺序（一次性，装配收官时做）：

```bash
onlyne server init --root . --listen 127.0.0.1:7812      # 写 [server] 真相、keys、cert_pin
# 把 cert_pin 与各 role 的 ed25519 key 填入 .onlyne/spec.toml（role key 由 onlyne-client init 产出）
# 填 [server].agent_package = "<onlyne checkout>/plugins/onlyne-agent-pi"
onlyne server generate --root .                          # 渲染 ws（产物零绝对路径）
onlyne-server run --root . &                             # 或前台 tab；ONLYNE_BACKEND 选后端
onlyne-client run --workspace <ws/<topo>/<role>>         # 每 role 一个 client，起法见 BOOTSTRAP
```

启动动作二选一：

1. 用户给方向，supervisor 写 `payload/first.md`（含问题、约束、期望），执行
   `onlyne --server-root . send --from _supervisor --to <entry_role> --file payload/first.md`。
2. 用户自己在 CLI 投第一发，supervisor 事后从 ledger 与 `runs/` 接上下文。

本主题的起始 role 见 `.onlyne/flywheel.json` 的 `entry_role`（与角色表 `★` 行同名）。第一发落地后环即成形：
起始 role 产出入池并自取 queued 派给下游 → 环在 role 之间自转。后续每轮靠接力任务推进，启动只需要一发；
supervisor 不进环，只在人问起时从 runs/ 与 ledger 汇报现场。

## 维护与配置（supervisor 用）

- `spec.toml` 是唯一真相：[[client]] 的 prose/ACL/`max_sessions`/`reuse` 与 `[client.timeout]`（ready_ms=30000、running_ms=120000、idle_ms=60000）、`[client.intent]`（attempts=3、backoff_ms=[1000,2000,4000]）都在 role 条目上配。改完 `onlyne server reload`（`--dry-run`/`spec-diff` 预览），失败保旧 spec 并记 `fault{spec_reload_failed}`。
- 后端选择：`ONLYNE_BACKEND` env（`auto|zellij|orca|exec|fake`）。空值与 `auto` 按能力探测，顺序 orca→zellij→fake；命令行型 role 用 zellij/orca 起 session_command。SWARM_RUNTIME 已退役。
- role 模型/思考档 = `.onlyne/templates/flywheel/<role>/.pi/settings.json` 三元组；生成后 ws 内的 `.pi/**` 归 role 与 supervisor 所有，重 generate 前先看 spec 的模板发现规则（templates/<topo>/<role>/，basename=role 名）。
- ws 整目录 `mv` 即搬迁（设计内能力），client 全部路径自 `--workspace` 推导，intents/游标随 `.onlyne/` 同行；搬完重启该 client。
- 故障运维：`onlyne faults --open-only` 看核心检测；`onlyne repair inspect|retry|close|fail|ack`、`rebind|adopt` 把任务指回活 pane。`DeliveryState::Exhausted` 是终态，只有这里的显式决定能重开。
- 生命周期：`onlyne server start|stop|status|wait-ready`；`onlyne client run|start|stop|status`。停环先 server stop，client 各自退出；杀进程禁按名字猜，先查 pid 文件（`.onlyne/run/`）与祖先链。
- 错误词汇表：`acl_denied`＝spec 缺边；`unauthorized`＝key 未注册；`recipient_offline`＝note 打离线 role；`duplicate`＝同 op_id 原帧重发（返回原 receipt）；`conflict`＝同 op_id 换了body；`not_admin`＝未注册身份用 `--from`。被拒不落账。
- 观察：`onlyne --server-root . ledger|sessions|watch --follow --tier durable`；`onlyne tui` 两页板（role 网络图 + ledger）。
- 子集群上报：本 root 若挂到更大集群，把本 role 条目 `aggregate` 填父层身份，用 `onlyne cluster export-prose` 交接口文案；子层 role 名从不出现在父层 ledger。

## 纪律

- 改 `experiment/`、`evaluation/` 前读 runs/ 里上一轮记录；改动在任务产物里写明。
- 数值只从 measured/ 引，报告只写跑出来的东西。
- 失败也交活：跑不动的结论写进 runs/，`onlyne_complete {outcome:"failed"}` 交失败报告（text 首行 `> hop-failed: <原因>` + 现场路径），让下游有据可依。
- 发布面/工作面：草稿、中间件、探针、staged 代码先落 role 自己的 ws（私有区）；定稿产物一次性发布到任务书点名的 root 路径，并在 `runs/<run-id>/run-log.md` 记一行本地→发布映射。追加式台账（pool/ideas.jsonl、frontier-notes.md、run-log.md、measured/ 流件）直写 root——接力唤醒要求实时。peer 的 ws 可只读翻看；交接与审稿判据仍是任务书与 root 发布物。
