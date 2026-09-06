# Research Flywheel v3 — swarm 公共约定

本文件位于 swarm root，pi 会沿父目录自动拼进树内每个 session 的上下文。
workspace = role = 记忆+设定+历史文件；session = 该 role 手头的一件工作。
一切信息落文件，一切结论可回溯到 runs/ 与 papers/ 的路径。

## 目录

- `pool/ideas.jsonl`：idea 池（唯一队列，一行一条，见下 schema）。scout 追加，supervisor 消费。
- `runs/<run-id>/`：一轮 idea 的全部过程件。`idea.json` 快照、`derivation.md`、`lean/`、`measured/`、`verdict.md`。
- `research/`：证据。`frontier-notes.md` 是联网检索记录（URL+单行结论，追加式）。
- `experiment/`：领域代码。`evaluation/`：评测器。`papers/`：成稿（`<run-id>.md`）。
- `_onlyne_workspaces/`：生成的 worker 实例；`onlyne_in/`：本 workspace 的出口软链视图。

## swarm 任务写法（worker 之间）

- 收任务：调度器把带 `---swarm` 头的任务书以 followUp 送进你的 session。
- 交回：`onlyne_swarm_reply` 写 out（成功信号），或 `onlyne_mark_no_reply` 结束不产出。
- 发子任务：新 UUID 作 task_id，把下面格式的正文写入 `onlyne_in/<目标>/`：

  ```text
  ---swarm
  task_id: <uuid4>
  from: <你的树路径，如 model>
  reply_to: <你当前任务的 task_id>
  attempt: 1
  ---
  <Markdown 任务书：目标、输入路径、期望产出、done_when>
  ```

- 发一个子任务后你的 `pending_replies` +1；回调以 followUp 回来。回调没收齐就 reply = 提前终止，禁止。
- 失败也要 reply：正文首段写 `> swarm-failed: <原因>`，随后注明已落盘的现场路径。

## idea schema（pool/ideas.jsonl 一行一条 JSON）

字段：`id`、`origin`(user_seed|derived)、`parent_run`、`question`、`hypothesis`、`method`、`evidence`（非空路径数组，含 research/frontier-notes.md）、`evaluation`、`done_when`、`status`(queued|running|keep|failed)。

`evaluation`: `{objectives:[{metric,evaluator,direction,epsilon,baseline}], constraints:[{check,description}], pass_rule:"all"|"any"}`。evidence 为空、objectives 为空、done_when 为空 → 不进池。

## 飞轮宏观流（由 supervisor 闭合环路）

scout 出 idea → supervisor 入队 → model 推导/形式化/实现（可派 bench）→ bench 回值 → writer 成稿（可派 critic）→ critic verdict → supervisor 归档：keep 留 papers/，failed 记 verdict.md；随后从 open questions 或失败结论提取下一条 idea，再 submit scout。环路在 supervisor 手里，人随时可接管该 session。

## 纪律

- 改 `experiment/`、`evaluation/` 前读 runs/ 里上一轮记录；改动在任务产物里写明。
- 数值只从 measured/ 引，报告只写跑出来的东西。
- 名字即路径：worker 名保持 ≤7 字符、树保持一层（socket 路径长度限制）。
