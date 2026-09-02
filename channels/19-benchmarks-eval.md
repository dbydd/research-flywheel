# 19 — 评测体系：PaperBench + DeepResearch Bench (I/II) + RE-Bench + EpiBench

| 维度 | 内容 |
|------|------|
| **机构** | PaperBench: OpenAI Preparedness (Starace 等, ICML 2025)；DeepResearch Bench I/II: 中科大 + Metastone (Du 等, arXiv:2506.11763 / 2601.08536)；RE-Bench: METR (Wijk 等, arXiv:2411.15114)；EpiBench: Dong 等 (arXiv:2604.05557, Claw 论文引用) |
| **发布时间** | PaperBench 2025-04-02 发布，20 篇 ICML 2024 Spotlight/Oral；DeepResearch Bench 2025-06 发布，100 任务；DeepResearch Bench II 2026-01 发布，132 任务；RE-Bench 2024-11 发布，7 环境；EpiBench 2026-04 发布，多轮多模态研究工作流 |
| **开源状态** | **全部开源**：PaperBench https://github.com/openai/paperbench + LLM judge；DeepResearch Bench https://github.com/Ayanami0730/deep_research_bench + https://deepresearch-bench.github.io + HF Leaderboard；RE-Bench https://github.com/METR/RE-Bench；EpiBench 开源评估套件 |
| **循环形态** | **评估即飞轮锚点**：任务定义 → 智能体执行 → 细粒度 rubric / 模型裁判评分 → 人类一致性校验 → 信号回流至平台与模型迭代；三体系分工覆盖复制、调研、工程三类能力 |
| **核心关键词** | Rubric co-developed with authors；RACE / FACT 双框架；LLM judge with human alignment；scaling law / kernel optimization；multi-turn multimodal |

## 1. 平台分层 (评测即基础设施)

评测体系本身构成可复用的基础设施分层，支撑上层平台的度量与进化：

```
Layer 4  飞轮应用层 — 榜单、回归检测、能力差距分析、训练信号回流
Layer 3  评分与裁判层 — PaperBench LLM judge / RACE 自适应加权 / FACT 引用审计 / RE-Bench 自动评分脚本
Layer 2  Rubric 与任务定义层 — 作者共创细粒度 rubric (PaperBench 8316 项 / Bench II 9430 项)、PhD 级任务 (Bench I 100 任务 22 领域 / Bench II 132 任务)、7 工程环境
Layer 1  执行与沙盒层 — 隔离执行环境、离线网页语料 (Bench I 每任务 10k-100k 页)、代码执行与产物采集
  横切  人类基线与一致性校验 — PaperBench 人类 PhD 41% vs 最强 agent 21%；RE-Bench 71 人次 8 小时人类尝试；Bench I 70+ 硕士标注员一致性标定
```

该分层体现评测作为平台的双重角色：对外提供可比分数，对内沉淀 rubric、裁判与人类基线三类可复用资产。

## 2. 各基准能力注册

- **PaperBench**：每篇论文 rubric 即能力契约，层级分解为可客观判分的子任务，涵盖理解贡献、编写完整代码库、复现实验与结果匹配；rubric 与原作者共创确保真实性；任务以可复现脚本形式注册，输入为论文原文，输出为代码与实验产物；变体 PaperBench Code-Dev 提供轻量注册。
- **DeepResearch Bench I**：100 个 PhD 级任务按 22 领域分布注册，任务分布依据 96,147 条真实用户查询中 44,019 条深度研究需求的聚类结果 (DeepSeek-V3-0324 分类)，中英各 50 题；每个任务绑定离线网页语料与参考报告，RACE 与 FACT 双框架分别注册为报告质量与检索能力评估器。
- **DeepResearch Bench II**：在 I 基础上扩展至 132 grounded 任务，引入 9,430 条二值专家 rubric，覆盖信息召回、分析、呈现三维度，提供更细粒度的诊断性评分与官方 evaluator 流水线 (数据集下载、报告生成 harness、格式转换、自动评分)。
- **RE-Bench**：7 个开放式 ML 研究工程环境注册为能力，包含 scaling law 拟合、GPU kernel 优化、超参预测等高天花板任务；每个环境提供参考解与自动评分，支持 Modular 与 AIDE 双 scaffold 接入。
- **EpiBench**：多轮多模态研究工作流基准，注册跨轮证据追踪与多模态产物评估能力，Claw 论文引用其作为长周期执行与证据完整性度量的补充视角。

注册共性：任务、参考答案、评分器均以版本化产物注册，支持按领域、难度、模态分面检索，执行时绑定明确输入输出与资源约束。

## 3. Trace 治理

