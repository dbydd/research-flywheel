# STRUCTURE —— 本仓目录结构与外部接入口径

本仓是一个 Obsidian vault，同时是一个 llmwiki bundle，同时是一条 deep research 工作流的产物库。别的集群要把它当知识库用，读这一份就够：下面说清每层装什么、谁能写、从哪进、怎么引。

## 资源层与知识层，零知识记录文件

```text
raw/      来源文件层，只增不改
  <YYYY-MM>/<学科>/<刊名>/<论文名>/   一篇论文的全部资料
    <论文名>.pdf / e-print/ / <论文名>.html / <论文名>.extracted.md / assets/
  <YYYY-MM>/<领域>/<站点>/<slug>/     一篇博客或在线文章的全部资料：网页快照、抽取正文、assets/
  <YYYY-MM-DD>-<slug>.<ext>          零散来源：采集快照、剪藏、导出
papers/   论文层，一页一论文；页面在论文主 slug 上挂种类后缀
  abstracts/<paper>-abstract.md          摘要页，兼这篇论文在库里的身份页，平铺
  context/<paper>-context.md             论文增强信息页（librarian 的产物），平铺
  readings/<YYYY-MM>/<学科>/<刊名>/<paper>-reading.md  精读报告（master 的产物），路径与 raw 同构
  decks/<slug>/                          演示产物（需要时）
blogs/   博客层，与论文层同构，一页一资源
  abstracts/<slug>-abstract.md           摘要页，兼身份页，平铺
  context/<slug>-context.md              文章增强信息页，平铺
  readings/<YYYY-MM>/<领域>/<站点>/<slug>-reading.md   精读报告，路径与 raw 同构
  decks/<slug>/                          演示产物（需要时）
people/   人物层，一个学者一个文件
wiki/     知识层：被打碎的知识点，子目录按知识层级组织
（仓根无知识记录文件：流水归 onlyne ledger 与页面 frontmatter，过程在各 role 的 ws STATE.md）
```

一份资源的本体目录名＝主 slug；资源层页面在主 slug 挂后缀：论文层 `papers/abstracts/<paper>-abstract.md`、`papers/context/<paper>-context.md`、`papers/readings/<YYYY-MM>/<学科>/<刊名>/<paper>-reading.md`；博客层同构：`blogs/abstracts/<slug>-abstract.md`、`blogs/context/<slug>-context.md`、`blogs/readings/<YYYY-MM>/<领域>/<站点>/<slug>-reading.md`。精读报告的年月等段沿用该资源在 `raw/` 下的同名层级。页面 frontmatter 带 `resource:` 指向本体目录，全库 slug 唯一。

## 每层装什么、谁能写

| 层 | 内容 | 写者 | 外部集群 |
|---|---|---|---|
| `raw/` | 资源本体：论文原文、网页快照、抽取文本、剪藏、快照 | scriber、librarian、astrologer、master、socrates | 只读 |
| `papers/abstracts/` | 论文身份与摘要 | scriber | 只读 |
| `papers/context/` | 论文增强信息 | librarian | 只读 |
| `papers/readings/` | 论文精读报告 | master、socrates | 只读 |
| `papers/decks/` | 演示产物 | master | 只读 |
| `blogs/abstracts/` | 文章身份与摘要 | scriber | 只读 |
| `blogs/context/` | 文章增强信息 | librarian | 只读 |
| `blogs/readings/` | 文章精读报告 | master、socrates | 只读 |
| `blogs/decks/` | 演示产物 | master | 只读 |
| `people/` | 学者画像 | astrologer | 只读 |
| `wiki/` | 知识点页面 | scraper、supervisor（答问落页） | 可按规范写 |

## 页面类型

`abstract`、`context`、`reading`（资源层：`papers/` 与 `blogs/` 两树同构）· `concept`、`entity`、`comparison`、`idea`（知识层）· `overview`（`wiki/overview.md`，全库活综述）。人落 `people/`，`type` 仍是 `entity`。

