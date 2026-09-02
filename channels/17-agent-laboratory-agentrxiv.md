# 17 — Agent Laboratory + AgentRxiv + Claw AI Lab 协作式自主研究平台

| 维度 | 内容 |
|------|------|
| **机构** | Agent Laboratory: Johns Hopkins University (Samuel Schmidgall 等)；AgentRxiv: 同团队扩展；Claw AI Lab: NTU + A*STAR + Moxin Technology + NUIST/THU/USTC 联合团队 (Fan Wu 等 19 人) |
| **论文/发布时间** | Agent Laboratory arXiv:2501.04227 (2025-01, Findings of EMNLP 2025)；AgentRxiv arXiv:2503.18102 (2025-03-24)；Claw AI Lab arXiv:2605.22662 (2025-05-21) |
| **开源状态** | **完全开源 (MIT)**：Agent Laboratory https://github.com/SamuelSchmidgall/AgentLaboratory (5.8k ⭐, 802 fork)；AgentRxiv 框架同仓库；Claw AI Lab https://github.com/Claw-AI-Lab/Claw-AI-Lab + Claw-Code Harness https://github.com/ultraworkers/claw-code (Rust 实现) |
| **循环形态** | **三阶段串行 + 跨智能体协作 + 跨实验室累积 + 仪表盘可控迭代**：Lab 内 PhD/Postdoc/MLEngineer/Professor 角色分工完成 Literature Review → Experimentation → Report Writing；AgentRxiv 将成果发布为可检索预印本供其他 Lab 复用迭代；Claw 在此之上增加 Explore / Discussion / Reproduce 三模式与五层金字塔架构及跨层反馈 |
| **核心关键词** | Role-specialized multi-agent；AgentRxiv as HuggingFace for agents；lab-native dashboard；Claw-Code Harness；artifact-centered；sandbox + anti-fabrication |

## 1. 平台分层

### Agent Laboratory 三阶段流水线
```
Layer 3  Report Writing — 大纲生成、图表绘制、LaTeX 撰写、迭代审稿
Layer 2  Experimentation — 协同规划 → 数据准备 → 自动编码实验 → 执行与调试
Layer 1  Literature Review — 多智能体独立搜集 arXiv 论文并交叉分析
   底座  工具层：arXiv Search / HuggingFace Datasets / Python 执行 / LaTeX 编译 / 检查点持久化
   底座  模型层：支持 OpenAI o1/o3-mini/gpt-4o、DeepSeek-V3，可插拔 --llm-backend
```

### AgentRxiv 累积层 (叠加在 Lab 之上)
```
Layer 4  AgentRxiv Server — 中心化预印本服务器，存储 agent 产生的论文与代码
Layer 3  相似度检索引擎 — SentenceTransformer 预训练模型编码论文，相似度搜索返回相关工作
Layer 2  累积迭代接口 — agent 上传/检索/二次改进，形成跨 Lab 知识复利
Layer 1  复用 Lab 三阶段 — 检索到的 AgentRxiv 论文作为 Literature Review 输入
```

### Claw AI Lab 五层金字塔 (对 Lab 的重构)
```
Layer 5  Writing — 大纲 → 可视化 → 撰写 → 迭代评审，与实验结果强一致性校验
Layer 4  Experiment — 迭代优化循环，异常结果可回跳 Planning/Idea 层
Layer 3  Coding — 以 Claw-Code Harness 为核心的 agentic coding loop
Layer 2  Planning — 任务/依赖/里程碑结构化计划 + Good Enough 验证循环，支持下游反馈自适应修正
Layer 1  Idea — 多智能体并行提案 → 结构化辩论 → 共识收敛
  横切  Dashboard — 统一仪表盘：实时事件流、多项目监控、产物巡检、一键回滚/恢复
  横切  Harness — 本地 codebase/dataset/checkpoint ↔ 可执行实验的桥梁
```

论文强调 Claw 的定位转变：从隐藏的 prompt-to-paper 管道转向可交互的 AI 实验室，科研被视为持久且可巡检的过程而非黑盒流水线。

## 2. Capability 注册

- **Agent Laboratory：显式角色与工具注册**
  - 角色注册：`agents.py` 定义 PhD / Postdoc / MLEngineer / Professor 等角色，每角色绑定职责与 prompt 模板，协作时按阶段调度。Co-Pilot 模式通过 yaml `copilot-mode: true` 切换人机协作粒度。
  - 工具注册：`tools.py` 统一封装 arXiv、HuggingFace、Python、LaTeX 等外部工具；`experiment_configs/*.yaml` 声明任务笔记 (task-notes)、语言、编译选项等能力契约。
  - 产物注册：每阶段产物 (文献综述、实验计划、代码仓库、论文 LaTeX) 落盘为可复用 artifact，通过 `state_saves` 检查点索引。
