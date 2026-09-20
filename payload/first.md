目标：把双子的一环跑通一次：castor 出第一步任务书交给 pollux，pollux 做完交回，castor 验收并按判据收束。

输入：
- `AGENTS.md`（共享目标记录：主线、支线 todo、外部索引）
- `.onlyne/AGENTS.md`（角色行为约定：一跳的生命周期、任务书四段、记事纪律、onlyne 工具面）

期望产物：
- `runs/<slug>/notes.md`（本轮现场记录，slug 自取）：本跳做了什么、留下哪些文件路径、交给 peer 的任务书全文。
- 记事三条各归各位：支线状态进仓根 `AGENTS.md`，本 role 的过程条目进自己 ws 的 `AGENTS.md`，产物进 `runs/<slug>/`。

下一跳建议：handoff pollux，任务书四段写全，第二步的动作与验收判据要具体到它能独立执行；pollux 交回后由 castor 验收，判据满足即收束（只 complete 不 handoff）。
