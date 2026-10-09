# Alexandria —— 一个让 AI 帮你读论文、攒 idea 的 Obsidian 笔记库

## 这是什么：这个仓库是干什么的

这是一群 AI 助手分工干活的仓库：一个读论文、把结论写成笔记、把笔记连成知识网、把网上的缺口变成 idea 的流水线。它同时是一个 Obsidian vault——用 Obsidian 打开本仓库的根目录，就能直接看到笔记和它们连成的图谱。你给它一个研究方向，它给你：论文摘要页、精读报告、人物页、知识点页面。适合想系统读一批论文、又不想自己整理笔记的科研工作者。

## 三分钟看懂工作原理

```text
supervisor ──第一发──▶ scriber ──┬──▶ librarian ─┐
（人机界面，不进环）              └──▶ astrologer ─┴─▶ master ⇄ socrates ──▶ scraper
```

- **supervisor** 是人机界面：你把任务交给它，它把第一发任务派给链上的第一个助手。
- **scriber** 把论文原文收进库、写摘要页；需要补充资料就交给 **librarian**，需要人物画像就交给 **astrologer**。
- **master** 汇总资料写精读报告；**socrates** 装作一无所知的读者来挑报告的毛病，挑不出毛病才放行。
- **scraper** 把定稿报告拆成一条条知识点，回写进 `wiki/`，然后整条线收束。

「role」指链上的一个助手岗位，每个岗位有固定职责；「一跳」指一个助手接一个任务、干完、交给下一个助手的完整过程。任务像接力棒往前传，每跳都自己决定下一步交给谁，直到最后一跳判定完成。

## 第一次跑：从零起到环转起来

前置：装好 cargo（Rust）和 pi，且 pi 已配好模型。

1. 安装 onlyne 四件套（命令行、server、client、测试工具，一行装齐）：

   ```bash
   cargo install --locked --version 2.1.1 onlyne-cli onlyne-server onlyne-client onlyne-testkit
   ```

2. 安装 pi 插件（让助手会话里能用 onlyne 工具）：

   ```bash
   pi install npm:pi-onlyne@2.1.0
   ```

3. 仓库已带 `.onlyne/spec.toml`，而 `server init` 只接受空 spec。先把现有 spec 安全移到临时文件，再初始化，最后还原 spec。不要用 `--force`，它会覆盖仓库拓扑。先在同一个终端块执行：

   ```bash
   spec_backup="$(mktemp)"
   mv .onlyne/spec.toml "$spec_backup"
   onlyne server init --root . --listen 127.0.0.1:7812
   mv "$spec_backup" .onlyne/spec.toml
   ```

4. 把第 3 步打出的 cert_pin 回填进还原后的 `.onlyne/spec.toml` 的 `[server].cert_pin`。再逐个助手渲染工作区并铸钥匙。每次 stdout 打出 `[[client]]` 和真公钥。把每把公钥粘回 spec.toml 对应条目的 `key`：

   ```bash
   for r in scriber librarian astrologer master socrates scraper; do onlyne generate --root . --role "$r"; done
   ```

5. 起服务器：开一个终端 tab，进仓库根目录，跑（前台常驻，这个 tab 不再干别的）：

   ```bash
   onlyne server run --root .
   ```

6. 起客户端前先体检（确认本机的会话后端可用，输出里各项正常即通过）：

   ```bash
   onlyne client doctor
   ```

7. 每个助手各开一个可见 tab，进仓库根目录，跑（六个 tab 各跑一条）：

   ```bash
   onlyne client run --workspace ".onlyne/ws/scriber"
   onlyne client run --workspace ".onlyne/ws/librarian"
   onlyne client run --workspace ".onlyne/ws/astrologer"
   onlyne client run --workspace ".onlyne/ws/master"
   onlyne client run --workspace ".onlyne/ws/socrates"
   onlyne client run --workspace ".onlyne/ws/scraper"
   ```

