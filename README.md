# Research Flywheel v3

这是一个基于 onlyne v1 的自动科研飞轮模板。工具链与 pi 插件都跟各渠道的最新版走。它把一个研究主题拆给五个 role。每个 role 拿到一跳任务，产物写回磁盘，再把下一跳任务交给下游。

**新人第一步：读 [`BOOTSTRAP.md`](BOOTSTRAP.md) 的「开场协议」节。** 把树 clone 下来后直接对你的 agent 会话说一句「帮我看看这棵树」即可——会话会主动介绍这套飞轮、核装 onlyne 依赖、问清你的研究主题与部署方式，然后代你完成装配。手工装配也走同一份文档。

workspace 表示一个 role 的长期工作区，里面有记忆、设定、历史文件。session 表示这个 role 当前手上的一件工作。任务、session、一跳是一回事。

飞轮按“射后不理”工作：恢复上下文 → 工作 → `handoff` 激发下游（可选）→ 写文件 → `onlyne_complete` 交活退出。role 不等下游回执。投递后立即返回一行 receipt JSON。过程与回执都写进 server ledger。结果通过文件返回。下一条接力任务会唤醒下一个 role。环路长期打开，由 supervisor 或人来停下。

## 前置

- onlyne v1 最新版（不钉版本号，新 fix 全部随 latest 发）。发布渠道一行装齐：`cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui`（crate `onlyne-cli` 装出的 bin 叫 `onlyne`，其余同名）。已装过要升级，同一条命令加 `--force` 重跑。兼容判据是 `onlyne version` 的 `protocol:1`。
- `pi`，插件走 `pi install npm:pi-onlyne`（拉 npm latest，relay 守卫在内）。role 会话由 client 启动，generate 把插件 vendor 到各 ws，ws 内副本零 npm 依赖。
- 源码构建作备用：`git clone https://github.com/dbydd/onlyne`（默认分支 main，未发布的 fix 在这儿）+ `cargo build --release`，五产物放 PATH。macOS 上 cp 完必做 `codesign --force --sign -`——复制后的二进制签名失效，直接 exec 收 SIGKILL。
- 会话后端需要 `herdr`、`orca` 或 `zellij`。`ONLYNE_BACKEND` 留空或 `auto` 时探测序是 herdr→orca→zellij，探不到退 fake；`onlyne-client doctor` 打印本机判定。
- pi model/provider 已经配好。

## 起飞

```bash
# 0. clone 后照 BOOTSTRAP.md 装配主题（THEME 槽、角色拓扑、种子 idea）；装具一律追 latest
onlyne version        # protocol 读 1 即兼容；号落后就按「前置」两条命令重跑（cargo install --force / pi install npm:pi-onlyne）
./scripts/promote.sh --dry-run && ./scripts/promote.sh

# 1. 通电（一次性；人执行，supervisor 会话不起常驻）
onlyne-server init --root . --listen 127.0.0.1:7812   # 产 keys/cert_pin，回填 spec.toml（key 先播合法占位再逐 role client init 换真身）   # 多树并机查重：7813=ARIS live，第二集群自选 7814+
onlyne-server generate --root .                       # 渲染 .onlyne/ws/flywheel/<role>/
onlyne-server start --root .                            # detached+pid；判活看 socket_present

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

根目录 `AGENTS.md` 写了完整接力拓扑。每个 session 都会自动继承它。调度与运维词汇见 `.agents/skills/onlyne-supervisor/SKILL.md`。worker 纪律见 `.agents/skills/onlyne-role/SKILL.md`。

## 协议样例

v0 的 marquee 流水灯样例已经随 onlyne-swarm 退役。v1 的五节点环示例在 onlyne 仓 `examples/supervisor/`。

## 动力源

第一颗 seed 由人给，内容是方向和问题。之后每轮结束，supervisor 从论文 open questions 或失败结论提取下一条 idea 入池。idea 需要证据和评测契约。缺任一项就不入池。自激发没有熔断。人用 `onlyne control cancel --task <id>` 终结任务族；v1 会按 task 血缘收敛。也可以在 TUI 里按终结键。
