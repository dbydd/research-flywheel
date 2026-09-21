---
name: wiki-format
description: Use when writing, editing, splitting, merging, or linting any markdown note in this workspace — abstract pages, reading pages, person pages, concept pages, entity pages, comparison pages, idea pages — or when restructuring the layers. Gives the four-layer layout (raw source files, paper abstracts and readings, people, wiki knowledge points), the atomic-note rule, frontmatter attributes, folder hierarchy, wikilink discipline that keeps the knowledge graph usable, and naming rules. There are no record files: the flow lives in the onlyne ledger, page frontmatter, and each role's own workspace notes.
---

# wiki-format —— 本仓知识笔记的基本格式

本仓的知识笔记按 llmwiki 格式写，落地面向 Obsidian。格式源：Karpathy 的 LLM Wiki pattern（三层加三操作）与它的开源实现（llmwiki.cc、ddsyasas/llm-wiki 的数据模型、Open Knowledge Format 的文件契约）。上游与本仓冲突时以本文件为准。

## 布局

```text
raw/      来源文件层，只增不改。论文按 <YYYY-MM>/<学科>/<刊名>/<论文名>/ 落盘，一目录一论文；零散来源平铺
  <论文名>/assets/   这一篇论文的图与媒体：从论文抽取的图、为它自绘的图
papers/   论文层：一页一论文一页
  abstracts/<paper>-abstract.md                        摘要页，兼身份页，平铺（检索入口）
  context/<paper>-context.md                           增强信息（librarian 产物），平铺
  readings/<YYYY-MM>/<学科>/<刊名>/<paper>-reading.md   精读报告（master 产物），路径与 raw 同构
  decks/<slug>/        演示产物，一个主题一个目录
people/   人物层：一个学者一个文件
wiki/     知识层：被打碎的知识点，子目录按知识层级组织，一页一知识点
tools/scripts/   脚本与工具，随树跟踪
tools/scratch/   临时文件，不入 git
（仓根无记录文件：流水归机器与 frontmatter）
```

- `raw/` 是证据层。文件进来之后不改写；来源有误就补一份新的，订正写进引用它的页面里。
- 一篇论文的全部资料（PDF、TeX 源、HTML、补充材料、抽取文本）放进同一个论文目录，一目录一论文。论文目录名＝主 slug；论文层页面在主 slug 上挂种类后缀（`-abstract`、`-context`、`-reading`），页面 slug 全库唯一；精读报告的路径与 `raw/` 里该论文的层级同构，其余平铺。口径见命名节。
- 论文不进 `wiki/`。论文层的摘要页与精读页记这一篇论文本身；从论文里拆出来的概念、方法、缺口、人物判断进 `wiki/` 与 `people/`。
- 四层各写各的，不互相搬内容：`wiki/` 的一页被论文层引用时用 `[[slug]]`，反过来论文层被知识页引用时同样只放链接。
- 导航不设全库目录页：type 由所在目录区分（`papers/abstracts`、`papers/readings`、`people/`、`wiki/…` 各是一类），找页靠 Obsidian 图谱、反链与搜索，`wiki/overview.md` 是人工维护的活综述。根目录不放 `index.md`，它在图谱里就是个连向一切的无用超级节点。
- 仓根不放任何记录文件。流水归三处：机器账在 onlyne ledger（每跳任务书、回执、残差流逐帧可回放），时刻在页面自身（frontmatter `created`/`updated`），过程在各 role 的 ws 记事。中央追加式账本在几十部文献的规模下必然腐成噪音堆，还会用陈旧流水误导后来者——不留。
- 机器件（`.onlyne/`、`.pi/`、`.agents/`、`.supervisor/`、`tools/`）不属这四层，本格式不管它们。工具区只放脚本、工具与临时文件，不写知识笔记。
- 任务书是瞬态交接面，不落盘不存档；仓里没有任务书目录。过程与结论落在各 role 自己的 ws 记事，机器侧流水在 onlyne ledger。

## 规则一：拆碎

