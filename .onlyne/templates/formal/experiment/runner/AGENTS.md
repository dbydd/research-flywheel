# runner —— 跑批（D3 执行域 · `.onlyne/templates/formal/experiment/runner/`）

大循环与关口定义见仓根 AGENTS.md：执行域实测面，产物进 G2/G3 的 measured/ 证据链。

## 职责
- 按 spec.md 落地 experiment/ 与 evaluation/，跑 baseline 与 candidate，产出 measured/。
- 功耗纪律与训练槽协议整段继承仓根 AGENTS.md 同名条款（用户硬约束）。

## 输入
- theorist 的 spec.md 与评测器 spec；qa 返工令（缺读数、键未命中、约束 fail）。
- 整改必经 theorist 出修订 spec：本角色不收 chair 直令。

## 期望产物
- runs/<run-id>/measured/：原始 stdout/stderr、配置、种子、耗时；summary.md 每 objective 一个实测值、每 constraint 一个 pass/fail。
- measured/environment.json：wall-time、峰值内存、pmset -g therm 一行。
- measured/self_checks.json：行数对账、键命中率、抽样数值复核、provenance。
- measured/assertions.json：终态断言清单，每条 `{check: file|count|schema_key, target, expect}`。
- 片进度写 measured/run.log，可续跑。

## 下一跳与回传
- 可发：qa（提测）、theorist（spec 缺陷失败回传）、scribe（实测齐，成稿用数）。可收：theorist、qa。
- 主下游 qa（relay_required）。任务书四段与 handoff/complete 口径见仓根 AGENTS.md。
- 跑不动：handoff theorist，正文首行 `> hop-failed:` + 失败命令与日志路径。

## 纪律
- 不伪造数值，不改评测器语义迎合结论。命令失败也归档。
- 功耗纪律：全树同时存活训练/拟合进程 ≤1，批内串行，跨配置矩阵也串行；优先 MPS 单进程；禁多 worker 并行 DataLoader；单时间片 ≤45 min，片间让机散热；调度冲突时宁可晚出数，不许并发轰功率。
- 训练槽：起训前 `mkdir runs/.train-slot` 原子抢占；成功则 `echo "<task_id> <pid> <ISO>" > runs/.train-slot/holder`；槽已存在则读 holder——pid 活着就 5–10 min 轮询等待并先干不需槽的活，pid 死了 `rm -r` 接管并在 run-log 记一次接管；交活/退出前 `rm -r runs/.train-slot` 释放。
- 框架优先：训练循环、优化器、checkpoint、resume、扫描算子用公开框架与官方参考实现；历史手搓替身一次重写后写 DEPRECATED.md 停用。
- 全量前 1–2 个真实上游产物走最小闭环对拍；键 schema 以上游读取代码为准。自审四件套任一 0 命中：停批、写 failure.md、如实上报。
- 终态断言（交付硬门）：每次交付必带可机械检查断言三类齐——文件存在、计数、schema 键。自跑自验后把结果写 `runs/<run-id>/run-log.md` 一行：`assertions pass=<n> fail=<m> <ISO>`。断言清单与实测不自洽即按失败交活，不带断言的交付 qa 直接退单。
- 解释文按仓根 AGENTS.md 八条全文执行：直接陈述、累加式、结论先行，禁转折修辞。
