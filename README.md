# Alexandria —— 读论文、找 idea 的工作区

本工作区辅助学生与科研工作者读论文、找 idea：role 读论文，把结论写成笔记，笔记连成图，图上的缺口变成 idea。

人只和 supervisor 对话。问题由 supervisor 直接答（从 `papers/abstracts/`、`wiki/` 与 Obsidian 图谱找页、读页、按 `sources` 引数），答完值得留的直接落成页面；需要新采集、新精读、补链的，写成四段任务书派给 role。岗位说明在 `.supervisor/AGENTS.md`。

仓根本身就是一个 Obsidian vault，同时是一个 llmwiki bundle：Obsidian 打开仓根，role 写下的知识笔记就是 vault 里的笔记，`raw/`、`papers/`、`people/`、`wiki/` 是笔记的四层。仓根不放任何记录文件——流水归 onlyne ledger 与页面 frontmatter，过程归各 role 的 ws 记事。机器件都在点目录里（`.onlyne/`、`.pi/`、`.agents/`、`.supervisor/`），Obsidian 不进点目录，图谱与搜索里只有笔记。

运行框架是最简形状的 onlyne 环：三层记事、任务书四段、射后不理、ledger 记账。角色与边的设计在下一步，落点见下面「角色树」一节。

两个词先说清：workspace 表示一个 role 的长期工作区，里面有记忆、设定、历史文件；session 表示这个 role 当前手上的一件工作。任务、session、一跳是一回事。

工作按「射后不理」进行：读任务书 → 干活 → 产物落任务书点名的路径 → handoff 下一跳 → `onlyne_complete` 交活退出。role 不等下游。投递后立即返回一行 receipt JSON。过程与回执写进 server ledger，结果通过文件返回。

## 三层文件

|文件|装什么|谁能改|
|---|---|---|
|仓根 `AGENTS.md`|共享目标记录：记叙段是主线（目标与判据），条目段是支线 todo 与索引表|环上每个 role 都能改|
|`.onlyne/AGENTS.md`|角色行为约定：一跳、任务书四段、记事纪律、工具面|模板定稿，运行期只读|
|`.onlyne/ws/<role>/AGENTS.md`|该 role 的私有记事：记叙段写过程，条目段写索引表|只有该 role 自己写|

三层都在 role 工作区的父目录链上，pi 在每个 session 启动时按外层到内层自动叠加：全局 `~/.pi/agent/AGENTS.md` → 仓根 `AGENTS.md` → `.onlyne/AGENTS.md` → 该 role 的 ws `AGENTS.md`。role 的工作区固定在自己的 `.onlyne/ws/<role>/` 目录下。

产物不设统一目录与固定格式：每一跳要交出的文件由该跳的任务书点名路径。工作文件各写各的，或者就地改同一份，由任务性质定。

## 记事纪律

正本在 `.onlyne/AGENTS.md`。要点：一份 AGENTS.md 分记叙段与条目段，分开摆；索引条目原位写标题（讲清这件事是什么）；索引不递归；不用字母加数字的缩记号指代条目；记事与账目用 `edit` 工具手记，第一人称自言自语，禁止脚本生成；修订规则时就地覆盖原条目，同一个意思只留一处；不写时间戳；todo 即删——列表只登进行中的事，不打完成标记，办完当场删条；任务族收敛时 scraper 兜底清仓根本族条目，各 role 的 ws 手帐同一规矩。

## 一跳的生命周期

1. 任务书到 role 手上：`[onlyne] task <task-id> from role:<sender> (kind task)`。
2. 读四段点名的输入路径。
3. 干活，产物落任务书点名的路径。
4. 下一跳写四段任务书，handoff 交给下一跳的 role（`parent_task` 与 hop+1 血缘自动落账）。
5. `onlyne_complete`：text 一行放结果与产物路径。

常态是跑完整条线：一跳干完就 handoff 下一跳，直到 scraper 收束。中途停只有一种合法理由：任务书显式写明「一跳即止」——那时只 complete 不 handoff。收束判定权在 socrates，别的 role 不自断去路。

## 任务书四段

```text
目标：<一句话，做完算什么>
输入：<一条一行：「路径」（括号里原位写清这份文件是什么）>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<handoff 谁、干什么；没有就写 无>
```

输入路径必须真实存在，接收方 session 是全新上下文，任务书里没写的路径它找不到。内容按引用交接：text 里给路径与标题，接收方读文件；工作区字节从不上总线。

## 笔记格式（llmwiki）

本仓的 md 笔记按 llmwiki 格式写。正本在 `.agents/skills/wiki-format/SKILL.md`；格式源是 Karpathy 的 LLM Wiki pattern 与它的开源实现（llmwiki.cc、ddsyasas/llm-wiki 的数据模型、Open Knowledge Format 的文件契约）。资源层两棵树加知识层，零记录文件：

