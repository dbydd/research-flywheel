目标：把双子的一环跑通一次：castor 出第一步任务书交给 pollux，pollux 做完交回，castor 验收并收束。

输入：
- `AGENTS.md`（角色表、一跳的生命周期、任务书四段、文件纪律）
- `runs/`（产物根，本轮从这里开新目录）

期望产物：
- `runs/<slug>/`（slug 自取，形如 `boot-01`）：本跳的现场记录 `notes.md`，写明本跳做了什么、留下哪些文件路径、交给 peer 的任务书全文。
- 产物路径进 `onlyne_complete` 的 text。

下一跳建议：handoff pollux，任务书四段写全，第二步的动作与验收判据要具体到它能独立执行；pollux 交回后由 castor 验收，判据满足即收束（只 complete 不 handoff）。