- **AgentRxiv：论文即能力**
  - 每篇 agent 论文以 embedding 入库，作为可检索 capability；检索 API 暴露为 Lab 的文献工具，下游 Lab 可直接引用其方法与代码作为起点，论文本身成为可组合能力单元。
  - 实验配置 `MATH_agentrxiv.yaml` 演示如何将 AgentRxiv 检索注入 Literature Review。
- **Claw AI Lab：Harness 能力网关**
  - Claw-Code Harness 将本地代码库、数据集、checkpoint 抽象为可调度能力：通过受控工具集 (bash / read / write / edit / glob / grep) 读写并执行，注入只读 Python controller 负责时间预算、指标上报、结果固化与 NaN/Inf 检测。
  - 能力执行在沙盒工作区隔离，每任务独立 workspace；支持 smoke test 与 anti-fabrication 检查 (虚假指标/占位代码/mock 实现自动拦截)。

## 3. Trace 治理

- **Agent Laboratory：检查点即 trace**
  - `state_saves` 持久化每子任务状态，支持从任意检查点加载恢复，天然形成执行轨迹。LaTeX 编译链路可开关 (`--compile-latex`)，确保产物可审计。
  - 人类可通过 `task_notes_LLM` 注入计算资源说明 (GPU 型号/显存/CPU/存储) 与实验约束，trace 中显式记录资源边界。
- **AgentRxiv：跨 Lab 血缘**
  - 每篇上传论文保留来源 Lab、检索依据与迭代关系，形成跨实验室血缘图；相似度检索分数与引用关系显式存储，支持复现链路追溯。论文报告 MATH-500 上协作相对隔离基线提升 13.7%，该增益本身作为 trace 指标沉淀。
- **Claw AI Lab：仪表盘可观测性**
  - 统一 dashboard 提供实时事件流、多项目并发监控、产物巡检与一键回滚/恢复，所有跨层反馈 (如实验异常触发 Planning 重修) 均有事件记录。
  - Harness 层执行产物 (论文、代码、图表、实验日志) 统一回流至研究循环，执行输出 → 报告的一致性被显式校验，缓解部分运行/结果表失真的常见失效模式。论文内部 5 个 AI 研究案例对比 AutoResearchClaw，Claw 在 idea novelty / experiment completeness / presentation 上被 AI expert judge 一致优选 (平均 +15.5~16.5 分，研究类；复现类 +5.0 分)。

## 4. Flywheel 机制

- **Lab 内飞轮**：三阶段产物天然形成闭环 — 文献综述影响实验设计，实验结果回流至报告，报告质量通过 LLM 评审反馈至下一轮 idea。提示工程强调写详尽笔记与按需选用更强模型，形成人工调参与模型能力共同驱动的迭代。
- **跨 Lab 飞轮 (AgentRxiv 核心价值)**：AgentRxiv 使 agent 实验室之间产生累积式进步，检索-复用-再发布循环让有效方法被快速扩散并在后续任务上放大收益，论文称之为 analog to arXiv but for agents。
- **Claw 跨层飞轮**：五层之间非线性反馈 — 编码失败或实验异常可回跳至 Planning 甚至 Idea 层修正；Harness 的执行反馈 (指标、日志、失败模式) 持续精化上游计划。仪表盘沉淀的执行数据进一步用于优化角色分工与验证策略。
- **社区飞轮**：三系统均为开源，GitHub 上持续接收 PR (新模型后端、多语言 README、实验配置)，issue 驱动能力演进，形成与 DeepModeling 类似的开放供给循环。

## 5. 智能体架构与工具链

- **Agent Laboratory 架构**：LLM 驱动的角色化协作；o1/o3-mini 负责长推理，gpt-4o/deepseek-chat 负责常规生成；每角色通过 `inference.py` 统一推理入口调用；支持中/英/日/韩等 15+ 语言分支。
- **AgentRxiv 架构**：SentenceTransformer 检索 + 预印本存储 + Lab 集成 SDK，检索结果以结构化上下文注入下游 prompt。
- **Claw 架构**：GPT-5.4 主模型 + Gemini-3-Pro-Image-Preview 图表生成 + Qwen3.5-Plus/Qwen-Plus 兜底；五层各由专职 agent 负责，层间通过 validation loop 与跨层反馈协调；Claw-Code Harness (Rust) 作为执行可靠性核心，职责超出简单 wrapper，承担本地资产到可执行实验的完整链路。

