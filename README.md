# formal-research：一套自动跑科研流程的多 agent 工作区

这个仓库是一套让多个 AI agent 分工协作、自动推进正式科研全流程的工作环境：从选定研究题目、审查提案、提出假设、做实验、核对结果，到最终验收归档。产出的东西全部是文件：研究项目档案、实验实测数据、审查判词、论文草稿。

两个底座工具：

- **onlyne**：多 agent 集群协调框架。负责把任务在角色之间传递、记账、监督会话生死（命令：`onlyne send / handoff / ledger / status`）。
- **pi**：本机运行的编码 agent 会话程序，接已配置的大模型。每个角色的实际工作（读文件、写文档、跑实验代码）都在一个 pi 会话里完成。

## 这套系统长什么样

新人第一步不用碰命令行。clone 下来后，对你的 agent 会话（pi / omp / claude 皆可）说一句「**帮我看看这棵树**」——会话会主动介绍这套飞轮、核装具版本、问清你的研究主题与部署方式，然后按 [`BOOTSTRAP.md`](BOOTSTRAP.md) 代你完成装配并投第一发。手工装配走同一份文档，逐条照抄。

11 个角色，每个角色 = 一份职责说明书 + 一个工作区 + 若干 pi 会话。角色之间按固定的边互相派任务，任务像飞轮一样转起来：

```text
planner → pi → examiner → theorist → speculator → runner → qa → chair → planner（主环，九段接力）
```

| 角色 | 干什么 |
|---|---|
| planner（立项策划） | 翻全局档案选研究方向，把题目连同证据、经费、待查文献打包交给 pi；项目终结时归档 |
| pi（开题负责人） | 为一个题目写四段开题材料：问题背景、前沿进展、研究目的、最终怎么算验证成功 |
| examiner（敌意评审官） | 职责是让这个提案死掉：从四个角度攻击（前提塌了/已被别人做过/根本测不了/自相矛盾），攻不破才放行 |
| theorist（形式化） | 把自然语言命题写成可检验的推导链（可用 Lean 证明助手编译核对） |
| speculator（假设与设计） | 提出假设、写实验设计、列断言清单（每个要测的数字一条：指标/评测器/方向/阈值/基线） |
| runner（跑批） | 按设计段跑实验，原始数据与汇总值落盘；一次只跑一个训练进程（省电纪律） |
| qa（质量审查） | 环上常驻：每条断言拿实测数字当场判 pass/fail；查数据泄漏/种子固定/预算三项约束；随时出中期判词；全部达标时放门（宣布可以进入验收） |
| chair（结题主编） | 像期刊主编：核验证据在盘、约三位审稿人、汇总意见合议裁决、对错最终算自己的 |
| referee（审稿人 ×3） | 独立出意见书，提交前互不通气；只认能重跑对上的数字 |
| librarian（文献官） | 公共检索资源：任何角色委托，交回可回查的文献台账行 |
| scribe（执笔） | 公共代笔位，暂未启用；文稿由各责任角色自己写 |

## 三个关口

流程里有三道强制审查，判词（审查结论文件）都落盘：

1. **开题审查**：examiner 与 pi 逐轮对线，记录追加进 `对线记录.md`。弹药（攻击点）耗尽判 `pass`；出现化解不了的实心攻击判 `fail`，提案废弃归案。轮数无上限，只看证据。
2. **中期检查**：qa 在理论⇄实验循环期间随时出判词：`continue`（继续）、`rectify`（开整改单直接命令相关角色）、`stop`（实锤停摆）。设计目标全部有实测支撑且三项约束通过时，追加放门判词。
3. **结题验收**：qa 把证据汇编成六节送审包；chair 先程序核验（抽一条断言当场重跑），再向三位 referee 独立约稿（约稿信零倾向）；chair 非补偿合议（任何一票硬伤不能靠其他票抵消）判 `accept` / `minor revise` / `reject`。

## 工作模型

- **射后不理**：一个会话发完接力任务就退出，不等下游。下游成果经文件与台账出现，新任务唤醒下一个会话。
- **一切落文件**：全部真相 = 文件 + git + onlyne 台账（`onlyne ledger --server-root .` 可查每个任务的来龙去脉）。没有状态数据库，没有轮次计数。
- **默认全自动**：三道关口自动通过；项目文件头 `human_gate:` 点名的关口暂停请示人。
- **纠错靠环上的边**：对线、整改单、revise 打回是内置修复机制；单个失败不新增兜底条款。

## 目录

