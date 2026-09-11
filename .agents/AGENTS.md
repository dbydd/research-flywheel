# Research Flywheel v3 — onlyne v1 公共约定（约定骨架）

本文件在 server-root。pi 沿父目录链把它拼进树内每个 role 会话的上下文。

workspace 就是一个 role，内容有记忆、设定、历史文件。session 是这个 role 手头的一件工作，一跳即结。所有信息写成文件。所有结论都能回溯到 runs/、papers/ 以及 `onlyne ledger/history` 的 task 行。

<!-- THEME:research-question
装配时替换本注释块，填入：
- 本主题研究什么问题（一到三句，具体到能判断某轮实验是否推进了它）。
- 什么算进步：主度量、次度量、各自的判定阈值。
- 算力与时间预算、禁区（不做的事、不碰的数据集/模型）。
-->

## 工作模型（射后不理）

每个 session 的生命周期：恢复上下文 → 工作 → 激发下游（handoff，可选若干）→ `onlyne_complete` 交活退出。

session 不等下游。投递后立即返回一行 receipt JSON。后续进展都在 ledger 与 client intent 里。下游成果经文件与 ledger 呈现。接力任务唤醒合适的单位继续。

## 目录

- `.onlyne/spec.toml`：拓扑唯一真相。里面有 [server] 一节，以及每 role 一个 [[client]]：prose、ACL、timeout、intent。出现未知键时启动直接被拒，报错形如 `spec.toml:<行号>`。运行期没有配置 API。改动落这份文件，然后跑 `onlyne reload --server-root .`。
- `.onlyne/templates/flywheel/<role>/`：role 内容模板。里面有 AGENTS.md 深规和 `.pi/settings.json` 模型位。`onlyne-server generate` 渲染出 ws。spec 里出现的每个 role 都要有模板目录，缺一个就全不写并退 4；_supervisor 也需要 stub。产物零绝对路径，整目录可 mv。
- `.onlyne/` 的其余部分：v1 运行时，含 state.db、run/s、keys、ws、logs。除 spec.toml 与 templates/ 外都不入 git。legacy 布局会被 v1 以 exit 2 拒绝并且零写入。旧树退役时把整目录改名 `.onlyne.v0-archive/`。
- `pool/ideas.jsonl`：idea 池，也是唯一队列。一行一条，schema 见下。scout 追加并自取消费。supervisor 不碰队列。
- `runs/<run-id>/`：一轮 idea 的全部过程件。里面有 `idea.json` 快照、`derivation.md`、`lean/`、`measured/`、`verdict.md`。
- `papers/`：成稿（`<run-id>.md`）与 `figs/<run-id>/`。figs 里放绘图脚本、成图、mermaid/tikz 源。图随稿件走，critic 的追溯锚点保持单一。figure 由 writer 兼职制作，没有独立的画图 role。
- `research/`：证据。`frontier-notes.md` 是联网检索记录，格式为 URL 加单行结论，追加式。
- `experiment/`：领域代码。`evaluation/`：评测器。
- `payload/`：注入给 entry role 的任务书落这里，例如 `payload/first.md` 及后续文件。
- `.onlyne/flywheel.json`（主题状态 stage/theme/roles/entry_role，运行态不入 git）与 `.onlyne/` 同层。v1 对未知文件无动作。

路径约定：本文件与一切任务书里的路径都相对 server-root。role session 的 cwd 在其 ws 目录。读写知识文件时用任务书里的 root 相对路径。文件不存在就先 `pwd` 确认站位。内容按引用交接：text 里给文件路径，接收方读文件。工作区字节从不上总线。

<!-- THEME:runs-layout
装配时替换本注释块，填入本主题对 runs/<run-id>/ 的目录结构与文件命名增补约定。
默认结构（idea.json/derivation.md/lean/measured/verdict.md）保持不变，主题专属产物列出落点。
-->

<!-- THEME:evaluation-contract
装配时替换本注释块，填入本主题的评测契约：
- objectives：指标、评测器、方向、epsilon、基线来源。
- constraints：check 项与描述（数据泄漏、随机种子、时间预算等）。
- pass_rule：all 或 any。
idea 的 `evaluation` 字段必须能按本节直接填写。缺项的 idea 不进池。
-->

## onlyne 工具（v1 pi 插件在 role 会话提供）

