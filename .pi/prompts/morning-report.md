---
description: 晨间复盘：汇总 keeper/discard 结果、成本与待人工复核项（不落盘）
subagent: analyst
fresh: true
---
生成本工作区（staged SFT research flywheel）的晨间复盘，作为你的文本回复；只读，不写任何文件。聚焦范围：$@（无参数时取最近 24 小时内的事件）。

数据来源（按你的只读工具读取）：
- `status.md` — 当前 phase、latest run、pending actions
- `archive/ideas.jsonl` — 想法队列与状态分布
- `research-ledger.jsonl` — 终态账本（keep / discard / inconclusive / execution_error）
- `runs/<run_id>/journal/` 与 `reports/` — 近期运行与评审记录

输出结构：
1. **终态摘要** — 区间内 keep / discard / inconclusive / execution_error 的数量与一句话理由。
2. **成本** — actual cost 合计，与 requested cost 的偏差。
3. **待人工复核项** — 需要用户决策的事项（如 scheduler 注册、研究任务定义、异常终态）。
4. **队列状态** — queued / paused run 数量，是否需要 idea-generator 补货。
5. **风险提示** — 任何完整性路径异常、门禁失败模式或审计发现的复发问题。

纪律：数字必须引用具体文件与字段；无法确认的数字写 `unknown`；不得修复或补写任何证据文件。
