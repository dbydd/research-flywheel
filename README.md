基于 onlyne v1.0.0 的全自动科研飞轮模板。workspace = role（记忆+设定+历史文件），session = 手头一件工作，任务 = session = 一跳。

工作模型是射后不理：恢复上下文 → 工作 → `handoff` 激发下游（可选）→ 落文件 → `onlyne_complete` 交活退出。session 对下游零等待；投递即返回一行 receipt JSON，过程与回执全进 server ledger。成果经文件回来，接力任务唤醒下一个单位。环路开放，靠 supervisor 或人闭合。

## 前置

- onlyne v1.0.0-beta.2（源码构建：clone -b + `cargo build --release`，五产物进 PATH；无 crates.io/npm 渠道）
- `pi`（role 会话由 client 起，插件 `plugins/onlyne-agent-pi` 经 generate vendor 进各 ws，零 npm 依赖）
- 会话后端二选一在场：`orca` 或 `zellij`（`ONLYNE_BACKEND` 探测序 orca→zellij→fake）
- 已配置的 pi model/provider

## 起飞

```bash
# 0. clone 后照 BOOTSTRAP.md 装配主题（THEME 槽、角色拓扑、种子 idea）
./scripts/promote.sh --dry-run && ./scripts/promote.sh

# 1. 通电（一次性；人执行，supervisor 会话不起常驻）
onlyne server init --root . --listen 127.0.0.1:7812   # 产 keys/cert_pin，回填 spec.toml
onlyne server generate --root .                       # 渲染 .onlyne/ws/flywheel/<role>/
onlyne-server run --root .                            # 前台 tab 保可见

# 2. 每 role 起 client（各一 tab）
onlyne-client run --workspace .onlyne/ws/flywheel/scout   # model/bench/writer/critic 同理

# 3. root 开 pi 会话即 supervisor；第一发注入
onlyne --server-root . send --from _supervisor --to scout --file payload/first.md
onlyne tui
```

## 角色树

```text
.        supervisor（root）：队列记账、归档、闭合飞轮环路
├─ scout   检索+证据+idea 入池 → 唤醒 supervisor
├─ model   推导+Lean 形式化+实现 → 激发 bench / writer
├─ bench   跑评测落 measured/ → 唤醒 writer
├─ writer  成稿（带溯源数字）→ 激发 critic
└─ critic  对照证据审稿 → verdict.md → 唤醒 writer（revise）或 supervisor（accept/reject）
```

接力拓扑完整描述在根目录 `AGENTS.md` 的宏观流一节——每个 session 自动继承该文件。调度面与运维词汇见 `.agents/skills/onlyne-supervisor/SKILL.md`（supervisor）与 `onlyne-role/SKILL.md`（worker）。

## 协议样例

（v0 的 marquee 流水灯样例随 onlyne-swarm 退役；v1 的五节点环示例见 onlyne 仓 `examples/supervisor/`。）
## 动力源

seed 由人给（方向+问题）。之后每轮收尾，supervisor 从论文 open questions 或失败结论提取下一条 idea 入池。idea 无证据或无评测契约不进池。自激发无熔断，终结靠人：`onlyne control cancel --task <id>`（v1 按 task 血缘收敛）或 TUI 终结键。
