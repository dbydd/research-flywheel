# 08 - Google AI Co-Scientist：假设生成与进化式协作

| 字段 | 内容 |
|------|------|
| **机构** | Google Research + Google DeepMind + Google Cloud AI 联合团队；一作 Juraj Gottweis / Vivek Natarajan 等；合作方含 Fleming Initiative / Imperial College London、Houston Methodist、Sequome、Stanford |
| **论文/发布时间** | 2025-02-19 官方博客发布；预印 arXiv:2502.18864 / storage.googleapis.com/coscientist_paper/ai_coscientist.pdf；Nature 报道 2025 年中；对应验证论文2025.02.11.637232（cf-PICI）、Cell 共时论文 |
| **用途** | 面向生物医学的假设生成与研究提案助手：输入自然语言研究目标，输出新颖可验证假设、研究综述与实验方案；重点覆盖药物重定位、靶点发现、抗菌耐药机制等跨学科难题 |
| **验证状态** | 已完成三类湿实验/计算验证：AML 药物重定位（体外细胞系）、肝纤维化表观靶点（人肝类器官）、cf-PICI 基因转移机制（与既有未公开实验独立复现） |

## 循环形态

Co-Scientist 采用 Supervisor 调度的异步锦标赛进化循环：

1. **目标解析**：Supervisor 将研究目标解析为研究计划配置，分配资源与 worker 队列。
2. **生成-反思**：Generation Agent 通过文献挖掘与自博弈科学辩论批量产生初始假设；Reflection Agent 做快速合理性与新颖性过滤。
3. **锦标赛排序**：Ranking Agent 以 Elo 锦标赛做两两对比，Proximity Agent 聚类相似假设以便科学家导航。
4. **进化精炼**：Evolution Agent 对头部假设做重组、变异与扩展，生成新一轮假设。
5. **元复盘**：Meta-review Agent 综合多轮反馈指导下一轮生成方向，形成自我提升闭环。
6. **人机协作**：科学家可注入 seed idea 或自然语言反馈，系统支持多轮迭代；计算侧采用 test-time compute scaling，投入算力越多假设质量越高（Elo 与 GPQA Diamond 准确率正相关）。

单轮假设生成从传统数周缩短至数日，支持异步并行扩展，Elo 曲线随计算量单调提升。

## 智能体架构

| 角色 | 职责 | 基座 |
|------|------|------|
| Supervisor | 任务解析、资源分配、队列调度 | Gemini 2.0 |
| Generation | 文献探索、自博弈辩论生成假设 | Gemini 2.0 |
| Reflection | 快速与深度同行评审，过滤不可行假设 | Gemini 2.0 |
| Ranking | Elo 锦标赛两两排序 | Gemini 2.0 |
| Proximity | 相似假设聚类与去重 | Gemini 2.0 |
| Evolution | 对优胜假设做迭代进化与组合 | Gemini 2.0 |
| Meta-review | 跨循环综合反馈，指导下一轮 | Gemini 2.0 |

全员共享 Gemini 2.0 基座，通过角色 prompt 与独立反馈通道实现分工；系统信息流与智能体间反馈分离，支持递归自批判与工具反馈精炼。

## 工具/数据库

- **Gemini 2.0**：所有 Agent 的推理基座，提供长程规划与跨领域综合。
- **Web Search**：检索开放获取文献，增强 grounding。
- **专用 AI 模型**：针对特定验证场景调用专用模型（如计算生物学筛选、剂量响应拟合）。
- **Elo 自评系统**：锦标赛产生的自动评估指标，经验证与 GPQA Diamond 准确率、人专家偏好一致。
- **外部工具（规划中）**：论文提及未来增强包括事实核查、外部工具交叉验证（当前版本主要依赖内生辩论与 Elo）。

## 度量

- **Elo 自评**：随 test-time compute 提升而提升，与 GPQA Diamond 正确率正相关。
- **专家盲评（15 个开放目标）**：Co-Scientist 在自动化 Elo 上超越其他 SOTA agentic/reasoning 模型；11 个目标的人工新颖性与影响力评估中专家更偏好 Co-Scientist 输出。
- **湿实验指标**：
  - AML：3 个新重定位候选在多 AML 细胞系中以临床相关浓度抑制肿瘤活力，剂量响应曲线验证（如 KIRA6 对 KG-1）。
  - 肝纤维化：人肝类器官中多个候选显示抗纤维化活性，p < 0.01，部分逆转疾病表型。
  - cf-PICI：独立复现已知未公开发现（cf-PICI 与多样噬菌体尾互作扩展宿主范围），作为方法学验证。
- **系统侧**：假设新颖性、跨学科广度、实验方案可执行性。

## 闭环验证（湿实验/临床）

验证均在合作实验室完成，非纯自评：AML 为体外细胞系活力实验与临床专家反馈；肝纤维化为人源肝类器官（3D 多细胞培养）药效评估；cf-PICI 为与 Imperial 团队既有湿实验的独立 in silico 复现。该模式证明假设生成到湿实验的端到端可行性，但大规模前瞻性验证仍在 Trusted Tester 扩展中。

## 开源状态

闭源。系统通过 Trusted Tester Program 向研究机构限量开放，需申请表单；Gemini CLI 以 Apache 2.0 开源但不等同于 Co-Scientist。论文与技术报告开放，可复现思路但无法一键部署。未来是否开源未承诺。

## 核心可借鉴点

1. **假设即资产**：将假设作为一等对象，赋予 Elo 分数与谱系，进化过程可追溯。
2. **锦标赛即评估**：用 Elo 锦标赛替代昂贵的人工排序，评估与生成共享同一基座，形成自举。
3. **自博弈辩论**：Generation 通过多智能体辩论产生分歧假设，显著提升新颖性而非单一 LLM 采样。
4. **异步可扩展**：Supervisor 队列模型天然支持横向扩展，test-time scaling 收益明确。
5. **人机双向接口**：seed idea 与自然语言反馈让专家在高层引导而非底层执行。

## 潜在坑

- 闭源依赖 Gemini 2.0，复现成本与供应商锁定高。
- Elo 自评与真实湿实验成功率并非完全一致，存在 Goodhart 风险。
- 文献 grounding 依赖开放获取子集，对非开放数据与最新预印覆盖不足。
- 多智能体辩论易产生看似新颖但不可证伪的假设，需配套实验可行性过滤。
- 评估样本小（15 目标、11 人评），统计效力有限。

## 落到 OMP Workspace 的可实现机制

| 借鉴点 | OMP 实现 |
|--------|----------|
| Elo 锦标赛 | `template/co-scientist/elo-tournament.ts` 实现两两对比与 Elo 更新，`hub` 调度多 worker 并行打分，结果落 `channels/08-elo-board.md` |
| 自博弈辩论 | 为 Generation 配置正反方双 Agent prompt，产出 `debate-{round}.md`，Reflection 只放行分歧度高的假设 |
| 假设谱系 | 每个假设写入 `local://hypotheses/{id}.md` 含 parent_ids、Elo、实验方案，Evolution 通过 `read` 继承谱系 |
| 人机反馈 | 在 `WATCHDOG.yml` 定义 `human-feedback: natural-language`，专家评论直接作为 Meta-review 输入 |
| test-time scaling | 将 compute budget 暴露为 `budget.total` 参数，Supervisor 按 budget 动态增发 Evolution 轮次，收益曲线可视化到 `artifact://co-scientist/scaling.png` |

> 来源：research.google/blog 官方博文、arXiv:2502.18864、Google DeepMind 博客、Gadgets360 报道；已通过 read 验证六角色与三类验证细节。
