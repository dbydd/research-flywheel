# Layer 1 — 化学 / 材料 / SDL / 机器人闭环：可迁移设计原则

> 范围：channels/_index-chemmat.md、11-coscientist-cmu.md、12-chemcrow-epfl.md、13-sciagents-mit.md、14-sdl-toronto-berkeley.md、15-mattergen-microsoft.md、22-cloud-synthesis.md
> 写作约束：区分来源事实与推断，来源事实标注 [事实]，推断标注 [推断]。每条原则提供证据、机制、收益、失效模式、对 OMP/PI 的启示。
> 调研时间：2026-09-02

---

## 原则 1 — 文档即驱动：向量化仪器文档替代手写适配器

**证据**
- 系统：Coscientist (CMU + Emerald Cloud Lab)
- 文件：`channels/11-coscientist-cmu.md`、`channels/_index-chemmat.md#硬件抽象的四种范式`
- 来源：Nature 624, 570-578 (2023) `10.1038/s41586-023-06792-0`；CMU 新闻稿；Chemistry World 报道

**机制**
- [事实] Coscientist 设 Documentation 模块，使用 OpenAI ada embedding 将 Opentrons OT-2 与 ECL Symbolic Lab Language (SLL) 文档切块向量化，按任务意图检索召回后注入 GPT-4 prompt，生成可执行 Python protocol 或 SLL 程序。
- [事实] 论文展示补充 SLL 文档即可让 GPT-4 学会新 DSL，无需重训。
- [推断] 该机制本质是把 capability 的 `doc_ref` 作为运行时知识，planner 通过 RAG 动态学习接口。

**收益**
- 新硬件接入成本接近零代码，仅需新增一条文档向量索引。论文验证同一架构同时打通高层 SLL 与低层 OT-2 两种抽象粒度。

**失效模式**
- 文档不全、过时、示例缺失导致幻觉代码，生成调用不存在的函数签名。
- Embedding 召回噪声引入无关 API，增加幻觉面。

**对 OMP/PI 的启示**
- 每个 capability 声明 `doc_ref` 字段，OMP 在调度时将向量化文档 Top-K 注入 planner 上下文。硬件/仿真接入流程统一为“注册文档→向量化→可用”。
- PI 工作区可复用该模式承载自定义工具，文档质量纳入 capability 健康度指标。

---

## 原则 2 — 化学语义原语：validate → execute 两段式硬件抽象

**证据**
- 系统：ChemCrow + RoboRXN (EPFL/IBM)；A-Lab 三站流水线；Coscientist EXPERIMENT
- 文件：`channels/12-chemcrow-epfl.md`、`channels/14-sdl-toronto-berkeley.md`、`channels/_index-chemmat.md#OMP 如何抽象硬件/仿真为 Capability — 统一可借鉴方案`
- 来源：Nature Machine Intelligence 6, 525-535 (2024) `10.1038/s42256-024-00832-8`；LBNL Nature 624, 86-91 `10.1038/s41586-023-06734-w`；IBM RoboRXN 文档

**机制**
- [事实] RoboRXN 暴露 `synthesize` 与 `validate` 两类 API，ChemCrow 先调 `validate` 校验溶剂量、纯化步骤合法性，返回结构化 `{valid, errors[]}`。
- [事实] A-Lab 三站流水线抽象为 `dose → heat(并行) → xrd(串行)`，站间由机械臂转运，参数通过配置文件声明。
- [推断] 两段式的价值在于把不可逆的物理执行前移一层可逆的符号校验。

**收益**
- 校验失败在符号层被拦截，触发 LLM 自修正，无需浪费真实耗材与炉时。
- 相同接口可同时被仿真实现，调度器按 `simulate` flag 路由。

**失效模式**
- 校验器本身不完备，漏过物理不可行配方，执行侧才暴露错误。
- 校验与执行语义漂移，校验通过的步骤在不同批次前驱体上仍失败。

**对 OMP/PI 的启示**
- OMP 统一契约：`validate(procedure) -> {valid, errors[]}` 与 `execute(procedure) -> observation` 同签名，硬件与仿真共用。PI 为每个新仪器实现轻量 validate 分支即可获得 ChemCrow 式的鲁棒修正循环。

---