每个页面的 frontmatter 带 `title`、`slug`、`type`、`created`、`updated`、`sources`；`idea` 页另加 `status`、`origin`、`test`；资源层加 `resource:`。

## 检索入口

- 找一篇论文：`papers/abstracts/` 里的一句话判断 → 沿 `resource:` 取本体文件 → 沿摘要页的链接取精读页。
- 找一篇文章：`blogs/abstracts/` 同口径。
- 找知识点：`wiki/` 子目录按知识层级铺开就是分类，配合 Obsidian 图谱、反链与搜索定位；`wiki/overview.md` 是人工维护的活综述入口。不设全库目录页（根 `index.md` 会在图谱里造出无用超级节点）。
- 找人：`people/<slug>.md`，`papers` 键列出其代表论文的摘要页。
- 看流水：仓内无流水文件。机器账走 `onlyne ledger/history --server-root .`（每跳任务书、回执、残差流逐帧），时刻看各页 frontmatter，过程看各 role 的 ws `STATE.md`。
- 看一次研究的链路：`onlyne history` 按 task 血缘回放（parent_task 与 hop），各 role 的 ws `STATE.md` 补过程细节。

## 外部集群接入口径

- **读**：`raw/`、`papers/`、`blogs/`、`people/`、`wiki/` 全部可读，没有访问控制。
- **写**：默认零。要落页就按 `.agents/skills/wiki-format/SKILL.md` 的规范建：一个知识点一个文件，slug 全库唯一，层级用目录表达，属性只写 frontmatter，`tags` 非要求不写。时刻写进被改页面的 `updated`，别处不放流水。
- **引用**：正文用 `[[slug]]` 或 `[[slug|显示名]]`，指节写 `[[slug#小节]]`；来源写进 frontmatter 的 `sources`，用相对仓根的文件路径。图与媒体只进论文目录的 `assets/`，用 `![[…]]` 按相对仓根路径引用，不复制。
- **不要**：建枢纽页（合作网络表一类的总表）、按话题乱建链、把资源层页面塞进 `wiki/`、给知识点建「属于哪篇论文」的映射表、往 `raw/` 改写已有文件。知识点由资源拆出，链接与 `sources` 就是溯源。
- **取数**：要新拉论文或人物，渠道目录、限额与 macOS 代理前缀见 `.agents/skills/paper-sources/SKILL.md`；人物采集流程见 `.agents/skills/scientist-profiles/SKILL.md`。

## 目录清单

```text
AGENTS.md                  注入面：目标与判据、持久索引表、指向 STATE.md 的指针
STATE.md                   手帐面：主线进度、支线 todo
STRUCTURE.md               本文件：目录结构与外部接入口径
raw/                       来源文件层（论文资料、零散来源）
blogs/abstracts/           文章摘要页
blogs/context/             文章增强信息页
blogs/readings/            文章精读报告
blogs/decks/               演示产物
papers/abstracts/          摘要页
papers/context/            论文增强信息页
papers/readings/           精读报告
papers/decks/              演示产物
people/                    人物画像页
wiki/                      知识点页面，子目录按知识层级
tools/scripts/             脚本与工具
tools/scratch/             临时文件（不入 git）
.onlyne/AGENTS.md          角色行为约定：角色表、残差流、一跳、任务书四段、记事纪律
.onlyne/spec.toml          集群拓扑与 ACL 的机器真相
.onlyne/templates/<role>/   role 岗位骨架与模型三元组
.onlyne/ws/<role>/          运行时渲染的 role 工作区（含 AGENTS.md 岗位口径与 STATE.md 手帐）
.agents/skills/            wiki-format、paper-sources、scientist-profiles、onlyne-role、onlyne-supervisor
.supervisor/AGENTS.md      supervisor 岗位说明：答问、派工、值班、记账
.supervisor/STATE.md       supervisor 手帐面：值班过程记录
.omp/AGENTS.md             omp 会话项目上下文：supervisor 指针与仓根 AGENTS.md
.pi/                       role 会话的 pi 配置
```

工作流形态与角色职责见 `README.md` 的「工作流」一节；本文件只说磁盘。
