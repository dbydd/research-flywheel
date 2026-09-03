---
name: not-enough-harness
description: "创造并反复迭代优化 LLM harness / agent workspace。把本该写成软件的需求改造成让 agent 直接干的环境：通过 supervisor/worker 双进程循环持续打磨工作区上下文、skills、运行时配置直到人类觉得好使。Use whenever user wants to create an environment harness, iterate a workspace, build an agent workspace that replaces software with agent labor, mentions RPG-Harness / autoresearch-everywhere / auto-research patterns, or needs supervisor-worker iterative workspace optimization. Also use for harness, workspace harness, 环境harness, 工作区打磨."
---

# Not Enough Harness — Harness 的 Harness

> 你不写软件，你造一个让 agent 把活干了的环境。然后让 supervisor 一遍遍改环境、换新 worker 重跑，直到人觉得“好使”。

灵感：[RPG-Harness](https://github.com/Ame-X/RPG-Harness) / [autoresearch-everywhere](https://github.com/Entrpi/autoresearch-everywhere) / [auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/auto-claude-code-research-in-sleep) — 共同范式是 **environment-as-software**。

---

## 0. 什么时候用这个 skill

- 用户说“帮我造个 harness / 工作区 / 让 agent 自己去干”
- 已有一个 harness 但不好使，需要迭代
- 需要 supervisor/worker / 双进程 / 分身 的工作流
- 提及上述三个 repo 或类似模式

## 1. 核心模型（必读，20 秒）

```
┌─────────────┐  改上下文/配置   ┌──────────────────┐
│ supervisor  │ ─────────────► │ workspace on disk│
│ (常驻/主)   │  观察&收割      │  AGENTS.md       │
│             │ ◄───────────── │  .agents/skills/ │
│  拉起/监控  │                 │  .pi/**/config   │
└──────┬──────┘                 │  env / plugins   │
       │ herdr pane split       └──────────────────┘
       │ 每次全新 worker               ▲
       ▼                               │ 下一次迭代 supervisor 再改
┌─────────────┐  完整任务链路    ┌─────┴────────────┐
│ worker #N   │ ─────────────► │ 任务产物/日志/   │
│ (一次性)    │  产生摩擦&工具  │ 可复用工具/痛点 │
└─────────────┘                 └──────────────────┘
       X  用完即弃，下一轮必须全新 worker（旧上下文视为已污染）
```

**铁律：**

1. supervisor 只改环境，不直接做任务；worker 只做任务，不改环境。
2. 每次迭代必须拉起**全新 worker**，不得复用旧 session / 旧 pane 里的 agent。
3. 有 herdr 时 supervisor 必须走 herdr 拉起；无 herdr 降级为 subagent。
4. 停止标准是**主观“好使”**——人类用起来不费力，而非指标阈值。

---

## 2. 执行流程

### Phase 0 — 接题（2 分钟内完成）

问清三件事（没答就用合理默认值先跑，边跑边纠）：

1. **造什么 harness？** — 一句话目标 + 一个“完整任务链路”示例（输入→输出）。
2. **工作区在哪？** — 新建目录还是就地改造？`git init` 了吗？
3. **任务从哪来？** — 人工给 prompt / 队列文件 / 定时拉取？

记录到 `workspace/QUEST.md`（若不存在则创建）。

### Phase 1 — Supervisor 就位

supervisor 是**当前主会话**。职责：

- 创建/修改三类文件（详见 `references/workspace-layers.md`）：
  - **上下文配置**：`AGENTS.md`, `MUSE.md`, `.agents/skills/`, `SKILL.md`, `QUEST.md`, `SOUL.md` 等
  - **环境文件**：`.env`, `package.json`, `Makefile`, `docker-compose.yml` 等
  - **运行时配置**：`.pi/` 下的 `settings.json`, `AGENTS.md`, `SYSTEM.md`, 覆盖配置、工作区插件
- 准备 `worker` 的启动 prompt（见 `references/worker-prompt.md` 模板）
- 初始化迭代日志 `harness-log.md`（iteration, 改了什么, worker 表现, 收获）

> 首次迭代：先搭最小可用 workspace（一个 AGENTS.md + 一个 skill 或一段 system prompt 就够），不要一次搭完。

### Phase 2 — 拉起 Worker（全新）

#### 有 herdr（`HERDR_ENV=1`）

```bash
# 1. 选方向：宽 pane 向右、窄/高 pane 向下；保留当前 cwd，不抢焦点
herdr pane split --current --direction right --cwd "$PWD" --no-focus
# → .result.pane.pane_id = NEW_PANE

# 2. 在新 pane 起 agent（命名含迭代号，避免复用）
herdr agent start harness-worker-N --kind pi --pane <NEW_PANE> -- --cwd <workspace>

# 3. 下发任务
herdr agent prompt harness-worker-N --wait --timeout 600000 "<worker prompt>"
```

#### 无 herdr（降级）

用 `subagent` 起一次性 worker：`agent: delegate` 或 `general`，`task` 为 worker prompt，`cwd` 指向 workspace。同样**每轮新建**，不得复用。

> 详见 `references/herdr-integration.md` 的完整命令与坑位。

### Phase 3 — 观察 & 收割（supervisor 的核心价值）

worker 运行期间 supervisor **不干预任务**，只观察：

- `herdr agent read <worker> --source recent-unwrapped --lines 200` 轮询（或 `herdr pane read`）
- 或 subagent 的流式输出

收割清单（每轮必做）：

- [ ] **可复用工具**：worker 是否手写了某段脚本/函数可沉淀为 `scripts/` 或 skill？→ 抽出来。
- [ ] **可改进点**：worker 在哪卡住/绕路/反复试错？→ 对应改 AGENTS.md / skill / .pi 配置。
- [ ] **上下文污染**：worker 是否因历史消息做出错误假设？→ 记入下轮 prompt 需显式约束。
- [ ] **人类摩擦**：如果人在旁边看，哪一步会觉得“还得我来”？→ 优先修。

把结论追加到 `harness-log.md`。

### Phase 4 — 迭代

supervisor 基于收割结果**只改环境**，然后回到 Phase 2 拉起 `worker #(N+1)`。

- 每次改动要小、可回滚（git commit per iteration）。
- 不要同时改多处导致无法归因。
- worker 产物保留在 `runs/<iteration>/`，供对比。

### Phase 5 — 停止（“好使”判定）

**无固定阈值**，由人感性判定。提供一个 30 秒自检清单，全部 ✅ 即可停：

- [ ] 新人（或未来的你）不读代码，只看 `AGENTS.md` 就能让 worker 跑通一次完整任务
- [ ] 连续 2 轮 worker 无需人工救场
- [ ] 没有“每次都要手动…”的步骤
- [ ] 你愿意把这个 workspace 发给同事而不觉得丢人

人说“好使了”就停；人说“再磨一轮”就继续。supervisor 不自行宣布完成。

---

## 3. 目录约定（建议，不强制）

```
<workspace>/
├── AGENTS.md              # 工作区上下文（supervisor 主改）
├── QUEST.md               # 一句话目标 + 任务链路示例
├── harness-log.md         # 迭代日志（supervisor 维护）
├── .pi/                   # pi 运行时配置/覆盖/插件
├── .agents/skills/        # 工作区 skills（supervisor 主改）
├── scripts/               # 从 worker 收割的可复用工具
└── runs/
    ├── 001/
    │   ├── worker.log
    │   └── output/
    └── 002/ ...
```

---

## 4. 反模式（别这么做）

- ❌ supervisor 顺手把任务做了 → 失去“环境是否好使”的检验
- ❌ 复用旧 worker → 上下文污染，误判 harness 质量
- ❌ 一次改 10 个文件 → 无法归因哪处改动起效
- ❌ 用固定指标（如 pass rate）替代人的“好使”感 → 本 skill 的停止条件就是主观的
- ❌ worker 里 `herdr server stop` / 关掉 supervisor 的 pane

---

## 5. 参考资料

- `references/workspace-layers.md` — 三类文件的详细清单与示例
- `references/herdr-integration.md` — herdr 拉起/监控/清理的完整命令
- `references/worker-prompt.md` — worker 启动 prompt 模板
- `references/stop-criteria.md` — “好使”的感性判定与演示脚本
