# theme_aris——全自动科研飞轮（复刻 ARIS）

## 这是什么

一群 AI 助手在同一个文件夹里分工，自动推进机器学习研究。流程：检索文献 → 提 idea → 跑实验推导 → 跨模型评审 → 写论文 → 审稿提意见，然后回到提 idea，循环往复。
你给它什么：一个研究方向和问题（叫 seed）。你得到什么：论文草稿、实验测量数据、下一条待研究的 idea 列表。
适合谁用：想让 AI 连续做研究、自己只在关键节点把关的人。

## 三分钟看懂工作原理

六个角色（role，分工固定的 AI 助手）接力，每个 role 有自己的工作文件夹（workspace）。一句话版：scout 检索并挑出 idea，交给 analyzer 提问、model 推导出实验方案，bench 跑实验拿到数据，writer 写成论文，critic 审稿给出意见回传改稿，实在过不了就回到 scout 开新一轮。

```text
.          _supervisor（管理员）：只做工作区维护与第一发，不进工作环
├─ scout    检索+证据+idea 入池+派工（★ 入口）→ analyzer
├─ analyzer 问题层分析 analysis.md（只提问，应对归 model）→ model / scout
├─ model    推导+Lean 形式化+出 spec（不写 experiment/ 代码）→ bench / writer / analyzer / scout
├─ bench    跑评测落 measured/ → writer / scout
├─ writer   成稿（带溯源数字）→ critic / scout
└─ critic   对照证据审稿 → verdict.md → writer（revise-文字）/ model（revise-理论）/ scout（accept/reject 开新轮）
```

为什么能转起来：每个 role 干完活把结果写成文件，再给下游发一条"该你了"的任务然后退出。发出去不等回复（射后不理），下一棒从文件恢复上下文继续干。整条环没有终点，靠人决定什么时候停。

## 第一次跑

前置：装 Rust 工具链和 pi，pi 已配好模型。装 onlyne 四件套和 pi 插件（role 的 agent 靠这个插件执行 onlyne 协议，没装 role 接到任务也不会动）：

```bash
cargo install --locked onlyne-cli onlyne-server onlyne-client onlyne-testkit
pi install npm:pi-onlyne@2.1.0
```

1. 生成六个 role 的工作区（`<role>` 依次代入 scout analyzer model bench writer critic；模板改过用 `--force` 重生成）。
   ```bash
   onlyne generate --root . --template aris/<role> --role <role> --force
   ```
2. 起 server。命令自己创建名为 onlyne-server 的独立 tab；保持它开着，关 tab 即停整个集群。
   ```bash
   orca terminal create --worktree path:$PWD --title onlyne-server --command "onlyne server run --root ."
   ```
3. 起 client 前必须先跑宿主判定检查（只读），确认本机 placement 正常。注意顺序：doctor 只探测不连集群，但六个 client 一旦起来就会按各自工作区的判定占宿主，先跑 doctor 再起 client 才能在起错宿主前发现；client 已在跑时再跑 doctor 不会纠正它们，所以要放在这一步，不要放到六发启动之后：
   ```bash
   onlyne client doctor
   ```
4. 为六个 role 各起一个 client，每个占自己的独立 tab（前台常驻；关某个 tab 即停该 role）。用循环一次起完：
   ```bash
   for r in scout analyzer model bench writer critic; do
     orca terminal create --worktree path:$PWD --title "client-$r" --command "onlyne client run --workspace .onlyne/ws/aris/$r"
   done
   ```
5. 起观测面板 TUI（看六个 role 谁在干什么）。
   ```bash
   orca terminal create --worktree path:$PWD --title onlyne-board --command "onlyne tui --server-root ."
   ```
6. 发第一发：把研究方向写进 `payload/first.md`，从入口 role scout 点火。
   ```bash
   onlyne --server-root . send --from _supervisor --to scout --file payload/first.md \
     --force --yes-i-am-supervisor-not-other-role
   ```
怎么确认成功了：`onlyne version` 报 `2.1.1`、`protocol:1` 算安装通过；第 3 步 doctor（必须在第 4 步起 client 之前跑）输出本机 placement 判定无异常；发完第一发后 TUI 里能看到 scout 在动、接力逐级传下去。想细节往下读，只想用，到此为止。

## 日常使用

- 看进度：`onlyne tui --server-root .` 开 TUI；或 `onlyne ledger --server-root .` 读账本，看每个任务状态和产物文件。
- 停一个任务：admin 面命令（gate 旗标必带），只取消该 task 及其下游接力，不动其他 role：
  ```bash
  onlyne --server-root . control cancel --task <id> --from _supervisor --reason "..." --force --yes-i-am-supervisor-not-other-role
  ```
- 停整个飞轮：飞轮自激发无熔断，终结靠人。关 server tab 停整个集群；关某个 client tab 只停该 role；或用会话接管。
- 换研究主题 / 加 idea：改 `payload/first.md` 重发第一发；idea 池在 `pool/ideas.md`。
- 出问题了：见下面的排障节。

## 术语表

| 词 | 大白话 |
|---|---|
| role / 角色 | 一个分工固定的 AI 助手（全文统一叫 role） |
| workspace | 该 role 的工作文件夹，存记忆+设定+历史文件 |
| session / 任务 | 手头一件工作；一次 session = 一跳 = 一个任务 |
| seed | 人给的研究方向和问题 |
| 射后不理 | 发出任务后不等回复，结果经文件与账本呈现 |
| 账本（ledger） | 记录所有任务与结果的流水账 |
| handoff | 一个 role 干完活后激发下游 role 的动作 |
| placement | 会话宿主，即 client 跑在哪种终端环境里 |
| TUI | 终端里的观测面板，看角色状态 |

## 工作原理细节