8. 开一个 supervisor 会话（在仓库根，先读 `.supervisor/AGENTS.md`），把你的研究方向写成六段任务书存进 `tools/scratch/first-task.md`，用 `--file` 当场发给入口助手 scriber，命令模板见下面的「工作原理细节 · 第一发」。发完把这份文件删掉——任务书是瞬态的，仓里不留档。
9. 确认成功：`onlyne status --server-root .` 显示 server 活着；`onlyne roles` 里六个助手都显示 connected。之后想看运行现场，起一个可见 tab 跑 `onlyne tui --server-root .`。

到这里就可以用了。想弄懂每个词、想看全部运维细节，往下读。

## 日常使用：你可能会想做的事

- 看进度：`onlyne tui --server-root .` 打开三页交互板（集群/任务/故障）。
- 停或终结一条任务线：`onlyne control cancel --task <id> --reason <原因> --from _supervisor --force --yes-i-am-supervisor-not-other-role`，或在 TUI 的表单里终结。
- 停整个环：到 server 和各 client 的 tab 里按 Ctrl-C 停掉前台进程；这和终结一条任务线是两回事——上面那条只撤任务，进程照跑。
- 换研究主题：把新任务发给 supervisor 即可；持久目标写进仓根 `AGENTS.md`。
- 切换各助手的思考等级：`python3 tools/scripts/model-mode.py [preset]`，预设见 `tools/scripts/model-modes.json`。
- 出问题了：看下面的「排障」。

## 术语表

| 词 | 意思 |
|---|---|
| role | 链上的一个助手岗位，如 scriber、master |
| 一跳 | 一个 role 接任务、干活、交给下一个 role 的完整过程 |
| 任务书 | 一份六段式任务说明：目标、背景、输入、期望产物、自由度、下一跳建议 |
| handoff | 把下一跳任务交给下一个 role |
| frontmatter | md 文件开头的一段属性（title、sources 等），Obsidian 显示为属性面板 |

## 工作原理细节（想深入再读）

### 注入面与手帐面：文件怎么分工、谁能改

|文件|面|装什么|谁能改|
|---|---|---|---|
|仓根 `AGENTS.md`|注入面|目标与判据、持久索引表、指向 `STATE.md` 的指针|环上每个 role 都能改|
|仓根 `STATE.md`|手帐面|主线进度、支线 todo|环上每个 role 与 supervisor 都能改|
|`.onlyne/AGENTS.md`|注入面|角色行为约定：一跳、任务书六段、记事纪律、工具面|模板定稿，运行期只读|
|`.onlyne/ws/<role>/AGENTS.md`|注入面|该 role 的岗位口径与自检清单、指向 ws `STATE.md` 的指针|只有该 role 自己写|
|`.onlyne/ws/<role>/STATE.md`|手帐面|该 role 的过程记录与本 role 索引|只有该 role 自己写|

三份 `AGENTS.md` 都在 role 工作区的父目录链上，pi 在每个 session 启动时按外层到内层自动叠加：全局 `~/.pi/agent/AGENTS.md` → 仓根 `AGENTS.md` → `.onlyne/AGENTS.md` → 该 role 的 ws `AGENTS.md`。`STATE.md` 不在这条链上，谁要用谁 read。role 的工作区固定在自己的 `.onlyne/ws/<role>/` 目录下。

产物不设统一目录与固定格式：每一跳要交出的文件由该跳的任务书点名路径。工作文件各写各的，或者就地改同一份，由任务性质定。

### 记事纪律：助手记笔记要守什么规矩

正本在 `.onlyne/AGENTS.md`。要点：注入面不留手帐，`AGENTS.md` 链每轮整份进 prompt，一改就打掉前缀缓存；一份 `STATE.md` 分记叙段与条目段，分开摆；索引条目原位写标题（讲清这件事是什么）；索引不递归；不用字母加数字的缩记号指代条目；记事与账目用 `edit` 工具手记，第一人称自言自语，禁止脚本生成；修订时就地覆盖原条目，同一个意思只留一处；不写时间戳；todo 即删——列表只登进行中的事，不打完成标记，办完当场删条；任务族收敛时 scraper 兜底清仓根 `STATE.md` 的本族 todo，各 role 的 ws `STATE.md` 同一规矩。

### 一跳的生命周期：一个任务从接到交出经过哪些步