- **PaperBench**：执行 trace 要求从论文文本出发重建完整实验管线，LLM judge 逐条 rubric 评分并给出证据，judge 本身在独立 judge benchmark 上验证可靠性；8,316 项原子评分形成细粒度可审计链路，支持定位失败位于理解、编码或执行哪一阶段。
- **DeepResearch Bench I**：RACE 框架采用参考驱动的自适应准则与动态加权，相对高质量参考报告评分，提升区分度；FACT 框架审计有效引用数与引用准确率，区分信息广度与溯源精度；人类一致性实验显示 RACE Full 整体 72.56%，显著高于 vanilla prompt 60.46%，其中去除参考项导致最大跌落，验证参考机制必要性；PAR 71.33% 超过人类互一致 68.44%，OPC 99.54% 体现强对齐。
- **DeepResearch Bench II**：以二值 rubric 替代模型裁判主观打分，提升可验证性与可解释性；132 任务 × 9,430 rubric 形成诊断矩阵，可定位智能体在召回、分析、呈现的具体短板；官方 leaderboard 上 OpenAI GPT-o3 Deep Research 整体 45.40% (召回 39.98 / 分析 49.85 / 呈现 89.16)，Gemini-3-Pro 44.60 紧随，呈现分数普遍高于召回与分析，揭示平台在信息综合与呈现上的相对优势。
- **RE-Bench**：每个环境提供插值损失等客观分数，71 人次人类 8 小时尝试形成人类基线分布 (82% 得分非零，24% 达到或超过强参考解)；模型端 Claude 3.5 Sonnet 在 2 小时预算下达到约 4 倍人类分数，Claude 3.7 Sonnet 在给定真实性能信息时表现突出；评分完全自动化，支持跨 scaffold 公平对比。
- **横切治理**：三体系均强调执行产物可回放、评分可复现、人类基线可对照；trace 中显式记录任务版本、裁判模型 (如 Bench I 选用 Gemini 2.5 Pro Preview 作为 judge，兼顾 72.56% 一致性与 $0.13 成本)、评分权重与引用链路，支撑回归检测与跨版本对比。

## 4. Flywheel 机制

- **分数回流至平台**：PaperBench 21% vs 人类 41% 的差距直接指向长周期研发能力的短板，OpenAI 将其纳入 Preparedness Framework 追踪；Bench I/II 的 RACE/FACT 双分揭示不同模型在广度与精度上的权衡，驱动 Perplexity 优化引用精度、Gemini 扩展有效引用广度的定向改进。
- **Rubric 沉淀**：作者共创 rubric 与专家二值 rubric 作为可复用知识资产，随任务迭代增量扩展；Bench II 相对 Bench I 的任务与 rubric 增长本身体现社区贡献飞轮。
- **裁判进化**：LLM judge 在独立 benchmark 上持续校验，Bench I 对比多种 judge (Gemini 2.5 Pro Preview / o3 / o4-mini / Claude 3.7 Sonnet) 的一致性与成本，o4-mini 以 $0.04 达到 71.63% 接近最优，形成成本-质量权衡信号回流至评估选型。
- **工程信号**：RE-Bench 的 7 环境覆盖 scaling law 与 kernel 优化等真实工程瓶颈，模型在其中的得分与人类基线的对比为训练与 scaffold 设计提供直接反馈；METR 预测 2026 年初 RE-Bench 1.3 分的目标未达成，该未达成信号本身驱动对长周期工程能力瓶颈的再定位。
- **跨基准协同**：PaperBench 测复制、DeepResearch Bench 测调研、RE-Bench 测工程，三者组合形成对自主研究全链路的覆盖，单一基准的提升需在其他基准上验证泛化，构成跨体系的制衡飞轮。

## 5. 智能体架构与工具链

- **PaperBench 执行栈**：隔离代码执行环境 + 论文文本输入 + 智能体 scaffold (支持 OpenAI o1/o3-mini、Claude 3.5 Sonnet、DeepSeek-R1、Gemini 2.0 Flash 等) + LLM judge 自动评分；作者共创 rubric 作为输入契约，执行产物为完整代码库与可复现脚本。
- **DeepResearch Bench 执行栈**：离线网页语料 + 报告生成 harness + 格式转换工具 + 官方 evaluator (RACE/FACT)；支持任意 DRA 接入，HF Leaderboard 统一展示；评估时以 Gemini 2.5 Pro Preview 为裁判，覆盖 Overall / Comprehensiveness / Depth / Instruction-following / Readability / Citation Accuracy / Effective Citations 七指标。
- **RE-Bench 执行栈**：7 容器化工程环境 + Modular / AIDE 双 scaffold + 自动评分脚本 + 人类基线数据集；支持 2 小时与 8 小时预算对比，输出插值损失等客观分数。
- **通用工具链**：Python 执行、搜索与文档解析、版本化数据集管理、HF Spaces 榜单、arXiv 论文与代码联动。