## 原则 3 — 安全作为 capability 的 pre_filter，而非 LLM 自觉

**证据**
- 系统：ChemCrow GHS 工具链；A-Lab 源头过滤；Coscientist 反例
- 文件：`channels/12-chemcrow-epfl.md#安全约束`、`channels/14-sdl-toronto-berkeley.md#安全约束`、`channels/11-coscientist-cmu.md#安全约束`
- 来源：ChemCrow 论文 Safety 类工具描述；A-Lab 论文空气稳定性筛选章节

**机制**
- [事实] ChemCrow 每次合成前强制调用 Safety 类工具评估 GHS 分类，属显式工具约束；论文强调“缓解实验室安全顾虑，自适应机器人平台特定条件”。
- [事实] A-Lab 在计算筛选阶段即排除在 O2/CO2/H2O 下不稳定的目标，前驱体限定为 binary 空气稳定化合物，属于源头过滤。
- [事实] Coscientist 未内置独立安全校验层，依赖 GPT-4 拒答与 ECL 云端人工审核，被汇总文件标记为反例。
- [推断] 安全约束在 capability 编排层强制执行优于在 prompt 中呼吁 LLM 自律。

**收益**
- 高危请求在路由前被阻断，可审计，可要求人工确认，风险可控。

**失效模式**
- 安全工具误判导致误放行或误拦截；工具输出错误会级联至推理层得出错误结论。
- 训练数据过滤不完整导致漏过新型危险组合。

**对 OMP/PI 的启示**
- OMP 在 `capability` 声明 `safety_tags` 与 `requires_approval`，任何 `execute` 前强制调用 `chem.safety.ghs` pre_filter。PI 工作区复用同一拦截器，危险操作进入人工确认队列。

---

## 原则 4 — 结构化错误回灌的自修复循环

**证据**
- 系统：Coscientist 加热振荡模块修正；ChemCrow 溶剂增量修正
- 文件：`channels/11-coscientist-cmu.md#失败处理`、`channels/12-chemcrow-epfl.md#失败处理`
- 来源：Coscientist 论文 Fig.1 与 SI 报错修正案例；ChemCrow 论文 validation-修正循环章节

**机制**
- [事实] Coscientist 对执行失败读取报错原文，重新检索文档，重写脚本后成功执行；PYTHON 模块具备同类错误回显自修复。
- [事实] ChemCrow 查询 RoboRXN validation data 定位 not enough solvent / invalid purify 等无效动作，迭代调整参数直至 fully valid。
- [推断] 自修复循环等价于 ReAct 的 observation→thought 边，关键是错误信息保持结构化与原文保真。

**收益**
- 单次幻觉或参数错误无需人工介入，串行任务自动恢复，显著提升千次/周末吞吐下的无人值守可用性。

**失效模式**
- 知识缺口型失败纯重试无效，Coscientist 对 ibuprofen 等复杂分子仍需外挂 Reaxys/SciFinder 反应数据库或引入 Tree-of-Thought。
- 错误信息噪声或截断导致 LLM 误诊，修正方向偏离。

**对 OMP/PI 的启示**
- OMP 的 `execute` 返回值统一包含 `stderr + doc_hints`，planner 固定执行“观测→检索→重写”一步。PI 的日志归档保留完整 validator 报错，为复盘提供可追溯链路。

---

## 原则 5 — 失败记忆持久化与 pairwise 反应数据库剪枝

**证据**
- 系统：A-Lab pairwise 反应数据库；Toronto ChemOS 异常样本标记；SciAgents 负样本入图
- 文件：`channels/14-sdl-toronto-berkeley.md#失败处理`、`channels/13-sciagents-mit.md#失败处理`、`channels/22-cloud-synthesis.md`
- 来源：A-Lab Nature SI 中间体去重与热力学驱动力章节；Chemistry World 2024-01-16 质疑分析

**机制**
- [事实] A-Lab 积累 pairwise 中间体反应记录，已见中间体对应的路径直接跳过，最多剪枝 80% 搜索空间；驱动力从 8 提升至 77 meV/atom 对应产率提升 70% 的案例验证该机制。
- [事实] A-Lab 将失败分为慢动力学、前驱体挥发、非晶化、DFT 误差四类，慢动力学占 11/17，单次 4h 烧结限制是主因。
- [事实] SciAgents 将验证失败的假说标记为 unverified 保留在图谱中，作为负样本参与后续采样。

