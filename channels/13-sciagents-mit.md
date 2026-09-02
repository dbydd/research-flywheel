# 13 — SciAgents (MIT LAMM / Buehler Lab)

| 维度 | 内容 |
|------|------|
| 机构 | MIT Laboratory for Atomistic and Molecular Mechanics (LAMM), Markus J. Buehler + Alireza Ghafarollahi |
| 论文/发布时间 | arXiv 2409.05556 (2024.09.09) → Synced/Advanced Materials 相关报道 2024 |
| 循环形态 | 图谱采样 → 多智能体假设生成 → Critic 批判 → 数据检索验证 → 假设精炼 → 新图谱边增量 |
| 智能体架构 | 群智多 Agent：Ontologist (概念抽取) + Scientist Agents (并行假说) + Critic (证伪) + 检索器 (LLM+RAG)，基于大规模本体知识图谱的图推理 |
| 工具链 | 本体知识图谱 (Ontological KG)、LLM (GPT-4 系列)、语义检索、图随机游走采样、开源 SciAgentsDiscovery GitHub |
| 度量 | 生物启发材料案例中发现多条人类未关联的跨学科路径；图谱规模化推理在假设多样性与新颖性上超越人类基线；框架可扩展至任意学科图谱 |
| 开源状态 | 开源 `lamm-mit/SciAgentsDiscovery`，含图谱构建与多 Agent 编排代码 |
| 潜在坑 | 图谱质量决定发现天花板；LLM 幻觉在图谱外推时放大；计算开销随图谱规模指数增长 |

## 闭环形态详解

SciAgents 的飞轮不是物理实验闭环，而是认知闭环。随机游走在本体知识图谱上采样概念子图，Ontologist 将其转为结构化定义，多个 Scientist Agent 并行生成假说，Critic 负责挑错与打分，检索器拉取最新文献验证或证伪，通过的假说以新边写回图谱，下一轮采样即可利用新增知识。论文在生物启发材料领域验证该循环能揭示"此前被认为无关"的隐藏关联，实现从假设到验证的自主迭代，相当于把 Design 阶段的文献与推理完全自动化。

## 智能体架构

核心是分工明确的"群智 (swarm of intelligence)"。Ontologist 负责概念规范化与关系抽取，Scientist Agents 各自持有不同视角并行探索，Critic 承担同行评审角色，形成生成-批判的对抗式协作。所有 Agent 共享同一知识图谱但持有独立 LLM 上下文，通过图谱作为共享记忆协调。in-situ learning 让 Agent 在执行中更新策略，而非仅靠预训练。架构灵感来自生物群体智能，强调模块化与可替换性。

## 工具链

- **知识图谱**：大规模本体图谱，节点为科学概念、材料、机制，边为因果/关联/层次关系
- **LLM**：GPT-4 类模型负责生成与批判，支持多模型混用
- **检索**：语义检索 + 数据拉取，用于假说验证与文献支撑
- **图算法**：随机路径采样、子图抽取、图推理
- **平台**：GitHub 开源实现，支持自定义图谱与 Agent 配置
近期扩展的 MARS 系统在此基础上集成 19 个 LLM Agent 与 16 个领域工具，形成层次化闭环的物理验证版本。

## 硬件抽象

SciAgents 本身不直连硬件，硬件抽象体现在"图谱→假设→可执行实验"的接口设计。假说输出为结构化设计原则与预期性质，可对接 A-Lab、RoboRXN 或仿真器作为下游执行器。抽象层将物理实验视为 `validate(hypothesis) -> evidence` 的 capability，图谱侧只关心输入输出 schema，不关心执行细节。这种"认知与执行分离"的设计让同一套假设生成器可对接不同实验室。

## 安全约束

论文未显式讨论化学/生物安全约束，安全隐含在 Critic 的"证伪"职责中——Critic 可被 prompt 为安全审查者，过滤高风险假设。图谱本体本身可编码安全本体 (如危险材料、受控路径)，在采样阶段即排除高风险子图。相比 ChemCrow 的 GHS 工具链，SciAgents 的安全是可插拔的策略层而非内置硬约束，部署时需显式加入。

## 调度

调度分为两层：图谱采样层随机并行采样多条路径，Agent 层并行生成与批判。天然支持批量假设生成，吞吐取决于 LLM 并发。批判与检索为同步关卡，只有通过验证的假设才写回图谱，避免污染。未披露显式任务队列，但架构支持异步多假说流水线。

## 失败处理

失败分为三类：图谱采样到无意义子图、LLM 生成 hallucinate 假说、检索验证失败。处理机制：Critic 直接打回并给出改进建议，触发 Scientist 重生成；检索失败的假说被标记为 "unverified" 而非丢弃，保留在图谱中待更多证据。论文强调通过多 Agent 交叉验证降低单一 LLM 幻觉，失败的假说本身也作为负样本丰富图谱。

## 度量与评估

评估聚焦假设质量：新颖性 (与现有文献的距离)、可验证性 (能否被检索/实验证实)、跨学科性 (连接此前无关领域)。案例研究显示系统在生物启发材料中发现的多条路径被专家认为"非平凡且有启发"。未用传统 accuracy，而是用专家盲评与图谱覆盖度衡量。

## 核心可借鉴点

1. **图谱作为共享记忆**：用本体图谱而非对话历史协调多 Agent，状态可持久化、可审计。
2. **生成-批判分工**：Ontologist/Scientist/Critic 三角色可直接映射为 OMP 的 planner/critic/verifier。
3. **随机游走采样**：用图算法保证探索多样性，避免 LLM 陷入局部模式。
4. **认知-执行分离**：假设生成与物理验证解耦，同一大脑可对接多实验室。

## 潜在坑

- 图谱构建成本高，冷启动需大量文献抽取与人工本体设计。
- LLM 批判能力受限于自身知识，Critic 可能漏判 hallucination。
- 图谱膨胀导致检索与推理成本飙升，需定期剪枝。
- 缺乏物理闭环时，假设无法被实验证伪，易产生"纸面创新"。

## OMP 硬件/仿真 Capability 抽象映射

- 将知识图谱抽象为 `capability: knowledge_graph { query(subgraph) -> concepts[], expand(hypothesis) -> new_edges[] }`，与硬件 capability 同级注册，Agent 统一通过 capability 调度器调用。
- 硬件与仿真均实现 `validate(hypothesis) -> {supported, evidence, confidence}` 接口，图谱侧的 Scientist 只发 `validate` 请求，OMP 根据 `mode: sim|real` 路由到 MatterSim/A-Lab/人工审核，返回的 evidence 自动写回图谱。
- 调度上把假设生成批处理化：`planner` 批量产出 N 个假设，`critic` 与 `validate` 并行执行，OMP 的 DAG 调度器将图谱采样→生成→批判→验证编排为流水线，失败假设触发重生成边而非阻塞整批。

> 来源验证：arXiv 2409.05556 全文 + GitHub lamm-mit/SciAgentsDiscovery + Synced/AlphaXiv 二次解读，交叉确认 Ontologist/Scientist/Critic 分工与群智隐喻。