1. 任务书到 role 手上：注入头一行写明来源 role 与任务号，正文与随附路径跟在后面。
2. 读六段点名的输入路径。
3. 干活，产物落任务书点名的路径。
4. 下一跳写六段任务书，`onlyne_handoff` 交给下一跳的 role（`parent_task` 与 hop+1 血缘自动落账）。
5. `onlyne_complete` 交活：`summary` 一行放结果与产物路径；承重结论进 `details` 或 `files` 指到的产物。

常态是跑完整条线：一跳干完就 handoff 下一跳，直到 scraper 收束。中途停只有一种合法理由：任务书显式写明「一跳即止」——那时只 complete 不 handoff。收束判定权在 socrates，别的 role 不自断去路。

session 的服务范围由 ws `config.toml` 的 `[client.session] scope` 决定：`oneshot`（默认）一发一 session，交付即关；`task`/`role` 让 session 活过一次交付。本环默认 oneshot。

### 任务书六段：一份任务说明要写哪六块

```text
目标：<一句话，做完算什么>
背景：<为什么做这件事：上游发现了什么、卡在哪、这个任务在整体里处于什么位置；两三句；没有就写 无>
输入：<必须读的路径，一条一行，括号里写清这份文件是什么；接收方是全新上下文，没点的路径它找不到>
期望产物：<写到哪里的什么文件，格式要求>
自由度：<除点名产物外鼓励顺手做什么：补检索、修断链、记负证据、建索引页；或写 按角色表惯例>
下一跳建议：<完成后用 onlyne_handoff 交给谁、干什么；没有就写 无>
```

输入路径必须真实存在。内容按引用交接：text 里给路径与标题，接收方读文件；工作区字节从不上总线。

### 笔记格式：llmwiki 怎么组织 raw、papers、people、wiki 四层

本仓的 md 笔记按 llmwiki 格式写。正本在 `.agents/skills/wiki-format/SKILL.md`；格式源是 Karpathy 的 LLM Wiki pattern 与它的开源实现（llmwiki.cc、ddsyasas/llm-wiki 的数据模型、Open Knowledge Format 的文件契约）。资源层两棵树加知识层，零记录文件：

```text
raw/      不可变来源层：原文 PDF、抽取文本、网页快照、剪藏，只增不改
papers/   论文层：摘要、增强、精读，一页一论文
blogs/    博客层：与论文层同构，一页一文章
people/   人物层：一个学者一个文件
wiki/     role 维护的页面层：一页一文件，子目录按知识层级组织
（仓根无知识记录文件：流水归 ledger 与 frontmatter）
```

- 拆碎：一个知识点一个文件；同一知识点合并进单个文件；主题长大开成子目录，层级由目录路径表达，目录改名合并拆分随时可做。
- 分层：`raw/` 存资源本体——凡检索与引证里过手的每篇论文、每篇文章都归档，一目录一资源，不只任务目标那份（拉下来的资料本身就是资料，先收进来越滚越厚）；`papers/` 与 `blogs/` 两棵树同构：`abstracts/` 与 `readings/` 存摘要与精读，`people/` 存人物，`wiki/` 只存从资源拆出来的知识点。各层不互相搬内容，层间只放链接。
- 检索路径：agent 从 `papers/abstracts/`（或 `blogs/abstracts/`）找到资源，沿摘要页的 `resource:` 取本体，沿摘要页的链接取精读页。
- 属性：节点属性只写 frontmatter 行（`title`/`slug`/`type`/`created`/`updated`/`sources`，`idea` 页另有 `status`/`origin`/`test`）；`tags` 非要求不写。
- 关联：一条链只表达一种真实关系（依赖、对比、反驳、同源、同一机制），写不出关系名的链不建；同域相邻知识点沿真实关系互链；来源冲突加 `> [!contradiction]`，两说并存。
- 每跳写完不记流水：任务书与回执逐帧在 ledger，时刻在页面 frontmatter；导航靠目录层级与图谱，不维护全库目录页（根 `index.md` 会在图谱里造出无用的超级节点）。
- 资源层页面在主 slug 上挂种类后缀：`<slug>-abstract.md`、`<slug>-context.md` 平铺，`<slug>-reading.md` 是唯一例外——路径与 `raw/` 同构（论文 `<YYYY-MM>/<学科>/<刊名>/`，博客 `<YYYY-MM>/<领域>/<站点>/`），人最终读的是精读报告，不能摊成一堆噪音。frontmatter 带 `resource:` 指向本体目录；精读页里的概念另建 `wiki/` 页面。
- 图与媒体只进资源本体目录的 `assets/`，页面用 `![[…]]` 按相对仓根路径引用，不复制图；绘图脚本落 `tools/scripts/`。
- 引用总律=可擦性：报告是连贯的文章，读者从头到尾不必打开第二个文件——正文记号擦掉不减句义，承载理解的引用在句中兑现（整段嵌入或归纳转述）；剩下的溯源记号须就地可兑现：外指他文冠名（「《论文名》§3.2.1」），内指对得上本页真标题；裸编号、点不开的链接、抽取文本行号一律悬空，禁入正文。图与表格豁免：嵌页图与自绘表格就是页面自身的内容，可存可引。
- 知识点与资源的错配不建映射表：知识点由资源拆出，链接与 `sources` 就是溯源。
- 记事与笔记互不搬：记事不写时间戳，知识笔记的时刻只写在 frontmatter。

