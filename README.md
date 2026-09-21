# Research Flywheel v3

这是一个基于 onlyne v1 的自动科研飞轮模板。它把一个研究主题拆给五个 role。每个 role 拿到一跳任务，产物写回磁盘，再把下一跳任务交给下游。

workspace 表示一个 role 的长期工作区，里面有记忆、设定、历史文件。session 表示这个 role 当前手上的一件工作。任务、session、一跳是一回事。

飞轮按“射后不理”工作：恢复上下文 → 工作 → `handoff` 激发下游（可选）→ 写文件 → `onlyne_complete` 交活退出。role 不等下游回执。投递后立即返回一行 receipt JSON。过程与回执都写进 server ledger。结果通过文件返回。下一条接力任务会唤醒下一个 role。环路长期打开，由 supervisor 或人来停下。

## 使用方式

使用omp再orca/herdr中打开此仓库，然后问他怎么操作

## 角色树

```text
.        supervisor（root）：值班、观察、记账，不进环
├─ scout   检索+证据+idea 入池，取单派 model                                    ★ 第一发入口
├─ model   推导+Lean 形式化+方法与评测器 spec → 派 bench / writer（理论缺口回 scout）
├─ bench   跑实验与评测落 measured/ → 派 writer（跑不动回 scout）
├─ writer  成稿（带溯源数字）+ 兼职出图 → 派 critic
└─ critic  对照证据审稿 → verdict.md → 派 writer（修订）/ model（理论级修订）/ scout（新轮）
```

角色链：scout → model → {bench, writer} → writer → critic → {writer、model、scout}。角色表、ACL 与模型位都在 `.agents/AGENTS.md`。每个 session 自动继承它。调度与值班词汇见 `.agents/skills/onlyne-supervisor/SKILL.md`，role 协同纪律见 `.agents/skills/onlyne-role/SKILL.md`。

## 前置

装具与插件各追自己渠道的最新，命令里没有版本号。兼容判据是 `onlyne version` 的 `protocol:1`。

- **onlyne v1 五件套**。发布渠道一行装齐：
  ```bash
  cargo install onlyne-cli onlyne-server onlyne-client onlyne-gateway onlyne-tui
  ```

  crate `onlyne-cli` 装出的 bin 叫 `onlyne`，其余同名。升级＝同一条命令加 `--force` 重跑。
- **pi 插件**：`pi install npm:pi-onlyne`。role 模板 `.pi/settings.json` 的 packages 已经写着 `npm:pi-onlyne`。
- **会话后端**：`herdr`、`orca` 或 `zellij` 之一。选择链是 `ONLYNE_BACKEND`（非空）&gt; 工作区 `config.toml` 的 `backend` &gt; auto。auto 探测序 herdr→orca→zellij。`exec`/`fake` 只在显式写出其名时启用。全无匹配时 `onlyne client run` 退 5。`onlyne-client doctor` 打印宿主判定。
- 要跟 onlyne 仓 main 上尚未发布的 fix：`git clone https://github.com/dbydd/onlyne && cargo build --release`，五产物放进 PATH。macOS 上 cp 完必做 `codesign --force --sign -`，复制后的二进制签名失效，直接 exec 收 SIGKILL。
- pi 的 model/provider。`templates/flywheel/<role>/.pi/settings.json` 的三元组在装配时填 defaultProvider / defaultModel / defaultThinkingLevel。

## 装配与通电

### 装配

装配把通用骨架填成一个具体研究主题的飞轮，产出一条 `theme/<slug>` 分支与一套可通电的拓扑。装配期间不启动集群，不跑实验。

