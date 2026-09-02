# 20 - AI4S 物理求解：AutoNumerics / PhysMaster / FlowX 系

> 领域：AI for Science / 计算物理 / PDE 数值求解
> 关键词：PDE-agnostic、classical solver generation、multi-agent verification、coarse-to-fine

## 1. 系统一览

| 系统 | 机构/作者 | 论文/发布时间 | 开源状态 |
|------|-----------|---------------|----------|
| **AutoNumerics** | Haizhao Yang 团队（Univ. of Maryland / 华人学者合作） | arXiv 2602.17607, 2026-02；OpenReview 同步 | 论文+代码预告，arXiv html 已公开，GitHub 待发布 |
| **PhysMaster** | 上海交通大学 | arXiv 2512.19799, 2025-12；Reddit/AlphaXiv 同步解读 | 论文公开，代码未开源 |
| **FlowX / Flow360** | FlexCompute | 产品文档持续更新（2024-2025） | 商业求解器，部分 API 开放 |
| PDEMaster（概念统称） | 多机构综述中的归纳名 | 无单篇代表作，指代 PDE 自动求解范式 | - |

## 2. 循环形态

### AutoNumerics：PDE-agnostic 多智能体流水线
```
自然语言 PDE 描述 → 任务规划 Agent（产出多条离散化候选：FDM/FEM/谱方法/守恒型格式）
  → 代码生成 Agent（生成可执行 Python/Julia 求解器）
  → coarse-to-fine 执行：粗网格试跑 → 细网格验证
  → 残差自验证 Agent（无解析解时算 PDE residual / 守恒量检查）
  → 调试 Agent（编译/运行报错自修复，最多 N 轮）
  → 择优 Agent（按精度+效率排序，输出最优 solver）
```
核心区别：**不做神经代理（neural surrogate），生成的是可解释的经典数值求解器**，而非 PINN/Neural Operator 黑盒。

### PhysMaster：全栈理论+计算物理学家
```
用户物理问题（自然语言+公式）→ 推理规划 → 符号推导/解析尝试
  → 数值方案选择（自动选 SPH 核函数/人工黏性/Balsara limiter 等）
  → 代码生成（Julia 为主）→ 执行与物理合理性校验
  → 区分真实物理效应 vs 坐标奇点/数值伪影
```
评测任务覆盖：Kerr 时空测地线、Union-Jack Bose-Hubbard 相变点、锂原子第一激发能（Schrödinger 方程 + Born-Oppenheimer 近似）。

### FlowX/Flow360：AI 增强的 CFD 求解器
AI 负责网格自动生成、物理模型选择、收敛性监控；底层仍是求解三维 Navier-Stokes。RANS/LES/混合模型、MRF/SRF 转子、Darcy-Forchheimer 多孔介质均内置。循环为 `AI 前处理 → 经典求解器迭代 → AI 收敛诊断 → 自适应重算`。

## 3. 智能体架构

| 系统 | 架构 | 关键设计 |
|------|------|----------|
| AutoNumerics | 多 Agent 协作（Planner / Coder / Debugger / Verifier / Ranker） | 规划-生成-执行-验证解耦；每个候选策略独立流水线，并行择优 |
| PhysMaster | 单体 LLM Agent + 工具链（符号+数值混合） | 强调"物理直觉"：主动识别 Christoffel 符号奇点、激波捕捉参数自适应 |
| FlowX | 单体 AI 编排 + 经典求解器内核 | AI 不替代求解器，只做配置与监控，可靠性高 |

## 4. 工具链

- **AutoNumerics**: LLM（GPT-4o/Claude 级别）、Python 科学计算栈（NumPy/SciPy）、残差计算器、CFL 稳定性检查、网格生成器
- **PhysMaster**: Julia 生态（DifferentialEquations.jl 等）、符号推导、数值微分/积分、物理量守恒校验
- **FlowX**: 自研 CFD 内核、AI 网格生成、湍流模型库、共轭传热求解器

## 5. 度量

- **AutoNumerics**: 在数十个 PDE benchmark 上评估（热传导、波动方程、流体等），指标为相对 L2 误差（有解析解）、PDE residual（无解析解）、守恒量偏差、运行时间/内存；与 PINN/Neural Operator 对比，强调精度与可解释性优势
- **PhysMaster**: 任务成功率（能否给出物理正确的结果）、数值误差、与参考解一致性、参数选择合理性（人工复核）
- **FlowX**: 经典 CFD 指标：残差收敛曲线、与实验/解析对照误差、网格无关性

## 6. 核心可借鉴点

1. **生成经典求解器而非神经代理**：AutoNumerics 证明 LLM 完全可以写出 FDM/FEM 代码，可解释、可审计，避免 PINN 的训练不稳定性。harness 可复用"生成可执行数值代码+残差自验证"模式。
2. **coarse-to-fine 执行流**：先粗网格快速试错，再细网格定量验证，节省 10x 调试成本。
3. **残差/守恒量作为无监督验证信号**：无 ground truth 时仍可自验证，适合物理、优化等有不变量的领域。
4. **多候选并行择优**：Planner 同时产出 3-5 种离散化方案，并行实现后按精度-效率 Pareto 排序，比单路径更稳健。
5. **物理合理性检查独立于数值正确性**：PhysMaster 额外区分"数值对但物理错"（如坐标奇点误判为物理效应），harness 可引入 domain-specific sanity check agent。
6. **AI 只做编排、不碰核心求解**：FlowX 的保守设计在工业场景更易落地，harness 中"AI 决策+确定性执行"的边界值得参考。

## 7. 潜在坑

- **CFL/稳定性陷阱**：LLM 生成的显式格式易忽略稳定性条件，需显式 CFL 检查 agent，否则粗网格通过、细网格发散。
- **边界条件遗漏**：PDE 描述转代码时边界/初值条件最易丢，AutoNumerics 靠 verifier 捕捉，但仍需人工 prompt 强调完整性。
- **Julia/Python 环境漂移**：PhysMaster 依赖 Julia 包版本敏感，复现时需锁版本；harness 若支持多语言需容器化。
- **评估成本高**：每个 PDE 候选都要实际运行求解器，批量评估时计算开销大，需并发控制与超时熔断。
- **FlowX 类商业求解器的黑盒风险**：AI 选型逻辑不透明，出错时难以归因；自研 harness 应保留决策日志。
- **论文较新、复现度低**：AutoNumerics（2026-02）与 PhysMaster（2025-12）均无成熟开源代码，借鉴时以论文方法为主，需自实现。

## 8. 信息来源

- AutoNumerics: arXiv 2602.17607 / haizhaoyang.github.io / OpenReview pZFontoH7w
- PhysMaster: arXiv 2512.19799 / AlphaXiv / Reddit r/accelerate
- FlowX: docs.flexcompute.com Flow360 Physics 章节
- MIT Peds technique (Nature Machine Intelligence, 2024-12) 作为背景补充

---
*调研时间：2026-09-02 | 验证方式：web_search + arXiv html 阅读*
