# gemini —— 两个 AI 助手互相推活的双子工作区

## 这是什么

一群 AI 助手在同一个文件夹里分工推进研究。本模板只有两个助手：castor 和 pollux。castor 干完一段活把下一棒交给 pollux，pollux 干完交回 castor，两人接力，没有中心调度。

你给它什么：一个研究题目和第一份任务书。

你得到什么：两个助手轮流产出的工作文件，文件落在哪里由每份任务书写明。

适合想搭一条最小自动接力线的人。

## 三分钟看懂工作原理

```text
.        supervisor（管理者节点，就是仓根）：值班、观察、记账，不进环
├─ castor   接任务书干活 → handoff pollux    ★ 第一发入口   模型位见模板 settings，thinking max
└─ pollux   接任务书干活 → handoff castor                    模型位见模板 settings，thinking max
```

role 指一个助手及其长期工作区。一跳指一个 role 接一份任务书干到交活。工作按「射后不理」进行：读任务书 → 干活 → 产物落任务书点名的路径 → handoff peer（把下一棒交给对方，环里另一个 role）→ `onlyne_complete` 交活退出。role 不等下游。投递后立即返回一行 receipt JSON（回执）。过程与回执写进 server ledger（服务端账本），完整结果经 `details`/`files` 送达上游，文件本体留在磁盘。

第一发是人发出的第一份任务书，环由此转起来；之后每一跳自己产生下一跳任务书。

## 第一次跑

前置：装好 onlyne 与 pi 插件，pi 已配好模型。

```bash
cargo install --locked onlyne-cli onlyne-server onlyne-client onlyne-testkit   # onlyne 四件套；crate onlyne-cli 装出的 bin 叫 onlyne
pi install npm:pi-onlyne@2.1.0                                                  # pi 插件；版本与 ws 内 .pi/settings.json 的 pin 一致
```

四步，可让 agent 代劳：

1. 对 agent 说：帮我按本仓模板装配。装配做五件事：定题（写 `.agents/AGENTS.md` 目标记录，并留一份六段第一发任务书草稿）、核模型位、核拓扑、装具、落分支。agent 会先报缺什么前置，缺的东西由人装。定题没写完不落分支。
2. 定题完成后 agent 跑 `./scripts/promote.sh --dry-run`（九检零写入），你复核清单后 agent 跑 `./scripts/promote.sh`（建 `theme/<slug>` 分支并 commit）。
3. 通电，一次性，由人执行。先初始化，再起进程；脚本不起任何常驻进程。

初始化（普通 tab，还没起任何常驻进程）：

```bash
# 仓里已带模板 .onlyne/spec.toml。server init 见到 spec.toml 在位就退 4；加 --force 会用一份
# 只剩 [server] 段的骨架覆盖它——role、边、ACL 全丢。所以走「挪开 → init → 还原」。
# init 的写入面只有 .onlyne/spec.toml 与 .onlyne/keys/server.key：templates/ 与 .onlyne/AGENTS.md
# 它不碰，不用陪着挪。临时路径用 mktemp 取；init 失败也先还原，拓扑不能被弄丢。
spec_backup="$(mktemp)"
mv .onlyne/spec.toml "$spec_backup"
cert_pin="$(onlyne server init --root . --listen 127.0.0.1:7812 2>/dev/null)"   # 铸 server 密钥对，真 cert_pin 打到 stdout
status=$?
mv "$spec_backup" .onlyne/spec.toml                   # 无条件还原模板 spec
test "$status" -eq 0 || exit "$status"
printf 'cert_pin=%s\n' "$cert_pin"                    # 这一行粘进 [server].cert_pin，替掉 32 字节全零占位

onlyne generate --root .                              # 渲染 .onlyne/ws/gemini/<role>/，逐 role 铸 key，stdout 打 [[client]] 行
# 把 generate 打出的每行 key 粘回 spec.toml 对应的 [[client]]，替掉 AQEBAQ... 占位
# （cert_pin 与 key 是这台机器这一套的真身，换机器重跑 init/generate 会换一副；
#  server 已在跑时改完要 onlyne reload --server-root .，还没起则 server run 自己会读）
```