Obsidian 直接打开仓根，这套东西就是它的可视图层：frontmatter 进属性面板，wikilink 进图谱与反链，callout 直接渲染，`raw/` 与 `wiki/` 是普通文件夹。机器件全在点目录里，不进图谱；`.obsidian/` 的机器态（工作区布局、缓存、插件二进制）留本地不入 git。

### 工作流细节：六个 role 之间的交接与放行规则

- 入口是 scriber，第一发由 supervisor 投递。astrologer 是可选路径，任务书点名才走；不点名时 scriber 以一条 note 把对 astrologer 的交付义务了结。
- master⇄socrates 的放行权在 socrates：报告收束由 socrates 判定并放行给 scraper，master 只回改。socrates 不带先验（残差流也不读），当一无所知的普通读者；放行判据=自足性——摘掉全部外链，报告仍连贯、能被没读过相关文献的人看懂个七七八八。socrates 的 `allowed_targets` 含 master 与 scraper：修订轮 handoff 回 master 后它不 complete（义务未清会被拒），判放行交 scraper 后再报终态。
- 残差流：线性链上后面的人看见前面所有人的产出。每次 handoff 由交出方构造产物索引（本任务族到目前的所有路径，一跳一行），接收方先读残差流再动手。口径见 `.onlyne/AGENTS.md`。
- scriber 与 master 每任务族单例，librarian、astrologer、socrates、scraper 可多播。单例是软约束，spec 不设并发闸。
- 主线与支线：任务书是主线，必须交出；主线之外每个 role 自由做支线（多跑检索、补断链、建概念页/人物页、拆碎回写、做体检），支线越多库越强。硬约束只一条——主线那跳别停在手上没 handoff/complete。口径见 `.onlyne/AGENTS.md`。
- 机器真相是 `.onlyne/spec.toml` 与 `.onlyne/templates/<role>/`；值班词汇见 `.agents/skills/onlyne-supervisor/SKILL.md`，role 协同纪律见 `.agents/skills/onlyne-role/SKILL.md`。
- 角色细则随流程演进：改 prose 与职责时同步改 `.onlyne/spec.toml`、`.onlyne/AGENTS.md` 角色表与本文件工作流节，三处一处不落。

思考等级位（各 role `.pi/settings.json` 的 `defaultThinkingLevel`）按预设整批切换，命令与预设见「日常使用」。模型与 provider 不由本仓指定：pi 用操作者机器上配置好的默认值。现有两档：

- **balanced**（分析位吃高思考、检索降低、快扫与粗判最低）：scriber low｜librarian high｜astrologer low｜master medium｜socrates max｜scraper medium。socrates 是故意的反配：读者立场越无知，嘴越便宜，思考给得越满。
- **fast**（速度优先：全员最低够用）：scriber low｜librarian medium｜astrologer low｜master medium｜socrates max｜scraper low。