1. **定题**。填 `.agents/AGENTS.md` 的「研究问题与判进标准」「runs/<run-id>/ 目录约定」「评测契约」三节：研究问题一句话加验收它的度量，主度量与次度量各自的阈值，算力与时间预算，禁区。
2. **拓扑**。role 增删与边改 `.onlyne/spec.toml` 的 `[[client]]`，同步 `.onlyne/templates/flywheel/<role>/` 目录。角色名的唯一事实源是模板目录名。prose 是身份与上报纪律，与角色表两处保持一致。ACL 铁律：A 的 `handoff B` 要求 B 条目 `allowed_senders` 含 A，且 A 条目 `allowed_targets` 含 B。`relay_required` 是完成守卫（session 在 complete 前必须已经 handoff 给列出的角色），本模板未启用。
3. **模型档位**。逐 role 填 `.onlyne/templates/flywheel/<role>/.pi/settings.json` 的三元组。
4. **种子**。写 `pool/ideas.md`：一条 idea 一个小节，`evidence`、`evaluation.objectives`、`done_when` 三项非空才进池。同时写 `research/` 的领域锚点文件，含 `frontier-notes.md` 表头与至少一条真实来源记录。
5. **装具**。跑上面「前置」的 onlyne 与 pi 插件两条安装命令；缺 `npm:pi-onlyne` 时 `pi list` 会点出来。
6. **落分支**：
  ```bash
   ./scripts/promote.sh --dry-run     # 九检零写入
   ./scripts/promote.sh               # 复核清单后执行
  ```

   脚本建 `theme/<slug>` 分支、把 `.agents/AGENTS.md` 提升为 root `AGENTS.md`、写 `.onlyne/flywheel.json`、删装配材料、commit。

### 通电

通电一次性，由人执行，脚本不起任何常驻进程。

```bash
onlyne server init --root . --listen 127.0.0.1:7812   # 产 keys 与 cert_pin；多树并机自选空闲端口
# 回填 spec.toml 的 [server].cert_pin，并逐 role 换真 key
onlyne client init --workspace .onlyne/ws/flywheel/<role> --role <role> --server-root .
onlyne server generate --root .                       # 渲染 .onlyne/ws/flywheel/<role>/
onlyne server start --root .                          # detached+pid；判活看 socket_present
onlyne-client doctor                                  # 只读：宿主探测结果
onlyne client run --workspace .onlyne/ws/flywheel/scout   # 每 role 一个 client，各占一个可见 tab
```

key 位在换真身前保持合法 32 字节 base64 占位（`AQEBAQ...AQE=`）。非法 key 会让全量 parse 连 `onlyne client init` 都跑不动。`[server].cert_pin` 在 `onlyne server init` 之前保持字符串形态。

三个断电口径：`onlyne server status` 的 `socket_present` 是 server 死活真相（`run` 不写 pid，`status.running` 只认 pid 文件；深层工作区再看 `.onlyne/run/socket`）；每个启用 role 在 `onlyne roles` 显示 connected 才算连上；ws 内 `.pi/settings.json` 的 packages 保持 `npm:pi-onlyne`。

daemon 类（`onlyne-server`、`onlyne-client`、`onlyne tui`）一律起在可见 tab，不进 agent 后台。`onlyne-client` 从目标 worktree 自己的 tab 起。

### 第一发

写 `payload/first.md`（目标、输入、期望产物、下一跳建议四段，口径见角色面正本的「任务书四段」），然后：

```bash
onlyne --server-root . send --from _supervisor --to scout --file payload/first.md
onlyne tui
```

示例按模板默认拓扑写 `--to scout`；实际入口以角色表 `★` 行为准，换主题时同步这一行。第一发落地后环即成形：entry role 产出入池并自取 queued 派给下游，后续每轮靠接力任务推进。supervisor 不进环。

## 动力源

第一颗 seed 由人给，内容是方向和问题。之后每轮结束，critic 从 open questions 或失败结论提取下一条 idea 入池。idea 需要证据和评测契约，缺任一项就不入池。自激发没有熔断。人用 `onlyne control cancel --task <id>` 终结任务族，也可以在 TUI 里按终结键。

## 目录

```text
AGENTS.md                  角色面正本：角色表、边义、runs 结构、评测契约、纪律
.agents/AGENTS.md          角色面正本源，promote 的复制起点
.agents/skills/            领域技能（paper-figures、paper-writing）与平台技能（onlyne-role、onlyne-supervisor）
.pi/SYSTEM.md              supervisor 值班会话的岗位说明
scripts/promote.sh         装配器：九检 + 落分支
onlyne 侧：.onlyne/spec.toml（拓扑真相）+ templates/flywheel/<role>/（细则与模型位）
知识产物：pool/（idea 池）、runs/（一轮过程件）、papers/（成稿与 figs）、research/（证据）
领域代码：experiment/、evaluation/；第一发任务书：payload/
```