```text
raw/      不可变来源层：原文 PDF、抽取文本、网页快照、剪藏，只增不改
papers/   论文层：摘要、增强、精读，一页一论文
blogs/    博客层：与论文层同构，一页一文章
people/   人物层：一个学者一个文件
wiki/     role 维护的页面层：一页一文件，子目录按知识层级组织
（仓根无记录文件：流水归 ledger 与 frontmatter）
```

- 拆碎：一个知识点一个文件；同一知识点合并进单个文件；主题长大开成子目录，层级由目录路径表达，目录改名合并拆分随时可做。
- 分层：`raw/` 存资源本体——凡检索与引证里过手的每篇论文、每篇文章都归档，一目录一资源，不只任务目标那份（拉下来的资料本身就是资料，先收进来越滚越厚）；`papers/` 与 `blogs/` 两棵树同构：`abstracts/` 与 `readings/` 存摘要与精读，`people/` 存人物，`wiki/` 只存从资源拆出来的知识点。各层不互相搬内容，层间只放链接。
- 检索路径：agent 从 `papers/abstracts/`（或 `blogs/abstracts/`）找到资源，沿摘要页的 `resource:` 取本体，沿摘要页的链接取精读页。
- 属性：节点属性只写 frontmatter 行（`title`/`slug`/`type`/`created`/`updated`/`sources`，`idea` 页另有 `status`/`origin`/`test`）；`tags` 非要求不写。
- 关联：一条链只表达一种真实关系（依赖、对比、反驳、同源、同一机制），写不出关系名的链不建；同域相邻知识点沿真实关系互链；来源冲突加 `> [!contradiction]`，两说并存。
- 每跳写完不记流水：任务书与回执逐帧在 ledger，时刻在页面 frontmatter；导航靠目录层级与图谱，不维护全库目录页（根 `index.md` 会在图谱里造出无用的超级节点）。
- 资源层页面在主 slug 上挂种类后缀：`<slug>-abstract.md`、`<slug>-context.md` 平铺，`<slug>-reading.md` 是唯一例外——路径与 `raw/` 同构（论文 `<YYYY-MM>/<学科>/<刊名>/`，博客 `<YYYY-MM>/<领域>/<站点>/`），人最终读的是精读报告，不能摊成一堆噪音。frontmatter 带 `resource:` 指向本体目录；精读页里的概念另建 `wiki/` 页面。
- 图与媒体只进资源本体目录的 `assets/`，页面用 `![[…]]` 按相对仓根路径引用，不复制图；绘图脚本落 `tools/scripts/`。
- 引用总律=可擦性：报告是连贯的文章，读者从头到尾不必打开第二个文件——正文记号擦掉不减句义，承载理解的引用在句中兑现（整段嵌入或归纳转述）；剩下的溯源记号须就地可兑现：外指他文冠名（「《DeepSeek-V4》§3.2.1」），内指对得上本页真标题；裸编号、点不开的链接、抽取文本行号一律悬空，禁入正文。图与表格豁免：嵌页图与自绘表格就是页面自身的内容，可存可引。
- 知识点与资源的错配不建映射表：知识点由资源拆出，链接与 `sources` 就是溯源。
- 记事与笔记互不搬：记事不写时间戳，知识笔记的时刻只写在 frontmatter。

Obsidian 直接打开仓根，这套东西就是它的可视图层：frontmatter 进属性面板，wikilink 进图谱与反链，callout 直接渲染，`raw/` 与 `wiki/` 是普通文件夹。机器件全在点目录里，不进图谱；`.obsidian/` 的机器态（工作区布局、缓存、插件二进制）留本地不入 git。

## 工作流（deep research 线性链）

本工作区不成环，一条 deep research 工作流走到底，scraper 收敛：

```text
supervisor ──第一发──▶ scriber ──┬──▶ librarian ─┐
（人机界面，不进环）              └──▶ astrologer ─┴─▶ master ⇄ socrates ──▶ scraper
```

|role|职责|产物|
|---|---|---|
|scriber ★|入口。原文整理进 `raw/`（文本与图都抽，图进 `assets/`），写摘要页；大批量快扫相关文献补前提背景|`papers/abstracts/<paper>-abstract.md`、`papers/context/<paper>-context.md`（博客资源走 `blogs/`，树同构）|
|librarian|资料搜集，出资源增强信息|`papers/context/<paper>-context.md`（博客资源走 `blogs/context/`）|
|astrologer|人物画像构建，可选路径|`people/<slug>.md`|
|master|汇总资料，写精读报告，需要时做 ppt；嵌原文图，必要时自绘图|`papers/readings/<YYYY-MM>/<学科>/<刊名>/<paper>-reading.md`、`papers/decks/<slug>/`（博客资源走 `blogs/`，树同构）|
|socrates|以「我一无所知」的视角对质——只读精读报告本体、不读残差流，验收自足性；循环的放行者；必要时看图核对|对质清单、放行决定|
|scraper|把定稿报告里的知识点拆碎回写 `wiki/`；收敛时清仓根 `AGENTS.md` 的本族 todo|`wiki/` 页面|

