# gemini —— 双子工作区

两个 role，两条互指的边。这是本模板的全部拓扑：castor 与 pollux 互相推任务，环由 handoff 自转，没有中心调度。

workspace 表示一个 role 的长期工作区，里面有记忆、设定、历史文件。session 表示这个 role 当前手上的一件工作。任务、session、一跳是一回事。

工作按「射后不理」进行：读任务书 → 干活 → 产物写 `runs/` → handoff peer → `onlyne_complete` 交活退出。role 不等下游。投递后立即返回一行 receipt JSON。过程与回执写进 server ledger，结果通过文件返回。

状态全在文件里：接收方是全新会话，只读任务书点名的路径。

## 角色树

```text
.        supervisor（root）：值班、观察、记账，不进环
├─ castor   接任务书干活 → handoff pollux    ★ 第一发入口   axonhub/generic-researcher-powerful，thinking max
└─ pollux   接任务书干活 → handoff castor                    axonhub/supercheap，thinking max
```

两个 role 职责相同，模型位不同；边的方向决定谁是下一跳。角色表、ACL 与模型位都在 `.agents/AGENTS.md`，每个 session 自动继承它。调度与值班词汇见 `.agents/skills/onlyne-supervisor/SKILL.md`，role 协同纪律见 `.agents/skills/onlyne-role/SKILL.md`。

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

### 装配

装配把模板填成一条 `theme/<slug>` 分支与一套可通电的拓扑。装配期间不启动集群，不跑实验。

1. **定题**。写 `payload/first.md`：任务书四段（口径见角色面正本的「任务书四段」）。它是第一发，也是本主题的种子。
2. **模型位**。逐 role 看 `.onlyne/templates/gemini/<role>/.pi/settings.json` 的三元组。
3. **拓扑**。role 增删与边改 `.onlyne/spec.toml` 的 `[[client]]`，同步 `.onlyne/templates/gemini/<role>/`。角色名的唯一事实源是模板目录名。prose 是身份与上报纪律，与角色表两处保持一致。ACL 铁律：A 的 `handoff B` 要求 B 条目 `allowed_senders` 含 A，且 A 条目 `allowed_targets` 含 B。
4. **装具**。跑上面「前置」的两条安装命令；缺 `npm:pi-onlyne` 时 `pi list` 会点出来。
5. **落分支**：

   ```bash
   ./scripts/promote.sh --dry-run     # 九检零写入
   ./scripts/promote.sh               # 复核清单后执行
   ```

   脚本建 `theme/<slug>` 分支、把 `.agents/AGENTS.md` 提升为 root `AGENTS.md`、写 `.onlyne/gemini.json`、删装配材料、commit。

### 通电

通电一次性，由人执行，脚本不起任何常驻进程。以下顺序在本机实测过。

```bash
onlyne-server init --root . --listen 127.0.0.1:7812   # 产 .onlyne/keys/server.key；cert_pin 打到 stdout
# 把本仓的 .onlyne/spec.toml 与 .onlyne/templates/ 放回 .onlyne/，回填 [server].cert_pin
onlyne-server generate --root .                        # 渲染 .onlyne/ws/gemini/<role>/，逐 role 铸 key，stdout 打 [[client]] 行
# 把每行 key 粘回 spec.toml 对应的 [[client]]；generate 只跑一次，重跑前先看 ws 内的 key 是否被换
onlyne-server start --root .                           # detached+pid；判活看 socket_present
onlyne-client doctor                                   # 只读：宿主探测结果
onlyne client run --workspace .onlyne/ws/gemini/castor  # 每 role 一个 client，各占一个可见 tab
onlyne client run --workspace .onlyne/ws/gemini/pollux
```

key 位在换真身前保持合法 32 字节 base64 占位（`AQEBAQ...AQE=`）。非法 key 会让全量 parse 连 `onlyne client init` 都跑不动。`[server].cert_pin` 在 `onlyne-server init` 之前保持字符串形态。

三个断电口径：`onlyne status` 的 `socket_present` 是 server 死活真相（`run` 不写 pid，`status.running` 只认 pid 文件；深层工作区再看 `.onlyne/run/socket`）；每个启用 role 在 `onlyne roles` 显示 connected 才算连上；ws 内 `.pi/settings.json` 的 packages 保持 `npm:pi-onlyne`。

daemon 类（`onlyne-server`、`onlyne-client`、`onlyne tui`）一律起在可见 tab，不进 agent 后台。`onlyne client run` 从目标 worktree 自己的 tab 起。

### 第一发

写 `payload/first.md`（四段），然后：

```bash
onlyne --server-root . send --from _supervisor --to castor --file payload/first.md
onlyne tui
```

示例按模板默认拓扑写 `--to castor`；实际入口以角色表 `★` 行为准。第一发落地后环即成形：每跳的产物落 `runs/`，下一跳任务书交给 peer。

## 动力源

第一颗 seed 由人给，内容是方向和问题，写在 `payload/first.md`。之后每一跳自己产生下一跳任务书。

收束判据写在任务书里：判据满足即只 complete 不 handoff，环停在那一跳。人用 `onlyne control cancel --task <id>` 终结任务族，也可以在 TUI 里按终结键。

## 目录

```text
AGENTS.md                  角色面正本：角色表、一跳的生命周期、任务书四段、文件纪律（装配期在 .agents/AGENTS.md）
.agents/AGENTS.md          角色面正本源，promote 的复制起点
.agents/skills/            onlyne-role（role 协同纪律）、onlyne-supervisor（值班词汇）
.pi/SYSTEM.md              supervisor 值班会话的岗位说明
scripts/promote.sh         装配器：九检 + 落分支
onlyne 侧：.onlyne/spec.toml（拓扑真相）+ templates/gemini/<role>/（细则与模型位）
产物面：runs/（一件任务一个子目录）；第一发任务书：payload/
```

领域目录（数据、代码、成稿、证据）按题目自建，装配时补进本节。
