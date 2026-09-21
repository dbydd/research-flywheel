# Alexandria —— 读论文、找 idea 的工作区

本工作区辅助学生与科研工作者读论文、找 idea：role 读论文，把结论写成笔记，笔记连成图，图上的缺口变成 idea。

仓根本身就是一个 Obsidian vault，同时是一个 llmwiki bundle：Obsidian 打开仓根，role 写下的知识笔记就是 vault 里的笔记，`raw/`、`wiki/`、`index.md`、`log.md` 是笔记的三层加两个保留文件。机器件都在点目录里（`.onlyne/`、`.pi/`、`.agents/`、`.supervisor/`），Obsidian 不进点目录，图谱与搜索里只有笔记。

运行框架是最简形状的 onlyne 环：三层记事、任务书四段、射后不理、ledger 记账。角色与边的设计在下一步，落点见下面「角色树」一节。

两个词先说清：workspace 表示一个 role 的长期工作区，里面有记忆、设定、历史文件；session 表示这个 role 当前手上的一件工作。任务、session、一跳是一回事。

工作按「射后不理」进行：读任务书 → 干活 → 产物落任务书点名的路径 → handoff 下一跳 → `onlyne_complete` 交活退出。role 不等下游。投递后立即返回一行 receipt JSON。过程与回执写进 server ledger，结果通过文件返回。

## 三层文件

|文件|装什么|谁能改|
|---|---|---|
|仓根 `AGENTS.md`|共享目标记录：记叙段是主线（目标与判据），条目段是支线 todo 与索引表|环上每个 role 都能改|
|`.onlyne/AGENTS.md`|角色行为约定：一跳、任务书四段、记事纪律、工具面|模板定稿，运行期只读|
|`.onlyne/ws/alexandria/<role>/AGENTS.md`|该 role 的私有记事：记叙段写过程，条目段写索引表|只有该 role 自己写|

三层都在 role 工作区的父目录链上，pi 在每个 session 启动时按外层到内层自动叠加：全局 `~/.pi/agent/AGENTS.md` → 仓根 `AGENTS.md` → `.onlyne/AGENTS.md` → 该 role 的 ws `AGENTS.md`。role 的工作区固定在自己的 `.onlyne/ws/alexandria/<role>/` 目录下。

产物不设统一目录与固定格式：每一跳要交出的文件由该跳的任务书点名路径。工作文件各写各的，或者就地改同一份，由任务性质定。

## 记事纪律

正本在 `.onlyne/AGENTS.md`。要点：一份 AGENTS.md 分记叙段与条目段，分开摆；索引条目原位写标题（讲清这件事是什么）；索引不递归；不用字母加数字的缩记号指代条目；记事与账目用 `edit` 工具手记，第一人称自言自语，禁止脚本生成；修订规则时就地覆盖原条目，同一个意思只留一处；不写时间戳。

## 一跳的生命周期

1. 任务书到 role 手上：`[onlyne] task <task-id> from role:<sender> (kind task)`。
2. 读四段点名的输入路径。
3. 干活，产物落任务书点名的路径。
4. 下一跳写四段任务书，handoff 交给下一跳的 role（`parent_task` 与 hop+1 血缘自动落账）。
5. `onlyne_complete`：text 一行放结果与产物路径。

收束判据满足，或任务书写明一跳即止：只 complete 不 handoff，环停在那一步，等下一次注入。

## 任务书四段

```text
目标：<一句话，做完算什么>
输入：<一条一行：「路径」（括号里原位写清这份文件是什么）>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<handoff 谁、干什么；没有就写 无>
```

输入路径必须真实存在，接收方 session 是全新上下文，任务书里没写的路径它找不到。内容按引用交接：text 里给路径与标题，接收方读文件；工作区字节从不上总线。

## 笔记格式（llmwiki）

本仓的 md 笔记按 llmwiki 格式写。正本在 `.agents/skills/wiki-format/SKILL.md`；格式源是 Karpathy 的 LLM Wiki pattern 与它的开源实现（llmwiki.cc、ddsyasas/llm-wiki 的数据模型、Open Knowledge Format 的文件契约）。三层加两个保留文件：