```text
AGENTS.md                 全套契约：角色表、边义、关口规程、纪律（每个会话自动读到）
设计议程.md               当前讨论事项清单（定案搬进契约后划账）
research_project/         研究项目文件（一项目一 .md）+ 每项目过程件目录（提案/送审包/判词/推导/实测数据）
research/                 文献检索台账（frontier-notes.md，URL+单行结论，追加式）
experiment/ evaluation/   领域代码与评测器（评测命令写进断言清单，qa 照命令重跑对账）
papers/                   论文成稿目录（随 scribe 启用）
payload/                  注入集群的第一发任务书
.onlyne/                  集群配置：spec.toml（角色与边的机器可读定义）+ templates/formal/（11 份角色说明书）
.agents/skills/           十件领域技能（绘图/写作/检索/统计等作业规范）
```

## 前置

- onlyne v1 五件套，装 latest（命令里没有版本号，随时发版随时追）：`cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui`——crate `onlyne-cli` 装出的命令叫 `onlyne`，其余四个 crate 名=命令名。升级＝同一条命令加 `--force` 重跑。兼容判据：`onlyne version` 报 `protocol:1`；各二进制版本号独立前进。要跟未发布的 fix：源码构建 `git clone https://github.com/dbydd/onlyne && cargo build --release`，产物进 PATH；macOS 上 cp 进 PATH 的二进制要先 `codesign --force --sign -` 重签，否则 exec 收 SIGKILL。
- pi + onlyne 插件：`pi install npm:pi-onlyne`（1.0.0 起讲 protocol 1，relay 守卫在内）；generate 会把插件 vendor 进各角色工作区，ws 内副本零 npm 依赖。
- 会话后端 `herdr`/`orca`/`zellij` 之一：`ONLYNE_BACKEND` 留空按 herdr→orca→zellij 探测，`onlyne-client doctor` 只读打印本机判定，探不到时 `onlyne-client run` 退 5。
- pi 侧 model/provider 配好（本主题三档模型设计见 `AGENTS.md` 角色表末列）。
- 运行纪律：server 和每个角色的 client 各占一个**可见前台终端 tab**（关 tab 即停该角色），不进任何 agent 后台。

## 起飞

手工路径（agent 代装配走同一套）：

```bash
# 0. 装具门禁：protocol 读 1 即兼容，号落后按「前置」命令重跑
onlyne version

# 1. 证书与密钥：server init 产 cert_pin 回填 spec [server]；逐 role client init 的 key 回填对应 [[client]]
#    （端口查重 lsof -i :7820；回填前占位值必须保持合法 base64，REPLACE_ME 全链拒跑。11 role 循环命令见 BOOTSTRAP 步骤 4）
onlyne-server init --root . --listen 127.0.0.1:7820

# 2. 用模板渲染 11 个角色工作区（模板改动后 --force 重渲；换机先改 11 份 settings.json 的插件绝对路径，见 BOOTSTRAP 步骤 3）
for p in initiation/pi initiation/examiner common/librarian common/scribe \
         theory/speculator theory/theorist experiment/runner \
         review/qa review/referee review/chair archive/planner; do
  onlyne-server generate --root . --template formal/$p --role $(basename $p) --force
done

# 3. 通电：server 与 11 个 client 各占一个可见 tab（以 orca 为例）
orca terminal create --worktree path:$PWD --title onlyne-server --command "onlyne-server run --root ."
for p in initiation/pi initiation/examiner common/librarian common/scribe \
         theory/speculator theory/theorist experiment/runner \
         review/qa review/referee review/chair archive/planner; do
  orca terminal create --worktree path:$PWD --title "onlyne-client-$(basename $p)" \
    --command "onlyne-client run --workspace .onlyne/ws/formal/$p"
done
onlyne status --server-root .   # connected 11/11 即环点亮；观测可加 onlyne-tui 一个 tab

# 4. 第一发：研究方向写进 payload/first.md，注入 ★ entry role pi，环开始自转
onlyne send --server-root . --from planner --to pi --file payload/first.md
```

终结靠人：`onlyne control cancel --task <id> --server-root .`，或直接接管任一会话。日常用法词表（send/handoff/complete/ledger/faults/repair/control）见 `AGENTS.md`「onlyne v1 工具面」节。

## 观测

`onlyne status|roles|sessions|ledger|faults|watch --server-root .`；pi 会话内 `/onlyne`。崩溃残影处置按 `AGENTS.md`「恢复运行纪律」节（`onlyne repair inspect|close|fail`）。