要加新档（如质量档）只改 JSON，脚本不用动。

角色职责与产物一览（新手层图上的解释以此为准）：

|role|职责|产物|
|---|---|---|
|scriber ★|入口。原文整理进 `raw/`（文本与图都抽，图进 `assets/`），写摘要页；大批量快扫相关文献补前提背景|`papers/abstracts/<paper>-abstract.md`、`papers/context/<paper>-context.md`（博客资源走 `blogs/`，树同构）|
|librarian|资料搜集，出资源增强信息|`papers/context/<paper>-context.md`（博客资源走 `blogs/context/`）|
|astrologer|人物画像构建，可选路径|`people/<slug>.md`|
|master|汇总资料，写精读报告，需要时做 ppt；嵌原文图，必要时自绘图|`papers/readings/<YYYY-MM>/<学科>/<刊名>/<paper>-reading.md`、`papers/decks/<slug>/`（博客资源走 `blogs/`，树同构）|
|socrates|以「我一无所知」的视角对质——只读精读报告本体、不读残差流，验收自足性；循环的放行者；必要时看图核对|对质清单、放行决定|
|scraper|把定稿报告里的知识点拆碎回写 `wiki/`；收敛时清仓根 `STATE.md` 的本族 todo，落点登进仓根 `AGENTS.md` 索引表|`wiki/` 页面|

### 前置与运行时检查：版本基线和运行时要核对什么

Onlyne 发布基线为 2.1.1，协议 1。兼容判据是 `onlyne version` 的 `protocol:1`；npm 插件基线为 `pi-onlyne@2.1.0`。

- crate `onlyne-cli` 装出的 bin 叫 `onlyne`，其余同名。升级＝同一条安装命令加 `--force` 重跑。没有独立 `onlyne-tui` 二进制：TUI 是 `onlyne tui` 动词，在本进程跑。
- 要跟 onlyne 仓 main 上尚未发布的 fix：clone 该仓后 `cargo build --release`，产物放进 PATH（`onlyne`、`onlyne-server`、`onlyne-client`；`onlyne-agent-fake` 由 testkit 源码构建）。装二进制优先走发布渠道：registry install、Homebrew tap 或 `packaging/install.sh`，它们都带校验。
- pi 的模型/provider：本仓不指定。每个 role 只定 `defaultThinkingLevel`，模型用操作者机器上 pi 已配置好的默认值。
- 会话后端（placement）：写在 role ws 的 `config.toml`，取值 `orca | zellij | tern | headless | external`。选择链是 `ONLYNE_BACKEND`（非空）> 工作区 `config.toml` 的 `placement` > 探测（tern → orca → zellij，全无落 headless）。`exec`/`fake` 只在显式写出其名时启用。全无匹配时 `onlyne client run` 退 5。
- 角色续家族使用插件 `onlyne_handoff`；家族元信息为 `family`、`hop_budget`、`origin`、`deadline`、`labels`。超预算的 handoff 在子任务铸造前被拒。
- `send`、`reply`、`handoff`、`complete`、`ack`、`reject`、`control` 七个 shell 动词需要 `--force --yes-i-am-supervisor-not-other-role`。缺 flag 时退出码为 2，socket 不会被打开。
- `[server].requeue_ttl_secs` 为 `0` 时保持默认排队；正数会让自动重投的行到期落 `expired`，`reason=requeue_ttl`（这口钟也够得着 `_supervisor` 收件箱）。
- TUI：`onlyne tui --server-root <root>` 三页交互板（集群/任务/故障）；`onlyne tui --server-root <root> --once` 打一帧 cluster 页文本退出。
- 交付义务：`allowed_targets` 除 origin 外的每个下游 role，报终态前必须交付过一跳（note 也算）。义务未清的 complete 被拒，拒绝句列出欠谁、已交谁。
- store 版标：server `state.db` revision 6，client `client.db` revision 3；版本不符退 6，无 `migrate` 命令。

### 通电与第一发：怎么启动服务器、铸造密钥、发出第一个任务

