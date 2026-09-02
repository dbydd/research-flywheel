# 15 — MatterGen / MatterSim (Microsoft Research AI for Science)

| 维度 | 内容 |
|------|------|
| 机构 | Microsoft Research AI for Science (Cambridge), Tian Xie 等 25+ 作者，含 Matter Lab 协作 |
| 论文/发布时间 | MatterGen arXiv 2312.03687 → Nature 639, 624-632 (2025.01.16/03) `10.1038/s41586-025-08628-5`；MatterSim arXiv 2405.04967 (2024.05) |
| 循环形态 | 腐蚀-去噪扩散生成 → MatterSim/DFT 验证 → Adapter 微调条件生成 → 实验合成验证 → 数据回流再训练 (材料飞轮) |
| 智能体架构 | 扩散生成模型 (MatterGen) + 通用机器学习力场 (MatterSim) 双模型飞轮，等变分数网络 + Adapter 条件微调 |
| 工具链 | 等变扩散 (A/X/L 联合去噪)、Adapter 微调、Classifier-Free Guidance、Alex-MP-20 (607k 稳定结构)、MatterSim 通用力场、LAMMPS/ASE 集成 |
| 度量 | SUN (Stable Unique New) 翻倍，RMSD 10× 更接近 DFT 极小；27 化学体系上优于 substitution/RSS；合成 TaCr2O6 实测体积模量与目标误差 20% 内 |
| 开源状态 | MatterGen 开源 `microsoft/mattergen` (含 MatterSim 评估脚本)；MatterSim 开源 `MatterSim-v1.0.0-5M.pth`，ASE/LAMMPS 可用，下载量数万 |
| 潜在坑 | DFT 误差、训练集偏差 (≤20 原子)、多约束联合微调难度、仿真-实验 gap |

## 闭环形态详解

MatterGen/MatterSim 构成"生成-验证"飞轮。MatterGen 通过逆向腐蚀过程直接生成满足性质约束的晶体结构，MatterSim 作为通用力场快速弛豫与评分，筛选出的候选再经 DFT 精算与实验合成 (如 TaCr2O6)，实测数据回流扩充训练集。与 A-Lab 的"筛选-合成"不同，MatterGen 是"逆向设计"——从性质反推结构，而非正向筛选。20% 误差内的实验验证证明闭环可落地。

## 智能体架构

- **MatterGen**：晶体扩散模型，联合对原子类型 A (categorical mask)、坐标 X (wrapped Normal，周期边界)、晶格 L (对称形式) 做腐蚀与去噪。分数网络为等变设计，天然满足晶体对称性，无需数据增强学对称。
- **MatterSim**：通用 ML 力场，覆盖前 89 元素、0-5000K、0-1000 GPa，预测能量/力/应力/磁矩/介电张量，MAE 36 meV/atom (MPF-TP)，比 M3GNet/CHGNet/MACE 精度高 10×，推理快 3-5×。
- **Adapter 微调**：在预训练基座每层注入可调 Adapter，用小规模带标签数据微调出化学组成/空间群/标量性质 (磁密度、带隙、体积模量) 的条件生成模型，配合 classifier-free guidance 定向生成。
- **飞轮**：MatterGen 提结构，MatterSim 快速验证，二者共享 Alex-MP 数据生态，形成自增强循环。

## 工具链

- **数据**：Alex-MP-20 607k 稳定结构 (MP + Alexandria 重算)，支撑预训练；带标签小数据集支撑 Adapter 微调
- **模型**：等变分数网络、Adapter、classifier-free guidance
- **仿真**：MatterSim (MatterSimCalculator for ASE, LAMMPS 多 GPU 加速)、DFT (VASP 等) 精算
- **评估**：SUN 指标、能量 above hull、RMSD vs DFT 弛豫结构、凸包分析 (V-Sr-O 等)
- **开源**：`microsoft/mattergen` 含生成与评估脚本，`mattersim` pip 包与预训练权重

## 硬件抽象

MatterGen/MatterSim 本身是纯计算系统，硬件抽象体现在"仿真即硬件"的统一接口。MatterSim 被抽象为 `calculator` capability，与 DFT、实验合成同接口：输入晶体结构，输出能量/力/性质。论文Fig.6 的 TaCr2O6 实验即把生成结构同时送 MatterSim (快速) 与 DFT (精确) 与实验室 (真实) 三路验证。抽象层让生成器无需关心验证是模拟还是实测，只需 `score(structure) -> property` 的统一契约。

## 安全约束

