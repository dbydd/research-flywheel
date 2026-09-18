# BOOTSTRAP —— 模板到主题的装配流程

读者：拿到本模板 clone 的人，或者替他干活的 supervisor 会话。

装配这项工作的定义：把通用骨架填成一个具体研究主题的飞轮，产出一条 `theme/<slug>` 分支，以及一套可通电的 onlyne v1 拓扑。装配期间不启动集群，不跑实验。红线是 `.agents/AGENTS.md` 与 `.onlyne/spec.toml` 的结构保持完整。

## 开场协议（会话读到本文件或被 clone 树唤起时，第一件事）

任何接手本模板的 agent 会话，动手前先主动向用户自我介绍并问清部署意图，一次问全，得到回答之后开工：

> 这是一棵 Research Flywheel 模板树：默认五角色（scout 侦察 → model 推导 → bench 测量 → writer 成稿 → critic 审稿）的自转科研环，任务经 onlyne 集群投递，知识全落文件。我能替你装配成你主题的实例，角色与拓扑都可以改。四个问题：
> 1. **主题是什么**？一句话研究问题 + 手头材料（论文/数据/代码/想法笔记，给路径）。没有明确主题也行——先跑一轮文献侦察把它问出来。
> 2. **角色环要自定义吗**？默认五角色适合「理论+实验+成稿」全链；也可增删（如加独立 figure 角色、去掉 writer 只做实证、双 bench 分训评），改角色表+模板目录+spec 三处同步即可，我按你的说法生成。
> 3. **装在哪、跑给谁**？单机一把梭最省事；也支持多机部署——server 挂在一台协调机上，各 role 的 client 分挂不同机器（TLS 证书钉扎走网络，`[server].listen` 配非回环地址即可），训练重活的 bench 单独占 GPU 机器是常见形态。只装不跑也可以。
> 4. **算力边界**？功耗/时段/预算约束说一声，决定 bench 时间片与训练槽条款怎么写。

用户只想浏览时，给出三句话全景（模板=骨架 / theme 分支=实例 / 通电=跑环），停在 §0 全景图，不推进任何文件改动。

依赖安装归 §2：supervisor 第一次接手就亲手跑 `pi install npm:pi-onlyne` 与五个 crate 的 latest。§5 九检全绿即装配完成，中途任何一检失败按 §8 常见坑对表自修，修不动再向用户报告卡点。

## 0. 全景

```mermaid
flowchart TD
  A[clone 模板] --> B[A 定题：THEME 槽×5]
  B --> C[B 拓扑：spec.toml [[client]] 增删 + ACL 边]
  C --> D[C 起草：角色文案/模型三元组/任务书口径]
  D --> E[D 种子：pool/ideas.md ≥1 条硬门字段]
  E --> F[装工具链：onlyne latest + pi install npm:pi-onlyne]
  F --> G[promote.sh --dry-run 九检]
  G --> H[人确认 → promote.sh 落分支]
  H --> I[通电：server init/generate/start + clients]
  I --> J[第一发：send --from _supervisor --to entry]
```

## 1. 上下文面（v1 谁读什么）

- `.agents/AGENTS.md` → promote 时复制为 root `AGENTS.md`。pi 沿父目录链把它拼进树内**每个**会话（role ws 在 root 之下）。它是全局约定的唯一载体。
- `.onlyne/spec.toml` → 拓扑唯一真相。`prose` 字段是 role 身份提示词：welcome 时下发，client 缓存进 `client.db`，pi 插件注入会话。改 prose 后 `onlyne server reload` 生效，旧 receipt 会话拿新 welcome。
- `.onlyne/templates/flywheel/<role>/AGENTS.md` → 该 role 的深规（工作顺序、产物纪律）。generate 渲进 ws 后，经 pi 链进该 role 每个会话。
- `.onlyne/templates/flywheel/<role>/.pi/settings.json` → 模型三元组（provider/model/thinkingLevel）加上 `packages: ["npm:pi-onlyne"]`。`[server].agent_package` 保持空串时，generate 原样留下这条 npm 路径。
- root `.pi/SYSTEM.md` → supervisor 会话的注入指引（admin 面、空转判定、职责边界）。

## 2. 工具链安装（发布渠道为主，源码构建备用；版本策略＝始终追 latest）

onlyne 发版频繁，1.0.0 之后每个小版本装的都是 bug fix 与增量能力。全文所有装具命令都取渠道当时的 latest，没有任何版本号需要装机者改。各 crate 版本号独立前进（server 常领先 cli 若干补丁），别拿一个二进制的号推断另一个。

**自展开第一次（supervisor 亲手跑，装渠道 latest）：**