本工作区流程固定：角色、边、目录、笔记格式都定死在仓里，没有装配步骤，没有模板态与活态之分。目标与判据、持久索引表留在仓根 `AGENTS.md`；主线进度与支线 todo 写进仓根 `STATE.md`，要改就地改。

唯一随部署变化的是 role 参数：每个 role 的思考等级写在 `.onlyne/templates/<role>/.pi/settings.json`，模型/provider 用操作者自己的 pi 默认值。改完 `onlyne reload --server-root .` 生效，其余一概不动。模板按 `templates/<role>/` 平铺放（`ClientEntry` 无 `template` 字段，`generate` 只按 `template_root/<role>` 找）。

起环的四条引导：

- supervisor 会话开在仓根，岗位说明在 `.supervisor/AGENTS.md`。
- 起环前先报前置缺什么（onlyne 四件套、pi 插件、会话后端），缺的东西由人装。
- 常驻进程（server、client）一律起在可见 tab，不进 agent 后台。
- 主线没写完不起环：让环空转没有意义。

通电一次性，由人执行，脚本不起任何常驻进程（完整命令块见上面「第一次跑」第 3–7 步）。放置还可以按 role 写进各自 ws 的 `config.toml`（`placement = "orca"` 等），这样 client run 不用带 `ONLYNE_BACKEND`。缺省探测 tern → orca → zellij，都没有落 headless。

渲染进 ws 的 `AGENTS.md` 是模板骨架，只含岗位口径与指向 ws `STATE.md` 的指针行。重跑 `generate` 不带 `--force` 会拒绝覆盖已有 ws（退 4）；带 `--force` 则把注入面换回骨架。

key 位在换真身前保持合法 32 字节 base64 占位（`AQEBAQ...AQE=`，32 字节全 0x01）。非法 key 会让全量 parse 连 `onlyne client init` 都跑不动。`[server].cert_pin` 是占位（32 个零字节的 sha256 值）；**部署必须跑 `onlyne server init` 铸自己的服务器密钥对，并回填 init 打出的真 cert_pin；各 role 的 key 同理在 generate 时铸真身**——本仓跟踪的只是合法占位，不是任何人的真身份。

三个断电口径：`onlyne status --server-root .` 是 server 死活真相（run 前台跑，不写 pid 文件）；每个启用 role 在 `onlyne roles` 显示 connected 才算连上；ws 内 `.pi/settings.json` 的 packages 保持 `npm:pi-onlyne@2.1.0`。

daemon 类（`onlyne server run`、`onlyne client run`）一律起在可见 tab，不进 agent 后台。`onlyne client run` 从目标 worktree 自己的 tab 起。

#### 搬家：把整个仓库移到别的路径要做什么

仓可以整体 `mv` 到任何位置，机器层路径无关：spec、模板、文档、知识页一律用仓根相对路径（写进仓的绝对路径是缺陷，见 `.onlyne/AGENTS.md` 路径条款）。搬家步骤：停 server 与各 role client 的可见 tab → `mv` → 在新路径按「通电」重起。`cert_pin` 与 role key 绑密钥对不绑路径，零改动。运行时的一次性现场不用管：机器层 runtime 目录里的 socket 注册、ws 缓存里的会话记录、`.pi/sessions/` 与 `state.db` 里带旧路径的历史行，重启后各自自愈或留作旧账，都不是真身。

#### 第一发：发给入口助手的第一个任务书怎么写

任务书不存档，交接是瞬态。第一发由人把六段任务书写进 `tools/scratch/first-task.md`，再用 `--file` 发出（六段口径见 `.onlyne/AGENTS.md`）：

先把下面这份写到 `tools/scratch/first-task.md`（照抄六段标题，尖括号里换成你的内容）：

```text
目标：<一句话，做完算什么>
背景：<为什么做这件事；没有就写 无>
输入：<一条一行：路径（这份文件是什么）>
期望产物：<写到哪里的什么文件，格式要求>
自由度：<顺手做什么；没有就写 按角色表惯例>
下一跳建议：<handoff 谁、干什么；没有就写 无>
```

然后发出（两个身份 flag 一个都不能少）：

