---
name: paper-sources
description: Use when finding papers, authors, metadata, reviews, code, or full text for this wiki — choosing a retrieval channel, calling an API with correct limits, or fixing a failed fetch. Gives the channel catalog (arXiv, OpenAlex, Semantic Scholar, Crossref, DBLP, ORCID, OpenReview, ACL Anthology, CVF, PMLR, Europe PMC, bioRxiv, Unpaywall, CORE, GitHub, Hugging Face), each channel's endpoint, auth and rate limits, and the macOS proxy prefix that arXiv and OpenAlex calls need.
---

# paper-sources —— 本仓的论文与人物情报渠道目录

取论文、取人物、取元数据、取全文、取评审意见，都从本目录选渠道。上游的 scientists-archive 过度单一地压在 OpenAlex 上；本仓按任务类型选主源，OpenAlex 只是其中一条。

## 使用三原则

- 一手优先。官方 API、官方 PDF、官方会议页是证据；聚合页、二手转述、博客解读只作线索。
- 每条结论可回溯：来源 URL、访问日期、命中的具体记录（DOI、arXiv id、OpenAlex id）。记进对应页面的 `sources` 键与 `log.md`。
- 限速与礼貌。带 `mailto:` 或账号的渠道走礼貌池；连续调用按各渠道的间隔要求 sleep；429 按 `Retry-After` 退避重试，不并发硬刷。

## 本机代理条款（必读）

macOS 系统代理会劫持 arXiv API、arXiv HTML 与论文下载。所有外呼命令一律带前缀：

```bash
env no_proxy='*' NO_PROXY='*' http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= <原命令>
```

## 渠道表

### 书目与作者权威源

| 渠道 | 端点 | 拿什么 | 鉴权与限额 | 坑 |
|---|---|---|---|---|
| OpenAlex | `api.openalex.org` | works/authors/sources/institutions/topics，filter/sort/select | 免 key 约 10 万次每日，mailto 进礼貌池，超 100 req/s 返 429 | 元数据偶有噪入与消歧错误，关键结论要交叉验证 |
| Semantic Scholar | `api.semanticscholar.org/graph/v1` | paper/author、参考文献与被引、推荐 | 无鉴权走共享池（约 1000 rps 共享，实际常被限流）；个人 key 给独立 1 rps，可申请提额；bulk 数据集要 key | 作者同名合并与拆分都发生过，按 id 不用名 |
| Crossref | `api.crossref.org` | DOI 元数据、作者作品、资助方 | 免 key，mailto 进礼貌池 | 预印本与部分会议论文覆盖弱 |
| DBLP | `dblp.org/search/publ/api`、`dblp.org/search/author/api` | 作者书目、会议卷次、期刊卷期 | 免 key，限速严，串行调用 | 计算机领域最干净，其他领域稀 |
| ORCID | `pub.orcid.org/v3.0` | 作者自述履历、任职、作品表 | 公开记录免 key；受限记录要 OAuth | 自报数据，可能与权威库不一致 |

### 预印本与开放全文

| 渠道 | 端点 | 拿什么 | 鉴权与限额 | 坑 |
|---|---|---|---|---|
| arXiv | `export.arxiv.org/api/query` | 题录、摘要、作者、分类、版本 | 免 key；连续调用间隔 3 秒；单次 `max_results` 分片 ≤2000，总量 ≤30000 | 必须带上面的代理前缀；大批量元数据走 OAI-PMH |
| arXiv HTML | `arxiv.org/html/<id>` | 分节正文、公式、表格、图 | 免 key | 新论文才有 HTML 版，旧文只有 PDF |
| bioRxiv / medRxiv | `api.biorxiv.org/details/<srv>/<doi>` | 生命科学预印本 | 免 key | 元数据字段少，被引数据要回 OpenAlex 补 |
| Europe PMC | `ebi.ac.uk/europepmc/webservices/rest` | 生物医学文献与 OA 全文 | 免 key | 覆盖偏生物医学 |
| PubMed | E-utilities | 生物医学题录与摘要 | 免 key | 不做全文，不做被引图 |

### 开放评审与会议论文集

| 渠道 | 端点 | 拿什么 | 鉴权与限额 | 坑 |
|---|---|---|---|---|
| OpenReview | `api2.openreview.net`，2024 年前老会议走 `api.openreview.net` | 投稿、评审意见、录用决定 | 需账号，按权限读 | 两套 API 的 JSON 结构不同，别混用 |
| ACL Anthology | `aclanthology.org` | NLP 论文 PDF 与 BibTeX | 免 key | 结构化书目用 DBLP 更省事 |
| CVF Open Access | `openaccess.thecvf.com` | CVPR/ICCV/WACV 论文 PDF | 免 key | 只覆盖 CVF 系会议 |
| PMLR | `proceedings.mlr.press` | ICML 及 PMLR 卷论文 PDF | 免 key | 卷次按年归档 |
| NeurIPS proceedings | `papers.nips.cc` | NeurIPS 论文 PDF | 免 key | 页面上有 supplementary 链接 |

