# Research Flywheel v3 — swarm 公共约定

本文件位于 swarm root，pi 会沿父目录自动拼进树内每个 session 的上下文。
workspace = role = 记忆+设定+历史文件；session = 该 role 手头的一件工作，一跳即结。
一切信息落文件，一切结论可回溯到 runs/、papers/ 与 .onlyne/ledger.jsonl 的路径。

## 工作模型（射后不理）

每个 session 的生命周期：恢复上下文 → 工作 → 激发下游（可选，若干）→ 交活退出。
session 对下游零等待。下游成果经文件与台账呈现，由接力任务唤醒合适的单位继续。

## 目录

- `pool/ideas.jsonl`：idea 池（唯一队列，一行一条，见下 schema）。scout 追加，supervisor 消费。
- `runs/<run-id>/`：一轮 idea 的全部过程件。`idea.json` 快照、`derivation.md`、`lean/`、`measured/`、`verdict.md`。
- `research/`：证据。`frontier-notes.md` 是联网检索记录（URL+单行结论，追加式）。
- `experiment/`：领域代码。`evaluation/`：评测器。`papers/`：成稿（`<run-id>.md`）。
- `.ws/`：生成的 worker 实例；`onlyne_in/`：本 workspace 的出口软链视图。
- `.onlyne/ledger.jsonl`：调度器台账（任务终态流水），所有单位可读，恢复上下文先查它。

路径约定：本文件与一切任务书里的路径都相对 swarm root。worker session 的 cwd 在 `.ws/<name>/`，root 即 `../../`；读写知识文件用这个锚点，发现文件不存在先 `pwd` 确认站位。

## swarm 工具（pi-onlyne 在 swarm 模式提供）

- `swarm_send {to, text}`：激发下游任务。to = 树相对路径（scout/model/bench/writer/critic，root 填 `_root`）。写完即忘，不等回执。text = 任务书（见下四段格式）。
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

## 飞轮宏观流（接力闭环）

1. supervisor：从 pool 取 queued idea，固化 `runs/<run-id>/idea.json`，`swarm_send model`，status 改 running。
2. model：推导+Lean+实现后 `swarm_send bench`（评测任务书），随后 `swarm_send writer`（带"等 measured/ 就绪"的提醒）。
3. bench：跑完落 `runs/<run-id>/measured/`，`swarm_send writer`（续作，指向 summary.md）。
4. writer：稿件成形后 `swarm_send critic`，随后 `swarm_complete`（批评家意见以接力任务进修订轮）。
5. critic：verdict + 编号 finding 落 `runs/<run-id>/verdict.md`；revise → `swarm_send writer`；accept/reject → `swarm_send _root`。
6. supervisor：被唤醒后归档（keep 留 papers/，failed 记 verdict.md），从 open questions 或失败结论提取下一条 idea 入池，推进队列。

环路在 supervisor 手里，人随时可接管该 session。自激发无熔断，终结靠人 `onlyne-swarm cancel <task-id>` 或 TUI。

## 纪律

- 改 `experiment/`、`evaluation/` 前读 runs/ 里上一轮记录；改动在任务产物里写明。
- 数值只从 measured/ 引，报告只写跑出来的东西。
- 失败也交活：跑不动的结论写进 runs/，`swarm_complete` 交失败报告（首段 `> hop-failed: <原因>` + 现场路径），让下游有据可依。