- `onlyne_send {to, text, kind}`：激发新任务族用 kind:"task"。给在飞任务追加 note 用 kind:"note"，这也是默认值。note 不建 session，目标离线即返回 `recipient_offline`。to 必须在本 role 的 `allowed_targets` 里，否则返回 `acl_denied`，行都不落。
- `onlyne_complete {outcome, text}`：交活结项。`outcome: done|failed`。`cancelled` 走 CLI `onlyne complete --outcome cancelled`。text 原样进 ledger 的 `out_head`：单行、200 字符封顶。这是唯一的上行通道，整句答案放这里，写不下就指产物路径。同一 task 第二次 complete 会被拒，只喊一次。
- CLI 同面（shell 里跑）：`onlyne handoff --to <role> --task <id> --text "..."` 表示转派新任务，并记 `parent_task` 与 hop+1 血缘。`onlyne send` 开新任务族。`onlyne reply --to <envelope-id>` 回执。`onlyne control recycle|probe|snapshot|cancel --task <id>` 管任务。
- 接力一律用 handoff。ledger 顺 `parent_task` 链能查出整条科研链路，追溯成本为零。
- 失败交活：handoff/complete 的 text 首行写 `> hop-failed: <环节> <一句话>`，并带 `outcome=failed`。产物与现场照写。
- 重试纪律：同一 `op_id` 换内容重发得到 `conflict`。重试时原帧重发。断线期照常干活：outgoing receipt 落 intent，重连后按序补投。
- role 会话查现场：`onlyne who`、`onlyne watch --follow`（ws 内自动解析本地 socket）。pi 内用 `/onlyne` 命令看连接与 task 统计。

## 任务书四段（send/handoff 的 text）

```text
目标：<一句话，做完算什么>
输入：<必须读的文件路径，runs/ 与 research/ 为准>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<完成后 handoff 谁、干什么；没有就写 无>
```

输入路径必须真实存在。接收方 session 是全新上下文。任务书里没写的路径它找不到。

## idea schema（pool/ideas.jsonl 一行一条 JSON）

字段：`id`、`origin`(user_seed|derived)、`parent_run`、`question`、`hypothesis`、`method`、`evidence`（非空路径数组，含 research/frontier-notes.md）、`evaluation`、`done_when`、`status`(queued|running|keep|failed)。

`evaluation`: `{objectives:[{metric,evaluator,direction,epsilon,baseline}], constraints:[{check,description}], pass_rule:"all"|"any"}`。evidence 为空、objectives 为空、done_when 为空，三者任缺一项就不进池。

## 角色表（叙述视图；拓扑真相在 spec.toml）

role 增删以 `.onlyne/spec.toml` 的 [[client]] 为准。本表与 `allowed_targets` 逐行对齐，promote 脚本会核对一致性。`entry` 列标出第一发的注入对象，全表恰好一个 `★`。`model` 列与该 role 模板 `.pi/settings.json` 一致。

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

1. scout：产出入池后自取一条 queued idea，把 `runs/<run-id>/idea.json` 固化（status 改 running），再 `handoff model` 交建模任务。supervisor 不进环。
2. 每个 role：完成后按 spec.toml 自己条目的 `allowed_targets` 发 `handoff` 接力任务书，然后 `onlyne_complete {outcome:"done"}` 交活退出。
3. 产物未齐的跳：用 `onlyne_complete {outcome:"cancelled", text:"等待条件说明"}` 体面交回，也可以静默终止，由 idle 回收兜底。等接力唤醒再动，不写无依据产物。
4. 闭环回到 scout：终局 verdict 由标出 accept/reject 流向的 role 自行归档。keep 的稿件留 papers/，pool 该行改 keep；failed 的记 verdict.md，pool 改 failed。随后提取下一条 idea 入池（origin=derived），`handoff scout` 开新一轮。
5. 回执自动回 origin，离线也排队。role 的 `allowed_targets` 从不含 `_supervisor`，上行零常驻边。

环路全在 role 之间自转。人通过 supervisor 或 TUI 观察现场。自激发有账：ledger 每跳一行，`onlyne ledger --task <id>` 顺链可查。终结靠人跑 `onlyne control cancel --task <id>`，或者用 TUI。

## 冷启动与第一发

装配完成的瞬间，工作区处于这些事实下：

- `stage=live`，`theme/<slug>` 分支已建，装配材料已消失。
- v1 运行时未起：`onlyne-server status` 无 socket；`ws/` 未生成；spec.toml 的 REPLACE_ME 未替换。
- `tasks` 空，`runs/` 空，`papers/` 空，`pool/ideas.jsonl` 里是种子或空。
- 飞轮是反应式的：没有入站任务就什么都不会发生。`onlyne-server start` 属于通电，第一发属于开跑。

通电顺序（一次性，装配收官时做）：

```bash
onlyne-server init --root . --listen 127.0.0.1:7812      # 写 [server] 真相、keys、cert_pin   # 多树并机查重：7813=ARIS live，第二集群自选 7814+
# 回填 spec.toml 的 cert_pin；哨兵统一 sed：
#   ABS="<onlyne checkout>/plugins/onlyne-agent-pi"
#   sed -i '' "s\|__AGENT_PACKAGE_ABS__\|$ABS\|g" .onlyne/spec.toml .onlyne/templates/flywheel/*/.pi/settings.json
# 各 role key 先播合法 32 字节占位 key（base64(32×0x01)=AQEBAQ...AQE=）——非法 key 全量 parse 连 client init 都跑不动
onlyne-client init --workspace .onlyne/ws/$TOPO/<role>   # 逐 role 产真 key，回填 spec.toml
onlyne-server generate --root .                          # 渲染 ws（vendor 插件、零绝对路径）
onlyne-server start --root .                             # detached+pid；判活用 status 的 socket_present
onlyne-client run --workspace .onlyne/ws/$TOPO/<role>    # 每 role 一个 client（各一 tab）
```

