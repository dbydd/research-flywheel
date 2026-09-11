# ARIS Flywheel（onlyne-swarm 复刻 ARIS 全自动科研环）

本工作区用 `onlyne-swarm` 五角色飞轮复刻 [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) 的全自动科研工作流。

ARIS 是一套 Markdown-only skills 的自主 ML 研究系统，流程为：文献→idea 发现→实验→跨模型评审循环→论文写作→同行评审 rebuttal。

ARIS 各技能到本飞轮的映射：

- `/idea-discovery` → scout
- `/experiment-bridge` → model + bench
- `/auto-review-loop`（4 轮评审、cross-model jury）→ critic 的 verdict 修订环
- `/research-pipeline` 全链 → 飞轮宏观流本身
- `/research-wiki` 持久记忆 → hindsight bank

主题证据锚点见 `research/aris-workflow-summary.md`。

三个词先说清：workspace = role，指该角色的「记忆+设定+历史文件」；session = 手头一件工作；任务 = session = 一跳。

工作模型是射后不理，即发出去就不等回复。一轮 session 的动作序列：恢复上下文 → 工作 → `swarm_send` 激发下游（可选）→ 落文件 → `swarm_complete` 退出。

session 对下游零等待。结果经文件与台账（`.onlyne/ledger.jsonl`）呈现，接力任务唤醒下一个单位。环路开放，靠 supervisor 或人闭合。

## 前置

- `onlyne` ≥0.5.1、`onlyne-swarm` ≥0.5.0、`orca`（含 `orca` CLI）、`pi` + `pi-onlyne` ≥0.8.1
- 已配置的 pi model/provider
- macOS unix socket 路径限制：实例目录 `.ws`、socket `run/s` 已缩短；root 路径 ≤90 字符即可，角色名与嵌套层数基本解放

## 起飞

```bash
# 1. 首次使用（本模板已跟踪 .onlyne/swarm.workspace.jsonc 与角色模板；克隆后重建运行时）
onlyne-swarm init && rm -rf .agents/.schedule/planner && onlyne-swarm export-skill

# 2. 生成 worker 实例树（读 .agents/.schedule/）
onlyne-swarm workspace create

# 3. 起调度器（前台，统一保活各 daemon）
onlyne-swarm run

# 4. 另开终端：root 开 pi 会话即 supervisor，或直接 CLI 提交
onlyne-swarm submit --to scout --payload payload.md
onlyne-swarm tui
```

## 角色树

```text
.        supervisor（root）：队列记账、归档、闭合飞轮环路
├─ scout   检索+证据+idea 入池 → 唤醒 supervisor
├─ model   推导+Lean 形式化+出 spec（不写 experiment/ 代码）→ 激发 bench / writer
├─ bench   跑评测落 measured/ → 唤醒 writer
├─ writer  成稿（带溯源数字）→ 激发 critic
└─ critic  对照证据审稿 → verdict.md → 唤醒 writer（revise）或 supervisor（accept/reject）
```

接力拓扑的完整描述在根目录 `AGENTS.md` 的宏观流一节，每个 session 自动继承该文件。调度机制与工具用法见 `.agents/skills/onlyne-swarm/SKILL.md`。

## 协议样例

[`examples/marquee`](examples/marquee/README.md) 是独立的五节点 `a→b→c→d→e→a` 流水灯。它的用途是验证三件事：session 自回收 ack、裸 relay / scheduler deliver 分层、环状自激与全量重试。

它不参与科研 idea 池与论文归档。执行时复制到短路径目录，按样例 README 启动。canonical 副本同时随 `onlyne-swarm/examples/marquee` 发布。

## 动力源

seed 由人给（方向+问题）。之后每轮收尾，supervisor 从论文 open questions 或失败结论提取下一条 idea 入池。idea 无证据或无评测契约不进池。

自激发无熔断，终结靠人：`onlyne-swarm cancel <task-id>`（按 `transfer_send_to` 血缘整族取消）或 TUI `c` 键。
