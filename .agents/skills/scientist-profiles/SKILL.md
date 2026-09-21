---
name: scientist-profiles
description: Use when building or updating a person page in this wiki — collecting an author's metadata from scholarly APIs, expanding a co-author graph from seed papers, or writing the entity page. Gives the page contract (frontmatter fields, body sections), the collection pipeline with its per-depth thresholds, the coverage check, and the boundaries (no collaboration-network hub page, no tags, no paper storage).
---

# scientist-profiles —— 人物画像协议

人物是 `type: entity` 的一种。设计吸收自 `dbydd/scientists-archive`（`scripts/pipeline.py` 的 `expand_levels`、`build_edges`、`portrait_md`，以及 `templates/person-profile.md`），改造成本仓格式：属性进 frontmatter，边写在页面上，取消枢纽页与标签。

渠道选择与各渠道的限额、代理前缀见 `paper-sources`。上游把 OpenAlex 当唯一主力；本仓按任务选主源，人物元数据用 OpenAlex 与 Semantic Scholar 双源交叉，DBLP 校书目，ORCID 校履历。

## 页面契约

落点 `people/<slug>.md`。人物层与论文层、知识层平级，都不进 `wiki/`。一个学者一个页面，同一学者全库一个 slug。

frontmatter（规则二的领域增补，属性只留这一处）：

| 键 | 必填 | 说明 |
|---|---|---|
| `title` | 是 | 学者显示名 |
| `slug` | 是 | 与文件名一致，kebab-case；重名时加 `-<openalex id>` 后缀 |
| `type` | 是 | 固定 `entity` |
| `created` / `updated` | 是 | `YYYY-MM-DD` |
| `sources` | 是 | 支撑本页的 raw 来源，含采集快照文件 |
| `openalex_id` | 是 | `A…` 形，权威 id |
| `orcid` | 否 | ORCID |
| `institution` | 是 | 当前机构，未知写空串 |
| `cited_by_count` | 是 | OpenAlex 被引数 |
| `works_count` | 是 | 作品数 |
| `h_index` / `i10_index` | 否 | 影响力指标 |
| `depth` | 是 | 采集层级，种子作者为 0 |
| `role` | 是 | 层级角色：核心作者 / 关联作者 / 外围 |
| `papers` | 是 | 该学者的代表论文摘要页 slug 数组（`papers/abstracts/` 下同名页），没有写 `[]` |

正文四节，指标不再在正文重复一遍（frontmatter 已有一份）：

```md
# <显示名>

## 简介

两三句：研究方向、在本图谱里的位置、影响力区间。写图内百分位时写明「相对本图谱」。

## 研究焦点（按时期）

- <起始年>–<结束年>: 主题一、主题二（N 篇）

## 机构履历

- <机构>（<起始年>–<结束年>）

## 代表论文

- [[<论文页 slug>|<标题>]]（<年>，被引 N）

## 主要合作者

- [[<人物页 slug>|<姓名>]]（合作 N 次）
```

`代表论文` 链接指向 `papers/abstracts/` 下的摘要页，`主要合作者` 链接指向其他人物页；目标页还没建时在 `index.md` 记待建行，本页照写链，lint 时补页。

## 采集流程

```text
seeds（arXiv id / DOI / OpenAlex work URL）
  → 解析成 work 元数据（arXiv API 或 Crossref，再回 OpenAlex 定位）
  → depth 0 = 该 work 的作者集合
  → 逐作者拉被引最高的 N 篇作品（OpenAlex select 裁字段）
  → 合著候选 = 与已入库作者同篇出现的其他作者
  → 逐层收紧筛选，扩张到 maxDepth
  → 建合著边（权重 = 合著篇数）
  → 落页面、写快照、更新 index.md 与 log.md
```

逐层收紧的超参（上游默认值，按任务可调）：

| 超参 | 默认 | 含义 |
|---|---|---|
| `maxDepth` | 2 | 扩张层数，depth 0 是种子作者 |
| `perDepthRules` | depth0 合著 ≥1、被引 ≥10；depth1 合著 ≥2、被引 ≥50；depth2 合著 ≥3、被引 ≥100 | 每层门槛，层越深越紧 |
| `maxPeople` | 500 | 入库人数上限，按合著强度与被引排序截断 |
| `undergradFilter` | 被引 <50 且 h <5 且合著不强者剔除 | 低影响力作者门槛 |
| `segmentYears` | 3 | 研究焦点分段年数 |

Semantic Scholar 只做交叉补充：同名确认、被引与参考文献补洞，只查种子作者前几位，避免限流。

## 覆盖度校验

每轮采集结束给出这几个数：入库人数、按层分布、图谱内部合著边数、孤点人数、是否触发 `maxPeople` 截断。

孤点是没有任何入库合著边的入库学者。孤点要么回采集阶段补采放宽阈值，要么从库里摘掉并记原因。摘人与补采都写进 `log.md`。

## 落账

- 采集快照写 `raw/<YYYY-MM-DD>-<seed 短名>.collection.json`：seeds、所用超参、种子作者 id、候选数、缓存作品数、合著频次前若干。快照只增不改。
- `log.md` 记一条 `## [YYYY-MM-DD HH:MM] ingest | <种子论文或主题>`，带 role、入库人数、按层分布、边数、孤点数、快照路径。
- `index.md` 的 Entities 分组增量更新新增与改动的人物条目。
- 拆分、合并、改目录等结构动作按 `wiki-format` 记 structure 行。

## 边界

- 不建合作网络枢纽页。合著关系写在每个学者页的「主要合作者」里，图谱由页面自然长出。上游的 `关系图谱/合作网络.md` 大表不搬。
- 不写 `tags`。身份信息由 `type: entity` 与 frontmatter 字段承载。
- 本协议不存论文。论文页由 reading 流程产出，这里只建链与建人。
- 指标注明来源与访问日期。图内百分位只在本图谱内有效，写出来必须带这句限定。