启动动作二选一：

1. 用户给方向，supervisor 写 `payload/first.md`（含问题、约束、期望），执行
   `onlyne --server-root . send --from _supervisor --to <entry_role> --file payload/first.md`。
2. 用户自己在 CLI 投第一发，supervisor 事后从 ledger 与 `runs/` 接上下文。

本主题的起始 role 见 `.onlyne/flywheel.json` 的 `entry_role`，与角色表 `★` 行同名。第一发落地后环即成形：
起始 role 产出入池并自取 queued 派给下游，环在 role 之间自转。后续每轮靠接力任务推进，启动只需要一发。
supervisor 不进环，只在人问起时从 runs/ 与 ledger 汇报现场。

## 维护与配置（supervisor 用）

- `spec.toml` 是唯一真相。[[client]] 的 prose/ACL/`max_sessions`/`reuse` 都在 role 条目上配。`[client.timeout]` 有 ready_ms=30000、running_ms=120000、idle_ms=60000。`[client.intent]` 有 attempts=3、backoff_ms=[1000,2000,4000]。改完跑 `onlyne reload --server-root .`，可用 `--dry-run`/`spec-diff` 预览。失败时保留旧 spec，并记 `fault{spec_reload_failed}`。
- 后端选择：`ONLYNE_BACKEND` env，取值 `auto|zellij|orca|exec|fake`。空值与 `auto` 按能力探测，顺序 zellij→orca→fake。命令行型 role 用 zellij/orca 起 session_command。SWARM_RUNTIME 已退役。
- role 模型/思考档 = `.onlyne/templates/flywheel/<role>/.pi/settings.json` 三元组。生成后 ws 内的 `.pi/**` 归 role 与 supervisor 所有。重 generate 前先看 spec 的模板发现规则（templates/<topo>/<role>/，basename=role 名）。
- ws 整目录 `mv` 即搬迁，这是设计内能力。client 的全部路径自 `--workspace` 推导，intents/游标随 `.onlyne/` 同行。搬完重启该 client。
- 故障运维：`onlyne faults --open-only` 看核心检测。`onlyne repair inspect|retry|close|fail|ack` 与 `rebind|adopt` 把任务指回活 pane。`DeliveryState::Exhausted` 是终态，重开要经过这里的显式决定。
- 生命周期：`onlyne-server init|run|start|stop|status|generate`。通电用 start；run 不写 pid，status.running 只认 pid 文件，判活看 socket_present。`onlyne-client run|start|stop|status`。查询与运维动词全在瘦入口 `onlyne --server-root .`。停环先 server stop，client 各自退出。杀进程不要按名字猜，先查 pid 文件（`.onlyne/run/`）与祖先链。
- 错误词汇表：`acl_denied`＝spec 缺边；`unauthorized`＝key 未注册；`recipient_offline`＝note 打离线 role；`duplicate`＝同 op_id 原帧重发（返回原 receipt）；`conflict`＝同 op_id 换了 body；`not_admin`＝未注册身份用 `--from`。被拒不落账。
- 观察：`onlyne --server-root . ledger|sessions|watch --follow --tier durable`；`onlyne tui` 有两页板（role 网络图 + ledger）。
- 子集群上报：本 root 若挂到更大集群，把本 role 条目 `aggregate` 填父层身份，用 `onlyne cluster export-prose` 交接口文案。子层 role 名从不出现在父层 ledger。

## 纪律

- 改 `experiment/`、`evaluation/` 前先读 runs/ 里上一轮记录。改动在任务产物里写明。
- 数值只从 measured/ 引。报告只写跑出来的东西。
- 失败也交活：跑不动的结论写进 runs/，用 `onlyne_complete {outcome:"failed"}` 交失败报告。text 首行写 `> hop-failed: <原因>` 加现场路径，让下游有据可依。
- 发布面/工作面边界：草稿、中间件、探针、staged 代码先落 role 自己的 ws（私有区）。定稿产物一次性发布到任务书点名的 root 路径，并在 `runs/<run-id>/run-log.md` 记一行本地→发布映射。追加式台账（pool/ideas.jsonl、frontier-notes.md、run-log.md、measured/ 流件）直写 root，接力唤醒要求实时。peer 的 ws 可以只读翻看。交接与审稿判据仍是任务书与 root 发布物。
