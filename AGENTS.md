# 共享目标记录

## 主线

## 支线（进行中的工作，无完成标记：办完当场删条，任务族收敛由 scraper 兜底清本族；历史去 ledger 与 git 查，这里不留已完成项）

- DeepSeek-V4.1-Flash 精读报告的对质与定稿：已 handoff socrates，收束判定权在它；定稿后再定要不要出 `papers/decks/deepseek-v41-flash/` 演示产物。
- 报告 102 条参考文献里 51 条无 arXiv 编号（Muon、ViT、SigLIP、Adafactor、RMSNorm、MiniLLM、四个自家仓库、GLM-5.2/5.3、MiniMax M2.2、Seed-2.1-Pro、Qwen3.6-Max 一类），要回一手页得逐条检索。切分判据：按抽取文本行 2018–2416（Appendix 前）行首排版切条，编号一律从条目文本读得、不猜；GSM8K（2110.14168）一条 arXiv API 取不到元数据未档成；同日早先误档的六个目录（clip/siglip/flamingo/blip2/internlm-xcomposer/nocad，编号与标题错配或空件）已删。
- 两页改名执行待办（口径已定进正本）：`papers/abstracts/deepseek-v41-flash.md` 与 `papers/context/deepseek-v41-flash.md` 改 `-abstract`/`-context` 后缀，frontmatter slug 同改，引用侧路径式链接一并修；两文件未进版本库，直接 mv。等本轮对质收敛后动手，避开在跑的行文。

## 索引

|条目|内容位置|
|---|---|
|DeepSeek-V4.1-Flash 的精读报告（含 890 bytes/token 的分项复算与逐行拆表）|`papers/readings/2026-09/cs.CL/DeepSeek-AI/deepseek-v41-flash-reading.md`|
|DeepSeek-V4.1-Flash 的引文落点、组归属与补齐的 34 篇原文|`papers/context/deepseek-v41-flash.md`|
|Microsoft General Reasoning 组的产出主线（YoCo、YOCO-S/YOIO 与效率这条线）|`wiki/entities/microsoft-general-reasoning.md`|
|层维度省法四条实现与 CED 的关系|`wiki/attention/hybrid-attention.md`|
|KV 缓存压缩的四个维度|`wiki/attention/kv-cache-compression.md`|
|稀疏注意力谱系与 CSA2 的候选池|`wiki/attention/sparse-attention-lineage.md`|
|低精度训练的三条独立线|`wiki/precision/quantized-kv-cache.md`|