```bash
command -v onlyne && onlyne version          # protocol=1 即兼容
command -v pi
pi list                                      # 找 npm:pi-onlyne
# 缺哪条装哪条；第一次手动跑，之后升级同命令：
cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui
pi install npm:pi-onlyne                     # npm latest：relay 守卫、activity panel、delivery-keyed 注入、短路径 socket
onlyne version                               # {"onlyne-cli":"<latest>","protocol":1,...}
cargo install --force onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui   # 升级＝同一条命令重跑
```

crate `onlyne-cli` 装出的 bin 叫 `onlyne`，其余同名。兼容判据是 `protocol=1`，不匹配握手报 `protocol_version`，fail-fast。

五份 role 模板 `.pi/settings.json` 已经写着 `npm:pi-onlyne`。supervisor 这一次 `pi install` 把 latest 装进用户级包目录；role 会话按 settings 里的 npm 路径加载。`[server].agent_package` 保持空串，generate 不 vendor、不改写 settings。

复现某个旧版本故障时用 `npm:pi-onlyne@<version>` 钉住。日常安装与升级走 latest。

名字陷阱：crates.io 上的 `onlyne` 0.5.x 与 `onlyne-swarm` 0.6.x 是旧形态占名；v1 的五个 crate 叫 `onlyne-cli`/`onlyne-server`/`onlyne-client`/`onlyne-gateway`/`onlyne-tui`。npm 上的 `pi-onlyne` ≤0.9.1 讲旧协议，≥1.0.0 讲 protocol 1，latest 即最新修复。

备用路走源码构建（要跟 main 上尚未发布的 fix，或 crates.io 限流补发期间用）：

```bash
git clone https://github.com/dbydd/onlyne && cd onlyne   # 默认分支 main，fix 落在这儿；不钉 tag
cargo build --release   # 全新 clone 实测 ~60s
cp target/release/{onlyne,onlyne-server,onlyne-client,onlyne-gateway,onlyne-tui} ~/.cargo/bin/
codesign --force --sign - ~/.cargo/bin/onlyne*   # macOS 必做：复制后的二进制签名失效，直接 exec 收 SIGKILL
```

后续更新：同目录 `git pull && cargo build --release`，重跑上面两条（cp + codesign）。源码跟插件未发布 fix 时，把 `[server].agent_package` 填成 checkout 里 `plugins/onlyne-agent-pi` 的绝对路径，generate 会 vendor 进每个 ws。发布模板默认走 npm 路径，这条留给跟仓调试。

动词面（照发布版 `--help` 核过，抄进脚本前用 `--help` 复核当期形态）：瘦入口 `onlyne --server-root <root>` 持有 `send|reply|complete|handoff|ack|reject|control|who|ping|status|roles|sessions|ledger|faults|watch|history|spec_diff|reload|generate|wait-ready|repair|cluster|tui|version`。`onlyne server` 分组持有 `init|run|start|stop|status|generate|reload|roles|sessions|ledger|faults|watch|history|repair`。`onlyne client` 把余下参数转给 `onlyne-client`（`run|init|status|roles|sessions|history|watch|agent|doctor`，ws 面一律 `--workspace <ws>`）。client 侧没有 `start`/`stop`：`run` 是唯一启动动词且待在前台，后台化归运维（可见 tab、launchd）。`onlyne-client doctor` 只读打印宿主探测结果，通电前跑一次最省事。`--from`/`--task` 这类 flag 是全局的，子命令前后都认：`onlyne control cancel --task <id> --from bench --reason r` 与 `onlyne control --task <id> cancel` 同解。send 回执 `{"ok":true,"data":{kind,msg_id,op_id,state,task}}`，task 为 uuid v4、state 取 in_flight|queued。

socket 解析次序：`--socket` > 环境变量 `ONLYNE_SOCKET` > `--server-root` > `--workspace`/cwd 上行查找。属主目录凭 `.onlyne/run/s` 或 `.onlyne/run/socket` 认定。规范路径 `<owner>/.onlyne/run/s` 不超过 103 字节时绑在这一条；越过上界时绑到系统临时目录下的短派生路径 `<temp>/onlyne-<16hex>/s`，实际服务的路径写进同目录 `run/socket`（0600，一条绝对路径加换行）。client 拉起 session 时注入 `ONLYNE_SOCKET`，role pane 里的 `onlyne` 凭它直达。绑不上 socket 的 client 以 exit 1 结束。