**收益**
- 实验预算聚焦未见路径，重复高温尝试显著减少，十次量级实验后搜索效率提升。

**失效模式**
- 数据库冷启动稀疏，早期剪枝过度导致漏过真实可行路径。
- 中间体判定依赖 XRD 相识别，误判会造成错误剪枝。

**对 OMP/PI 的启示**
- 在 OMP 引入 `memory_store` capability，固化三类记忆：pairwise 反应表、合成校验错误、图谱负样本。planner 每次提配方前先查 `memory_store` 做负向过滤。PI 侧将该表作为跨运行共享的持久化知识库。

---

## 原则 6 — 设计与执行物理分离、逻辑闭环的全球联邦

**证据**
- 系统：DigCat 全球闭环；Toronto AC 联邦 SDL；RoboRXN 云端合成；MatterGen 计算-实验分离
- 文件：`channels/22-cloud-synthesis.md`、`channels/14-sdl-toronto-berkeley.md`、`channels/15-mattergen-microsoft.md`
- 来源：DigCat ChemRxiv 2024-jsqqn；AC 官网 ChemOS 联邦描述；MatterGen Nature 639, 624-632 `10.1038/s41586-025-08628-5`

**机制**
- [事实] DigCat 定义云端 AI 设计（>400k 实验记录+400k 催化剂结构训练）→ 云端指令分发 → 分布式自动合成 → 表征回流 → 双模型更新。
- [事实] Toronto AC 通过 ChemOS 实现 40+ 实验室共享同一接口，6+1 设施联邦运行，闭环可在不同物理站点迁移。
- [事实] MatterGen 飞轮中生成器无需区分验证来自 MatterSim、DFT 还是实验室，只认 `score(structure)` 统一契约。

**收益**
- AI 侧获得广度，硬件侧获得可信度，异地并行提升吞吐，小团队可借用云端能力而非自建 600 sq ft 级实验室。

**失效模式**
- 跨站点硬件指纹差异导致配方不可复现，前驱体批次与炉温均匀性引入系统偏差。
- 通信与权限隔离增加调度复杂度，远程指令需多级安全互锁。

**对 OMP/PI 的启示**
- OMP 将 capability 声明 `endpoint: local | remote | sim`，同一 planner 可编排多站点 DAG。PI 工作区支持“本地模拟→远程真机”两段式提交，附加硬件指纹校准参数。

---

## 原则 7 — 生成-批判分工与图谱作为共享记忆

**证据**
- 系统：SciAgents Ontologist/Scientist/Critic 群智；ChemCrow Critic 扩展
- 文件：`channels/13-sciagents-mit.md`、`channels/_index-chemmat.md#闭环形态对比`
- 来源：arXiv 2409.05556；lamm-mit/SciAgentsDiscovery GitHub；MARS 19 Agent 扩展报道

**机制**
- [事实] SciAgents 在本体知识图谱上随机游走采样子图，Ontologist 规范化概念，多个 Scientist 并行生成假说，Critic 挑错打分，检索器拉取文献验证，通过的假说以新边写回图谱。
- [事实] 图谱作为多 Agent 共享记忆，状态可持久化、可审计，in-situ learning 支持执行中策略更新。

**收益**
- 认知闭环无需物理执行即可产出高新颖性假说，批量并行提升多样性，批判关卡减少污染。

**失效模式**
- 图谱构建成本高，冷启动依赖大量文献抽取与人工本体设计。
- Critic 受限于自身知识漏判 hallucination，图谱膨胀导致检索与推理成本飙升。
- 缺乏物理验证时产生纸面创新，无法被实验证伪。

**对 OMP/PI 的启示**
- OMP 将知识图谱注册为 `knowledge_graph.query / expand` capability，与硬件 capability 同级调度。planner 批量产出 N 个假设，critic 与 validate 并行执行，失败项重入队而非阻塞整批。PI 的议题探索可用该流水线先做认知闭环，再对接 SDL 真机。

---

## 原则 8 — 仿真即硬件：统一 calculator/score 接口与分层验证

