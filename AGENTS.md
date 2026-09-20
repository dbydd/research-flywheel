# 本工作区尚未启用（gemini 双子模板，开发中）

你是本工作区第一个 pi 会话。这是双子模板的开发区，不是运行区。

- 流程与运维正本：`README.md`。
- 角色面正本：`.agents/AGENTS.md`（promote 后成为仓根 `AGENTS.md`）。
- 拓扑唯一真相：`.onlyne/spec.toml`；role 细则与模型位：`.onlyne/templates/gemini/<role>/`。

落定前不启动 onlyne server/client，不跑领域实验，不动 `spec.toml` 的结构与模板目录结构。

设计重点未决：防漂移的文件组织（一跳的入口文件、长度封顶、历史归档形态）。这一层讨论清楚前，`runs/` 只保留「一件任务一个子目录」的最小约定。