未显式讨论化学安全，约束体现在物理合理性：扩散过程的噪声分布基于物理启发的先验 (立方晶格平均密度、周期边界)，生成结构天然更接近物理可实现。Adapter 微调时可加入 `low supply-chain risk (HHI)` 等约束 (Fig.5 联合优化磁密度+供应链风险)，展示多约束安全/可持续性建模能力。高风险材料 (如剧毒/放射性) 可通过训练数据过滤与条件约束排除。

## 调度

计算侧调度为批量生成→批量验证流水线。MatterGen 一次生成 1024 结构，MatterSim 并行弛豫与打分，DFT 对 top-k 精算，实验对最终候选合成。论文在 27 化学体系各生成 100 结构、跨 9 体系统计，体现批处理与统计调度。未涉及物理实验室的机械臂调度，但飞轮支持异步：生成与验证可解耦，验证结果回流触发再训练。

## 失败处理

- **DFT 不稳定**：生成结构经 DFT 弛豫后 hull 能过高则判失败，SUN 指标直接剔除，失败样本不进入下游。
- **RMSD 过大**：生成结构与 DFT 极小距离过大表明生成质量差，论文用 RMSD 分布衡量，MatterGen 比基线 10× 更优。
- **多约束冲突**：Fig.5 显示单约束 (磁密度) 与双约束 (磁密度+HHI) 的 Pareto 前沿，冲突时通过联合 Adapter 与权重调节平衡，失败的约束组合在 HHI-磁密度平面上可视化。
- **实验合成失败**：TaCr2O6 实测为无序版本 (disordered)，但 Rietveld 精修仍确认主相，说明对无序容忍。

## 度量与评估

- **稳定性**：SUN 比例 (Stable+Unique+New) 翻倍，energy above hull 分布显著左移
- **结构质量**：RMSD vs DFT 弛豫 10× 更小
- **条件生成**：磁密度、带隙、体积模量三类性质密度峰对准目标虚线 (Fig.4)，27 体系上 SUN 数超越 substitution/RSS 基线
- **实验**：TaCr2O6 体积模量 DFT 值与实测趋势一致，ICSD 未见结构的匹配验证跨 4 个目标模量值

## 核心可借鉴点

1. **扩散三要素独立腐蚀**：A/X/L 分别设计噪声分布，适配晶体周期性，比通用扩散更物理。
2. **Adapter 条件化**：小标签数据即可微调出新性质约束，避免全量重训，对 OMP 的多任务适配极有价值。
3. **MatterSim 通用力场**：一个力场覆盖全周期表与极端温压，验证成本降数个量级，是飞轮的加速器。
4. **飞轮数据回流**：生成→验证→再训练的闭环让模型随实验数据持续进化。

## 潜在坑

- 预训练集 ограничено ≤20 原子，大晶胞外推能力未知。
- 多约束联合生成时 Pareto 权衡复杂，需显式多目标优化。
- DFT 本身误差会通过训练集与评估回流放大，需与实验交叉验证。
- 仿真-实验 gap：生成结构理论稳定但实验可能因动力学/缺陷无法合成，需对接 A-Lab 类 SDL。

## OMP 硬件/仿真 Capability 抽象映射

- 将 MatterGen 与 MatterSim 注册为 OMP 的 `simulation` capability：`capability: { id: "mattergen", type: "sim.generate", input: { property_constraints }, output: { structures[] } }` 与 `capability: { id: "mattersim", type: "sim.score", input: { structure }, output: { energy, forces, property } }`，与 `lmp|dft|lab` 同接口。
- 硬件/仿真统一契约：`score(structure) -> { hull_energy, rmsd, property }`，OMP 调度器先走 `mattersim` 快速分支 (36 meV/atom, 3-5× 加速)，top-k 再走 `dft` 精确分支，最终候选走 `lab.synthesize` 真机分支，三层验证的阈值与超时在 OMP 的 `capability.policy` 中声明。
- Adapter 机制映射为 OMP 的 `capability.fine_tune(dataset, constraints) -> new_capability`，小标签数据即可衍生新条件生成器，OMP 的模型注册表管理多版本 Adapter，支持按 `property: bulk_modulus|band_gap|hhi` 动态路由。

> 来源验证：Nature 论文全文 (Fig.1-6) + Microsoft Research 官方博客 (MatterGen/MatterSim) + mattergen/mattersim GitHub + arXiv 2405.04967 MatterSim 全文，交叉确认 SUN/RMSD/Adapter 与 TaCr2O6 实验。