## 6. 度量体系详表

| 基准 | 任务规模 | 评分粒度 | 最强 Agent | 人类基线 | 关键发现 |
|------|----------|----------|------------|----------|----------|
| PaperBench | 20 论文 | 8,316 原子 rubric | Claude 3.5 Sonnet (new) 21% | 顶尖 ML PhD 41% | 复制仍远低于人类，长周期研发为瓶颈 |
| DeepResearch Bench I | 100 任务 22 领域 | RACE 5 维 + FACT 2 维 | Gemini-2.5-Pro DR 48.88 / OpenAI DR 46.98 | 70+ 标注员一致性 68.44% PAR | DRA 有效引用数显著高于带搜索 LLM，Perplexity 引用精度 90.24% 领先 |
| DeepResearch Bench II | 132 任务 | 9,430 二值 rubric | GPT-o3 DR 45.40% (呈现 89.16 / 分析 49.85 / 召回 39.98) | 专家 rubric 诊断 | 呈现远高于召回，信息召回为主要短板 |
| RE-Bench | 7 环境 | 自动客观分数 | Claude 3.5/3.7 Sonnet 约 4 倍人类 (2h) | 71 人次 8h，24% 超强参考解 | 2 小时 AI 已超人类，工程能力接近实用阈值，1.3 分目标未达成 |

EpiBench 补充多轮多模态维度，具体分数随任务集而异，核心价值在于跨轮证据追踪的诊断能力。

## 7. 核心可借鉴点 → OMP 映射

| 评测模式 | OMP 对应构件 | 移植建议 |
|----------|-------------|----------|
| 作者共创 rubric 层级分解 | `eval` rubric 注册 | 为每个 `channels/*.md` 定义层级 rubric (理解/复现/验证三级)，与任务作者共创，确保可客观判分 |
| RACE 参考驱动自适应加权 | `eval` 报告质量评估 | 引入高质量参考报告，相对评分并按维度动态加权，区分 comprehensiveness / depth / instruction-following |
| FACT 引用审计双指标 | `eval` 引用校验 | 自动统计有效引用数与引用准确率，引用不可验证直接扣分，作为 Deep Research 类任务的必检项 |
| 二值专家 rubric 诊断矩阵 | `eval` 细粒度诊断 | 对关键任务引入二值 rubric (通过/不通过)，形成召回/分析/呈现三维诊断，定位短板 |
| LLM judge 人类一致性标定 | `eval` 裁判选型 | 对裁判模型做 PAR/OPC/FAP/FAS 四指标标定，兼顾一致性与成本 (参考 Bench I 选型方法) |
| 人类基线对照 | `eval` 基线管理 | 为核心任务维护人类 8 小时基线分布，模型分数与基线同图展示，避免分数虚高 |
| 榜单与回归检测 | `hub` + `schedule_prompt` | `hub` 暴露 leaderboard 视图，`schedule_prompt` 定期重跑核心任务做回归检测，分数异常自动告警 |

## 8. 潜在坑

- **LLM judge 偏差**：裁判模型与被评模型同源时存在偏好偏差，Bench I 通过多裁判对比与人类一致性标定缓解，单一裁判易产生系统性高估。
- **Rubric 维护成本**：PaperBench 8,316 项与 Bench II 9,430 项 rubric 需与原作者协同，新增任务时人力成本高，自动化 rubric 生成质量待验证。
- **离线语料时效**：DeepResearch Bench 离线网页语料固定，难以反映实时网络变化，线上复测与离线分数可能背离。
- **工程环境泄露**：RE-Bench 任务若被纳入训练数据，分数虚高风险高，需严格隔离测试集与训练集。
- **单一维度优化**：针对 RACE 或 FACT 单一指标优化易产生偏科 (如堆引用数而忽略精度)，需双框架联合约束。
- **跨基准泛化**：在某一基准上领先不保证跨基准泛化，三体系需联合解读，单一榜单排名易误导迭代方向。

## 参考

- Starace et al., PaperBench: Evaluating AI's Ability to Replicate AI Research, arXiv:2504.01848 / https://openai.com/index/paperbench / ICML 2025
- Du et al., DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents, arXiv:2506.11763 — https://deepresearch-bench.github.io / https://github.com/Ayanami0730/deep_research_bench
- Bench II: Diagnosing Deep Research Agents via Rubrics from Expert Report, arXiv:2601.08536 — https://agentresearchlab.com/benchmarks/deepresearch-bench-ii/
- Wijk et al., RE-Bench: Evaluating Frontier AI R&D Capabilities, arXiv:2411.15114 — https://github.com/METR/RE-Bench / https://metr.org/blog/2024-11-22-evaluating-r-d-capabilities-of-llms
- Dong et al., EpiBench, arXiv:2604.05557