模型位（`<role>/.pi/settings.json` 三元组，provider 全 axonhub）按预设整批切换：`python3 tools/scripts/model-mode.py [preset]`，预设表在 `tools/scripts/model-modes.json`（双写模板与活 ws，新 session 生效，在飞会话不动）。现有两档：

- **balanced**（分析位吃 powerful、检索降 weak、快扫与粗判 supercheap）：scriber supercheap/low｜librarian weak/high｜astrologer supercheap/low｜master powerful/medium｜socrates supercheap/max｜scraper supercheap/medium。socrates 是故意的反配：supercheap/max，大智若愚——读者立场越无知，嘴越便宜，思考给得越满。
- **fast**（速度优先：全员 supercheap，思考等级只按任务需要给）：scriber low｜librarian medium｜astrologer low｜master medium｜socrates max｜scraper low。

要加新档（如质量档）只改 JSON，脚本不用动。

- 入口是 scriber，第一发由 supervisor 投递。astrologer 是可选路径，任务书点名才走。
- master⇄socrates 的放行权在 socrates：报告收束由 socrates 判定并放行给 scraper，master 只回改。socrates 不带先验（残差流也不读），当一无所知的普通读者；放行判据=自足性——摘掉全部外链，报告仍连贯、能被没读过相关文献的人看懂个七七八八。
- 残差流：线性链上后面的人看见前面所有人的产出。每次 handoff 由交出方构造产物索引（本任务族到目前的所有路径，一跳一行），接收方先读残差流再动手。口径见 `.onlyne/AGENTS.md`。
- scriber 与 master 每任务族单例，librarian、astrologer、socrates、scraper 可多播。单例是软约束，spec 不设并发闸。
- 主线与支线：任务书是主线，必须交出；主线之外每个 role 自由做支线（多跑检索、补断链、建概念页/人物页、拆碎回写、做体检），支线越多库越强。硬约束只一条——主线那跳别停在手上没 handoff/complete。口径见 `.onlyne/AGENTS.md`。
- 机器真相是 `.onlyne/spec.toml` 与 `.onlyne/templates/<role>/`；值班词汇见 `.agents/skills/onlyne-supervisor/SKILL.md`，role 协同纪律见 `.agents/skills/onlyne-role/SKILL.md`。

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
- pi 的 model/provider：每个 role 的模型三元组在 `.onlyne/templates/<role>/.pi/settings.json`，随部署改，改完 reload。

## 通电与第一发

本工作区流程固定：角色、边、目录、笔记格式都定死在仓里，没有装配步骤，没有模板态与活态之分。仓根 `AGENTS.md` 就是那份共享目标记录——记事本写主线，支线开成 todo，材料走索引表，要改就地改。

唯一随部署变化的是 role 参数：每个 role 的 model/provider/thinking 三元组写在 `.onlyne/templates/<role>/.pi/settings.json`，改完 `onlyne reload --server-root .` 生效，其余一概不动。模板按 `templates/<role>/` 平铺放（`ClientEntry` 无 `template` 字段，`generate` 只按 `template_root/<role>` 找）。

起环的四条引导：

- supervisor 会话开在仓根，岗位说明在 `.supervisor/AGENTS.md`；omp 开这个会话时 `.omp/AGENTS.md` 自动带上这句话。
- 起环前先报前置缺什么（onlyne 五件套、pi 插件、会话后端），缺的东西由人装。
- 常驻进程（server、client、tui）一律起在可见 tab，不进 agent 后台。
- 主线没写完不起环：让环空转没有意义。

### 通电

通电一次性，由人执行，脚本不起任何常驻进程。

```bash
onlyne-server init --root . --listen 127.0.0.1:7812    # 产 keys/server.key，cert_pin 打到 stdout；已放 spec.toml 则 init 拒绝覆盖，先挪开再放回并回填 cert_pin
# 回填 [server].cert_pin；模板须按 templates/<role>/ 平铺
# 逐 role 渲染并铸 key：bare generate 会为无模板的 _supervisor 报错，用 --role 限定 6 个 agent
for r in scriber librarian astrologer master socrates scraper; do onlyne-server generate --root . --role "$r"; done
#   每次 stdout 打 [[client]] 带真 pub key，粘回 spec.toml 对应 [[client]].key
onlyne server start --root .                            # detached；判活用 onlyne status --server-root .（status 不认 --root）
# supervisor 在仓根开 omp 会话读 .supervisor/AGENTS.md（.omp/AGENTS.md 自动提示）；运维观察起可见 tab：onlyne tui --server-root <abs>
ONLYNE_BACKEND=orca onlyne client run --workspace .onlyne/ws/<role>   # 每 role 一个 client，pi 开在可见 orca tab
```

