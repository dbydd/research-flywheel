# formal-research：一套自动跑科研流程的多 agent 工作区

这个仓库是一套让多个 AI agent 分工协作、自动推进正式科研全流程的工作环境：从选定研究题目、审查提案、提出假设、做实验、核对结果，到最终验收归档。产出的东西全部是文件：研究项目档案、实验实测数据、审查判词、论文草稿。

两个底座工具：

- **onlyne**：多 agent 集群协调框架。负责把任务在角色之间传递、记账、监督会话生死（命令：`onlyne send / handoff / ledger / status`）。
- **pi**：编码 agent 会话程序，接已配置的大模型。每个角色的实际工作（读文件、写文档、跑实验代码）都在一个 pi 会话里完成。

## 这套系统长什么样

新人第一步不用碰命令行。clone 下来后，对你的 agent 会话（pi / omp / claude 皆可）说一句「**帮我看看这棵树**」——仓根的薄引导会把会话带到本文的[「装配与通电」节](#装配与通电)：先问四件本机事实（终端宿主、端口、模型档位、有无 vault），再跑 `scripts/bootstrap.sh --assemble` 代装，最后 `--promote` 让公共约定上位、薄引导就地消失。手工装机照抄同一节。

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
AGENTS.md                 clone 态＝薄引导（指向本文「装配与通电」节）；--promote 后＝全套契约：角色表、边义、关口规程、纪律
.agents/AGENTS.md         契约正本（11 角色公共约定），提升动作的复制源
.pi/SYSTEM.md             supervisor 值班会话的岗位说明（装配引导、通电、账目、残影恢复）
scripts/bootstrap.sh      装配器：--check 门禁 / --assemble 幂等装配 / --promote 契约上位
research_project/         研究项目文件（一项目一 .md）+ 每项目过程件目录（提案/送审包/判词/推导/实测数据）
research/                 文献检索台账（frontier-notes.md，URL+单行结论，追加式）
experiment/ evaluation/   领域代码与评测器（评测命令写进断言清单，qa 照命令重跑对账）
papers/                   论文成稿目录（随 scribe 启用）
payload/                  注入集群的第一发任务书
.onlyne/                  集群配置：spec.toml（角色与边的机器可读定义）+ templates/formal/（11 份角色说明书）
.agents/skills/           十件领域技能（绘图/写作/检索/统计等作业规范）
```

## 前置

- onlyne v1 五件套，装 latest（命令里没有版本号，随时发版随时追）：`cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui`——crate `onlyne-cli` 装出的命令叫 `onlyne`，其余四个 crate 名=命令名。升级＝同一条命令加 `--force` 重跑。兼容判据：`onlyne version` 报 `protocol:1`；各二进制版本号独立前进。要跟未发布的 fix 就走源码构建（仓库地址问集群 owner，`cargo build --release` 后产物进 PATH；macOS 上复制进 PATH 的二进制要先 `codesign --force --sign -` 重签，Linux 免）。
- pi + onlyne 插件：模板 packages 写 `npm:pi-onlyne`。第一次装配执行 `pi install npm:pi-onlyne`（1.0.0 起讲 protocol 1，relay 守卫在内），装当期 latest。
- 会话后端 `herdr`/`orca`/`zellij` 之一：选择链 `ONLYNE_BACKEND`（非空）> 工作区 `config.toml` 的 `backend` > auto。auto 探测序 herdr→orca→zellij。`exec`/`fake` 只认点名。全无匹配时 `onlyne client run` 退 5。`onlyne-client doctor` 打印宿主判定。
- pi 侧 model/provider 配好（本主题三档模型设计见 `.agents/AGENTS.md` 角色表末列；装配后同一份内容在仓根 `AGENTS.md`）。
- 运行纪律：server 和每个角色的 client 各占一个**可见前台终端 tab**（关 tab 即停该角色），不进任何 agent 后台。

## 装配与通电

`theme/formal-research` 是模板发布分支：拓扑（11 角色）、角色细则、领域技能、评测契约都已定稿。装配不改设计，只补三件本机事实——服务器证书指纹、11 个角色密钥、模型路由与可选 vault 路径。装配脚本零守护进程，跑完环还是停的。

### 装机前四条确认

agent 会话接手本树时向用户一次问全，手工装机同样先定这四件：

1. **终端宿主**：herdr / orca / zellij 之一——server 与 11 个 client 之后各占一个用户可见的前台 tab。
2. **端口**：spec 现值 `127.0.0.1:7820`；一台机器并跑多棵树就换号（`--listen`）。
3. **模型供应商与档位路由**：powerful 档（pi/examiner/theorist/speculator/chair/referee/planner）与 supercheap 档（librarian/runner/qa/scribe）的实际 model id；沿用模板现值就不给 flag。
4. **Obsidian vault 与功耗边界**：给 vault 根路径就接四软链，没有就跳过，约定里的 vault 节在这台机器上整段失效；算力口径默认「训练单进程、串行、单片 ≤45 min」，要改在约定正本「功耗与训练槽纪律」节改。

### 装配

```bash
scripts/bootstrap.sh --check                      # 只读门禁，零写入；报这台机器缺哪几件
scripts/bootstrap.sh --assemble --dry-run         # 先看要做啥
scripts/bootstrap.sh --assemble \
  --provider <名> --model-powerful <id> --model-supercheap <id> \
  --vault <vault 根路径> --listen 127.0.0.1:7821
```

`--assemble` 六步全幂等，已达状态打 `SKIP`：

| 步 | 动作 | 幂等判据 |
|---|---|---|
| 1 | 证书：暂移 `spec.toml` → `onlyne-server init --root . --listen <addr>` → 还原跟踪版并把打印的 `cert_pin` 写回 `[server]` | `cert_pin` 非占位且 `.onlyne/keys/server.key` 在盘 |
| 2 | 密钥：逐 role `onlyne-client init --workspace .onlyne/ws/formal/<phase>/<role> --role <role>`，把打印行的 `key` 回填进对应 `[[client]]` | spec 里 11 个 key 非占位 |
| 3 | 模型档位：按 flag 重写 11 份模板 `.pi/settings.json` 的 `defaultProvider`/`defaultModel`，effort 档不动，`packages` 钉回 `["npm:pi-onlyne"]` | flag 全缺省即整步 SKIP |
| 4 | 渲染：逐 role `onlyne server generate --root . --template formal/<phase>/<role> --role <role> --force` | 以 spec/keys 为准，可反复跑 |
| 5 | vault：`obsidian/{论文,reports,draft,templates}` 四软链（`obsidian/` 已 gitignore） | `--vault` 给了才做 |
| 6 | 门禁：自动接跑 `--check` | — |

第 1 步为什么要暂移：`onlyne-server init` 见 `spec.toml` 存在即拒（无 `--force` 时 refuse）。**别给 init 加 `--force`**——那会用它自带的极简模板覆盖整份 spec，11 行拓扑与 ACL 全丢。脚本因此在暂移前留 `spec.toml.pre-bootstrap` 改前备份，中途异常还原后退出。

`--check` 十二项覆盖：五件套与 protocol 闸、pi 插件在册、spec 可 parse 且 11 role 与模板目录双向一致、relay 边双向闭合、`_supervisor` 零上行边、cert_pin 与 server.key 同机、11 key 非占位、11 工作区在盘且 packages 为 `npm:pi-onlyne`、终端宿主可探测、listen 端口空闲、文档卫生（跟踪件零本机绝对路径、零装机者标识、零已废栈字样）、vault 软链一致性。未装配的模板树跑 `--check` 会红三项（证书/密钥/工作区），属正常提示。

### 契约上位

```bash
scripts/bootstrap.sh --promote     # cp .agents/AGENTS.md → 仓根 AGENTS.md
```

仓根 `AGENTS.md` 在 clone 态是一份薄引导（只讲去哪读、怎么装）。`--promote` 用 11 角色公共约定正本原样覆盖它，此后 pi 沿父目录链拼进树内每个 role 会话的正是那份约定，薄引导就地消失。判据：仓根 `AGENTS.md` 首行是「formal-research 大循环 — onlyne v1 公共约定」。已上位时再跑 `--promote` 报 `SKIP`，零写入。装配手册就是本文这一节。

### 通电

daemon 起在用户可见的前台终端 tab，关 tab 即停环；禁入任何 agent 后台，禁 nohup。起 client 的宿主目录决定会话 spawn 定向，起错检出=会话一起就死。

```bash
onlyne server start --root .                                   # 一个 tab；判活 socket_present
onlyne client run --workspace .onlyne/ws/formal/initiation/pi  # 11 个 role 各一个 tab
# phase/role 全集：initiation/{pi,examiner}、common/{librarian,scribe}、theory/{speculator,theorist}、
#                 experiment/runner、review/{qa,referee,chair}、archive/planner
onlyne tui --server-root .                                     # 可选观测位
onlyne status --server-root .                                  # connected 11/11 = 环点亮
```

### 第一发与验收

研究方向写进 `payload/first.md`（目标 / 输入 / 期望产物三段，见约定正本「任务书三段」），投给角色表 ★ entry role（pi）：

```bash
onlyne send --server-root . --from planner --to pi --file payload/first.md
```

`--from` 须是在册持边角色（supervisor 不注册 `[[client]]`，走 admin 面代发，落账 `admin=true`）。用户自己在 CLI 投也行，supervisor 事后从 ledger 与项目目录接上下文。第一发落地后环自转：pi 出头四段申报 examiner，后续推进全靠接力任务。

通电后先跑最小闭环用例：向 pi 投一条自包含小任务（内容如「读 AGENTS.md 后回一句本环入口确认」）→ session 起 → pi 内 `onlyne_complete` outcome=done → `onlyne ledger --server-root .` 出现 task acked 与 completion 回 origin 两行 → `onlyne faults --open-only` 空。绿了再投研究方向的第一发。

### 换机速查

要动的本机项三件：`cert_pin`、11 个 `[[client]].key`、各 settings.json 的模型三元组；vault 路径可选。全部由 `--assemble` 幂等代做，其余文件跨机通用。`.onlyne/run|store|keys|logs|ws/`、`obsidian/`、`.train-slot/` 是运行态，不入 git，装机过程自然再生。装机产生的 `spec.toml` 与仓根 `AGENTS.md` 改动属本机实例状态：往模板分支提交前先问用户，缺省不入库。

### 常见坑

- 装具报 command not found 或行为像旧版：核 `which onlyne` 与 PATH 序（cargo install 与手拷二进制并存时先入 PATH 者生效），`onlyne version` 不过闸就重跑「前置」那五条。
- 非法 key 会让 spec 全量 parse 连 `client init` 都跑不动：回填前 key 位必须保持合法 32 字节 base64（模板占位 `ed25519/AQEB…` 即合法），改成 `REPLACE_ME` 之类字面串会全链拒跑。
- `onlyne client run` 退 5 报 NO_SUPPORTED_HOST：终端宿主缺失或 `ONLYNE_BACKEND` 点错，跑 `onlyne-client doctor` 看判定。
- 深路径工作区 socket 绑不上：看 `.onlyne/run/socket` 里的短派生路径，属正常行为。
- client 重挂后有 working 残影（faults 只覆盖投递层）：逐条 `onlyne repair inspect --task <id>`，死 pane 的用 `onlyne repair close --task <id>` 收口（close 记 cancelled、fail 记 failed，两者都向属主 client 发 Cancel 并回收宿主资源）。
- 停某个 client：`onlyne-client` 不写 pid 文件，用 `ps` 按 args+cwd 精确匹配再定点发信号，禁按名杀。

终结靠人：`onlyne control cancel --task <id> --server-root .`，或直接接管任一会话。日常用法词表（send/handoff/complete/ledger/faults/repair/control）与值班恢复纪律见 `.pi/SYSTEM.md`。

## 观测

`onlyne status|roles|sessions|ledger|faults|watch --server-root .`；pi 会话内 `/onlyne`；观测台 `onlyne tui --server-root .` 再起一个 tab。
