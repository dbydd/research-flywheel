# Layer 1 物理、数值科学、跨学科假设生成证据分析

> 范围：`channels/_index-physics-misc.md`、`20-physics-autonumerics.md`、`21-denaro-rumi.md`、`22-cloud-synthesis.md`、`23-misc-university-labs.md`
> 产出：10 条可迁移设计原则 + 3 条领域边界
> 约束：每条含证据、机制、收益、失效模式、对 OMP/PI 工作区启示；区分来源事实与推断

---

## 原则 1 — 生成可解释经典求解器

**证据**
- 系统：AutoNumerics
- 文件：`channels/20-physics-autonumerics.md` 第 2、6 节；`channels/_index-physics-misc.md` 对比总表
- 来源：arXiv:2602.17607（Haizhao Yang 团队，2026-02），OpenReview pZFontoH7w
- 【来源事实】AutoNumerics 流水线产出离散化候选 FDM/FEM/谱方法/守恒型格式，生成可执行 Python/Julia 求解器代码，强调不做 neural surrogate。
- 【推断】该路径选择刻意规避 PINN 训练不稳定性，此为架构意图解读，原文未给 PINN 对比的完整 ablation。

**机制**
规划 Agent 产出多条离散化策略，代码生成 Agent 将每条策略编译为独立可执行脚本，粗网格试跑通过后再进入细网格定量验证。求解器代码保留数值格式显式表达，审计者可直接检查差分 stencil、时间推进格式、边界离散。

**收益**
可解释性支撑审计与复现。求解器作为产物可脱离 LLM 独立运行、独立测试。残差与守恒量检查可在无解析解场景提供自验证信号。论文在数十个 PDE benchmark 上以相对 L2 误差、PDE residual、守恒量偏差为指标报告优势。

**失效模式**
LLM 生成显式格式时遗漏 CFL 稳定性条件，粗网格通过、细网格发散。边界条件与初值条件在自然语言转代码环节缺失，调试轮次消耗评估预算。论文较新，GitHub 代码待发布，复现依赖自实现，引入实现偏差风险。

**对 OMP/PI 工作区启示**
PI 工作区增加 `solver-generation` 能力：输入为 PDE 自然语言描述与系数，输出为可执行脚本与粗细网格两级运行报告。能力注册包含 CFL 检查器与边界完整性检查器。OMP harness 将"生成经典代码+残差自验证"固化为计算飞轮标准流，产物落盘为可复跑脚本，非一次性 LLM 文本。

---

## 原则 2 — Coarse-to-Fine 分级执行

**证据**
- 系统：AutoNumerics
- 文件：`channels/20-physics-autonumerics.md` 第 2、6 节
- 来源：arXiv:2602.17607
- 【来源事实】AutoNumerics 显式定义 coarse-to-fine：粗网格试跑，细网格验证，配合残差自验证与调试 Agent。
- 【推断】该分级可节省约 10 倍调试成本，此为文件第 6 节归纳陈述，非论文直接给出的量化实测。

**机制**
粗网格承担快速语法与稳定性筛选，失败候选在低成本阶段淘汰。存活候选进入细网格，度量精度与效率 Pareto 前沿。调试 Agent 仅对粗网格失败做有限轮修复，避免在细网格上做昂贵试错。

**收益**
评估成本分层，批量 PDE 候选并行时资源利用更平滑。粗网格阶段可并行度高，细网格阶段仅对优选子集投入算力。

**失效模式**
粗网格掩盖细网格不稳定模态，CFL 条件在细网格才触发。粗网格误差估计与细网格收敛阶不一致导致择优失真。超时与并发控制缺失时，细网格任务堆积阻塞流水线。

**对 OMP/PI 工作区启示**
PI 工作区为数值类任务默认启用两级执行配置：`trial_grid` 与 `validate_grid` 分离，超时与内存上限分级设定。OMP 调度器对数值任务实施分级熔断，粗阶段失败不进入复现队列。

---

## 原则 3 — 残差与守恒量作为无监督验证信号

**证据**
- 系统：AutoNumerics、PhysMaster
- 文件：`channels/20-physics-autonumerics.md` 第 2、5、6 节；`channels/_index-physics-misc.md` 跨组共性
- 来源：arXiv:2602.17607，arXiv:2512.19799
- 【来源事实】AutoNumerics 在无解析解时计算 PDE residual 与守恒量偏差作为验证信号。PhysMaster 增加物理合理性校验，区分真实物理效应与坐标奇点/数值伪影。
- 【推断】该信号可推广至有不变量的优化与仿真领域，此为跨组共性段落的类比推广，非两系统论文原句。