**证据**
- 系统：MatterGen/MatterSim；A-Lab DFT 凸包筛选；Coscientist sim/real 双注册
- 文件：`channels/15-mattergen-microsoft.md`、`channels/14-sdl-toronto-berkeley.md#硬件抽象`、`channels/11-coscientist-cmu.md#OMP 硬件/仿真 Capability 抽象映射`
- 来源：MatterGen Nature；MatterSim arXiv 2405.04967；ASE/LAMMPS MatterSimCalculator 文档

**机制**
- [事实] MatterSim 被抽象为 `calculator` capability，输入晶体结构输出能量/力/应力/介电张量，MAE 36 meV/atom，覆盖前 89 元素、0-5000K、0-1000 GPa，推理速度比 M3GNet/CHGNet/MACE 快 3-5×。
- [事实] TaCr2O6 案例同时走 MatterSim 快速分支、DFT 精确分支、实验室真实分支三路验证，生成器只认 `score(structure) -> property`。
- [推断] 分层验证让验证成本下降数个量级，生成-验证飞轮得以高频迭代。

**收益**
- 1024 结构的批量生成可由 MatterSim 并行打分，仅 top-k 进入 DFT 与合成，实验预算聚焦最有希望候选。

**失效模式**
- DFT 误差、训练集偏向 ≤20 原子体系、多约束 Pareto 冲突在仿真层不可见，生成结构理论稳定但因动力学或缺陷无法合成。
- 仿真-实验 gap 持续放大，需实验室回流数据校正。

**对 OMP/PI 的启示**
- OMP 声明 `capability.policy: {mattersim: 快速阈值, dft: 精确阈值, lab: 合成阈值}`，调度器自动执行三层路由。PI 的材料工作区可先在 sim 分支做大规模扫参，再对精选结构触发真机。

---

## 原则 9 — 小样本条件化的 Adapter 与飞轮数据回流

**证据**
- 系统：MatterGen Adapter 微调 + classifier-free guidance；DigCat 双模型更新；SciAgents 图谱增量
- 文件：`channels/15-mattergen-microsoft.md#智能体架构`、`channels/22-cloud-synthesis.md#循环形态`
- 来源：MatterGen 论文 Fig.4-Fig.6 Adapter 章节；DigCat 双模型更新描述

**机制**
- [事实] MatterGen 在预训练基座每层注入可调 Adapter，用小规模带标签数据微调出化学组成、空间群、磁密度/带隙/体积模量等条件生成模型，含 HHI 供应链风险联合约束演示。
- [事实] MatterGen 飞轮为生成→MatterSim/DFT 验证→实验→数据回流再训练，SUN 指标涵盖 Stable/Unique/New 三维，论文报告 SUN 翻倍、RMSD 10× 优于基线、27 体系超越 substitution/RSS、TaCr2O6 体积模量误差 20% 内。
- [事实] DigCat 采用数据驱动+物理模型双更新，误差回流需显式记录。

**收益**
- 新性质约束无需全量重训，小标签数据即可衍生新条件生成器，模型随实验数据持续进化。

**失效模式**
- 多约束联合微调时 Pareto 权衡复杂，权重设置不当导致单目标过拟合。
- 回流数据含噪声或系统偏差会污染下一轮训练。

**对 OMP/PI 的启示**
- OMP 将 Adapter 映射为 `capability.fine_tune(dataset, constraints) -> new_capability`，模型注册表按 `property: bulk_modulus|band_gap|hhi` 动态路由。PI 的迭代任务可把实验回流数据自动转成 Adapter 训练集，形成本地飞轮。

---

## 原则 10 — 表征自动判读是闭环瓶颈，主动学习优于网格搜索

**证据**
- 系统：A-Lab XRD 概率 ML 解析 + 自动 Rietveld；Ada/ChemOS HPLC/MS；RoboRXN LC-MS/NMR；DigCat 异常检测
- 文件：`channels/14-sdl-toronto-berkeley.md#工具链`、`channels/22-cloud-synthesis.md#度量`
- 来源：A-Lab 论文 XRD 解析章节；Ada 平台药物筛选描述；Atinary SDLabs 贝叶斯优化案例