版本闸只设下限，不钉版本：promote check 9 核 `onlyne version` ≥ 1.0.0，这条线划在 v0 旧协议之外，装 latest 自然满足。深路径工作区的短 socket 属于 1.1.1。beta 线（beta.2/d0f4e60、beta.3/125e351、beta.4/2666ede）作废，正式版从 1.0.0 起算，往后的补丁全是修复与新增。v1 见到 legacy `.onlyne/`（含旧 state.db 表 / `channels/` / swarm marker）会 exit 2 且零写入，这是设计内的行为。旧树先整目录 `mv .onlyne .onlyne.v0-archive/`。迁移前用旧 CLI 把在飞任务记 failed 收官，用 `sqlite3` 导旧 ledger CSV 进 runs/。

## 3. 主题要改的面（文件级清单）

| # | 文件 | 改什么 | 生效点 |
|---|---|---|---|
| 1 | `.agents/AGENTS.md` 五个 THEME 槽 | 研究问题/runs 结构/评测契约/角色表/entry | root AGENTS.md（全链） |
| 2 | `.onlyne/spec.toml` [[client]] | role 增删、prose、allowed_*、timeout/intent、max_sessions/reuse | `server reload` |
| 3 | `.onlyne/templates/flywheel/<role>/AGENTS.md` | role 深规 | 该 role ws |
| 4 | `.onlyne/templates/flywheel/<role>/.pi/settings.json` | 模型三元组；`packages` 保持 `npm:pi-onlyne` | 该 role ws |
| 5 | `pool/ideas.md` | 种子 idea（硬门字段，小节制） | scout 消费 |
| 6 | `[server].agent_package` | 发布模板保持空串。generate 留下 settings 里的 `npm:pi-onlyne`。跟仓调试未发布插件时填 checkout 的 `plugins/onlyne-agent-pi` 绝对路径，generate 会 vendor | generate |
| 7 | `[server].cert_pin` / 各 role `key` | `server init` / `client init` 产出回填；未 init 前先播合法长度 32 字节占位（`AQEBAQ...AQE=`），非法 key 会让全量 parse 连 `client init` 都跑不动 | 握手 |
| 8 | `.pi/SYSTEM.md`、`README.md` | 口径微调（一般不动） | supervisor 会话 |

relays 一致性铁律：A 的 `handoff B` 要求 B 条目 `allowed_senders` 含 A，且 A 条目 `allowed_targets` 含 B。`_supervisor` 永不出现在任何 `allowed_targets`（上行零常驻边，completion 走 origin 自动通道不经 ACL）。promote check 4 机器核这条。

## 4. 通电三门（promote 之后，一次性）

1. **server 活**：`onlyne server start --root .`（自带 detached+pid）后 `onlyne server status --root .` 的 `socket_present=true` 是真相。`run` 不写 pid，`status.running` 只认 pid 文件。深路径时再核 `<root>/.onlyne/run/socket` 与日志里的 served path。
2. **client 连**：每个启用 role 在 `onlyne roles` 显示 connected；welcome/provisioned 完成（首轮 attach 自动）。此时能得 receipt `state=in_flight`，role 会话里出现任务注入，`onlyne ledger` 有投递与 ack 行。绿了再批量起其余 client。`onlyne-client doctor` 先看宿主：`ONLYNE_BACKEND` 非空 > 工作区 `config.toml` 的 `backend` > auto（herdr→orca→zellij）。`exec`/`fake` 只在显式写出其名时启用。全无匹配时 `onlyne-client run` 退 5。
3. **渲染抽检**：`python3 -c "import json;print(json.load(open('<ws>/.pi/settings.json'))['packages'])"` 必须是 `['npm:pi-onlyne']`。`pi list` 在该 ws 下列出 `npm:pi-onlyne`。

拓扑纪律：daemon 类（`onlyne-server`、`onlyne-client`、`onlyne tui`）一律起在可见 tab，不进 agent 后台；`onlyne-client` 从目标 worktree 自己的 tab 起，worktree 错配会开错检出。会话结清后宿主资源随会话回收（herdr pane / Orca 标签 / zellij session / exec 子进程），client 日志记 `retiring idle session resource`。`reuse = true` 时仍挂着的 agent 留给下一跳。

## 5. promote.sh 九检（校验语义）

1 THEME 槽清空。2 每 role 模板目录 + settings 三元组非空，`packages == ["npm:pi-onlyne"]`。3 `★` 恰好一个且是 spec 在册 role。
4 spec[[client]]==模板目录、_supervisor admin=true、prose 非空、relay 边双向闭合、targets 不含 _supervisor。
5 角色表与 spec 逐名对齐。6 种子 idea 过 schema 硬门。7 payload/ 与 research/ 有实物。
8 `[server].agent_package` 空串，五份 settings 都是 `npm:pi-onlyne`，`pi list` 含 `npm:pi-onlyne`（第一次装配 supervisor 跑 `pi install npm:pi-onlyne`）。9 四二进制在 PATH、`onlyne version` ≥ 1.0.0（下限，日常装 latest）、herdr/orca/zellij 至少一个供 auto 探测（`exec`/`fake` 需显式 `ONLYNE_BACKEND`；全无则 `run` 退 5；`onlyne-client doctor` 看判定）。

