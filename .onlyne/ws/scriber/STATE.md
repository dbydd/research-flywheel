本文件是 scriber 的手帐面：记叙段写过程，条目段写本 role 索引；它不在注入链上

## 记叙

Qwen3.8-Flash-Next 一族本跳干完。仓库只有 README 与 tech_report.pdf 两件，任务书点名的 docs/ 与 release notes 当场查无，按现场写进核验备注，没回环要料。

抽图走的路线：pymupdf 的 `get_images` 只拉到 34 个嵌入子图面板（全在 18–21 页），矢量图拿不到；改成按 caption 定位、整页区域渲染，13 张 Figure 一张不差，dpi 220。抽取正文用 `pdftotext -layout` 加一段轻量结构化（节号转标题、Figure/Table 行转引用块），公式与表格线有失真，承重数字全部回 PDF 原页核过。

两处发现是顺手挖出来的。一：报告在 arXiv 有正式条目 2608.30320v1（2026-08-31，cs.CL，36 个个人作者），仓库 README 与模型卡都只指 PDF 与博客，没给 arXiv 链；两版 PDF 页数一致、摘要逐字一致、MD5 不同，两件都留在本目录。二：发布件里 `config.json` 与模型卡逐项对得上（48 层、full_attention_interval=4、512 专家、indexer_budget=2048、ngram_vocab_size_base=20000000、ple_layer_ids=[2]、hc_lowrank=320），架构类名直接叫 `Qwen4ExpForConditionalGeneration`，这跟 README 说的「Qwen4 架构预览」对得上，所以下游读 QSA 与 n-gram 的超参不用回博客。

取不到的东西三处，全部标了访问状态：官方博客 qwen.ai 三个页都是前端渲染，静态抓判为依赖 JavaScript；GitHub API 未认证额度在查 FlashQLA 仓库时触发 403，建仓时间与星数未取；OpenAlex 的 authors 端点与 raw_author_name 过滤都没回记录，作者面改由 arXiv 题录、报告 §6 名单与 Wikipedia 条目支撑。

引用谱系逐条回了 arXiv API（三批共 30 多个 id，均带发表日），一次批量查、带 sleep，没碰限额。改完一轮发现五个日期凭印象写错了（Megatron、Pascanu、临界批量、Highway、DenseNet），回查后就地修正——这提醒我：凡带日期的条目一律先查后写。承重断言里还有一处风险：基准条目的 arXiv id 凭记忆写进了表，回查发现参考文献列表里那些条目只给了会议名或 CoRR 号，于是整行改成按报告自身引法记录，把没核到的 id 删掉。

发布件时间线：权重仓 2026-08-24 建、报告 2026-08-26、commit 2026-08-27、arXiv 2026-08-31；同代三件并行（Qwen3.8-27B 08-05、Qwen3.8-2.4T-A95B 08-08、Flash-Next 08-24）。领导层换人这条写进了组特点：Junyang Lin 不在本件任何一档名单里，公开报道记他 2026-03 离开阿里。

## 条目

|条目|内容位置|
|---|---|
|Qwen3.8-Flash-Next 仓库本体、两版技术报告 PDF、抽取正文与 13 张图|`raw/2026-09/llm-architecture/github/qwen3.8-flash-next/`|
|Qwen3.8-Flash-Next 摘要页（规格表、四处架构改动、训练与评测数字）|`papers/abstracts/qwen3.8-flash-next-abstract.md`|
|Qwen3.8-Flash-Next context 增强页（五问、引用逐条回一手渠道、发布件 config 对齐表、核验备注）|`papers/context/qwen3.8-flash-next-context.md`|
|按 caption 定位整页区域渲染抽 PDF 矢量图的做法（pymupdf `get_images` 对矢量图无效时的替代）|`tools/scratch/qwen38next/`（临时件，用完可删）|
