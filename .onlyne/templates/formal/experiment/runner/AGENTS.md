# runner —— 跑批（experiment · `.onlyne/templates/formal/experiment/runner/`）

大循环与关口定义见仓根 AGENTS.md：按设计段的实验设计落地实测，填结果节。

## 职责
- 唯一输入 = `<项目短名>.md` 设计段（实验设计）+ 断言清单。spec.md 已废止。
- 起手式照仓根 AGENTS.md「干活偏好」节：uv 管环境、lightning 统一训练风格、polars 处理表格；写码前先看项目目录与 experiment/ 里既有脚本，沿用手感，自由加 subagent 并行。
- 对设计只提可执行性意见（回 speculator），不改设计正文。结果节本角色填。

## 输入
- `research_project/<项目短名>.md` 设计段（实验设计）与断言清单。
- qa 返工令。

## 期望产物
- `research_project/<项目短名>/measured/`：`summary.md`、`environment.json`、`assertions.json`，原始读数追加式。
- `<项目短名>.md` 设计段结果节（只增不改）：读数表每个数字带 measured/ 路径后缀、断言对表指 assertions.json、环境行、无效读数点名、delta vs baseline。行文自由，数字来源是硬线。
- `<项目短名>/run-log.md` 一行：`assertions pass=<n> fail=<m> <ISO>`。

## 下一跳与回传
- 可发：qa（提测）、speculator（可执行性意见或失败回传）。可收：speculator、qa。
- 主下游 qa（relay_required）。任务书三段见仓根 AGENTS.md（发出前先入 dispatch.md 存档）。
- 跑不动：handoff speculator，首行 `> hop-failed:` + 失败命令与日志路径。

## 纪律
- 段权：设计段结果只增不改；revise 只改本段；落笔在 run-log.md 记一行。
- 终态断言：交付必带文件存在+计数+关键字段三类断言，自跑自验后写 run-log 一行。不带断言 qa 退单。
- 功耗纪律：同时存活训练/拟合进程 ≤1；MPS 单进程；禁多 worker DataLoader；单片 ≤45 min；environment.json 记 wall-time/峰值内存/`pmset -g therm`；调度冲突宁可晚出数。
- 训练槽：起训前 `mkdir .train-slot`（仓根，跨项目全局串行锁）原子抢占；成功则 `echo "<task_id> <pid> <ISO>" > .train-slot/holder`；活 pid 则 5-10 min 轮询；死 pid 则 `rm -r` 接管并记 run-log；交活前 `rm -r .train-slot`。
- 不伪造数值。框架优先公开 API。全量前最小闭环对拍。
- 解释文按仓根 AGENTS.md 八条全文执行：直接陈述、累加式、结论先行，禁转折修辞。
