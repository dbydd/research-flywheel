# 本工作区尚未装配

你是这个 clone 的第一个 pi 会话。先读
`.agents/skills/flywheel-setup/SKILL.md`，按它的阶段一步步配。
配完跑 `./scripts/promote.sh --dry-run`，逐项过校验后向用户复述将删除
哪些文件，用户确认再执行 `./scripts/promote.sh`。

红线：落定前不起 onlyne server/client，不跑领域实验，不动 `.agents/AGENTS.md`、
`.onlyne/spec.toml` 的结构与 `.agents/skills/onlyne-{supervisor,role}/`。
