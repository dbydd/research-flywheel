# 14 — 自驱动实验室 SDL：Toronto Acceleration Consortium + Berkeley A-Lab

| 维度 | Toronto Acceleration Consortium (U Toronto, Alan Aspuru-Guzik) | Berkeley A-Lab (LBNL, Gerbrand Ceder / Kristin Persson) |
|------|---------------------------------------------------------------|--------------------------------------------------------|
| 机构 | 多伦多大学 Acceleration Consortium, Matter Lab, Vector Institute | Lawrence Berkeley National Laboratory, CEDER Group, 材料科学部 |
| 论文/发布时间 | AC 官网 + ChemOS/Ada 2022-至今；SDL2 有机小分子平台 6 个用户设施 | Nature 624, 86-91 (2023.11.29) `10.1038/s41586-023-06734-w` |
| 循环形态 | Design–Make–Test–Analyze 全自动闭环，AI 提配方 → 机器人合成 → HPLC/MS 表征 → 主动学习迭代 | 计算筛选 → 文献启发配方 → 机器人固相合成 → XRD/ML 解析 → ARROWS3 主动学习重提配方 |
| 智能体架构 | ChemOS 编排层 + 模块化 SDL (Ada 等) + 贝叶斯优化 / LLM 规划 | 双 ML 配方模型 (相似度 + 温度) + ARROWS3 热力学主动学习 + XRD 概率深度学习解析 |
| 工具链 | ChemOS, 机械臂, 液体处理, 合成反应器, HPLC/MS, 40+ 联盟 SDL 联邦 | Materials Project + Google DeepMind 数据库, 文本挖掘合成模型, 4 台箱式炉, XRD + 自动 Rietveld 精修 |
| 度量 | 联盟 6+1 设施、40+ 联邦 SDL；Ada 支撑药物早期发现筛选 | 17 天 353 实验，57 目标中 36 成功 (63%)，吞吐 20-25 实验/天 (50-100× 人工)，最终校正后 67-70% |
| 开源状态 | ChemOS 开源 (GitHub AccelerationConsortium), 硬件设计开放 | 算法与数据开放，硬件为 LBNL 定制；ARROWS3 论文开源 |
| 潜在坑 | 硬件异构整合难、跨实验室可复现性、耗材补给 | 慢动力学/前驱体挥发/非晶化/0K DFT 误差；单次 4h 烧结限制纯度 |

## 闭环形态详解

**Toronto AC** 的 SDL 强调 Design–Make–Test–Analyze 四步飞轮。设计由 AI (贝叶斯优化或 LLM) 提出候选分子/配方，Make 由液体处理与合成机器人执行，Test 由 HPLC/MS 等分析仪器完成，Analyze 由 ChemOS 汇总数据并驱动下一轮设计。Ada 作为旗舰 SDL 专攻有机小分子，支持药物与功能材料发现。联邦模式让 40+ 实验室共享同一 ChemOS 接口，闭环可在不同物理站点间迁移。

**Berkeley A-Lab** 闭环更重无机粉末固相合成。起点是 Materials Project 与 DeepMind 的 DFT 凸包筛选出空气稳定的新材料 (57 目标)，经文本挖掘的相似度模型提至多 5 个配方，再由温度预测模型定烧结温度。机器人执行称量-混合-装坩埚-装炉-烧结-研磨-XRD 全流程，ML 解析 XRD 产物相纯度，未达 50% 产率则进入 ARROWS3 主动学习，选择最大热力学驱动力的替代路径。

## 智能体架构

- **Toronto**：ChemOS 为中央编排器，类似操作系统内核，向上暴露 `design/make/test` API，向下对接各仪器驱动。智能体可为贝叶斯优化器、LLM 或人类，形成"AI 提议 + ChemOS 执行"的松耦合。
- **A-Lab**：双阶段智能体——文献启发阶段模仿人类类比思维，失败后切换 ARROWS3，基于成对反应数据库与 DFT 反应能做热力学推理。XRD 解析由两个概率 ML 模型协同完成，结果自动精修后回灌 ARROWS3。

## 工具链

- **Toronto**：ChemOS (开源 Python), 机械臂、液体工作站、合成反应器、HPLC/MS、开放硬件文档；与 Matter Lab/Vector Institute 协作的软件栈。
- **A-Lab**：Materials Project API、文献文本挖掘模型、箱式炉阵列、XRD + ICSD 训练的概率相识别模型、自动 Rietveld 精修、ARROWS3 反应路径推理。

## 硬件抽象

**Toronto ChemOS** 是硬件抽象的典范：所有仪器背后用统一工作流语言描述，AI 只发高层 `transfer / heat / analyze` 指令，ChemOS 负责翻译为设备特定协议。新仪器接入只需实现 ChemOS 驱动接口，无需改上层算法。联邦 SDL 共享同一抽象，支持跨站点任务迁移。

**A-Lab** 抽象为三站式流水线：样品制备站 (粉末定量/混合)、加热站 (4 炉并行)、表征站 (研磨+XRD)，机械臂负责站间转运。全部通过 API 支持人类或 Agent 动态提交任务 (on-the-fly job submission)，加热与表征参数通过配置文件声明，切换目标材料无需重编程机械臂。

