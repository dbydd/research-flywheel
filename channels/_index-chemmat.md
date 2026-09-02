# 化学 / 材料 / 自驱动实验室 (Chem/Mat/SDL) — 渠道汇总

> 覆盖 11-15 五个渠道：Coscientist、ChemCrow、SciAgents、Toronto AC/SDL + Berkeley A-Lab、MatterGen/MatterSim。每个渠道详见同目录独立 .md。

## 一览表

| # | 渠道 | 机构 | 循环形态 | 智能体架构 | 开源 | 详述 |
|---|------|------|----------|------------|------|------|
| 11 | Coscientist | CMU + Emerald Cloud Lab | 文献→规划→文档→代码→云执行→分析→迭代 | Planner(GPT-4) + Web Searcher + Doc RAG + Docker + ECL/OT-2 | 论文全披露，未开源 | [11-coscientist-cmu.md](11-coscientist-cmu.md) |
| 12 | ChemCrow | EPFL + IBM RoboRXN | ReAct 思考→工具→观测→终答/上机 | 单 GPT-4 ReAct + 18 工具 + RoboRXN | `ur-whitelab/chemcrow-public` | [12-chemcrow-epfl.md](12-chemcrow-epfl.md) |
| 13 | SciAgents | MIT LAMM | 图谱采样→多 Agent 假说→Critic→检索→图谱增量 | Ontologist + Scientist×N + Critic + KG | `lamm-mit/SciAgentsDiscovery` | [13-sciagents-mit.md](13-sciagents-mit.md) |
| 14 | SDL 联邦 + A-Lab | Toronto AC + Berkeley LBNL | Toronto: Design-Make-Test-Analyze；A-Lab: 计算筛选→文献配方→机器人固相→XRD→ARROWS3 | ChemOS 编排 / 双ML+ARROWS3+XRD ML | ChemOS 开源 / ARROWS3 开源 | [14-sdl-toronto-berkeley.md](14-sdl-toronto-berkeley.md) |
| 15 | MatterGen/MatterSim | Microsoft Research | 扩散生成→MatterSim/DFT 验证→Adapter 条件生成→实验→回流 | 扩散生成 + 通用力场双模型飞轮 | `microsoft/mattergen` + `mattersim` | [15-mattergen-microsoft.md](15-mattergen-microsoft.md) |

## 闭环形态对比

- **Coscientist / ChemCrow**：LLM 为主控的"推理-工具-执行"小闭环，单次实验秒级，靠 ReAct/Planner 串行驱动，验证靠硬件返回的校验错误自修复。
- **SciAgents**：纯认知闭环，无物理执行，靠知识图谱作为可持久化共享记忆，失败以"批判打回"形式处理。
- **A-Lab / Toronto SDL**：重硬件的"计算-合成-表征-学习"大闭环，周期小时级，靠 pairwise 反应数据库与贝叶斯/热力学推理做搜索剪枝，失败分类最细。
- **MatterGen**：纯计算的"生成-验证"飞轮，MatterSim 将验证成本降数个量级，实验仅对最终候选做一次合成，数据回流再训练。

## 硬件抽象的四种范式

1. **文档即驱动 (Coscientist)**：向量化仪器文档，LLM 按需检索生成代码，新硬件零代码接入。
2. **语义原语 (ChemCrow/RoboRXN)**：暴露 `synthesize/validate` 化学语义 API，隐藏机械臂细节。
3. **OS 内核 (ChemOS/A-Lab)**：ChemOS 为实验室操作系统，仪器即驱动，三站流水线为资源池。
4. **仿真即硬件 (MatterGen/MatterSim)**：`calculator` 统一接口，生成器不区分 MatterSim/DFT/实验室。

## 安全约束光谱

- **显式**：ChemCrow GHS 工具链 (执行前强制检查)；A-Lab 源头过滤不稳定目标。
- **隐式**：Coscientist 依赖 ECL 云端审核与 GPT-4 拒答；SciAgents 靠 Critic 与本体过滤。
- **可借鉴**：安全应为 capability 的 `pre_filter`，而非 LLM 自觉。

## 调度与失败处理精要