```text
raw/      不可变来源层：原文 PDF、抽取文本、外部剪藏，只增不改
wiki/     role 维护的页面层：一页一文件，type 取 source/concept/entity/comparison/overview/idea
index.md  面向内容：全库页面目录，按 type 分组
log.md    面向时间：追加式流水，最新条目在最上面
```

- 页面：文件名即 slug，frontmatter 带 `title`、`slug`、`type`、`created`、`updated`、`sources`、`tags`；`idea` 页另有 `status`、`origin`、`test`。
- 链接：`[[slug]]`，指到某一节写 `[[slug#小节]]`；来源冲突加 `> [!contradiction]` callout，两说并存。
- 每跳写完更新 `index.md` 对应分组与 `log.md` 顶部，两条都是先读后改、增量更新。
- 记事与笔记互不搬：记事不写时间戳，知识笔记的时刻写在 frontmatter 与 `log.md` 里。

Obsidian 直接打开仓根，这套东西就是它的可视图层：frontmatter 进属性面板，wikilink 进图谱与反链，callout 直接渲染，`raw/` 与 `wiki/` 是普通文件夹。机器件全在点目录里，不进图谱；`.obsidian/` 的机器态（工作区布局、缓存、插件二进制）留本地不入 git。

## 角色树

拓扑定案后写入本节：role、边的方向、entry、模型位。机器真相是 `.onlyne/spec.toml` 与 `.onlyne/templates/alexandria/<role>/`；值班词汇见 `.agents/skills/onlyne-supervisor/SKILL.md`，role 协同纪律见 `.agents/skills/onlyne-role/SKILL.md`。

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
- pi 的 model/provider：`.onlyne/templates/alexandria/<role>/.pi/settings.json` 的三元组按拓扑定案填写。

## 装配与通电

自展开四步：定题 → 核拓扑与模型位 → 落分支 → 通电与第一发。仓根 `AGENTS.md` 就是那份共享目标记录——记事本写主线，支线开成 todo，材料走索引表；模板态和活态是同一份，装配时就地改它。下面是逐条细节。

起环的四条引导：

- 值班会话开在 `.supervisor/`，岗位说明在该目录的 `AGENTS.md`。
- 起环前先报前置缺什么（onlyne 五件套、pi 插件、会话后端），缺的东西由人装。
- 常驻进程（server、client、tui）一律起在可见 tab，不进 agent 后台。
- 定题没写完不落分支：让环空转没有意义。

### 装配

装配把模板填成一条 `theme/<slug>` 分支与一套可通电的拓扑。装配期间不启动集群，不跑实验。

1. **定题**。写目标记录 `.agents/AGENTS.md`（主线、判据、支线 todo、索引；它落分支后就是仓根 `AGENTS.md`），再写 `payload/first.md` 的第一发任务书（四段，口径见 `.onlyne/AGENTS.md`）。
2. **模型位**。逐 role 填 `.onlyne/templates/alexandria/<role>/.pi/settings.json` 的三元组。
3. **拓扑**。role 增删与边改 `.onlyne/spec.toml` 的 `[[client]]`，同步 `.onlyne/templates/alexandria/<role>/`。角色名的唯一事实源是模板目录名。prose 是身份与上报纪律，与 `.onlyne/AGENTS.md` 的角色表两处保持一致。ACL 铁律：A 的 `handoff B` 要求 B 条目 `allowed_senders` 含 A，且 A 条目 `allowed_targets` 含 B。
4. **装具**。跑上面「前置」的两条安装命令；缺 `npm:pi-onlyne` 时 `pi list` 会点出来。
5. **落分支**。装配器 `scripts/promote.sh`（九检加落分支）与拓扑、spec、模板同批落地；脚本到位前按同一顺序手工走：`git checkout -b theme/<slug>` → 把 `.agents/AGENTS.md` 提升为仓根 `AGENTS.md` → 写 `.onlyne/alexandria.json`（stage=live、theme、entry_role、roles）→ commit。

