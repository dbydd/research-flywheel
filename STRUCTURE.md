# STRUCTURE —— 本仓目录结构与外部接入口径

本仓是一个 Obsidian vault，同时是一个 llmwiki bundle，同时是一条 deep research 工作流的产物库。别的集群要把它当知识库用，读这一份就够：下面说清每层装什么、谁能写、从哪进、怎么引。

## 四层加两个保留文件

```text
raw/      来源文件层，只增不改
  <YYYY-MM>/<学科>/<刊名>/<论文名>/   一篇论文的全部资料
    <论文名>.pdf / e-print/ / <论文名>.html / <论文名>.extracted.md / assets/
  <YYYY-MM-DD>-<slug>.<ext>          零散来源：采集快照、剪藏、导出
papers/   论文层，一页一论文
  abstracts/<slug>.md                摘要页，兼这篇论文在库里的身份页
  context/<slug>.md                  论文增强信息页（librarian 的产物）
  readings/<slug>.md                 精读报告（master 的产物）
  decks/<slug>/                      演示产物（需要时）
people/   人物层，一个学者一个文件
wiki/     知识层：被打碎的知识点，子目录按知识层级组织
index.md  面向内容：全库页面目录，按 type 分组
log.md    面向时间：追加式流水，最新在最上面
```

一篇论文的四个落点共用同一个 slug：`raw/…/<slug>/`、`papers/abstracts/<slug>.md`、`papers/context/<slug>.md`、`papers/readings/<slug>.md`。摘要页与精读页的 frontmatter 带 `paper:` 指向论文本体目录。

## 每层装什么、谁能写

| 层 | 内容 | 写者 | 外部集群 |
|---|---|---|---|
| `raw/` | 论文原文、抽取文本、剪藏、快照 | scriber、librarian、astrologer、master、socrates | 只读 |
| `papers/abstracts/` | 论文身份与摘要 | scriber | 只读 |
| `papers/context/` | 论文增强信息 | librarian | 只读 |
| `papers/readings/` | 精读报告 | master、socrates | 只读 |
| `papers/decks/` | 演示产物 | master | 只读 |
| `people/` | 学者画像 | astrologer | 只读 |
| `wiki/` | 知识点页面 | scraper、supervisor（答问落页） | 可按规范写 |
| `index.md` / `log.md` | 目录与流水 | 每个写完产物的 role | 只读 |

## 页面类型

`abstract`、`context`、`reading`（论文层）· `concept`、`entity`、`comparison`、`idea`（知识层）· `overview`（`wiki/overview.md`，全库活综述）。人落 `people/`，`type` 仍是 `entity`。

每个页面的 frontmatter 带 `title`、`slug`、`type`、`created`、`updated`、`sources`；`idea` 页另加 `status`、`origin`、`test`；论文层加 `paper:`。

## 检索入口

- 找一篇论文：`papers/abstracts/` 里的一句话判断 → 沿 `paper:` 取本体文件 → 沿摘要页的链接取精读页。
- 找知识点：`index.md` 的 Concepts、Entities、Comparisons、Ideas 分组 → 进 `wiki/` 对应页。
- 找人：`people/<slug>.md`，`papers` 键列出其代表论文的摘要页。
- 看流水：`grep "^## \[" log.md`，最新在最上面，每条带 role、增删页面、快照路径。
- 看一次研究的链路：残差流随 handoff 传递，不单独存档；`log.md` 逐跳有行，各 role 的 ws 记事有过程，两处合起来能重建。

## 外部集群接入口径

- **读**：`raw/`、`papers/`、`people/`、`wiki/`、`index.md`、`log.md` 全部可读，没有访问控制。
- **写**：默认零。要落页就按 `.agents/skills/wiki-format/SKILL.md` 的规范建：一个知识点一个文件，slug 全库唯一，层级用目录表达，属性只写 frontmatter，`tags` 非要求不写。改 `index.md` 与 `log.md` 前先读后改、增量更新。
- **引用**：正文用 `[[slug]]` 或 `[[slug|显示名]]`，指节写 `[[slug#小节]]`；来源写进 frontmatter 的 `sources`，用相对仓根的文件路径。图与媒体只进论文目录的 `assets/`，用 `![[…]]` 按相对仓根路径引用，不复制。
- **不要**：建枢纽页（合作网络表一类的总表）、按话题乱建链、把论文页塞进 `wiki/`、给知识点建「属于哪篇论文」的映射表、往 `raw/` 改写已有文件。知识点由论文拆出，链接与 `sources` 就是溯源。
- **取数**：要新拉论文或人物，渠道目录、限额与 macOS 代理前缀见 `.agents/skills/paper-sources/SKILL.md`；人物采集流程见 `.agents/skills/scientist-profiles/SKILL.md`。

## 目录清单

```text
AGENTS.md                  共享目标记录：主线（目标与判据）、支线 todo、索引表
STRUCTURE.md               本文件：目录结构与外部接入口径
index.md                   全库页面目录，按 type 分组
log.md                     追加式流水，最新在最上面
raw/                       来源文件层（论文资料、零散来源）
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
.onlyne/templates/alexandria/<role>/   role 记事骨架与模型三元组
.onlyne/ws/alexandria/<role>/          运行时渲染的 role 工作区（含各自私有记事）
.agents/skills/            wiki-format、paper-sources、scientist-profiles、onlyne-role、onlyne-supervisor
.supervisor/AGENTS.md      supervisor 岗位说明：答问、派工、值班、记账
.omp/AGENTS.md             omp 会话项目上下文：supervisor 指针 + 引入仓根 AGENTS.md
.pi/                       role 会话的 pi 配置
```

工作流形态与角色职责见 `README.md` 的「工作流」一节；本文件只说磁盘。
