# Research Flywheel v3

基于 `onlyne-swarm` 的全自动科研飞轮模板。workspace = role（记忆+设定+历史文件），session = 手头一件工作，task = session，回调即消息。环路开放，靠 supervisor 或人闭合。

## 前置

- `onlyne` ≥0.5、`onlyne-swarm` ≥0.1.2、`orca`（含 `orca` CLI）、`pi` + `pi-onlyne` ≥0.6
- 已配置的 pi model/provider
- macOS unix socket 路径限制：swarm root 路径 ≤90 字符，worker 名 ≤7 字符、树一层

## 起飞

```bash
# 1. 首次使用（本模板已跟踪 .onlyne/ 描述文件；克隆后重建运行时并刷新 skill）
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
.        supervisor（root）：队列记账、派单、闭合飞轮环路
├─ scout   检索+证据+idea 入池
├─ model   推导+Lean 形式化+实现，可派 bench
├─ bench   跑评测，回实测值与 delta
├─ writer  成稿（带溯源数字），可派 critic
└─ critic  对照证据审稿，verdict+编号 finding
```

公共约定（目录、swarm 头写法、idea schema、宏观流）全在根目录 `AGENTS.md`——每个 session 自动继承。调度机制细节见 `.agents/skills/onlyne-swarm/SKILL.md`。

## 动力源

seed 由人给（方向+问题）。之后每轮收尾，supervisor 从论文 open questions 或失败结论提取下一条 idea 入池。idea 无证据或无评测契约不进池。
