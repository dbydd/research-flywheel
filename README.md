# gemini —— 双子工作区

两个 role，两条互指的边。这是本模板的全部拓扑：castor 与 pollux 互相推任务，环由 handoff 自转，没有中心调度。

workspace 表示一个 role 的长期工作区，里面有记忆、设定、历史文件。session 表示这个 role 当前手上的一件工作。任务、session、一跳是一回事。

工作按「射后不理」进行：读任务书 → 干活 → 产物落任务书点名的路径 → handoff peer → `onlyne_complete` 交活退出。role 不等下游。投递后立即返回一行 receipt JSON。过程与回执写进 server ledger，结果通过文件返回。

## 三层文件

|文件|装什么|谁能改|
|---|---|---|
|仓根 `AGENTS.md`|共享目标记录：记叙段写主线与判据，条目段写支线与材料|两个 role 都能改|
|`.onlyne/AGENTS.md`|角色行为约定：一跳、任务书四段、工具面、记事纪律|模板定稿，运行期只读|
|`.onlyne/ws/gemini/<role>/AGENTS.md`|该 role 的私有记事：记叙段写过程，条目段写索引|只有该 role 自己写|

三层都在 role 工作区的父目录链上，pi 在每个 session 启动时按外层到内层自动叠加：全局 `~/.pi/agent/AGENTS.md` → 仓根 `AGENTS.md` → `.onlyne/AGENTS.md` → 该 role 的 ws `AGENTS.md`。role 的工作区固定在自己的 `.onlyne/ws/gemini/<role>/` 目录下。

产物不设统一目录与固定格式：每一跳要交出的文件由该跳的任务书点名路径。工作文件各写各的，或者就地改同一份，由任务性质定。

## 记事纪律

正本在 `.onlyne/AGENTS.md`。要点：一份 AGENTS.md 分记叙段与条目段，分开摆；索引条目原位写标题（讲清这件事是什么）；索引不递归；不用字母加数字的缩记号指代条目；记事与账目用 `edit` 工具手记，第一人称自言自语，禁止脚本生成；修订规则时就地覆盖原条目，同一个意思只留一处；不写时间戳。

## 角色树

```text
.        supervisor（管理者节点，就是仓根；会话开在 .supervisor/，由人拉起）：值班、观察、记账，不进环
├─ castor   接任务书干活 → handoff pollux    ★ 第一发入口   axonhub/generic-researcher-powerful，thinking max
└─ pollux   接任务书干活 → handoff castor                    axonhub/supercheap，thinking max
```

两个 role 职责相同，模型位不同；边的方向决定谁是下一跳。角色表、ACL 与模型位都在 `.onlyne/AGENTS.md` 与 `.onlyne/spec.toml`，每个 session 自动继承。调度与值班词汇见 `.agents/skills/onlyne-supervisor/SKILL.md`，role 协同纪律见 `.agents/skills/onlyne-role/SKILL.md`。

## 前置

装具与插件各追自己渠道的最新，命令里没有版本号。兼容判据是 `onlyne version` 的 `protocol:1`。

- **onlyne v1 五件套**。发布渠道一行装齐：

  ```bash
  cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui
  ```

  crate `onlyne-cli` 装出的 bin 叫 `onlyne`，其余同名。升级＝同一条命令加 `--force` 重跑。
- **pi 插件**：`pi install npm:pi-onlyne`。role 模板 `.pi/settings.json` 的 packages 已写 `npm:pi-onlyne`。
- **会话后端**：`herdr`、`orca` 或 `zellij` 之一。选择链是 `ONLYNE_BACKEND`（非空）> 工作区 `config.toml` 的 `backend` > auto。auto 探测序 herdr→orca→zellij。`exec`/`fake` 只在显式写出其名时启用。全无匹配时 `onlyne client run` 退 5。`onlyne-client doctor` 打印宿主判定。
- 要跟 onlyne 仓 main 上尚未发布的 fix：`git clone https://github.com/dbydd/onlyne && cargo build --release`，五产物放进 PATH。macOS 上 cp 完必做 `codesign --force --sign -`，复制后的二进制签名失效，直接 exec 收 SIGKILL。
- pi 的 model/provider：`templates/gemini/<role>/.pi/settings.json` 的三元组已填 `axonhub` 与两个模型名，装配时按需改。

## 装配与通电

自展开四步：定题 → 核拓扑与模型位 → 落分支 → 通电与第一发。仓根 `AGENTS.md` 就是共享目标记录本身，定题时就地改它；落分支不搬运、不替换它。本节是逐条细节。

### 装配

装配把模板填成一条 `theme/<slug>` 分支与一套可通电的拓扑。装配期间不启动集群，不跑实验。