一个知识点一个文件。这是本格式的第一规则，其余规则都为它让路。

拆不拆看知识点本身，不看篇幅长短。篇幅是知识点的自然结果，拿字数当判据治不到根上。

- 一个文件承载两个及以上可独立引用的判断时拆开，拆出的各页各写一个知识点。
- 同一知识点散在多处时合并进单个文件。名字不同内容同一，是同一知识点。
- 一个主题长大时开成子目录：`wiki/<域>/<主题>/<点>.md`，该主题的知识点归到那一层。层级由目录表达，拆出来的页永远有落点。
- 拆分、合并、改目录是常规结构动作，随时可做；落点写进相关页面的 frontmatter 与各自 ws 记事，改动痕迹由 git 历史承载。

## 规则二：属性写在 frontmatter 行

节点属性只写在文件头的 frontmatter 行，Obsidian 属性面板读同一份。正文里不再摆一份属性表。

| 键 | 必填 | 说明 |
|---|---|---|
| `title` | 是 | 页面标题，与正文一级标题一致 |
| `slug` | 是 | 与文件名一致 |
| `type` | 是 | 见下表 |
| `created` | 是 | `YYYY-MM-DD`，本页建立的日期 |
| `updated` | 是 | `YYYY-MM-DD`，最近一次改动的日期 |
| `sources` | 是 | 支撑本页的 raw 来源文件路径（相对仓根），没有写 `[]` |
| `tags` | 非要求不写 | 用户或任务书点名时才写 |

type 取值：

| type | 层 | 装什么 |
|---|---|---|
| `abstract` | `papers/abstracts/` | 一篇论文的摘要页，兼这篇论文在库里的身份页 |
| `context` | `papers/context/` | 一篇论文的增强信息页 |
| `reading` | `papers/readings/` | 一篇论文的精读报告 |
| `concept` | `wiki/` | 跨论文的概念、方法、术语 |
| `entity` | `people/`（人）或 `wiki/`（机构、会议、数据集、基准、工具） | 实体页 |
| `comparison` | `wiki/` | 两个及以上页面的对照 |
| `overview` | `wiki/overview.md` | 全库的活综述，每篇新论文进来时改写 |
| `idea` | `wiki/` | 本仓的领域增补：候选研究想法 |

人落 `people/<slug>.md`，`type` 仍是 `entity`；其余实体按知识层级落 `wiki/`。一篇论文的摘要职责由 `abstract` 页承担，不再设 `source` 类型。

`idea` 页在三层键之外另加三个：

| 键 | 说明 |
|---|---|
| `status` | `seed` / `active` / `parked` / `killed` |
| `origin` | 缺口出处的页面 slug，一条 |
| `test` | 一行：怎么验证它 |

## 论文层与人物层

摘要页、精读页、人物页各占一个目录，都不进 `wiki/`。三者的 frontmatter 都用上面的七键，另加本节两个领域键：

| 键 | 必填 | 说明 |
|---|---|---|
| `paper` | 论文层必填 | 论文本体的 raw 目录路径（相对仓根） |
| `openalex_id` | 人物页必填 | 权威 id |

### 摘要页（`papers/abstracts/<paper>-abstract.md`）

论文的身份页：属性、官方摘要、一句话判断、去向链接。agent 检索一篇论文从这里进。

```md
# <标题>

> [!quote] 官方摘要
> <逐字摘录，不改写>

## 一句话判断

<三到六句：做了什么、核心机制、最关键数字（带 Table/Figure/公式锚点）、影响读数的条件>

## 本体与去向

- 论文本体：`raw/<YYYY-MM>/<学科>/<刊名>/<slug>/`
- 精读：[[<paper>-reading|<标题>精读]]（还没建就直接留这个未解析链接，它就是待建标记）
```

### 精读页（`papers/readings/<YYYY-MM>/<学科>/<刊名>/<paper>-reading.md`）

精读报告：论文事实与「我的分析」分区。按需建，不是每篇论文都有。

