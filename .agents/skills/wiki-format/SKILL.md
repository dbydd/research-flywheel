---
name: wiki-format
description: Use when writing, editing, splitting, merging, or linting any markdown note in this workspace — source pages, concept pages, entity pages, comparison pages, idea pages, the index, the log — or when restructuring the wiki folders. Gives the llmwiki file layout, the atomic-note rule, frontmatter attributes, folder hierarchy, wikilink discipline that keeps the knowledge graph usable, naming rules, and the reserved index/log files.
---

# wiki-format —— 本仓知识笔记的基本格式

本仓的知识笔记按 llmwiki 格式写，落地面向 Obsidian。格式源：Karpathy 的 LLM Wiki pattern（三层加三操作）与它的开源实现（llmwiki.cc、ddsyasas/llm-wiki 的数据模型、Open Knowledge Format 的文件契约）。上游与本仓冲突时以本文件为准。

## 布局

```text
raw/      不可变来源层。论文按 <YYYY-MM>/<学科>/<刊名>/<论文名>/ 落盘，一目录一论文；零散来源平铺
wiki/     页面层，子目录按知识层级组织，一页一文件
根 index.md / log.md    两个保留文件：目录与流水
```

- `raw/` 是证据层。文件进来之后不改写；来源有误就补一份新的，订正写进 wiki 层对应页面的证据边界。
- 一篇论文的全部资料（PDF、TeX 源、HTML、补充材料、抽取文本）放进同一个论文目录，一目录一论文；目录名与它的 `type: source` 页同名，口径见命名节。
- `wiki/` 是页面层。role 都往这里写，写法见下面各节。
- `index.md` 面向内容：全库页面的目录，按 type 分组。
- `log.md` 面向时间：追加式流水，可 grep。
- 机器件（`.onlyne/`、`.pi/`、`.agents/`、`.supervisor/`、`payload/`、`scripts/`）不属这三层，本格式不管它们。

## 规则一：拆碎

一个知识点一个文件。这是本格式的第一规则，其余规则都为它让路。

拆不拆看知识点本身，不看篇幅长短。篇幅是知识点的自然结果，拿字数当判据治不到根上。

- 一个文件承载两个及以上可独立引用的判断时拆开，拆出的各页各写一个知识点。
- 同一知识点散在多处时合并进单个文件。名字不同内容同一，是同一知识点。
- 一个主题长大时开成子目录：`wiki/<域>/<主题>/<点>.md`，该主题的知识点归到那一层。层级由目录表达，拆出来的页永远有落点。
- 拆分、合并、改目录是常规结构动作，随时可做，做完在 `log.md` 记一条 structure 行。

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

| type | 装什么 |
|---|---|
| `source` | 一份来源的摘要页，一篇论文一张 |
| `concept` | 跨来源的概念、方法、术语 |
| `entity` | 作者、机构、会议、数据集、基准、工具 |
| `comparison` | 两个及以上页面的对照 |
| `overview` | 全库的活综述，每份新来源进来时改写 |
| `idea` | 本仓的领域增补：候选研究想法 |

`idea` 页在三层键之外另加三个：

| 键 | 说明 |
|---|---|
| `status` | `seed` / `active` / `parked` / `killed` |
| `origin` | 缺口出处的页面 slug，一条 |
| `test` | 一行：怎么验证它 |

## 规则三：目录承载层级

知识层级由目录路径表达，不靠标签，不靠枢纽页。

- 页面落点 `wiki/<域>/<子域>/…/<slug>.md`。域与子域按知识点归类决定，归类变化时跟着变。
- 目录改名、合并、拆分是常规动作。目录里只放该层级的页面，不做二次索引。
- 目录改名或移动时，同一对象全程一个 slug；文件名不动，链接就不动。
- `overview` 页只留一篇，放 `wiki/overview.md`，写全库综述，不做分类目录。

## 规则四：关联只写真实关系

乱写关联会造出超级节点，叶子之间又是散的。链条按关系建，不按话题建。

