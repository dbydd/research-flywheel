---
name: wiki-format
description: Use when writing or editing any markdown note in this workspace — source pages, concept pages, entity pages, comparison pages, idea pages, the index, the log — or when linting the wiki. Gives the llmwiki file layout, page frontmatter fields, page types, wikilink syntax, naming rules, and the reserved index/log discipline this repo follows.
---

# wiki-format —— 本仓 md 笔记的基本格式（llmwiki）

本仓的知识笔记按 llmwiki 格式写。格式源：Karpathy 的 LLM Wiki pattern（三层加三操作）与它的开源实现（llmwiki.cc、ddsyasas/llm-wiki 的 data model、Open Knowledge Format 的文件契约）。本文件是本仓的落地口径，两份源文件冲突时以本文件为准，本文件与上游冲突时以本文件为准。

## 三层

```text
raw/      不可变来源层：原文 PDF、抽取出的文本、外部剪藏
wiki/     role 维护的页面层：一篇笔记一个文件，互链
根 index.md / log.md    两个保留文件：目录与流水
```

- `raw/` 是证据层。文件进来之后不改写；来源有误就补一份新的，订正写进 wiki 层对应页面的证据边界。
- `wiki/` 是页面层。role 都往这里写，写法见下面各节。
- `index.md` 面向内容：全库页面的目录，按 type 分组，每次写入后增量更新。
- `log.md` 面向时间：追加式流水，一行一条，可 grep。
- 机器件（`.onlyne/`、`.pi/`、`.agents/`、`.supervisor/`、`payload/`、`scripts/`）不属这三层，本格式不管它们。

## 页面

一个页面一个文件，文件名就是 slug（kebab-case）。frontmatter 键：

| 键 | 必填 | 说明 |
|---|---|---|
| `title` | 是 | 页面标题，与正文一级标题一致 |
| `slug` | 是 | 与文件名一致 |
| `type` | 是 | 见下表 |
| `created` | 是 | `YYYY-MM-DD`，本页建立的日期 |
| `updated` | 是 | `YYYY-MM-DD`，最近一次改动的日期 |
| `sources` | 是 | 支撑本页的 raw 来源（文件名去扩展名），没有写 `[]` |
| `tags` | 否 | 主题标签，小写，数组 |

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

页面正文的硬形状：一级标题一行，然后是正文；笔记里不用字母加数字的缩记号指代条目，指代一律用标题原文。

## 交叉链接

`[[slug]]` 或 `[[slug|显示名]]`，指到某一节写 `[[slug#小节]]`。Obsidian 与 llmwiki 都按文件名（slug）解析。

- 链接指到真实存在的页面。要建还没建的页面，先在 `index.md` 的待建行记一笔，lint 时补齐。
- 同一对象全程一个 slug；改名时改动点一次改齐。
- 页面里的 `[[slug]]` 是关联，`sources` 键是账；正文断言尽量都能对回 `sources` 里某一份来源。

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

## log.md

追加式，最新的写最上面（本仓取 newest-first，先读到的就是最近发生的）。条目形状：

```md
## [YYYY-MM-DD HH:MM] <op> | <标题>
- role: <role>
- created pages: <slug>, <slug>
- updated pages: <slug>
```

`<op>` 词表：`ingest`（进一份来源）、`query`（一次问答）、`lint`（体检）、`idea`（产出 idea 页）。前缀固定，`grep "^## \[" log.md` 倒着翻流水。

## 命名

- 页面文件名＝slug：kebab-case，ASCII，避开 `#`、`|`、`^`、`:`、`/`。
- raw 文件名：`YYYY-MM-DD-short-slug.ext`；文本抽取产物同名加 `.extracted.md`，与原文并排。
- 标题里可以有汉字与标点。slug 保持稳定，改名等于全库改链接，走一次 lint。

## Obsidian 兼容

仓根就是 vault，上面这些写法都在 Obsidian 的原生语义里：frontmatter 进属性面板，`[[…]]` 进图谱与反链，callout 直接渲染，`raw/` 与 `wiki/` 是普通文件夹。机器件全在点目录里，不进图谱。

## 记事的分界

本格式管知识笔记。role 记事（三层 `AGENTS.md`）另有一套纪律：不写时间戳，记叙段加条目段，手记。两套互不搬：知识笔记的时刻写在 frontmatter 与 `log.md` 里，记事里只写过程与指针。

## lint 四条

- 断链：`[[…]]` 指不到页面。
- 孤页：没有入链的页面。
- 缺账：正文断言在 `sources` 里找不到出处。
- 冲突：同一断言在两页上对立，其中一页没有对应 callout。