渲染进 ws 的 `AGENTS.md` 是模板骨架，之后由该 role 手记维护。重跑 `generate` 不带 `--force` 会拒绝覆盖已有 ws（退 4）；带 `--force` 则把记事换回骨架。

key 位在换真身前保持合法 32 字节 base64 占位（`AQEBAQ...AQE=`）。非法 key 会让全量 parse 连 `onlyne client init` 都跑不动。`[server].cert_pin` 在 `onlyne-server init` 之前保持字符串形态。

三个断电口径：`onlyne status` 的 `socket_present` 是 server 死活真相（`run` 不写 pid，`status.running` 只认 pid 文件；深层工作区再看 `.onlyne/run/socket`）；每个启用 role 在 `onlyne roles` 显示 connected 才算连上；ws 内 `.pi/settings.json` 的 packages 保持 `npm:pi-onlyne`。

daemon 类（`onlyne-server`、`onlyne-client`、`onlyne tui`）一律起在可见 tab，不进 agent 后台。`onlyne client run` 从目标 worktree 自己的 tab 起。

### 搬家

仓可以整体 `mv` 到任何位置，机器层路径无关：spec、模板、文档、知识页一律用仓根相对路径（写进仓的绝对路径是缺陷，见 `.onlyne/AGENTS.md` 路径条款）。搬家步骤：`onlyne server stop --server-root .` → 关各 role client 的可见 tab → `mv` → 在新路径按「通电」重起 server 与 client。`cert_pin` 与 role key 绑密钥对不绑路径，零改动。运行时的一次性现场不用管：`.onlyne/run/` 的 socket 文件、ws 缓存里的 pane 记录、`.pi/sessions/` 与 `state.db` 里带旧路径的历史行，重启后各自自愈或留作旧账，都不是真身。

### 第一发

任务书不存档，交接是瞬态。第一发由人当场写进命令（四段口径见 `.onlyne/AGENTS.md`）：

```bash
onlyne --server-root . send --from _supervisor --to <角色表 ★ 行的 role> --text "目标：<一句话，做完算什么>
输入：<一条一行：路径（这份文件是什么）>
期望产物：<写到哪里的什么文件，格式要求>
下一跳建议：<handoff 谁、干什么；没有就写 无>"
onlyne tui
```

任务书长的时候先落到 `tools/scratch/`，用 `--file` 指过去，用完即删。仓里没有任务书存档目录，也没有流水文件：过程与结论写在各 role 自己的 ws 记事里，机器账在 ledger。

第一发落地后环即成形：每跳自己定产物路径，下一跳任务书交给下一跳的 role。

## 动力源

第一颗 seed 由人给，写在仓根 `AGENTS.md` 的主线与第一发任务书里。之后每一跳自己产生下一跳任务书。

收束判据写在任务书里：判据满足即只 complete 不 handoff，环停在那一跳。人用 `onlyne control cancel --task <id>` 终结任务族，也可以在 TUI 里按终结键。

## 目录

```text
AGENTS.md                  共享目标记录：主线（目标与判据）、支线 todo、索引表
STRUCTURE.md               目录结构与外部集群接入口径（别的集群当知识库用，读这一份）
.onlyne/AGENTS.md          角色行为约定：角色表、残差流、一跳、任务书四段、记事纪律、工具面
.agents/skills/            wiki-format（知识笔记格式正本）、paper-sources（论文与人物情报渠道目录）、scientist-profiles（人物画像协议）、onlyne-role（role 协同纪律）、onlyne-supervisor（值班词汇）
.supervisor/AGENTS.md      supervisor 值班岗位说明（omp 开在仓根，先读它）
.omp/AGENTS.md             omp 会话的项目上下文：supervisor 指针 + 引入仓根 AGENTS.md
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
（仓根无记录文件：流水归 ledger 与 frontmatter）
role 工作区：.onlyne/ws/<role>/（运行时渲染，含该 role 的记事 AGENTS.md）
onlyne 侧：.onlyne/spec.toml（拓扑真相）+ .onlyne/templates/<role>/（记事骨架与模型三元组）
```

角色细则随流程演进：改 prose 与职责时同步改 `.onlyne/spec.toml`、`.onlyne/AGENTS.md` 角色表与本文件工作流节，三处一处不落。
