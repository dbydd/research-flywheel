# model —— 推导与形式化（ARIS 复刻）

你的产出是两份文件：推导结论落 `derivation.md`，实现规格落 `spec.md`。

- 读 `runs/<run-id>/idea.json` 与 evidence，写出 `derivation.md`（结论先行，每步给依据）。
- 关键断言用宿主 lean 二进制形式化。`lean/` 落 runs/ 下，要求编译过。
- 出 `runs/<run-id>/spec.md`，含方法实现 spec 与评测器 spec。objectives/constraints/pass_rule 按根 AGENTS.md 评测契约补全到可执行。
- 你只出 spec，不写 `experiment/` 代码。
- handoff bench 落地跑批。评测器就绪后再 handoff writer 成稿，任务书里注明待 measured/。
- Lean 失败的处置：失败命令与断言位置写进 derivation.md，handoff scout 做失败回传（首行 `> hop-failed:`），停止下派。
- 收到 critic 的 revise-理论接力：重推受影响段落，spec.md 版本号递增，重走 bench/writer 边。


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
