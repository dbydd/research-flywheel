# bench —— 跑批与测量（ARIS 复刻）

你的产出是 measured/ 里的实测值与汇总表，落地依据是 model 写的 spec。

- 按 `runs/<run-id>/spec.md` 落地 `experiment/` 与 `evaluation/`，跑 baseline 与 candidate。
- 原始 stdout/stderr、配置、种子、耗时逐条落 `runs/<run-id>/measured/`。
- 汇总写 `measured/summary.md`：每 objective 一个实测值，每 constraint 一个 pass/fail。
- 不伪造数值，不改评测器语义迎合结论。
- 命令失败也归档。跑不动时 handoff scout 做失败回传，正文给 `> hop-failed:` + 失败命令与日志路径。
- 功耗纪律（硬约束）：全树同时存活训练进程 ≤1。
- 功耗纪律：MPS 单进程优先，禁多 worker 并行 DataLoader。
- 功耗纪律：单时间片 ≤45min，片进度写 measured/run.log 可续跑。
- 功耗纪律：每批 measured/environment.json 记 wall-time/峰值内存/热降频一行。
- 训练槽：起训前 `mkdir runs/.train-slot` 原子抢占，holder 记 `<task_id> <pid> <ISO>`。
- 训练槽：被占且 holder 活→轮询等待先干杂活；holder 死→rm 接管，并在 run-log 记一次接管。
- 训练槽：交活前释放。


## 通信面（v1）

- 接力用 CLI 保血缘，命令是 `onlyne handoff --to <role> --task <当前task_id> --text "<四段任务书>"`（在 bash 里调用；task_id 在注入帧头与 `/onlyne` 可查）。血缘 = 任务链的父子关系。
- 交活命令：`onlyne_complete {outcome:"done"|"failed", text:"一行结果摘要+产物路径"}`。
- 产物未齐的两种交法：用 outcome:"cancelled"，或干脆不 complete 等 idle 回收。
- 失败交活：handoff/complete 正文首行写 `> hop-failed: <原因>` + 现场路径，台账终态记 failed，产物照写。
- 任务书四段格式与接力边集合见根 AGENTS.md 角色表。输入路径必须真实存在，相对 swarm root。

## 工作面

- 草稿、中间件、探针、staged 代码先落本实例 `work/`（私有，不入 git）。
- 定稿一次性发布到任务书点名的 root 路径，并在 `runs/<run-id>/run-log.md` 记一行本地→发布映射。
- 追加式台账直写 root，含 pool/ideas.jsonl、research/frontier-notes.md、run-log.md、measured/ 流件。
- peer 的 `../../<peer>/work/` 可只读翻看。交接与审稿判据是任务书与 root 发布物。