**机制**
求解器执行后，验证 Agent 独立计算离散残差场、边界残差、全局守恒量漂移。守恒量校验与残差校验正交部署，两者同时通过才进入排序。

**收益**
无需 ground truth 仍可自验证，适合物理、守恒律、约束优化类任务。验证信号可作为 reward 或排序依据，支撑无人值守筛选。

**失效模式**
残差小不代表解正确，离散一致性错误可同时让残差与解偏小。守恒型格式离散错误导致守恒量"伪守恒"。验证器与生成器同源时，系统性偏差被共同忽略。

**对 OMP/PI 工作区启示**
PI 工作区引入 L1 自动验证层：残差、守恒量、量纲一致性三项必检。验证器与生成器分离部署，检验脚本独立版本管理。harness 飞轮将 L1 门控作为计算任务的强制关卡，未通过不进入 L2 表征或人工审查。

---

## 原则 4 — 物理合理性检查独立于数值正确性

**证据**
- 系统：PhysMaster
- 文件：`channels/20-physics-autonumerics.md` 第 2、3、5、6 节
- 来源：arXiv:2512.19799，AlphaXiv/Reddit r/accelerate 解读
- 【来源事实】PhysMaster 在 Kerr 时空测地线、Bose-Hubbard 相变、锂原子激发能等任务中，主动识别 Christoffel 符号奇点、激波捕捉参数自适应，区分坐标奇点与物理效应。工具链以 Julia DifferentialEquations.jl 为主。
- 【推断】该检查可建模为 domain-specific sanity check agent，此为文件第 6 节可借鉴点的抽象命名。

**机制**
数值求解完成后，物理校验层独立运行：检查解的量纲、渐近行为、对称性、奇点分类、参数敏感性。校验层可调用符号推导与量纲分析工具，输出"数值通过/物理存疑"二元判定与理由。

**收益**
拦截"数值对但物理错"类错误，减少伪发现。校验理由可回流至规划 Agent，驱动离散化或参数重选。

**失效模式**
物理校验规则覆盖不全，新物理场景缺少先验判据。符号推导与数值结果不一致时归因困难。Julia 生态版本漂移导致复现失败，校验器在漂移环境下误报。

**对 OMP/PI 工作区启示**
PI 工作区为物理与仿真类任务配置独立 `sanity-check` 能力，注册为 verifier 角色，输入为求解器输出与物理问题描述，输出为结构化校验报告。harness 要求数值正确性与物理合理性双门控，报告落盘可审计。

---

## 原则 5 — AI 编排与确定性内核的硬边界

**证据**
- 系统：FlowX / Flow360
- 文件：`channels/20-physics-autonumerics.md` 第 2、3、6 节；`channels/_index-physics-misc.md` 硬件边界段
- 来源：docs.flexcompute.com Flow360 Physics 章节，2024-2025 产品文档
- 【来源事实】FlowX 中 AI 负责网格自动生成、物理模型选择、收敛性监控，底层仍求解三维 Navier-Stokes，循环为 AI 前处理到经典求解器迭代到 AI 收敛诊断到自适应重算。RANS/LES/MRF/SRF/多孔介质均内置。
- 【推断】该边界设计在工业场景更易落地，此为文件第 6 节的落地性判断。

**机制**
AI 仅做配置与监控，不替代数值内核。内核暴露确定性接口：网格、模型、求解器参数、收敛判据。AI 的决策日志可追溯，内核执行结果可复现。

**收益**
可靠性由内核保证，AI 错误可通过重配置纠正。复杂 CFD 任务保留网格无关性与实验对照等经典度量，AI 增强不破坏既有验证体系。

**失效模式**
AI 选型逻辑不透明，出错归因困难。日志缺失时难以区分模型选型错误与网格质量问题。商业求解器黑盒限制外部审计。

**对 OMP/PI 工作区启示**
PI 工作区对"AI 决策+确定性执行"类能力强制接口分离：`propose_config` 与 `execute_solver` 解耦，决策日志与执行日志分文件落盘。OMP harness 在重仪器或重求解器场景优先采用此边界，AI 不直接操控数值内核内部状态。

---

## 原则 6 — 状态图编排与 Docker 隔离执行