actions：建 `theme/<slug>` 分支 → root AGENTS.md → `.onlyne/flywheel.json`（stage=live、roles、entry_role）→
退役装配材料（`.agents/AGENTS.md`、`BOOTSTRAP.md`、`.agents/skills/flywheel-setup/`）→ commit。
运行时通电在 AGENTS.md 冷启动节，人执行，脚本不起任何 daemon。

## 6. 装配阶段表

| 阶段 | 决策 | 动的文件 | 完成判据 |
|---|---|---|---|
| A 定题 | 研究什么、什么算进步、禁区 | 五个 THEME 槽 | 槽内注释块全部替换 |
| B 拓扑 | role 增删、边、模型档位、长跑 timeout | spec.toml + templates/ 目录 | check 2/4/5 绿 |
| C 起草 | 术语、runs 结构、稿件口径、★ 选谁 | 槽、role prose/AGENTS、SYSTEM/README | 角色表==spec，★ 恰好一个 |
| D 种子 | 首批 idea | pool/ideas.md | check 6 硬门绿 |
| E 装具 | 工具链、`pi install npm:pi-onlyne` | §2 全套 | check 8/9 绿 |
| F 落分支 | 复核 dry-run 清单，人确认 | promote.sh | stage=live |
| G 通电+第一发 | 方向给不给、谁投 | server/clients、payload/first.md | §4 三门绿 + ledger 首行 in_flight |

## 7. 装配后退役面（theme 分支上应消失的东西）

| 材料 | 处置 |
|---|---|
| `.agents/AGENTS.md`、`BOOTSTRAP.md`、`.agents/skills/flywheel-setup/` | promote 删除（root AGENTS.md 接班） |
| `.onlyne/spec.toml`、`templates/`、`.agents/skills/onlyne-{supervisor,role}/` | 保留，运行期要读 |
| `.onlyne.v0-archive/`（若从旧树升上来） | 保留为只读历史，gitignore 已挡 |

## 8. 常见坑

- 四二进制装好后任何 `onlyne` 命令报 command not found 或行为像旧版：先核 `which onlyne` 与 `~/.cargo/bin` 是否在 PATH、`onlyne version` 读数是否 ≥ 1.0.0 且为渠道当前 latest（落后就 `cargo install --force` 重跑）。双份安装（cargo install 与手 cp 并存）时 PATH 序决定谁生效，这是新人第一坑。
- 新 fix 出来只升 server 或只升 client 会出现半边行为：握手 protocol 相同、语义不同，账难对。升级把五个 crate 一次跑完，插件 `pi install npm:pi-onlyne` 同批更新，`onlyne version` 的 `binaries` 字段能看出各兄弟二进制取自哪条 PATH。
- `pi list` 看不到 `npm:pi-onlyne`：supervisor 第一次漏了 `pi install npm:pi-onlyne`。装完再跑 promote check 8。
- `onlyne server status` 连不上等于未通电，属于正常状态。通电用 `onlyne server start`（detached+pid），判活看 `socket_present`。深层工作区再看 `run/socket` 与 `ONLYNE_SOCKET`。
- note 打给离线 role、或打给在线但手头无 working session 的 role，都得 `recipient_offline`（server 的 `note_queue=false` 下两条门都在）。要排队就把 `[server].note_queue` 设 true 并带 `--ttl`，或者改发 task。
- 同 `op_id` 换内容重发得 `conflict`。重试时原帧重发。
- prose 改完必须跑 `onlyne reload --server-root .`（原子校验，坏 spec 保旧并记 `fault{spec_reload_failed}`）。reload 没有 `--dry-run`；看待应用差异用只读动词 `onlyne spec_diff --server-root .`。
- 满容量 role 仍收 `recycle`/`cancel`/`focus`：client 用 `control_only` pull。会话结清后宿主 pane 随会话回收；已完成任务不再报 `stalled`。
- e2e/验证脚本开头清库，或者用 `onlyne control ... recycle` 收残 session（v1 无自动回收，D12 设计）。
- role 会话默认不带 `-ns`（omp 裁定：模板 skills 三件套靠 pi 发现进会话）。「确定零 skill 的极简 role」由装机者自选加回。
- `promote.sh --dry-run` 零写入，可反复跑。正式跑需要用户逐项确认退役清单，脚本会打印清单。