回填 cert_pin 与各 role key 是同一件事的两半：cert_pin 认服务端，key 认 role。两处留着占位时 server 起得来、client 对不上真身，所以这两步不能跳。

起服务端（新开一个命名 `onlyne-server` 的可见 tab，前台常驻；在它起来之前什么都发不出去）：

```bash
onlyne server run --root .    # 前台常驻跑在这个 tab；判活看 socket_present
```

体检（另开一个普通 tab，在任何 client 起来之前跑，只读不写）：

```bash
onlyne client doctor   # 只读：宿主探测结果，异常先处理再往下
```

起 client（每个 role 一个 client，各占一个以 role 名命名的可见 tab）：

```bash
onlyne client run --workspace .onlyne/ws/gemini/castor   # tab 名 castor
onlyne client run --workspace .onlyne/ws/gemini/pollux   # tab 名 pollux
```

supervisor：在仓根开一个 agent 会话（pi、omp 都行），先读 `.supervisor/AGENTS.md`。

4. 发第一发：

任务书是瞬态交接面：交接一过就不用留，仓里不设存档目录。`payload/first.md` 是模板给的样例草稿，装配期供你比着写；发信链路上不读它——第一发由人当场把六段写进一个临时文件、走 `--file` 发出、再删掉：

```bash
cat > /tmp/gemini-first.md <<'TASK'
目标：为仓根 `AGENTS.md` 主线定下的研究问题做一轮前沿侦察，产出至少一条能过判据的 idea。

背景：第一发注入，环刚成形。仓根 `AGENTS.md` 主线里已有主题与判据，还没有任何检索台账与候选 idea；本跳要从零把前沿面铺出来，给环后续每一跳提供材料。

输入：
（全部相对仓根，接收方是全新上下文，没点名的路径它找不到）
- `AGENTS.md` 的「主线」节：研究问题、判据、禁区。
- `AGENTS.md` 的「索引」节：已有材料台账；空表就跳过。
- `research/` 下的本地物料：存在就先翻旧账再查新。

期望产物：
- `research/frontier-notes.md`：检索台账，一行一结论，每条结论带来源路径或链接。
- 仓根 `AGENTS.md`「索引」表新增一行，指向该台账。

自由度：顺手补查与主线相邻的方向，负证据（查过没有）也记进台账；发现判据写不动的地步，在台账里单开一节说明原因，供下一跳参考。

下一跳建议：完成后用 `onlyne_handoff` 交给 pollux，任务书点名 `research/frontier-notes.md`，让它从台账里挑一条做成候选 idea。
TASK

onlyne --server-root . send --from _supervisor --to castor \
  --file /tmp/gemini-first.md --force --yes-i-am-supervisor-not-other-role
rm -f /tmp/gemini-first.md     # 传完即删；过程与结论落在各 role 自己的 ws AGENTS.md 与 server ledger
onlyne tui --server-root .
```

六段标题字面固定（目标/背景/输入/期望产物/自由度/下一跳建议），接收方按标题找段；口径正本在 `.onlyne/AGENTS.md`。上面这份填满了，可以直接发，也可以照它的样子改成自己的主题；改的时候守住两条：`输入` 段点名的路径必须真实存在，产物路径写清落到哪个文件。

两个身份 flag 一个都不能少：`--force` 与 `--yes-i-am-supervisor-not-other-role` 缺一个即退 2，socket 都不打开（提示指回 role 会话内该走的 `onlyne_send`）。`--file` 换成 `--text "<六段正文>"` 也能发；`--file -` 走 stdin。