**证据**
- 系统：Denario
- 文件：`channels/21-denaro-rumi.md` 第 2、3、6 节；`channels/_index-physics-misc.md` 对比总表
- 来源：arXiv:2510.26887（2025-10），AG2 + LangGraph 社区实现
- 【来源事实】Denario 基于 AG2 + LangGraph 状态图，角色分工为 idea、literature、plan、code、report，链式调用可回溯修正，代码执行在 Docker 沙箱内，经济学演示含 FRED 数据拉取、清洗、计量回归、可视化、LaTeX 生成。NeurIPS 2025 Fair Universe 冠军验证多学科通用性。
- 【推断】该编排可直接复用为 harness 的 plan-code-report 状态机，此为文件第 6 节的复用建议。

**机制**
状态图定义节点与边，支持中断恢复与回溯修正。每个 code 节点在隔离容器内执行，产物为可运行脚本、图表、报告片段。文献与数据节点通过工具调用接入 arXiv、Semantic Scholar、FRED 等外部源。

**收益**
执行隔离降低环境污染与安全风险。中断恢复支撑长链路研究任务。多学科演示验证通用编排框架的可移植性。

**失效模式**
通用指令下易退化为被动助手，主动性依赖强 prompt 约束。经济学数据清洗环节幻觉率高，Docker 镜像版本与依赖漂移导致可运行率下降。文献评估被 LLM 互评污染。

**对 OMP/PI 工作区启示**
PI 工作区将执行能力统一封装为容器化 `execute` 接口，输入为代码与依赖声明，输出为运行日志、产物文件、资源用量。OMP harness 复用 AG2/LangGraph 状态图模式，supervisor/worker 双进程与状态图编排互补，workspace 层提供决策上下文，执行层提供隔离与可追溯性。

---

## 原则 7 — 知识图谱记忆与锦标赛多样性

**证据**
- 系统：Rumi
- 文件：`channels/21-denaro-rumi.md` 第 2、3、6 节；`channels/_index-physics-misc.md` 多样性机制段
- 来源：github.com/josemanuelm9203/rumi，rumi.ai 服务至 2026-07-24，arXiv:2608.05179 Survey，dev.to Subhansh 自述
- 【来源事实】Rumi 为 terminal-native 架构，10 阶段发现流水线，82 发现模块，知识图谱承载文献矛盾与假设演化，GFlowNet 假设锦标赛与对抗性 skeptic review 为特色，案例含 KRAS G12C 耐药机制分析。商业服务 2026-07-24 下线，开源版功能滞后。
- 【推断】图谱记忆比纯文本上下文更可追溯，此为文件第 6 节的对比判断。

**机制**
文献摄入后构建图谱，节点为实体与陈述，边为引用与矛盾关系。矛盾检测触发假设生成，假设经可检验性过滤进入锦标赛，多候选并行接受 skeptic 评审，优胜者进入实验设计。图谱增量更新支撑跨轮剪枝与复利。

**收益**
跨阶段记忆可追溯假设来源与演化路径。对抗性评审提升假设鲁棒性。终端原生适配 CLI-first harness 设计。

**失效模式**
依赖单点商业服务时存在下线风险。跨 8 领域通用导致单域深度不足。假设新颖性评估主观，自动化度量易被 LLM 互评互吹污染。图谱规模膨胀导致检索与一致性维护成本上升。

**对 OMP/PI 工作区启示**
PI 工作区引入 `memory_store` 图谱能力，统一承载文献矛盾、假设谱系、实验结果三类节点。harness 飞轮在 idea 阶段强制锦标赛采样，idea 到 plan 的输入为图谱子图，非扁平文本。记忆读写纳入版本化落盘，支撑跨轮复利与剪枝。

---

## 原则 8 — 多样性采样按 Reward 正比

**证据**
- 系统：GFlowNet Hypothesis
- 文件：`channels/21-denaro-rumi.md` 第 2、6 节；`channels/_index-physics-misc.md` 多样性机制段
- 来源：Mila / Yoshua Bengio 团队 2022 奠基，IBM GT4SD 开源库，PMC12932417，ACS AMI 2026，arXiv:2505.04651
- 【来源事实】GFlowNet 按 reward 正比采样假设或结构，循环为采样到评估到 reward 更新到重采样，与 RL/贝叶斯优化追最优不同，追求多样且高潜力的候选集。IBM GT4SD 提供开箱即用实现。度量含 distinct high-reward modes 与 mode coverage。
- 【推断】该思想适合假设生成阶段避免早熟收敛，此为文件第 6 节的 harness 映射。

**机制**
生成器按学习到的流量正比于 reward 分布采样，评估器在仿真或自动实验室中观测结果，reward 模型增量更新，重采样覆盖未探索高 reward 区域。采样器与评估器分离，reward 建模为核心。

