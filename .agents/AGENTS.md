# Research Flywheel v3 — swarm 公共约定（约定骨架）

本文件位于 swarm root，pi 会沿父目录自动拼进树内每个 session 的上下文。
workspace = role = 记忆+设定+历史文件；session = 该 role 手头的一件工作，一跳即结。
一切信息落文件，一切结论可回溯到 runs/、papers/ 与 .onlyne/ledger.jsonl 的路径。

<!-- THEME:research-question
装配时替换本注释块，填入：
- 本主题研究什么问题（一到三句，具体到可判断某轮实验是否推进了它）。
- 什么算进步：主度量、次度量、各自的判定阈值。
- 算力与时间预算、禁区（不做的事、不碰的数据集/模型）。
-->

## 工作模型（射后不理）

每个 session 的生命周期：恢复上下文 → 工作 → 激发下游（可选，若干）→ 交活退出。
session 对下游零等待。下游成果经文件与台账呈现，由接力任务唤醒合适的单位继续。

## 目录

- `pool/ideas.jsonl`：idea 池（唯一队列，一行一条，见下 schema）。侦察位追加，supervisor 消费。
- `runs/<run-id>/`：一轮 idea 的全部过程件。`idea.json` 快照、`derivation.md`、`lean/`、`measured/`、`verdict.md`。
- `research/`：证据。`frontier-notes.md` 是联网检索记录（URL+单行结论，追加式）。
- `experiment/`：领域代码。`evaluation/`：评测器。`papers/`：成稿（`<run-id>.md`）。
- `payload/`：注入给起始 role 的任务书落这里（`payload/first.md` 及后续）。
- `.ws/`：生成的 worker 实例；`onlyne_in/`：本 workspace 的出口软链视图。
- `.onlyne/ledger.jsonl`：调度器台账（任务终态流水），所有单位可读，恢复上下文先查它。
- `.onlyne/flywheel.json`：主题状态（stage、theme、roles、entry_role），运行态，不入 git。

路径约定：本文件与一切任务书里的路径都相对 swarm root。worker session 的 cwd 在 `.ws/<name>/`，root 即 `../../`；读写知识文件用这个锚点，发现文件不存在先 `pwd` 确认站位。

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

## swarm 工具（pi-onlyne 在 swarm 模式提供）

- `swarm_send {to, text}`：激发下游任务。to = 树相对路径（角色名见下表，root 填 `_root`）。写完即忘，不等回执。text = 任务书（见下四段格式）。
- `swarm_complete {text}`：交活结项，本跳成功信号。text = 结果摘要 + 产物路径清单。
- `swarm_quit {reason?}`：静默退出，调度器记 failed。任务书前提不成立、无事可做时用。
- `swarm_status`：只读兜底，查当前 task_id 与已激发列表。
- 头构造在工具内部完成。手写 `---swarm` 块、直写 FIFO 都是错误做法。

## 任务书四段（swarm_send 的 text）

```text
目标：<一句话，做完算什么>
输入：<必须读的文件路径，runs/ 与 research/ 为准>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<完成后该 swarm_send 谁、干什么；没有就写 无>
```

输入路径必须真实存在。接收方 session 是全新上下文，任务书里没写的路径它找不到。

## idea schema（pool/ideas.jsonl 一行一条 JSON）

字段：`id`、`origin`(user_seed|derived)、`parent_run`、`question`、`hypothesis`、`method`、`evidence`（非空路径数组，含 research/frontier-notes.md）、`evaluation`、`done_when`、`status`(queued|running|keep|failed)。

`evaluation`: `{objectives:[{metric,evaluator,direction,epsilon,baseline}], constraints:[{check,description}], pass_rule:"all"|"any"}`。evidence 为空、objectives 为空、done_when 为空 → 不进池。

## 角色表（本主题拓扑的唯一事实源）

角色名与 `.agents/.schedule/<目录名>` 一一对应；增删 role 同时改这张表和这些目录。
supervisor 派工、`onlyne-swarm submit --to <role>`、`swarm_send <role>` 的目标名都查这张表。
`entry` 列标出第一发的注入对象，全表恰好一个 `★`。

<!-- THEME:role-table
装配时替换本注释块为 markdown 表，列：

| role | 职责 | 上游 | 下游 | entry | model |
|---|---|---|---|---|---|

每行对应 `.agents/.schedule/` 里的一个目录；`model` 与 template.workspace.jsonc 的 `model.*` 一致；
`★` 全表恰好一个。
-->

<!-- THEME:entry-role
装配时替换为起始 role 的名字（与上表 `★` 行同名）。
本名字同时是 `onlyne-swarm submit --to <这里>` 的参数。
-->

## 飞轮宏观流（接力闭环，从角色表推导）

接力规则按角色表的 `上游` / `下游` 列执行。通用条款：

1. supervisor：从 pool 取 queued idea，固化 `runs/<run-id>/idea.json`，派给表中标 `★` 的 entry role，status 改 running。
2. 每个 role：完成后按自己的 `下游` 列 `swarm_send` 接力任务书，然后 `swarm_complete` 交活退出。
3. role 的产物未齐时 `swarm_quit` 静默退出，等接力唤醒，不写无依据产物。
4. 闭环回到 root：终局 verdict 由表中标出 accept/reject 流向的 role `swarm_send _root`；supervisor 归档（keep 留 papers/，failed 记 verdict.md），从 open questions 或失败结论提取下一条 idea 入池，推进队列。

环路在 supervisor 手里，人随时可接管该 session。自激发无熔断，终结靠人 `onlyne-swarm cancel <task-id>` 或 TUI。

## 冷启动与第一发

装配完成的瞬间，工作区处于这些事实下：

- `stage=live`，`theme/<slug>` 分支已建，装配材料已消失。
- scheduler 未运行（promote 脚本不起常驻进程）；起 `onlyne-swarm run` 后各 workspace daemon 逐个 ready。
- `tasks` 表 0 行，`.ws/<role>` 下无 session，`runs/` 空，`papers/` 空，`pool/ideas.jsonl` 只有种子或空。
- 飞轮是反应式的：没有入站任务就什么都不会发生。`onlyne-swarm run` 属于通电，属于开跑。

启动动作二选一：

1. 用户给方向，supervisor 写 `payload/first.md`（含问题、约束、期望），执行
   `onlyne-swarm submit --to <entry_role> --payload payload/first.md`。
2. 用户自己在 CLI 投第一发，supervisor 事后从 ledger 与 `runs/` 接上下文。

本主题的起始 role 是投第一发时 `--to` 的那个名字（见上表 entry 列），它同时写进
`.onlyne/flywheel.json` 的 `entry_role` 字段。第一发落地后环才成形：
起始 role 产出入池 → `swarm_send _root` 唤醒 supervisor → supervisor 取 queued 派给下一个 role。
后续每轮的推进靠接力任务，启动只需要一发。

## 纪律

- 改 `experiment/`、`evaluation/` 前读 runs/ 里上一轮记录；改动在任务产物里写明。
- 数值只从 measured/ 引，报告只写跑出来的东西。
- 失败也交活：跑不动的结论写进 runs/，`swarm_complete` 交失败报告（首段 `> hop-failed: <原因>` + 现场路径），让下游有据可依。