`castor` 是第一发入口，标在 `.onlyne/AGENTS.md` 角色表的 ★ 行（spec 里同义的 `# ★ entry role`）。`_supervisor` 的 `allowed_targets` 是 castor 与 pollux 两个，所以发给 pollux 也能收——环会反着转起来。要按模板的设定跑，就发 castor。

确认成功：TUI 里能看到 castor 接单开工。第一发落地后环即成形：每跳自己定产物路径，下一跳任务书交给 peer。想细节往下读；只想用，到此为止。

## 日常使用

- 看进度：`onlyne tui --server-root .`。
- 终结任务族：`onlyne control cancel --force --yes-i-am-supervisor-not-other-role --task <id>`，也可以在 TUI 里按终结键。
- 环怎么停：收束判据写在任务书里，判据满足即只 complete 不 handoff，环停在那一跳。
- 换研究主题：改仓根 `AGENTS.md` 的主线，再按「第一次跑」第 4 步当场写一份新任务书发一发。
- 出问题看下文「排障（出问题先查这里）」。

## 术语表（按正文出现顺序可查）

| 词 | 意思 |
|---|---|
| role | 一个助手及其长期工作区 |
| workspace | 一个 role 的长期工作区，装记忆、设定、历史文件 |
| session | 该 role 当前手上的一件工作；任务、session、一跳是一回事 |
| 任务书 | 一份六段的活单，写清做什么、产物落到哪个路径 |
| 第一发 | 人发出的第一份任务书，环由此转起来 |
| handoff | 把下一棒交给对方 |
| peer | 环里与自己互指的另一个 role |
| receipt JSON | 投递后立即返回的一行回执 |
| server ledger | 服务端账本，记过程与回执 |
| spec.toml | `.onlyne/spec.toml`，拓扑真相 |
| 放置 | 终端宿主，写进 `.onlyne/config.toml` 的 `placement` |
| supervisor | 管理者节点，值班、观察、记账，不进环 |

## 工作原理细节

### 拓扑与 ACL

两个 role 职责相同，模型位不同；边的方向决定谁是下一跳。角色表与 ACL 在 `.onlyne/AGENTS.md` 与 `.onlyne/spec.toml`，模型位在 `templates/gemini/<role>/.pi/settings.json`，每个 session 自动继承；模板不发具体模型名，装配时由人填。`allowed_targets` 既限可发方向，也是收面义务：交齐下游才能 terminal outcome，派单方 origin 自动豁免。调度与值班词汇见 `.agents/skills/onlyne-supervisor/SKILL.md`，role 协同纪律见 `.agents/skills/onlyne-role/SKILL.md`。

### 三层文件

|文件|装什么|谁能改|
|---|---|---|
|仓根 `AGENTS.md`|共享目标记录：记叙段是主线（目标与判据），条目段是支线 todo 与索引表|两个 role 都能改|
| `.onlyne/AGENTS.md`|角色行为约定：一跳、任务书六段、工具面、记事纪律|模板定稿，运行期只读|
|`.onlyne/ws/gemini/<role>/AGENTS.md`|该 role 的私有记事：记叙段写过程，条目段写索引表|只有该 role 自己写|

三层都在 role 工作区的父目录链上，pi 在每个 session 启动时按外层到内层自动叠加：全局 `~/.pi/agent/AGENTS.md` → 仓根 `AGENTS.md` → `.onlyne/AGENTS.md` → 该 role 的 ws `AGENTS.md`。role 的工作区固定在自己的 `.onlyne/ws/gemini/<role>/` 目录下。

产物不设统一目录与固定格式：每一跳要交出的文件由该跳的任务书点名路径。工作文件各写各的，或者就地改同一份，由任务性质定。

### 记事纪律

正本在 `.onlyne/AGENTS.md`。要点：一份 AGENTS.md 分记叙段与条目段，分开摆；索引条目原位写标题（讲清这件事是什么）；索引不递归；不用字母加数字的缩记号指代条目；记事与账目用 `edit` 工具手记，第一人称自言自语，禁止脚本生成；修订规则时就地覆盖原条目，同一个意思只留一处；不写时间戳。