**机制**
- [事实] A-Lab XRD 解析由两个概率 ML 模型协同完成，结果自动精修后回灌 ARROWS3，XRD 表征为三站流水线的串行瓶颈。
- [事实] DigCat/A-Lab/RoboRXN 均采用 Bayesian/主动学习选择下一批实验，在 10-20 轮内收敛，替代网格搜索。
- [事实] Toronto Ada 与 DigCat 把异常检测作为独立模块，异常样本触发重采样。

**收益**
- 结果判读自动化让闭环无需人工盯盘，主动学习显著降低达到收敛所需的实验轮次。

**失效模式**
- 产物非晶化导致 XRD 无法识别，需补充其他表征，自动判读覆盖率受限。
- 高通量 ≠ 低成本，A-Lab 级硬件投入仅顶级机构可承担，小团队吞吐受限。

**对 OMP/PI 的启示**
- OMP 的实验闭环必须包含 `analyze` capability，调度器将 `dose→heat→xrd` 视为 DAG 并显式建模炉与表征资源的争用。PI 的实验规划默认配置主动学习策略，并为 XRD 失败预留多模态表征回退路径。

---

## 领域边界

**边界 1 — 粉末固相与液体/薄膜体系的物理不可迁移性**
- [事实] A-Lab 的失败分析指出粉末密度/流动性/硬度异构、前驱体挥发、单次 4h 烧结与是否研磨的限制显著影响成功率，液体 SDL 经验难以直接迁移。
- [推断] 固相合成的硬件约束需在调度中显式建模，化学工作区的配方模板按相态分仓管理。

**边界 2 — 仿真规模与保真度的上限**
- [事实] MatterGen 预训练集限定 ≤20 原子，大晶胞外推能力未知；DFT 0K 近似导致凸包假阳性浪费实验；MatterSim 误差随体系复杂度上升。
- [事实] A-Lab 63%→67%→70% 的校正路径显示，计算侧精度直接决定实验浪费比例。
- [推断] 仿真结论需经分层验证与实验交叉，工作区需为 DFT/MatterSim 误差设置显式不确定度通道。

**边界 3 — 自主合成的“成功”认定与新颖性审计**
- [事实] A-Lab Nature 论文声称 36-43 个新材料被 Chemistry World 质疑多为已知相或误判，2026-01 发布 correction，63% 成功率校正为 67-70%，争议焦点为 XRD 证据充分性。
- [事实] ChemCrow 的 14 用例采用 EvaluatorGPT 与专家三维评分，EvaluatorGPT 偏好流畅但 hallucinate 的回答。
- [推断] 工作区的成功度量必须可审计，要求附 XRD 原始数据与 Rietveld 精修报告，LLM 自评不能替代专家盲评。

---

## 推断汇总与不确定度

- 以上 [推断] 均基于跨系统类比与 OMP 能力映射，未在原文中逐字出现。置信度最高的是“文档即驱动→doc_ref 注册表”与“validate→execute 双接口”，已有 Coscientist 与 ChemCrow 的工程实现支撑。置信度较低的是“图谱共享记忆可直接对接 SDL 真机”，SciAgents 原文未提供物理闭环的端到端演示，MARS 扩展仍在早期。
- 本层未覆盖催化剂电化学性能的在线测试细节与 RobeRXN 多雲成本模型，属调研盲区，留待第二层深化。

---

## 来源索引

- Coscientist：Nature `10.1038/s41586-023-06792-0`；`channels/11-coscientist-cmu.md`
- ChemCrow：Nature MI `10.1038/s42256-024-00832-8`；arXiv 2304.05376；`channels/12-chemcrow-epfl.md`
- SciAgents：arXiv 2409.05556；`lamm-mit/SciAgentsDiscovery`；`channels/13-sciagents-mit.md`
- SDL Toronto + A-Lab：Nature `10.1038/s41586-023-06734-w`；AC 官网；`channels/14-sdl-toronto-berkeley.md`
- MatterGen/MatterSim：Nature `10.1038/s41586-025-08628-5`；arXiv 2312.03687 / 2405.04967；`channels/15-mattergen-microsoft.md`
- Cloud Synthesis：ChemRxiv 2024-jsqqn；`channels/22-cloud-synthesis.md`
- 汇总抽象：`channels/_index-chemmat.md`