精读报告必须自足：没读过任何相关文献的读者，只看这一页要能懂个七七八八。概念首次出现就地解释，承重数字写进正文，外部链接只做溯源锚点、承载考证不承载理解——摘掉全部链接，正文仍是一篇连贯完整的文章。把理解外包给「详见 [[…]]」或外链，对质位会打回。

引用纪律：报告是连贯的文章，读者从头到尾不需要打开第二个文件。需要原文为证的段落，整段嵌进报告或归纳转述一次；§ 节号、Table/Figure、公式号、PDF 页码只作稀疏的溯源记号挂在已经自明的论断后（一节内至多一两个），供事后核对，不承载任何理解环节。抽取文本的行号是机器对账坐标，禁入正文。满页的「见行 xxx」「详见 §」是未完成品的形状，对质位打回。

```md
# <标题> 精读

- 论文本体：`raw/<YYYY-MM>/<学科>/<刊名>/<paper>/`
- 摘要：[[<paper>-abstract|<标题>摘要]]

## 问题与做法

## 关键证据

<每条证据自明：数字改写成人话陈述，原文为证的整段嵌入或归纳转述；句尾至多挂一个稀疏溯源记号（§/Table/Figure/页码），不写「见行 xxx」「详见」>

## 局限与缺口

## 我的分析

<机制直觉、跨论文联系、可延伸实验；标明「我的分析」，不冒充论文事实>

## 关联

- [[<slug>]]：<关系名>
```

精读页里值得独立引用的概念、方法、缺口，另建 `wiki/` 页面，精读页只放链接。抓取与落盘的渠道口径见 `paper-sources`，人物页的采集流程见 `scientist-profiles`。

### 增强信息页（`papers/context/<paper>-context.md`）

librarian 的产物，回答五个问题：这篇论文做了什么、可能是在什么基础上做的、相关引用文献引用在哪里、哪个组做的、这个组有什么特点。每条结论带来源（URL 与访问日期），猜想的标明是猜想。落点写 §/Table/Figure/PDF 页码这类人可定位的位置；抽取文本行号只进自己的 ws 对账，不进页面正文。页面只做这一篇论文的脉络，不写精读判断。

## 图与媒体

图、截图、图表一律放进论文目录的 `assets/`，一处生成，多处引用，不在任何页面旁边复制一份。

- 从论文抽取的图：`assets/<slug>-fig<N>.<ext>`，`N` 取论文的 Figure 编号。
- 自绘的图：`assets/<引用页 slug>-<n>.<ext>`，`n` 从 1 起。绘图脚本落 `tools/scripts/`，图落论文目录，脚本与图各就各位。
- 页面里用 `![[…]]` 嵌入，路径写相对仓根的完整路径，避免同名歧义：`![[raw/<YYYY-MM>/<学科>/<刊名>/<slug>/assets/<slug>-fig3.png]]`。
- 图在正文里带锚点：抽取图标论文 Figure 号，自绘图标数据来自哪份 `sources`。
- 知识点与论文的错配不建映射表。知识点由论文拆出，`[[…]]` 与 `sources` 就是溯源；缺链时补链，不加中间层。

## 规则三：目录承载层级

知识层级由目录路径表达，不靠标签，不靠枢纽页。

- 页面落点 `wiki/<域>/<子域>/…/<slug>.md`。域与子域按知识点归类决定，归类变化时跟着变。
- 摘要层、增强层、人物层平铺不分层：`papers/abstracts/`、`papers/context/`、`people/` 各一层摊平；精读报告是例外，按 `<YYYY-MM>/<学科>/<刊名>/` 与 `raw/` 同构落，人最终读的是它，不能摊成一堆噪音。页面 slug 全库唯一。
- 目录改名、合并、拆分是常规动作。目录里只放该层级的页面，不做二次索引。
- 目录改名或移动时，同一对象全程一个 slug；文件名不动，链接就不动。
- `overview` 页只留一篇，放 `wiki/overview.md`，写全库综述，不做分类目录。

## 规则四：关联只写真实关系

乱写关联会造出超级节点，叶子之间又是散的。链条按关系建，不按话题建。