### 装配细则

装配把模板填成一条 `theme/<slug>` 分支与一套可通电的拓扑。装配期间不启动集群，不跑实验。

仓根 `AGENTS.md` 就是那份共享目标记录——记事本写主线，支线开成 todo，材料走索引表；模板态和活态是同一份，装配时就地改它。

起环的四条引导：

- 值班会话开在 `.supervisor/`，岗位说明在该目录的 `AGENTS.md`。
- 起环前先报前置缺什么（onlyne 四件套、pi 插件、放置后端），缺的东西由人装。
- 常驻进程（server、client、tui）一律起在可见 tab，不进 agent 后台。
- 定题没写完不落分支：让双子空转没有意义。

1. **定题**。写目标记录 `.agents/AGENTS.md`（主线、判据、支线 todo、索引；它落分支后就是仓根 `AGENTS.md`），并备好一份六段第一发任务书（口径见 `.onlyne/AGENTS.md`，模板样例在 `payload/first.md`）。任务书是瞬态交接面，装配只把它备到位，不发：发信在通电后由人当场写临时文件走 `--file`（见「第一次跑」第 4 步）。
2. **模型位**。逐 role 看 `.onlyne/templates/gemini/<role>/.pi/settings.json`：`defaultThinkingLevel` 模板已定；`defaultProvider`/`defaultModel` 留空用 pi 默认，装配时按需填。
3. **拓扑**。role 增删与边改 `.onlyne/spec.toml` 的 `[[client]]`，同步 `.onlyne/templates/gemini/<role>/`。角色名的唯一事实源是模板目录名。prose 是身份与上报纪律，与 `.onlyne/AGENTS.md` 的角色表两处保持一致。ACL 铁律：A 的 `handoff B` 要求 B 条目 `allowed_senders` 含 A，且 A 条目 `allowed_targets` 含 B。
4. **装具**。跑「第一次跑」的两条安装命令；缺 `npm:pi-onlyne` 时 `pi list` 会点出来。
5. **落分支**：

   ```bash
   ./scripts/promote.sh --dry-run     # 九检零写入
   ./scripts/promote.sh               # 复核清单后执行
   ```

   脚本建 `theme/<slug>` 分支、把 `.agents/AGENTS.md` 提升为仓根 `AGENTS.md`、写 `.onlyne/gemini.json`、保留装配快照、commit。

### 通电细则

渲染进 ws 的 `AGENTS.md` 是模板骨架，之后由该 role 手记维护。重跑 `generate` 不带 `--force` 会拒绝覆盖已有 ws（退 4）；带 `--force` 则把记事换回骨架。

key 位在换真身前保持合法 32 字节 base64 占位（`AQEBAQ...AQE=`，即 32×0x01）。非法 key 会让全量 parse 连 `onlyne client init` 都跑不动。`[server].cert_pin` 在 `onlyne server init` 之前保持 32 字节全零 hex 占位。

断电口径：`onlyne server status` 的 `socket_present` 反映 admin socket 文件在位（server 死活的机器级真相）；每个启用 role 在 `onlyne roles` 显示 connected 才算连上；ws 内 `.pi/settings.json` 的 packages 保持 `npm:pi-onlyne@2.1.0`。

常驻类（`onlyne server run`、`onlyne client run`、`onlyne tui`）一律起在可见 tab，不进 agent 后台。`onlyne client run` 从目标 worktree 自己的 tab 起。

### 前置补充

