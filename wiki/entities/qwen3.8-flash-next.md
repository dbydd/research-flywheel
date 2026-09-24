---
title: Qwen3.8-Flash-Next
slug: qwen3.8-flash-next
type: entity
created: 2026-09-23
updated: 2026-09-23
sources:
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/README.md
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/tech_report.pdf
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/hf_model_card.md
  - raw/2026-09/llm-architecture/github/qwen3.8-flash-next/hf_config.json
  - papers/readings/2026-09/llm-architecture/github/qwen3.8-flash-next-reading.md
---

# Qwen3.8-Flash-Next

Qwen3.8-Flash-Next 是阿里巴巴 Qwen 团队放出的稀疏 MoE 多模态语言模型，125B 总参数、每 token 激活 6B，另有 51B n-gram 嵌入表放在加速器之外的主机内存、4B 多 token 预测参数。官方把它定位成架构预览件：这一版权重充当 Qwen4 所用架构的早期预览，角色等同于 Qwen3-Next 之于 Qwen3.5。发布件 `config.json` 的架构类名写作 `Qwen4ExpForConditionalGeneration`、model_type 写作 `qwen4_exp`。

发布节奏：Hugging Face 权重仓库 2026-08-24 创建，技术报告 PDF 元数据与 README 的 News 落在 2026-08-26，arXiv 条目 2608.30320v1 于 2026-08-31 提交（cs.CL）。权重先于报告、报告先于 arXiv 挂出。

## 规格

|项|取值|
|---|---|
|类型|带视觉编码器的因果语言模型（pipeline_tag 为 image-text-to-text）|
|参数|125B 总量、每 token 激活 6B；另加 51B n-gram 嵌入与 4B 多 token 预测|
|层数与排布|48 层，每四层一个稀疏注意力层，其余为 Gated DeltaNet 与 MoE|
|hidden / 词表|hidden 2560；token embedding 248320|
|GDN 线性注意力|V 头 48、QK 头 16，head_dim 128，短卷积核 4|
|QSA|核心注意力 head_dim 256、旋转维 64；索引器 MQA 4 查询头加 1 共享键头，head_dim 128，压缩比 4，预算 512 块（2048 token）|
|MoE|512 个路由专家，每 token 激活 10 个路由加 1 个共享|
|Gated Residual|4 条残差支路，低秩瓶颈 320，输出门 sigmoid|
|n-gram 嵌入|三阶，基础表 20,000,000 项，8 个哈希头，只挂第 2 层|
|多 token 预测|1 层|
|上下文|原生 262,144，按 YaRN 外推到 1,000,000|
|许可|Qwen Community License 1.0|

## 四处承重改动

注意力用 [[gated-deltanet|Gated DeltaNet]] 与全注意力的混合，配比取每四层一个全注意力层（见 [[hybrid-attention-layer-ratio|混合注意力的层间配比]]）；继续预训练阶段把这些全注意力层换成 [[qwen-sparse-attention|Qwen Sparse Attention]]。残差流加宽到 4 支并用[[gated-residual|逐元素读门]]读写。容量加在骨干之外的[[n-gram-embedding|一层 n-gram 嵌入]]。优化器换成按权重类别分工的[[muon-parameter-partitioning|Muon 加 AdamW]]，并为新架构[[batch-size-and-lr-scaling-refit|重拟合缩放律]]。四处改动同时读三条轴，协议见 [[three-axis-architecture-eval-protocol|三轴架构评估协议]]。

## 能力与成本

预训练基座对照取内部 Base 管线，14 项基准。Qwen3.8-Flash-Next-Base 对 27B 稠密基座 14 项全胜；对 397B-A17B 的 Qwen3.7-Plus-Base 赢 8 项，输的 6 项最大差 2.59 分（MultiPL-E）。

|基准|Flash-Next-Base|Qwen3.7-Plus-Base|
|---|---|---|
|MMLU|90.36|90.43|
|MMLU-Redux|90.68|91.47|
|MMLU-Pro|73.23|70.90|
|SuperGPQA|51.36|48.42|
|BBH|90.87|89.41|
|GPQA|51.42|51.52|
|GSM8K|93.29|92.95|
|MATH|72.78|74.38|
|EvalPlus|78.76|78.06|
|MultiPL-E|79.09|81.68|
|SWEBench-Pretrain|50.99|49.24|
|MGSM|89.33|85.42|
|MMMLU|84.86|84.53|
|INCLUDE|78.40|78.90|

成本口径：约三分之一激活参数、三分之一训练 token、约九分之一训练 FLOPs，对照对象是 397B-A17B 旗舰。

后训练件读数只出自模型卡自述，评测 harness 与采样参数写进脚注（温度 1.0、top_p 0.95、256K 窗口，两套 harness 取最高）。抽样：DeepSWE 1.1 取 58.7、SWE-bench Pro 62.5、SWE-bench Multilingual 81.0、CoWorkBench 73.9、ToolBench 类 Toolathlon Verified 73.5、IFBench 81.3、GPQA Diamond 91.7、LiveCodeBench v6 91.9、HLE 35.9、Agents' Last Exam pass@1 24.3；多模态侧 AndroidWorld 84.5、OSWorld 2.0 二值 19.4 与部分 52.3、Vision2Web 64.0、RecreationBench 49.9、ClawEval-MM pass@3 64.4、MathVision 无工具 90.6、CharXiv 无工具 84.6、LVBench 76.6、RealWorldQA 88.5、ERQA 72.3。口径折扣两条：CoWorkBench、RecreationBench、NL2Repo-Bench、ClawEval-MM 是自建基准；对照表里并列的 DeepSeek-V4-Flash-0731 与 Claude-Opus-4.6 (Max) 读数是 Qwen 侧跑的。

## 已知缺口

QSA 替换全注意力层时哪些预训练权重被丢弃、哪些被继承，报告未写。n-gram 表放主机内存的吞吐代价，本件没给同口径数字。训练算力、GPU 时数、语料量与数据配比一律没有绝对值，成本全部以相对 Qwen3.7-Plus 的比例表达。机制级结论全部来自 25B-A3B、35B-A3B、10.8B-A0.89B、156B-A7B 四档中小模型，生产件只出现在最终对照表与早期段对照。

本体的摘要页见 [[qwen3.8-flash-next-abstract|Qwen3.8-Flash-Next 摘要]]，精读报告见 [[qwen3.8-flash-next-reading|Qwen3.8-Flash-Next 精读]]。
