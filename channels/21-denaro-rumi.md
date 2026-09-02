# 21 - Denario / AstroPilot-AI / Rumi / GFlowNet 假设生成系

> 领域：跨学科自主科研 / 天文 / 经济学 / 通用假设生成
> 关键词：端到端研究助理、假设多样性采样、知识图谱、terminal-native

## 1. 系统一览

| 系统 | 机构/作者 | 论文/发布时间 | 开源状态 |
|------|-----------|---------------|----------|
| **Denario** | AG2 + LangGraph 社区 / 科学计算研究者 | arXiv 2510.26887, 2025-10 | 论文公开，架构基于 AG2/LangGraph 可复现，部分 demo 代码 |
| **AstroPilot-AI** | 天文 AI 社区（Hyper Suprime-Cam / Rubin 相关团队） | Daedalus / NCSA / NRAO 综述 2024-2025 | 依托开放巡天数据，方法公开，平台未单点开源 |
| **Rumi (RUMI)** | Subhansh（17 岁独立开发者，后被 Decidr 收购） | GitHub 2025-2026，rumi.ai 服务至 2026-07-24 | GitHub 开源（josemanuelm9203/rumi），商业服务已下线 |
| **GFlowNet Hypothesis** | Mila / Yoshua Bengio 团队 + IBM GT4SD | 2022 奠基，2024-2026 集成到自主科学综述（ACS 2026, PMC 12932417） | IBM GT4SD 开源库含 GFlowNet 实现 |

## 2. 循环形态

### Denario：端到端科学助理
```
用户课题 → Idea Agent（生成研究想法）→ Literature Agent（检索+评估文献）
  → Plan Agent（制定研究计划）→ Code Agent（写代码+执行+可视化）
  → Report Agent（草拟论文/报告）→ 迭代链式调用，可回溯修正
```
基于 AG2 + LangGraph 编排，模块化工具调用。经济学演示：自动拉取 FRED 数据、清洗、跑计量回归、迭代模型设定、合成报告。定位是"有工具的推理模型"，而非单纯聊天机器人。NeurIPS 2025 Fair Universe 冠军验证了其在 10+ 学科的通用性。核心循环为 idea→文献→方法→Docker 执行→可视化→LaTeX→peer review。

### AstroPilot-AI：天文自主观测-分析-写作
```
巡天数据（HSC/LSST/Rubin）→ 深度学习视觉（实例分割：恒星/星系/暂态）
  → LLM 文献推理（基于全量天文文献训练的可信 LLM 提假设）
  → 分析流水线自动设计+代码生成 → 绘图+论文草稿
  → 观测提案自动提交 + 天气/仪器状态监控 + 目标重调度（闭环）
```
亮点：星系-恒星分类精度比传统 pipeline 高 5-10%，数据到可发表结果从数周压缩到数小时。非私有数据+开源工具链使天文成为 AI 自主科研的最佳试验场。

### Rumi：终端原生认知架构
```
用户 query → 领域自动检测 → 10 阶段发现流水线：
  文献摄入 → 知识图谱构建 → 矛盾/空白点检测 → 假设生成
  → 可检验性过滤 → 实验设计建议 → 持续迭代
```
数十个模块化 "brain" 组件，82 发现模块，16 阶段流水线，强调跨域通用（药物发现、材料、神经科学、气候、天文、生态、物理、数学）。GFlowNet 假设锦标赛+对抗性 skeptic review 是其特色。案例：KRAS G12C 耐药机制分析。特点是 terminal-native，适合 harness 的 CLI-first 设计。

### GFlowNet 假设生成：多样性采样驱动的闭环
```
GFlowNet 按 reward 正比采样假设/结构（分子图、材料配方、科学陈述）
  → 自动实验室/仿真平台评估 → 观测结果更新 reward 模型
  → GFlowNet 重采样 → 循环收敛
```
与传统 RL/贝叶斯优化"追最优"不同，GFlowNet 追求**多样且高潜力**的候选集，适合科学发现中多解释并存的场景。IBM GT4SD 已提供开箱即用实现，可与多智能体推理+机器人实验室集成。

## 3. 智能体架构

| 系统 | 架构 | 关键设计 |
|------|------|----------|
| Denario | Multi-agent (AG2+LangGraph) | 角色分工明确（idea/lit/plan/code/report），状态图驱动，可中断恢复，Docker 执行隔离 |
| AstroPilot-AI | LLM + Vision + 调度器三层 | 感知（视觉）与推理（LLM）解耦，调度器负责望远镜资源编排 |
| Rumi | 终端原生 + 10-stage pipeline + 知识图谱 | 82 brain 模块可插拔，知识图谱作为共享记忆，锦标赛保持多样性 |
| GFlowNet | 生成模型 + 闭环控制器 | 采样器与评估器分离，reward 建模是核心，适合与 MAS 集成 |