**收益**
显式抗 mode collapse，保留多解释并存。科学发现中多假设并存场景下，发现效率优于单一最优追踪。多样性指标可量化调参。

**失效模式**
Reward 稀疏或噪声大时采样退化，多样性退化为随机性。Reward 设计不当导致采样偏向易评分子空间。不确定性建模缺失时主动学习失效。

**对 OMP/PI 工作区启示**
PI 工作区将 idea 生成能力配置为多样性采样器，接口参数包含 `num_modes`、`diversity_weight`、`reward_model`。harness 在 idea 阶段设置多样性闸门，未达到 distinct modes 阈值不进入执行阶段。GT4SD 可作为参考实现接入评估。

---

## 原则 9 — 设计执行分离与表征自动解析为闭环瓶颈

**证据**
- 系统：DigCat、A-Lab
- 文件：`channels/22-cloud-synthesis.md` 全文；`channels/_index-physics-misc.md` 硬件边界段
- 来源：DigCat ChemRxiv 2024-jsqqn，大连化物所；A-Lab Nature 10.1038/s41586-023-06734-w，LBNL/Berkeley，2023-11-29，C&EN 2026-01 correction
- 【来源事实】DigCat 采用云端设计、异地执行闭环，训练数据超 400k 实验记录与 400k 催化剂结构，支持活性/选择性/稳定性多目标优化，双模型更新为核心，支持多实验室并行。A-Lab 为 3 臂 8 炉 600 sq ft 实验室，文献+GNoME 生成候选，机器人执行，ML 自动解析 XRD 判定成败，17 天连续运行约 21 实验/天，尝试 57-58 目标，合成 36-43 个新材料，成功率 63% 到 71% 口径不一，后续新颖性存疑并发布 correction。共识：XRD 自动解析是核心壁垒。
- 【推断】设计与执行物理分离在软件 harness 中可用中央大脑加分布式执行器模拟，此为文件第 6 节的迁移建议。

**机制**
设计端在云端产出合成指令，执行端在自动实验室并行合成与高通量表征，表征结果经 ML 自动解析回流至设计端，双模型增量训练。表征解析独立于执行控制，判定标准显式落盘。

**收益**
异地并行提升吞吐，设计与执行解耦支撑全球闭环。自动解析将闭环瓶颈从执行转向判读，10 到 20 轮主动学习内可收敛。

**失效模式**
负样本稀缺导致模型乐观偏差，已发表成功案例主导训练分布。跨硬件可复现性差，前驱体批次与炉温均匀性引入系统偏差。硬件故障占失败大头，粉末堵塞、高温炉漂移需冗余与自动恢复。成功判定标准不审计导致新颖性争议。

**对 OMP/PI 工作区启示**
PI 工作区对实验闭环能力强制双接口：`validate` 与 `execute` 分离，`safety pre_filter` 显式阻断，`validate` 返回结构化判定与原始数据引用。harness 要求 XRD/谱学/性能等表征结果附原始数据与精修报告，成功判定可审计。数据策略显式采集失败实验，缓解乐观偏差。

---

## 原则 10 — 约束主动学习、人机协同与开源硬件抽象

**证据**
- 系统：Stanford SUNCAT、Toronto Matter Lab / Acceleration Consortium、MIT Coley/Jensen、Caltech SARA、Oxford 量子实验室、Cambridge、ETH
- 文件：`channels/23-misc-university-labs.md` 第 23.1 到 23.7 节、跨校共性总结；`channels/_index-platform.md` 可横向参考
- 来源：Stanford SUNCAT PMC7686338，Toronto matter.toronto.edu / AUTODIAL / Project Ada，MIT coley.mit.edu / PyLabRobot / arXiv:2506.19613 Agent Index，Caltech Genesis Mission / SARA，Oxford physics.ox.ac.uk 自驱量子实验室，Cambridge 化学语言模型，ETH Yokogawa/Atinary 方案
- 【来源事实】Stanford 采用代理模型加贝叶斯不确定度加物理约束选下一实验，支持云端 DFT 弹性调度与 human-in-the-loop 可选。Toronto 以 10 年/$10M 到 1 年/$1M 的 10 倍压缩为北极星，Ada 到 AUTODIAL 展示平台化演进，Acceleration Consortium 获 $200M CFREF 资助，多组共享基础设施。MIT PyLabRobot 提供开源硬件抽象层，Agent Index 定义自主性分级。Caltech SARA 采用分层主动学习建相图，先建 landscape 再选点。Oxford 实现自然语言到量子硬件控制代码编译。共性为设计到执行到表征到学习四段式，AI 核心在实验设计与结果判读。
- 【推断】10 倍压缩可作为 harness 北极星指标，约束主动学习适合仿真与实验混合闭环，此为跨校总结的迁移判断。

