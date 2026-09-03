# Workspace 三层文件清单

supervisor 只改环境，环境分三层。按需改，不必一次改完。

---

## Layer 1 — 上下文配置（最常改）

决定 worker“看到什么”和“知道怎么做”的文件。

| 文件 | 作用 | 何时改 |
| ------ | ------ | -------- |
| `AGENTS.md` / `MUSE.md` | 工作区总纲：目标、约束、工作流 | 每轮都可能微调，worker 反复误解的地方就该写进去 |
| `QUEST.md` | 一句话目标 + 完整任务链路示例（输入→输出） | 目标澄清或链路变更时 |
| `SOUL.md` / `IDENTITY.md` | 角色/语气设定 | worker 风格跑偏时 |
| `.agents/skills/<name>/SKILL.md` | 局部能力：触发条件 + 执行步骤 | worker 某类子任务反复手写相似脚本 → 沉淀为 skill |
| `.agents/skills/*/references/*.md` | skill 的按需参考资料 | 细节太多塞不进 SKILL.md 时外置 |
| `AGENTS.md` / `CLAUDE.local.md` 等 | 补充覆盖 | 项目有特殊覆盖需求时 |

**写法要点：**

- 写给 agent 看，不是写给人看——用祈使句，给步骤，不给散文。
- 每次只加“刚好让上一轮 worker 不再踩坑”的那几行，不做完美重构。

---

## Layer 2 — 环境文件（按需）

决定 worker“能跑起来”的文件。

| 文件 | 作用 | 何时改 |
| ------ | ------ | -------- |
| `.env` / `.env.example` | 环境变量、API Key 占位 | 新增外部依赖时 |
| `package.json` / `requirements.txt` / `pyproject.toml` | 依赖 | worker 需要新库且该库值得固化时 |
| `Makefile` / `justfile` / `Taskfile.yml` | 快捷命令 | 重复敲的长命令 → 收敛为一个 make target |
| `docker-compose.yml` / `Dockerfile` | 容器环境 | 任务依赖特定运行时才加 |
| `scripts/*.sh | py` | 可复用工具脚本 | 从 worker 收割的“写过第二遍的东西” |
| `.gitignore` | 忽略规则 | `runs/`、`*.log` 等产物目录 |

---

## Layer 3 — 运行时配置（pi / codex 专属，最易被忽略）

决定 agent 运行时“被怎么拉起和约束”的文件。

| 路径 | 作用 | 何时改 |
| ------ | ------ | -------- |
| `.pi/settings.json` | 模型、provider、thinking level、重试策略 | 需要固定模型或行为时 |
| `.pi/AGENTS.md` | 项目级 AGENTS，覆盖全局 | 工作区需要独立于全局的指令时 |
| `.pi/SYSTEM.md` | 覆盖 system prompt（信任项目级时生效） | 需要定制系统提示时 |
| `.pi/APPEND_SYSTEM.md` | 追加到 system prompt 末尾 | 轻量追加指令 |
| `.pi/skills/` | 项目私有 skills（仅本工作区可见） | 同 Layer 1，但作用域限于 pi |
| `.pi/plugins/` / `.pi/extensions/` | 工作区插件 | 有可复用工具要以插件形式常驻时 |
| `~/.pi/agent/settings.json` | 全局配置（慎改） | 仅当需要全局生效时，优先改 `.pi/` 项目级 |

**注意：**

- `.pi/` 下的改动对新拉起的 worker 立即生效——这正是“每次全新 worker”的价值：验证配置是否真的起作用。
- 不要让 worker 自己改 `.pi/`——这是 supervisor 的职责，保持职责边界清晰。