## 4. 工具链

- **Denario**: AG2, LangGraph, Python 数据科学生态, FRED API, 文献检索（arXiv/Semantic Scholar）、Docker 沙箱、可视化（matplotlib/plotly）、LaTeX 生成
- **AstroPilot-AI**: HSC/LSST 数据管道、实例分割网络、光度红移估计、LLM（天文文献微调）、观测调度 API
- **Rumi**: Terminal UI、知识图谱（图数据库）、文献爬取、假设评分器、GFlowNet 锦标赛、对抗性 skeptic
- **GFlowNet**: GT4SD、PyTorch GFlowNet 实现、分子/材料表征工具、贝叶斯 reward 建模、机器人实验室接口

## 5. 度量

- **Denario**: 任务完成度（能否产出可执行分析+报告）、代码可运行率、图表质量、人工复核"可发表基础"评分；经济学案例以回归显著性与稳健性为辅助指标
- **AstroPilot-AI**: 分类准确率（+5-10% vs 传统）、光度红移误差、端到端时间（周→小时）、观测提案接受率
- **Rumi**: 假设新颖性/可检验性（人工+LLM 评）、跨域覆盖度、知识图谱矛盾检测召回、锦标赛多样性指标
- **GFlowNet**: 采样多样性（distinct high-reward modes）、发现效率（达到阈值所需评估次数）、与 MCMC/RL 对比的 mode coverage

## 6. 核心可借鉴点

1. **AG2+LangGraph 状态图编排**：Denario 证明用成熟编排框架即可搭出可用研究助理，harness 可直接复用其"plan→code→report"状态机与中断恢复机制。
2. **Docker 执行隔离**：Denario 的 Docker 沙箱是 OMP harness 沙箱的直接参考，harness 需同等隔离。
3. **领域数据开放性决定自动化天花板**：天文因数据非私有、工具开源，成为自主科研最顺滑的领域。harness 选试点领域时优先选数据开放、评估客观的赛道。
4. **感知-推理-调度三层分离**：AstroPilot 的视觉与 LLM 解耦避免"LLM 什么都做"的脆弱性，仪器调度独立一层保证实时性。
5. **知识图谱作为跨阶段记忆**：Rumi 用图谱承载文献矛盾与假设演化，比纯文本上下文更可追溯，harness 的"研究飞轮"可借鉴图式记忆。
6. **多样性采样而非最优化**：GFlowNet 的"按 reward 正比采样"思想对假设生成至关重要，避免早熟收敛到单一解释，harness 的 idea 阶段应显式鼓励多样性，锦标赛机制可直接复用。

## 7. 潜在坑

- **Denario 的"助理而非研究员"定位**：通用指令下易退化为被动助手，需强 prompt 约束其主动性；经济学数据清洗环节幻觉率高。
- **天文数据规模陷阱**：LSST 级数据量（TB/夜）对 pipeline 吞吐与存储要求极高，demo 易在小样本上过拟合。
- **Rumi 收购下线风险**：独立开发者项目被收购后服务即下线（2026-07-24），依赖单点商业服务不可持续；开源版功能滞后。
- **GFlowNet reward 设计难**：reward 信号稀疏/噪声大时采样退化，需配合主动学习与不确定性建模，否则多样性沦为随机性。
- **跨域通用 vs 深度不足**：Rumi/GFlowNet 宣称跨 8+ 领域，但每域深度不及专用系统，harness 需在通用与专用间做取舍。
- **评估主观性**：假设新颖性、可发表性高度依赖人工判断，自动化度量易被 LLM 互评"互吹"污染。

## 8. 信息来源

- Denario: arXiv 2510.26887
- AstroPilot: amacad.org Daedalus "AI Reaches for the Stars", NCSA DeepDISC, NRAO Cosmic AI Institute
- Rumi: dev.to Subhansh 自述, github.com/josemanuelm9203/rumi, rumi.ai 下线公告, arXiv 2608.05179 Survey
- GFlowNet: moonfire.com AI for Scientific Discovery 读书单, PMC12932417, ACS AMI 2026 8/6, IBM GT4SD, arXiv 2505.04651

---
*调研时间：2026-09-02 | 验证方式：web_search + 论文/官网交叉验证*