**机制**
约束主动学习在物理约束与不确定度共同驱动下选点，human-in-the-loop 作为可选门控介入高风险实验。硬件层通过 PyLabRobot 等抽象统一驱动，化学语言模型等序列建模提供 domain LLM 参考。Consortium 共享基础设施支撑多组协作。

**收益**
约束与不确定度结合比纯探索更高效，human-in-the-loop 兼顾自主性与可控性。开源硬件抽象降低自建门槛，平台化演进支持横向扩展。10 倍压缩目标提供可量化工程北极星。

**失效模式**
高维组合空间主动学习易陷维度灾难，DFT 误差与实验偏差鸿沟需校准。化学空间局部最优震荡需 diversity 约束。硬件定制化高，复现成本大，多组协作数据标准与调度复杂度为隐形挑战。量子硬件稀缺与校准漂移限制通用性。商业化平台成本门槛高，小团队难以自建。

**对 OMP/PI 工作区启示**
PI 工作区引入三件套：`constrained_active_learning` 策略、human-in-the-loop 门控、PyLabRobot/Atinary 风格硬件抽象。仪器文档向量化，`safety pre_filter` 前置。harness 将 10 倍时间与成本压缩设为工程度量锚点，能力注册表统一描述仿真、表征、硬件抽象三类能力，Consortium 共享模式映射为多 task 节点协作与统一数据标准。

---

## 领域边界

**边界 1 — 数值与物理闭环的验证天花板在"可形式化不变量"**
20 系与 21 系互补揭示一条边界：AutoNumerics/PhysMaster 的残差与守恒量验证仅在 PDE 具明确不变量时有效。GFlowNet/Rumi 的多样性采样与锦标赛仅在假设可检验且 reward 可建模时有效。两类验证在开放式、缺乏不变量或 reward 稀疏的探索型物理问题中同时弱化。
【来源事实】AutoNumerics 以 PDE benchmark 与残差为度量，GFlowNet 以 mode coverage 为度量，两者均依赖预设验证信号。
【推断】超出可形式化验证边界的课题需引入 L3 人工物理审查，此边界划分来自跨组共性中"数值-假设-物理-工程"全谱验证的互补性解读。

**边界 2 — 云端合成与自驱实验室的经济与可复现性边界**
22 系与 23 系共同标定一条工程边界：A-Lab 600 sq ft 8 炉 3 臂与 Toronto $200M Consortium 证明高通量自主合成的吞吐依赖重资产投入，小团队自建不经济。跨硬件复现性受前驱体批次、炉温均匀性、仪器校准漂移支配，云端设计在不同执行端表现不一致。
【来源事实】A-Lab 成功率 63% 到 71% 且后续新颖性存疑，Toronto 明确 10 倍压缩目标但依赖大规模资助，DigCat 数据偏向已发表成功案例。
【推断】该边界下，harness 对重硬件场景应优先采用"云端借用+硬件指纹校准"而非自建，此为对成本与可复现性权衡的工程推断。

**边界 3 — 端到端自主科研的自主性与深度权衡边界**
21 系与 23 系共同揭示一条自主性边界：Denario 的"助理而非研究员"定位、Rumi 跨 8 域通用但单域深度不足、Agent Index 的自主性分级共同指向"通用助理易退化为被动执行，深专系统才有领域穿透"。天文因数据开放与工具链成熟成为自主科研最顺滑领域，化学与材料因数据偏差与硬件异构最难泛化。
【来源事实】Denario 需强 prompt 约束主动性，Rumi 开源版滞后且收购下线，MIT Agent Index 定义从 chat 到 enterprise tool-use 分级，天文数据非私有、评估客观。
【推断】harness 选试点领域时应优先数据开放、评估客观、工具链成熟的赛道，通用与专用间做显式取舍，此为对"领域数据开放性决定自动化天花板"的策略推断。

---

*写入位置：`debate/layer1/physics-crossdomain.md`*
*覆盖文件：`channels/_index-physics-misc.md`、`20-physics-autonumerics.md`、`21-denaro-rumi.md`、`22-cloud-synthesis.md`、`23-misc-university-labs.md`*
*调研时间：2026-09-02*