```bash
onlyne --server-root . send --from _supervisor --to <角色表 ★ 行的 role> --force --yes-i-am-supervisor-not-other-role --file tools/scratch/first-task.md
onlyne tui --server-root .
```

发完即删 `tools/scratch/first-task.md`——任务书是瞬态交接面，用完即弃。仓里没有任务书存档目录，也没有流水文件：过程与结论写在各 role 自己的 ws `STATE.md` 里，机器账在 ledger。

`send`、`reply`、`handoff`、`complete`、`ack`、`reject`、`control` 这七个动词是 supervisor 维护面：命令行调用必须同时带 `--force` 与 `--yes-i-am-supervisor-not-other-role`，缺一个即拒，提示指向 role 该走的插件工具（`onlyne_send` / `onlyne_handoff` / `onlyne_complete`）。role 在会话内一律走插件，不走 bash。

第一发落地后环即成形：每跳自己定产物路径，下一跳任务书交给下一跳的 role。

### 动力源：环靠什么持续运转、怎么收束

第一颗 seed 由人给，主线目标写在仓根 `AGENTS.md`，第一发任务书经 `tools/scratch/first-task.md` 以 `--file` 当场传给角色，传完即删。之后每一跳自己产生下一跳任务书。

收束判据写在任务书里：判据满足即只 complete 不 handoff，环停在那一跳。人用 `onlyne control cancel --task <id> --reason <原因> --from _supervisor --force --yes-i-am-supervisor-not-other-role` 终结任务族，也可以在 TUI 的表单里终结（admin 面的动词都要 `--from _supervisor`，control 与 send 一样）。

## 排障：出问题了先看哪里

（原 README 无排障表；常见故障信号散见上文：server 死活看 `onlyne status --server-root .`，role 连接看 `onlyne roles`，store 版标不符退 6，key 非法导致 parse 不动，placement 全无匹配退 5，`generate` 重复跑退 4。）

## 目录结构

```text
AGENTS.md                  注入面：目标与判据、持久索引表、指向 STATE.md 的指针
STATE.md                   手帐面：主线进度、支线 todo
STRUCTURE.md               目录结构与外部集群接入口径（别的集群当知识库用，读这一份）
.onlyne/AGENTS.md          角色行为约定：角色表、残差流、一跳、任务书六段、记事纪律、工具面
.agents/skills/            wiki-format（知识笔记格式正本）、paper-sources（论文与人物情报渠道目录）、scientist-profiles（人物画像协议）、onlyne-role（role 协同纪律）、onlyne-supervisor（值班词汇）
.supervisor/AGENTS.md      supervisor 值班岗位说明（supervisor 会话开在仓根，先读它）
.supervisor/STATE.md       supervisor 手帐面：值班过程记录
知识笔记的落点由任务书点名，不设统一目录；任务书本身不存档
raw/                     不可变来源层：论文 <年月>/<学科>/<刊名>/<论文名>/、博客 <年月>/<领域>/<站点>/<slug>/，一目录一资源；零散来源平铺
  <资源目录>/assets/      该资源的图与媒体：抽取的图、自绘的图
papers/abstracts/<paper>-abstract.md           论文摘要页（兼身份页），平铺
papers/context/<paper>-context.md              论文增强信息页（librarian），平铺
papers/readings/<YYYY-MM>/<学科>/<刊名>/<paper>-reading.md  论文精读报告（master），路径与 raw 同构
papers/decks/<slug>/        演示产物（master，需要时）
blogs/    博客层：与论文层同构（abstracts/ context/ readings/ decks/，路径口径见 wiki-format 命名节）
people/   人物层：一个学者一个文件（协议见 scientist-profiles）
wiki/     知识层：被打碎的知识点，子目录按知识层级组织，一页一知识点
tools/scripts/           脚本与工具（随树跟踪）
tools/scratch/           临时文件（不入 git）
（仓根无知识记录文件：流水归 ledger 与 frontmatter）
role 工作区：.onlyne/ws/<role>/（运行时渲染，含 AGENTS.md 岗位口径与 STATE.md 手帐）
onlyne 侧：.onlyne/spec.toml（拓扑真相）+ .onlyne/templates/<role>/（岗位骨架与思考等级）
```