### 代码与复现

| 渠道 | 端点 | 拿什么 | 鉴权与限额 | 坑 |
|---|---|---|---|---|
| GitHub | `api.github.com` | 官方实现、复现仓库、issue 里的坑 | 未认证 10 req/min，token 30 req/min | 仓库名不等于论文名，按论文标题与作者双条件搜 |
| Hugging Face | `huggingface.co` 模型卡、数据集卡、`/papers` 每日论文 | 实现、权重、数据、趋势 | 免 key 读公开内容 | 模型卡里的数字是自述，标注来源等级 |
| Papers with Code 归档 | `paperswithcode-data`（Hugging Face 与 Zenodo 冻结快照） | 历史上的任务、榜、论文实现映射 | 免 key | 官网 2025 年 7 月关停，SOTA 榜不再维护；引用必须写「冻结归档」并带快照日期 |

### 全文获取

| 渠道 | 端点 | 拿什么 | 鉴权与限额 | 坑 |
|---|---|---|---|---|
| Unpaywall | `api.unpaywall.org/v2/<doi>?email=<邮箱>` | OA 位置与 PDF 直链 | 邮箱必填 | OA 状态随时间变，记访问日期 |
| CORE | `core.ac.uk` API | OA 仓储聚合全文 | 需 API key | 抽取质量参差，关键页回原文核对 |
| 出版方 OA 页 | 各会议期刊官网 | 权威版本 PDF | 免 key | 有些站对自动化访问不友好 |

### 趋势与热度

Hugging Face 每日论文、X、Reddit（`r/MachineLearning` 一类）、Hacker News。热度信号只用来发现线索，不作证据。要写进笔记的判断都要回到一手渠道核过。

## 按任务选主源

- 找一批论文：arXiv 与 OpenAlex 双跑，Semantic Scholar 补被引与参考文献。
- 定一篇论文的元数据：OpenAlex 或 Crossref 为主，arXiv 补预印本版本。
- 建人物图谱：OpenAlex 与 Semantic Scholar 为主，DBLP 校书目，ORCID 校履历（协议见 `scientist-profiles`）。
- 要评审意见：OpenReview；没有 OpenReview 的会议回官方 rebuttal 或公开评审渠道。
- 要代码与复现：GitHub 与 Hugging Face；Papers with Code 用冻结归档。
- 要全文：Unpaywall 找 OA 位置，再 arXiv、ACL Anthology、CVF、PMLR、NeurIPS proceedings 直取。

## 反模式

- 拿 Google Scholar 当唯一来源：无官方 API，抓取会被封，且条目常带错。
- 拿 Papers with Code 官网当活数据：已关停，只剩冻结归档。
- 拿聚合页或二手解读当一手证据：写进笔记前必须回到一手渠道。
- 并发硬刷任一渠道：先看限额表，429 退避，串行推进。

## 落盘（非 md 资料）

论文的 PDF、TeX 源、HTML、补充材料按 `raw/<YYYY-MM>/<学科>/<刊名>/<论文短名>/` 落盘，一目录一论文，目录名与它的摘要页、精读页同名；博客与其他在线文章按 `raw/<YYYY-MM>/<领域>/<站点>/<slug>/` 落盘，存网页快照与抽取正文，同走一目录一资源。四个段的取值口径见 `wiki-format` 的命名节。

- PDF：Unpaywall 给的 OA 直链、arXiv PDF、CVF、PMLR、NeurIPS proceedings 直取；付费墙后的版本记 URL 与访问状态，不留占位文件。
- TeX 源：arXiv e-print 包（`arxiv.org/e-print/<id>`），解开取主 tex 与图片，整包留在论文目录里。
- HTML：`arxiv.org/html/<id>` 或出版方 OA 页，供分节正文、公式、表格、图的阅读。
- 抽取文本：下载完成后在论文目录产出 `<slug>.extracted.md`，供检索与无 PDF 阅读器的链路使用。
- 代码不克隆进本仓：仓库 URL 与 commit 记进论文页，需要时临时拉到工作区再读。
- 从论文里抽取的图与该论文的自绘图都进这个论文目录的 `assets/`，命名与引用口径见 `wiki-format` 的图与媒体一节；页面用 `![[…]]` 按相对仓根路径引用，不复制图。
- 绘图脚本落 `tools/scripts/`，临时文件落 `tools/scratch/`（不入 git）。
- 摘要页落 `papers/abstracts/<slug>.md`（博客层 `blogs/abstracts/<slug>-abstract.md`），精读报告落 `papers/readings/<slug>.md`，slug 与资源目录同名。摘要页与精读页都带 `resource:` 指向本体目录，摘要页另链到精读页。两页的形状见 `wiki-format` 的资源层一节。
- 零散来源（采集快照、剪藏、对话导出）走 `raw/<YYYY-MM-DD>-<slug>.<ext>`。