## 安全约束

- **Toronto**：依托化学实验室标准安全规程与 ChemOS 的权限控制，未披露显式 GHS 自动拦截，安全更多靠实验室准入与操作员监督。联盟层面承诺 ethical design principles。
- **A-Lab**：筛选阶段即排除在 O2/CO2/H2O 下不稳定的目标，限制前驱体为 binary 空气稳定化合物，从源头降低安全风险。硬件在开放空气环境操作，未涉及有毒气体闭环处理。

## 调度

- **Toronto**：ChemOS 负责跨仪器调度，支持多任务队列与联邦调度，SDL2 已验证多 SDL 协同。
- **A-Lab**：API 驱动的作业队列，4 炉并行加热，机械臂串行转运，XRD 表征为瓶颈。通过 pairwise 反应数据库剪枝，可将搜索空间减少至 20% (最多 80% 剪枝)，显著降低无效实验。17 天连续运行体现 24/7 调度能力。

## 失败处理

**A-Lab** 对失败分类最细致，四类 failure modes：
1. **慢动力学** (11/17 失败)：驱动力 <50 meV/atom，需更高温/更长时间/中间研磨，A-Lab 当前单次 4h 限制导致，需人工二次研磨+高温补救 (成功 2 例，成功率提至 67%)。
2. **前驱体挥发** (如 CaCr2P2O9 的铵盐磷酸盐 >450°C 蒸发)：若磷酸盐先与 Mn 氧化物低温反应生成 Mn2(PO4)3 则可锁定，数据库积累后可学习规避。
3. **产物非晶化**：XRD 无法识别，需补其他表征。
4. **DFT 计算误差** (0K 近似)：3 个目标分解能存疑，改进计算可再提至 70%。
处理策略是数据库记忆 pairwise 反应，已见中间体对应的路径直接跳过 (同中间体不同前驱体不重复高温尝试)，并优先大驱动力路径 (如 CaFe2P2O9 从 8 → 77 meV/atom 产率提升 70%)。

**Toronto** 失败处理依赖 ChemOS 的错误回传与贝叶斯优化的探索-利用平衡，异常样本自动标记并触发重采样。

## 度量与评估

- **A-Lab**：353 配方中仅 30% 产出目标，但 63% 目标至少一次成功，说明配方选择比单一实验更关键。成功率随目标-参考文献相似度正相关。
- **Toronto**：以联盟规模与药物发现管线提速为度量，单一 SDL 吞吐未公开绝对数字，但强调"分数时间与成本"对比人工。

## 核心可借鉴点

1. **ChemOS 式 OS 抽象**：把实验室抽象为操作系统，仪器即驱动，对 OMP 设计最有参考价值。
2. **文献类比 + 热力学主动学习两段式**：先模仿人类，再用物理原理纠错，兼顾知识与原理。
3. **Pairwise 反应数据库**：用实验积累的反应知识剪枝搜索空间，比纯模型预测更可靠。
4. **联邦 SDL**：40+ 实验室共享接口，证明硬件抽象可跨站点复用。

## 潜在坑

- 固相粉末的物理异构 (密度/流动性/硬度) 让液体 SDL 经验难以直接迁移。
- 单次烧结时长与是否研磨的限制显著影响成功率，硬件能力边界需在调度中显式建模。
- DFT 凸包筛选的假阳性会浪费大量实验，计算-实验闭环需双向反馈。
- 联邦模式的跨实验室标定与耗材补给是运营难点。

## OMP 硬件/仿真 Capability 抽象映射

- 借鉴 ChemOS，将每类仪器注册为 `capability`：`capability: { id: "furnace_array", type: "hardware", actions: ["dose","mix","heat","grind","xrd"], params_schema: {...}, constraints: { max_temp, max_time, air_stable_only } }`，OMP 调度器只认 capability 接口，不认具体型号。
- 仿真与真机同接口：`MatterSim / DFT` 实现 `heat` 的仿真分支，返回模拟 XRD 与相纯度；真机 `xrd` capability 返回实测数据。ARROWS3 这类主动学习器同时消费两种来源，OMP 通过 `capability.simulate: true` flag 路由。
- 调度层实现三站流水线的 DAG：`dose -> heat (4 并行) -> xrd (串行)`，资源争用由 OMP 的 `resource_pool: { furnaces: 4, xrd: 1, arms: 2 }` 建模；pairwise 反应数据库作为 OMP 的 `memory_store` 持久化，失败路径自动剪枝并反馈给 planner。
- 安全约束前置：`capability` 声明 `air_stable_only: true` 时，OMP 在设计阶段即过滤不稳定目标，不等到执行才失败。

> 来源验证：LBNL Nature 论文全文 (含 Fig.1-4 与 SI) + AC 官网/LinkedIn + Berke­ley CEDER 组页 + Chemistry World 对 A-Lab 的质疑与校正报道 (2026.01 校正 40/57)。