1. **定题**。改写仓根 `AGENTS.md`：记叙段写主线与判据，条目段写支线与材料。再写 `payload/first.md` 的第一发任务书（四段，口径见 `.onlyne/AGENTS.md`）。
2. **模型位**。逐 role 看 `.onlyne/templates/gemini/<role>/.pi/settings.json` 的三元组。
3. **拓扑**。role 增删与边改 `.onlyne/spec.toml` 的 `[[client]]`，同步 `.onlyne/templates/gemini/<role>/`。角色名的唯一事实源是模板目录名。prose 是身份与上报纪律，与 `.onlyne/AGENTS.md` 的角色表两处保持一致。ACL 铁律：A 的 `handoff B` 要求 B 条目 `allowed_senders` 含 A，且 A 条目 `allowed_targets` 含 B。
4. **装具**。跑上面「前置」的两条安装命令；缺 `npm:pi-onlyne` 时 `pi list` 会点出来。
5. **落分支**：

   ```bash
   ./scripts/promote.sh --dry-run     # 九检零写入
   ./scripts/promote.sh               # 复核清单后执行
   ```

   脚本建 `theme/<slug>` 分支、写 `.onlyne/gemini.json`（stage=live）、commit。仓根 `AGENTS.md` 与 `.agents/skills/` 原样保留。

### 通电

通电一次性，由人执行，脚本不起任何常驻进程。以下顺序在本机实测过。

```bash
onlyne-server init --root . --listen 127.0.0.1:7812   # 产 .onlyne/keys/server.key；cert_pin 打到 stdout
# 把本仓的 .onlyne/spec.toml、.onlyne/templates/、.onlyne/AGENTS.md 放回 .onlyne/，回填 [server].cert_pin
onlyne-server generate --root .                        # 渲染 .onlyne/ws/gemini/<role>/，逐 role 铸 key，stdout 打 [[client]] 行
# 把每行 key 粘回 spec.toml 对应的 [[client]]
onlyne server start --root .                           # detached+pid；判活看 socket_present
onlyne-client doctor                                   # 只读：宿主探测结果
# supervisor：由人在 .supervisor/ 开一个 agent 会话（pi、omp 都行），该目录的 AGENTS.md 是值班说明
onlyne client run --workspace .onlyne/ws/gemini/castor  # 每 role 一个 client，各占一个可见 tab
onlyne client run --workspace .onlyne/ws/gemini/pollux
```

渲染进 ws 的 `AGENTS.md` 是模板骨架，之后由该 role 手记维护。重跑 `generate` 不带 `--force` 会拒绝覆盖已有 ws（退 4）；带 `--force` 则把记事换回骨架。

key 位在换真身前保持合法 32 字节 base64 占位（`AQEBAQ...AQE=`）。非法 key 会让全量 parse 连 `onlyne client init` 都跑不动。`[server].cert_pin` 在 `onlyne-server init` 之前保持字符串形态。

三个断电口径：`onlyne status` 的 `socket_present` 是 server 死活真相（`run` 不写 pid，`status.running` 只认 pid 文件；深层工作区再看 `.onlyne/run/socket`）；每个启用 role 在 `onlyne roles` 显示 connected 才算连上；ws 内 `.pi/settings.json` 的 packages 保持 `npm:pi-onlyne`。

daemon 类（`onlyne-server`、`onlyne-client`、`onlyne tui`）一律起在可见 tab，不进 agent 后台。`onlyne client run` 从目标 worktree 自己的 tab 起。

### 第一发

写 `payload/first.md`（四段），然后：

```bash
onlyne --server-root . send --from _supervisor --to castor --file payload/first.md
onlyne tui
```

示例按模板默认拓扑写 `--to castor`；实际入口以 `.onlyne/AGENTS.md` 角色表 `★` 行为准。第一发落地后环即成形：每跳自己定产物路径，下一跳任务书交给 peer。

## 动力源

第一颗 seed 由人给，写在仓根 `AGENTS.md` 的主线与 `payload/first.md`。之后每一跳自己产生下一跳任务书。

收束判据写在任务书里：判据满足即只 complete 不 handoff，环停在那一跳。人用 `onlyne control cancel --task <id>` 终结任务族，也可以在 TUI 里按终结键。

## 目录

```text
AGENTS.md                  共享目标记录：记叙段写主线与判据，条目段写支线与材料
.onlyne/AGENTS.md          角色行为约定：一跳、任务书四段、工具面、记事纪律
.agents/skills/            onlyne-role（role 协同纪律）、onlyne-supervisor（值班词汇）
.supervisor/AGENTS.md      supervisor 值班岗位说明（会话开在 .supervisor/，由人拉起）
scripts/promote.sh         装配器：九检 + 落分支
onlyne 侧：.onlyne/spec.toml（拓扑真相）+ templates/gemini/<role>/（role 记事骨架与模型位）
第一发任务书：payload/；产物路径由任务书点名，不设统一目录
role 工作区：.onlyne/ws/gemini/<role>/（运行时渲染，含该 role 的记事 AGENTS.md）
```

领域目录（数据、代码、成稿、证据）按题目自建，装配时补进本节。