- 一条链只表达一种关系：依赖、对比、反驳、同源、同一机制。写不出关系名的链不建。
- 链写在正文对应论断旁边，不堆在文末「相关阅读」清单里。
- 同域相邻的知识点沿真实关系互链。指向 `overview` 的链接不算关联。
- 链接指到真实存在的页面。要建还没建的页面，直接写一个未解析的 `[[slug]]` 占位：Obsidian 把它显示成待建页，lint 的「断链」条目就是待建清单，补齐后自然消掉。
- 同一对象全程一个 slug；改名时改动点一次改齐。
- 正文断言尽量都能对回 `sources` 里某一份来源；`[[slug]]` 是关联，`sources` 键是账。
- 锚点最少化：位置记号（§节号、Table/Figure、公式号、PDF 页码）只在已经自明的论断后稀疏出现，作溯源用；读者顺着正文就能读完，一次都不用跳。抽取文本行号永不入正文；引原文就整段嵌入或归纳转述。

## 矛盾与过期

新来源与旧页面冲突时两说并存，旧页面上加 callout：

```md
> [!contradiction] <新来源 slug> 与本节冲突：<一句话说明分歧>
```

本页 `sources` 补上新来源。删旧结论要留痕：写清哪份来源推翻了它。断言被取代时加 `> [!warning] 已被 [[slug]] 取代`。

## 命名

- 页面文件名＝slug：kebab-case，ASCII，避开 `#`、`|`、`^`、`:`、`/`。全库 slug 唯一。
- 论文来源：`raw/<YYYY-MM>/<学科>/<刊名>/<论文短名>/`，一目录一论文；目录名＝论文主 slug。目录里放这一篇的全部资料：原文 PDF、TeX 源、HTML、补充材料、抽取文本 `<paper>.extracted.md`。
  - `<YYYY-MM>`：官方发表年月；预印本取首次提交年月。
  - `<学科>`：arXiv 主分类（`cs.CV` 一类）；无分类时用小写连字符的领域短语。
  - `<刊名>`：归一化的会议或期刊短名；预印本写 `arXiv`。
  - `<论文短名>`：标题转 kebab-case，超长截断并保持唯一。
- 论文层页面在主 slug 上挂种类后缀：`papers/abstracts/<paper>-abstract.md`、`papers/context/<paper>-context.md` 平铺；`papers/readings/<YYYY-MM>/<学科>/<刊名>/<paper>-reading.md` 与 `raw/` 同构（年月、学科、刊名沿用该论文在 raw 下的同名层级）。链接一律用页面 slug（含后缀），`paper:` 键指论文本体目录。
- 零散来源（采集快照、剪藏、对话导出）：`raw/<YYYY-MM-DD>-<slug>.<ext>`。
- 人物页：`people/<slug>.md`，slug 取学者名的 kebab-case；重名时加 `-<openalex id>` 后缀。
- 目录名：该层级的主题短语，可读，不编号。

## Obsidian 兼容

仓根就是 vault。frontmatter 进属性面板，`[[…]]` 进图谱与反链，callout 直接渲染，`wiki/` 的子目录就是知识层级。图谱只呈现按关系建的链，看起来稀是对的；图谱变密先查链是不是按话题乱建的。机器件全在点目录里，不进图谱。

## 记事的分界

本格式管知识笔记。role 记事（三层 `AGENTS.md`）另有一套纪律：不写时间戳，记叙段加条目段，手记。两套互不搬：知识笔记的时刻只写在 frontmatter，记事里只写过程与指针。

## lint 六条

- 断链：`[[…]]` 指不到页面。
- 孤页：没有入链的页面。
- 缺账：正文断言在 `sources` 里找不到出处。
- 冲突：同一断言在两页上对立，其中一页没有对应 callout。
- 没拆碎：一页装了多个可独立引用的判断。处置是开子目录或拆页，不是删内容。
- 超级节点：一页出链超过 12 条或入链超过 24 条；处置是拆页，不是加链。