### 本飞轮如何映射 ARIS 的技能

本工作区用 `onlyne` 2.1.1 六角色飞轮复刻 [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) 的全自动科研工作流。ARIS 是一套 Markdown-only skills 的自主 ML 研究系统，流程：文献→idea 发现→实验→跨模型评审循环→论文写作→同行评审 rebuttal。技能映射：

- `/idea-discovery` → scout（检索与入池）+ analyzer（novelty-check 深化位：问题层分析）
- `/experiment-bridge` → model（plan→spec）+ bench（deploy→collect）
- `/auto-review-loop`（4 轮评审、cross-model jury）→ critic 的 verdict 修订环
- `/research-pipeline` 全链 → 飞轮宏观流本身
- `/research-wiki` 持久记忆 → 文件台账（`runs/`、`pool/ideas.md`、ledger）

上游技能清单以公开仓库 `skills/` 目录为准（research-pipeline / idea-discovery / auto-review-loop / paper-writing 等）。

### 一个 session 的动作序列与接力闭环的四条回路

一个 session 的动作序列：恢复上下文 → 工作 → `onlyne_handoff` 激发下游（可选，若干）→ 落文件 → `onlyne_complete` 退出。session 对下游零等待，结果经文件与账本呈现，接力任务唤醒下一个单位。接力闭环分四组：
- 主环：scout→analyzer→model→bench→writer→critic→scout。
- 修订环：critic→writer（revise-文字）、critic→model（revise-理论）。
- 补析环：model→analyzer（回请）→model，两轮封顶。
- 回传边：analyzer→scout、model→scout、bench→scout、writer→scout。

### allowed_targets 如何同时承担 ACL 与完成守卫

`allowed_targets` 一个列表同时承担 ACL 与完成守卫。role 报终态前必须已向列表里每个下游投递；欠投的 `onlyne_complete` 被拒并点名欠谁。拓扑唯一事实源 = 根 `AGENTS.md` 角色表与 `.onlyne/spec.toml`，每个 session 自动读到根 `AGENTS.md`。

### 研究动力从哪里来：seed 与 idea 的四条准入门

seed 由人给，含方向与问题。每轮收尾时 critic 从论文 open questions 或失败结论提取下一条 idea。idea 入池前过四条硬门：evidence、objectives、done_when、headroom 预筛（判据见根 AGENTS.md），任一条不过不进池。自激发无熔断，终结靠人（见日常使用节）。

### 拓扑配置、placement 与运行时重建

集群真相在两处：`.onlyne/spec.toml`（拓扑/ACL/runtime/timeout）与 `.onlyne/templates/aris/<role>/`（细则+thinking 档）。模板改后用 `onlyne generate --root . --template aris/<role> --role <role> --force` 重建运行时。placement（会话宿主）值域 `orca|zellij|tern|headless|external`，写在各 role 工作区 `.onlyne/config.toml` 的 `placement` 键；配置缺失时按序探测 tern→orca→zellij→headless，非空 `ONLYNE_BACKEND` 优先，`onlyne client doctor` 只读打印本机判定。

### 其他安装方式：源码构建、pi 插件与升级

- 源码构建备用路（默认分支 main，未发布的 fix 在这儿）：
  ```bash
  git clone https://github.com/dbydd/onlyne && cd onlyne && cargo build --release
  ```
  把 `target/release/onlyne` 放进 PATH。升级 onlyne＝安装命令加 `--force` 重跑。
- pi 插件：`pi install npm:pi-onlyne@2.1.0`（第一次跑已装），版本号钉住，v2 协议面对旧版插件不兼容。找代码认仓库 `plugins/onlyne-agent-pi`，装包认 `pi-onlyne`。
- 模型配置：pi 的 provider/model 由操作者自己的 pi 配置给默认。本树模板 `.pi/settings.json` 只钉 per-role thinking 档，部署时按算力预算自定。

### 运行纪律、账本与残留进程清理

server 与 TUI 跑在本 worktree 的可见前台 tab，关 tab 即停环，两者不进任何 agent 后台。client 只有 `onlyne client run`（前台常驻），必须从本 worktree 的 tab 起。账本用 `onlyne ledger --server-root .` 读；账本结算杀不到 setsid 出去的 detached 子树，收口 bench 类任务时补一步进程树扫荡。

## 排障

| 症状 | 处置 |
|---|---|
| `onlyne version` 不报 `2.1.1` / `protocol:1` | 重新执行安装命令；升级用同条命令加 `--force` |
| client 起不来或宿主判定不对 | 跑 `onlyne client doctor` 看本机 placement 探测；必要时写 `.onlyne/config.toml` 的 `placement` 键或设 `ONLYNE_BACKEND` |
| 模板改了但行为没变 | `onlyne generate` 加 `--force` 重建 |
| bench 任务结束后仍有残留进程 | 账本结算杀不到 setsid 的 detached 子树，补一步进程树扫荡 |
| `onlyne_complete` 被拒 | 完成守卫点名欠投的下游，先向该 role 补投递 |
| 飞轮停不下来 | 自激发无熔断；用 `control cancel` 停单个任务（见日常使用），关 server tab 停整个集群 |

## 目录结构

```text
AGENTS.md                        根角色表，拓扑事实源之一
.onlyne/spec.toml                拓扑/ACL/runtime/timeout 事实源
.onlyne/templates/aris/<role>/   每角色细则+thinking 档模板
.onlyne/ws/aris/<role>/          各 role 工作区（含 .onlyne/config.toml）
.onlyne/config.toml              placement 配置键所在
payload/first.md                 第一发 seed
runs/                            实验运行台账
pool/ideas.md                    idea 池
analysis.md / verdict.md         analyzer / critic 产物
.pi/settings.json                per-role thinking 档
```