## 6. 度量体系

- **Agent Laboratory**：以论文与代码仓库完整度、实验可复现性、报告质量为隐式度量；官方推荐在 MATH 等基准上用准确率衡量智能体实验增益。
- **AgentRxiv**：以跨 Lab 复用后的基准提升幅度量飞轮收益 (如 MATH-500 +13.7% relative gain)。
- **Claw AI Lab**：内部评估 4 主题 × 2 评审模型 (ChatGPT 5.4 Thinking / Gemini 3.1 Pro) × 6 维度 (技术深度与可复现性、结构与章节流、新颖性与贡献、清晰度与术语、逻辑论证、引用与证据支撑)，研究类任务平均增益 +15.5~16.5/100，复现类 +5.0/100。

## 7. 核心可借鉴点 → OMP 映射

| Lab/Rxiv/Claw 模式 | OMP 对应构件 | 移植建议 |
|---|---|---|
| 角色化 agent 分工 (PhD/Postdoc/MLEngineer/Professor) | `task` 角色 prompt 模板 | 为 `task` 定义角色枚举与职责契约，Conductor 按阶段 (文献/实验/写作) 路由到对应角色 prompt，避免单体过载 |
| 三阶段 + 检查点 state_saves | `task` 分阶段执行 + `hub` 状态持久化 | 将长研究拆为 LiteraturReview / Experiment / Report 三个 `task`，每阶段产物写入 `channels/` 并在 `hub` 登记 checkpoint，支持断点恢复与并发巡检 |
| AgentRxiv 论文即能力 + 相似度检索 | `channels/` 知识库 + 向量检索 | 将已沉淀的 `channels/*.md` 以 embedding 入库，新任务 Literature Review 阶段先做相似度检索，命中则作为上下文注入，实现跨任务复利 |
| Claw 五层金字塔 + 跨层反馈 | `task` DAG + `hub` 事件总线 | 用 `task` DAG 描述 Idea→Planning→Coding→Experiment→Writing 依赖，层间失败通过 `hub` 事件回跳上游重修，而非线性重试 |
| Claw-Code Harness 沙盒 + anti-fabrication | `eval` 沙盒执行 + 伪造检测 | `eval` 阶段在隔离 workspace 执行代码，注入只读 controller 做时间/指标/NaN 检测与 smoke test，结果不一致直接阻断报告生成 |
| Dashboard 实时事件流 + 一键回滚 | `hub` 仪表盘 + `schedule_prompt` 定时巡检 | 在 `hub` 上暴露事件流与 artifact 巡检视图，`schedule_prompt` 定期扫描失败任务并提供回滚/恢复入口 |

## 8. 潜在坑

- **角色协作开销**：多角色 LLM 调用成本与延迟随阶段线性增长，需通过模型分级 (强模型仅用于关键实验/终审) 控制预算，论文 Tip #2 明确提示此权衡。
- **检查点膨胀**：`state_saves` 持久化所有中间状态，长期运行易产生存储与序列化开销，需定期归档与裁剪。
- **AgentRxiv 质量漂移**：agent 生成论文若缺乏人工或自动验证闸门，低质内容会污染检索库并放大后续错误，依赖相似度而非质量分数排序时风险更高。
- **Harness 沙盒逃逸与资源竞争**：本地 codebase/dataset 直连执行需严格隔离与配额，否则多项目并发易产生文件系统与 GPU 竞争；Rust Harness 虽提供时间预算，但对超长训练任务仍需外部调度器。
- **评估主观性**：Claw 内部评估依赖 LLM judge (ChatGPT/Gemini)，与人类评审一致性未充分验证，易高估 presentation 而低估技术深度。

## 参考

- Schmidgall et al., Agent Laboratory: Using LLM Agents as Research Assistants, arXiv:2501.04227 — https://arxiv.org/pdf/2501.04227 / https://github.com/SamuelSchmidgall/AgentLaboratory
- Schmidgall & Moor, AgentRxiv: Towards Collaborative Autonomous Research, arXiv:2503.18102 — https://agentrxiv.github.io / https://www.alphaxiv.org/abs/2503.18102
- Wu et al., Claw AI Lab: An Autonomous Multi-Agent Research Team, arXiv:2605.22662 — https://arxiv.org/html/2605.22662v1 / https://github.com/Claw-AI-Lab/Claw-AI-Lab
- Claw-Code Harness https://github.com/ultraworkers/claw-code
