目标：先查 pool/ideas.md 有无 queued idea。如果无，则先做 ARIS 前沿检索入池。然后取一条 queued idea。固化 runs/<run-id>/idea.json。派工 analyzer。按 AGENTS.md 冷启动节核对本环拓扑。
背景：本环刚装配，pool/ 与 runs/ 均为空，这是飞轮第一跳。scout 供题、analyzer/model 出方案、bench 跑批、writer 成稿、critic 审稿归档；环转不转得起来，取决于池里有没有过硬的题。
输入：AGENTS.md（全约定，尤其「任务书六段」「idea 格式」与角色表）
pool/ideas.md（idea 池，一条一个小节；可能尚未建文件）
research/frontier-notes.md（检索台账，URL + 单行结论，追加式）
期望产物：runs/<run-id>/idea.json + 接力 analyzer 的任务书
自由度：按角色表惯例。检索时顺手记负证据与检索词命中数；idea 入池时把 parent_run 与 question 写清，方便 critic 归档时回溯血缘。
下一跳建议：analyzer（问题层分析 analysis.md）
