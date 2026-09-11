# 第一发（v1 环复跑）

目标：续跑先前的研究循环。从 pool/ideas.jsonl 取 status=queued 的第一条，按你 AGENTS.md 的入池硬门复核后固化为 runs/<run-id>/idea.json（status 改 running），handoff model 建模。

现场注记：pool 里另有四条 status=running 的历史条目（003/006/008 及 004-torch 线，v0 环中断遗留）。它们的处置（跑完的判据文件在 runs/ 里核对后改状态、失败回传、或续用）属你的队列职责：先读对应 runs/ 现场再定，不许凭状态字段猜测，也不许无依据改写。

输入：pool/ideas.jsonl、runs/、research/frontier-notes.md、根 AGENTS.md。
期望产物：runs/<run-id>/idea.json、pool 状态更新、handoff 给 model 的任务书（四段格式）。
下一跳建议：无（按角色表自流转）。