- 装具各追自己渠道的最新：cargo 侧命令不带版本号，pi 插件按 settings 的 pin `npm:pi-onlyne@2.1.0` 定版（ws 内 `.pi/settings.json` 的 `packages` 与安装命令保持同一个值）。兼容判据是 `onlyne version` 的 `protocol:1`。
- 升级＝`cargo install --locked onlyne-cli onlyne-server onlyne-client onlyne-testkit` 同一条命令加 `--force` 重跑，其余 bin 同名。
- 放置：`orca` 或 `zellij` 之一即可，`tern` 与 `headless` 也合法。放置写进工作区 `.onlyne/config.toml` 的 `placement`；省略时探测序 tern → orca → zellij → headless；非空 `ONLYNE_BACKEND` 优先。全无匹配时 `onlyne client run` 退 5。`onlyne client doctor` 只读打印宿主判定。
- 要跟 onlyne 上游 main 上尚未发布的 fix：`git clone https://github.com/dbydd/onlyne && cargo build --release`，产物放进 PATH。
- pi 的 model/provider：`templates/gemini/<role>/.pi/settings.json` 省略 `defaultProvider`/`defaultModel` 这两个键即用 pi 自己已配置的默认；要定点配就装配时填。

## 排障（出问题先查这里）

| 现象 | 处置 |
|---|---|
| `onlyne client run` 退 5 | 放置后端全无匹配：装 `orca`/`zellij`/`tern` 之一，或在 `.onlyne/config.toml` 写 `placement` |
| `onlyne generate` 退 4 | 已有 ws，不带 `--force` 拒绝覆盖；确认后加 `--force`（会把记事换回骨架） |
| `onlyne server init` 退 4 | 已有 spec.toml。按「第一次跑」挪开再还原。**不要**加 `--force`：它会写回一份只剩 `[server]` 段的骨架，role、边、ACL 全丢，模板 spec 里注释过的那些键一并消失 |
| `onlyne send` 退 2 | 身份 flag 不全：`--force` 与 `--yes-i-am-supervisor-not-other-role` 缺一个即拒，socket 都不打开 |
| `onlyne send` 退 3 | 找不到 admin socket：server 没起，或 `--server-root` 指错目录。先 `onlyne server status --server-root .` 看 `socket_present` |
| 第一发发出去、TUI 里没人动 | 先确认 `--to` 是角色表 ★ 行的 `castor`；发给 `_supervisor` 的 `allowed_targets` 之外的 role 会被挡回，那一跳不落账。收件方在册但仍不动，看它的 client tab 在不在、`onlyne roles` 里是不是 connected |
| 全量 parse 失败，`onlyne client init` 跑不动 | key 非法；换真身前保持合法 32 字节 base64 占位（`AQEBAQ...AQE=`，即 32×0x01） |
| client 连不上、role 始终 offline | cert_pin 或各 role key 还留着占位。回填完要 `onlyne reload --server-root .`（server 还没起则 `server run` 自己会读） |
| 判断 server 死活 | 看 `onlyne server status` 的 `socket_present`（admin socket 文件在位，机器级真相）；每个启用 role 在 `onlyne roles` 显示 connected 才算连上 |

## 目录结构

```text
AGENTS.md                  共享目标记录：主线（目标与判据）、支线 todo、索引表
.onlyne/AGENTS.md          角色行为约定：一跳、任务书六段、工具面、记事纪律
.agents/AGENTS.md          共享目标的正本源，落分支的复制起点
.agents/skills/            onlyne-role（role 协同纪律）、onlyne-supervisor（值班词汇）
.supervisor/AGENTS.md      supervisor 值班岗位说明（任意 harness 开在仓根，先读它）
scripts/promote.sh         装配器：九检 + 落分支
onlyne 侧：.onlyne/spec.toml（拓扑真相）+ templates/gemini/<role>/（role 记事骨架与模型位）
第一发任务书样例：payload/first.md（装配期草稿，不进发信链路；发信走临时文件 --file）
产物路径由任务书点名，不设统一目录
role 工作区：.onlyne/ws/gemini/<role>/（运行时渲染，含该 role 的记事 AGENTS.md）
```

领域目录（数据、代码、成稿、证据）按题目自建，装配时补进本节。