- 调度从单线程 ReAct (Coscientist/ChemCrow) 到多 Agent 并行 (SciAgents) 再到多炉并行+DAG (A-Lab) 与批量生成流水线 (MatterGen)。
- 失败处理共同模式：**结构化错误回灌 + 知识库记忆 + 热力学/统计剪枝**。A-Lab 的 pairwise 数据库与 ChemCrow 的 validate-修正循环是最可复用的两段实现。

## 度量

- Coscientist：6 类任务全通过，千次/周末吞吐。
- ChemCrow：14 用例，4+1 合成验证，专家评分复杂任务领先。
- SciAgents：跨学科新颖性与图谱覆盖度，专家盲评。
- A-Lab：63%→70% 目标成功率，353 配方中 30% 产出，吞吐 20-25/天。
- MatterGen：SUN 翻倍、RMSD 10× 优、27 体系超越基线、TaCr2O6 误差 20% 内。

---

## OMP 如何抽象硬件/仿真为 Capability — 统一可借鉴方案

以下为综合五渠道提炼的 OMP 落地形态，五个独立渠道文件各有具体映射，此处为统一契约。

### 1. Capability 注册表

```yaml
capability:
  id: "ot2_pipette | roboRxn.synthesize | furnace_array | mattersim.score | dft.score | knowledge_graph.query"
  type: "hardware | simulation | knowledge"
  input_schema: { json_schema }
  output_schema: { json_schema }
  doc_ref: "仪器文档/论文/API spec 路径"
  executor: "docker | ecl | chemOS | ase | lammps"
  cost: { time, money, risk }
  safety_tags: ["ghs", "air_stable_only"]
  requires_approval: true|false
  simulate: true|false   # 同一 id 可注册 sim 与 real 两个实现
```

- 命名空间借鉴 ChemCrow 五类划分：`chem.reaction.*`, `chem.molecule.*`, `chem.safety.*`, `chem.search.*`, `std.*`, `lab.*`, `sim.*`。
- 文档即驱动：`doc_ref` 向量化后注入 prompt，新硬件只需新增一条注册，无需改 planner。

### 2. 硬件/仿真同接口，双层验证

```
validate(procedure) -> { valid: bool, errors: [] }   # 仿真/硬件共用
execute(procedure)  -> observation                    # 仿真返回模拟观测，真机返回实测
score(structure)    -> { hull_energy, property }      # MatterSim/DFT/实验同契约
```

- 调度器先走 `validate` 仿真分支，失败触发 Agent 修正循环 (Coscientist/ChemCrow 模式)，成功后再路由真机。
- 仿真与真机通过 `capability.simulate` flag 路由，ARROWS3/MatterSim 这类学习器同时消费两种来源。

### 3. 资源与 DAG 调度

- A-Lab 三站流水线建模为 `resource_pool: { furnaces: 4, xrd: 1, arms: 2 }`，OMP DAG 调度器负责 `dose -> heat(并行) -> xrd(串行)` 的资源争用。
- SciAgents/MatterGen 的批量假设/批量生成建模为 `planner 批量产出 N -> critic/validate 并行 -> 写回` 流水线，失败项重入队而非阻塞整批。
- ChemOS 联邦模式证明同一 capability 接口可跨站点复用，OMP 通过 `capability.endpoint` 区分本地/远程实现。

### 4. 安全与失败的系统化

- 安全为 `pre_filter`：任何 `execute` 前 OMP 强制调用 `chem.safety.ghs` capability，高风险阻断并要求人工确认 (ChemCrow 显式模式)。
- 失败记忆持久化：pairwise 反应数据库 / 合成校验错误 / 图谱负样本统一落 `memory_store`，OMP 的 planner 下次直接剪枝已见路径 (A-Lab 80% 剪枝)。
- 自修复：执行报错原文回灌 LLM，结合 `doc_ref` 重写，对应 Coscientist 的加热模块修正与 ChemCrow 的溶剂增量。

### 5. 最小可落地组合 (给 OMP 的建议)

- 先实现 `validate→execute` 双接口 + `safety pre_filter` + `memory_store` 三件套，即可复现 ChemCrow/A-Lab 的核心鲁棒性。
- 再叠加 `simulate` 分支 (MatterSim/DFT) 与 `resource_pool` 调度，支撑计算-实验混合飞轮。
- 最后引入知识图谱 capability，将 SciAgents 的认知闭环作为上游假设源，对接下游 SDL 执行。

> 来源：各渠道独立文件均经 web_search + 原文 read 验证，见文件末尾来源标注。