### 通电

通电一次性，由人执行，脚本不起任何常驻进程。

```bash
onlyne-server init --root . --listen 127.0.0.1:7812   # 产 .onlyne/keys/server.key；cert_pin 打到 stdout
# 把本仓的 .onlyne/spec.toml、.onlyne/templates/、.onlyne/AGENTS.md 放回 .onlyne/，回填 [server].cert_pin
onlyne-server generate --root .                        # 渲染 .onlyne/ws/alexandria/<role>/，逐 role 铸 key，stdout 打 [[client]] 行
# 把每行 key 粘回 spec.toml 对应的 [[client]]
onlyne server start --root .                           # detached+pid；判活看 socket_present
onlyne-client doctor                                   # 只读：宿主探测结果
# supervisor：在仓根开一个 agent 会话（pi、omp 都行），先读 .supervisor/AGENTS.md
onlyne client run --workspace .onlyne/ws/alexandria/<role>   # 每 role 一个 client，各占一个可见 tab
```

渲染进 ws 的 `AGENTS.md` 是模板骨架，之后由该 role 手记维护。重跑 `generate` 不带 `--force` 会拒绝覆盖已有 ws（退 4）；带 `--force` 则把记事换回骨架。

key 位在换真身前保持合法 32 字节 base64 占位（`AQEBAQ...AQE=`）。非法 key 会让全量 parse 连 `onlyne client init` 都跑不动。`[server].cert_pin` 在 `onlyne-server init` 之前保持字符串形态。

三个断电口径：`onlyne status` 的 `socket_present` 是 server 死活真相（`run` 不写 pid，`status.running` 只认 pid 文件；深层工作区再看 `.onlyne/run/socket`）；每个启用 role 在 `onlyne roles` 显示 connected 才算连上；ws 内 `.pi/settings.json` 的 packages 保持 `npm:pi-onlyne`。

daemon 类（`onlyne-server`、`onlyne-client`、`onlyne tui`）一律起在可见 tab，不进 agent 后台。`onlyne client run` 从目标 worktree 自己的 tab 起。

### 第一发

写 `payload/first.md`（四段），然后：

```bash
onlyne --server-root . send --from _supervisor --to <角色表 ★ 行的 role> --file payload/first.md
onlyne tui
```

第一发落地后环即成形：每跳自己定产物路径，下一跳任务书交给下一跳的 role。

## 动力源

第一颗 seed 由人给，写在仓根 `AGENTS.md` 的主线与 `payload/first.md`。之后每一跳自己产生下一跳任务书。

收束判据写在任务书里：判据满足即只 complete 不 handoff，环停在那一跳。人用 `onlyne control cancel --task <id>` 终结任务族，也可以在 TUI 里按终结键。

## 目录

```text
AGENTS.md                  共享目标记录：主线（目标与判据）、支线 todo、索引表
.onlyne/AGENTS.md          角色行为约定：一跳、任务书四段、记事纪律、工具面
.agents/AGENTS.md          共享目标的正本源，落分支的复制起点
.agents/skills/            onlyne-role（role 协同纪律）、onlyne-supervisor（值班词汇）、wiki-format（知识笔记格式正本）
.supervisor/AGENTS.md      supervisor 值班岗位说明（任意 harness 开在仓根，先读它）
第一发任务书：payload/；知识笔记的落点由任务书点名，不设统一目录
raw/                     不可变来源层（原文、抽取文本、剪藏）
wiki/                    页面层（一页一文件，type 六种）
index.md / log.md         两个保留文件：目录与流水
role 工作区：.onlyne/ws/alexandria/<role>/（运行时渲染，含该 role 的记事 AGENTS.md）
onlyne 侧（随拓扑落地）：.onlyne/spec.toml（拓扑真相）+ .onlyne/templates/alexandria/<role>/
装配器（随拓扑落地）：scripts/promote.sh
```

按论文组织精读页、按人组织提问这两类页面骨架随角色设计定案，定案后补进本节。
