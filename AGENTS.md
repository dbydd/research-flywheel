# 本工作区尚未装配

你是这个 clone 的第一个 pi 会话。先读 `.agents/skills/flywheel-setup/SKILL.md`，再按里面的阶段一步步配。

配完先跑 `./scripts/promote.sh --dry-run`。逐项校验通过后，向用户复述脚本会删除哪些文件。用户确认后再执行 `./scripts/promote.sh`。

红线：落定前不启动 onlyne server/client，不跑领域实验，不动 `.agents/AGENTS.md` 的结构，不动 `.onlyne/spec.toml` 的结构，不动 `.agents/skills/onlyne-{supervisor,role}/`。