- 一条链只表达一种关系：依赖、对比、反驳、同源、同一机制。写不出关系名的链不建。
- 链写在正文对应论断旁边，不堆在文末「相关阅读」清单里。
- 同域相邻的知识点沿真实关系互链。指向 `index.md` 与 `overview` 的链接不算关联。
- 链接指到真实存在的页面。要建还没建的页面，先在 `index.md` 的待建行记一笔，lint 时补齐。
- 同一对象全程一个 slug；改名时改动点一次改齐。
- 正文断言尽量都能对回 `sources` 里某一份来源；`[[slug]]` 是关联，`sources` 键是账。

## 矛盾与过期

新来源与旧页面冲突时两说并存，旧页面上加 callout：

```md
> [!contradiction] <新来源 slug> 与本节冲突：<一句话说明分歧>
```

本页 `sources` 补上新来源。删旧结论要留痕：写清哪份来源推翻了它。断言被取代时加 `> [!warning] 已被 [[slug]] 取代`。

## index.md

分组固定顺序：Overviews、Sources、Concepts、Entities、Comparisons、Ideas。组内按标题字母序。条目形状：

```md
- [[slug|标题]]：一句话说明
```

每跳写完把新增与改动的页面条目增量更新进对应分组。要建还没建的页面也在这里记一行，标题写清打算写什么。

## log.md

追加式，最新的写最上面。条目形状：

```md
## [YYYY-MM-DD HH:MM] <op> | <标题>
- role: <role>
- created pages: <slug>, <slug>
- updated pages: <slug>
```

`<op>` 词表：`ingest`（进一份来源）、`query`（一次问答）、`lint`（体检）、`idea`（产出 idea 页）。拆分、合并、移动目录时加一行 `- structure: split <slug> -> <a>, <b>` 或 `- structure: merge <a>, <b> -> <slug>`。前缀固定，`grep "^## \[" log.md` 倒着翻流水。

## 命名

- 页面文件名＝slug：kebab-case，ASCII，避开 `#`、`|`、`^`、`:`、`/`。全库 slug 唯一。
- 论文来源：`raw/<YYYY-MM>/<学科>/<刊名>/<论文短名>/`，一目录一论文。目录名就是该论文的 slug，与它的 `type: source` 页同名。目录里放这一篇的全部资料：原文 PDF、TeX 源、HTML、补充材料、抽取文本 `<slug>.extracted.md`。
  - `<YYYY-MM>`：官方发表年月；预印本取首次提交年月。
  - `<学科>`：arXiv 主分类（`cs.CV` 一类）；无分类时用小写连字符的领域短语。
  - `<刊名>`：归一化的会议或期刊短名；预印本写 `arXiv`。
  - `<论文短名>`：标题转 kebab-case，超长截断并保持唯一。
- 零散来源（采集快照、剪藏、对话导出）：`raw/<YYYY-MM-DD>-<slug>.<ext>`。
- 目录名：该层级的主题短语，可读，不编号。

## Obsidian 兼容

仓根就是 vault。frontmatter 进属性面板，`[[…]]` 进图谱与反链，callout 直接渲染，`wiki/` 的子目录就是知识层级。图谱只呈现按关系建的链，看起来稀是对的；图谱变密先查链是不是按话题乱建的。机器件全在点目录里，不进图谱。

## 记事的分界

本格式管知识笔记。role 记事（三层 `AGENTS.md`）另有一套纪律：不写时间戳，记叙段加条目段，手记。两套互不搬：知识笔记的时刻写在 frontmatter 与 `log.md` 里，记事里只写过程与指针。

## lint 六条

- 断链：`[[…]]` 指不到页面。
- 孤页：没有入链的页面。
- 缺账：正文断言在 `sources` 里找不到出处。
- 冲突：同一断言在两页上对立，其中一页没有对应 callout。
- 没拆碎：一页装了多个可独立引用的判断。处置是开子目录或拆页，不是删内容。
- 超级节点：一页出链超过 12 条或入链超过 24 条；处置是拆页，不是加链。
