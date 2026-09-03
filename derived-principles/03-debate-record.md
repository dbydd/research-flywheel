# 辩论溯源与合议记录 v1.0

> 定位：Layer 1 至 Layer 3 全链路辩论的合议溯源。记录每条合议原则的候选来源、争议裁决、证据等级、冲突处置与未决风险，保证从 `channels/` 原始系统到 `derived-principles/` 合议结果的可回放性。
> 输入：`channels/README.md` 46 系统索引与 `_index-*.md`、`debate/layer1/*.md` 五份、`debate/layer2/*.md` 三份、`debate/layer3/philosophy-a.md` 与 `debate/layer3/operating-model.md` 两份。
> 方法：逐层回溯，区分来源事实与推断，推断显式标注。按 `epistemic.md` 三阶证据分级标定。
> 版本：2026-09-02

---

## 0 全链路概览

```
channels/ 46 系统原始证据
  └─ debate/layer1/ 5 份领域证据分析（约 54 条候选原则与 15 条领域边界）
       └─ debate/layer2/ 3 份交叉辩论（10 争议 10 共识 5 拒绝 + 10 决议 5 延期 + 11 护栏 5 不确定性）
            └─ debate/layer3/ 2 份独立裁判（各 12 条 + 5 拒绝/处置 + 5 开放/延期）
                 └─ derived-principles/ 4 份合议终稿（12 条哲学 + 12 条注册表 + 4 份映射 + 本溯源记录）
```

各层职责：Layer 1 提炼候选原则与边界，Layer 2 交叉辩论收敛共识与护栏，Layer 3 双裁判独立裁决，Derived 层合议并落地到注册表与模板映射。

---

## 1 Layer 1 来源分层与候选统计

| 域 | 文件 | 候选原则数 | 边界数 | 代表系统 | 可借鉴核心 |
|---|------|-----------|-------|---------|-----------|
| CS/ML | `debate/layer1/cs-ml.md` | 11 | 3 | Karpathy autoresearch, Sakana, Dolphin, CycleReviewer | 单文件赛马 + 树搜索 + 异常局部修复 |
| 生物医学 | `debate/layer1/bio.md` | 11 | 3 | Virtual Lab, Biomni, Co-Scientist, TxAgent | PI 会议 + 150 工具检索 + Elo 锦标赛 |
| 化学材料 | `debate/layer1/chem-materials.md` | 10 | 3 | Coscientist, ChemCrow, SciAgents, A-Lab | 18 工具 guard + 图推理 + 机器人闭环 |
| 平台基建 | `debate/layer1/platform.md` | 10 | 3 | Bohrium, Agent Lab, Deep Research, Benchmarks | 四层能力注册 + 预印本协作 + 双轨评测 |
| 物理跨域 | `debate/layer1/physics-crossdomain.md` | 10 | 3 | AutoNumerics, Denario, Rumi, DigCat | 残差自验证 + GFlowNet 多样性 + 云端分发 |

合计约 54 条候选原则与 15 条领域边界参与 Layer 2 去重。来源事实均可在 `channels/*.md` 末尾来源节回溯至论文、官网、GitHub。

统计锚点：`channels/README.md` 登记 46 条系统，开源比例约 65%。

---

## 2 Layer 2 收敛记录

### 2.1 adversarial.md — 10 争议 10 共识 5 拒绝

| 争议 | 主张 | 裁决 | 共识落点 |
|------|------|------|---------|
| 1 固定预算可泛化 | 单一 wall-clock 推广到湿实验 | 分层预算 | 共识 1 指纹化分层预算 |
| 2 自由树搜索无条件优于模板 | 去模板多样性采样天然更优 | 有约束多样性 | 共识 9 有约束多样性 |
| 3 语义 keeper 独立裁决 | 模拟分/VLM/Elo 独立 keep | 主次双 keeper + 校准 | 共识 2 主次双 keeper |
| 4 注册表零成本规模化 | 百级工具零成本接入 | 有治理注册表 | 共识 3 契约化注册表 |
| 5 文档即驱动零代码接入硬件 | RAG 注入即学会新 DSL | 文档+符号校验+指纹校准 | 共识 4 validate→execute + pre_filter |
| 6 安全可由 LLM 自觉覆盖 | prompt 呼吁覆盖安全 | 路由层硬门控 | 共识 4 安全硬门控 |
| 7 知识图谱可无差别替代 | 图谱/世界模型/pairwise 可互换 | 分层记忆 + U 标记 | 共识 6 分层持久记忆 |
| 8 仿真即硬件 | score 可替代实验成功 | 分层验证 + 成功可审计 | 共识 7 仿真分层路由 |
| 9 全自主优于人机分叉 | 端到端无人类闭环 | 分叉点人机协同 | 共识 8 分叉点人机协同 |
| 10 论文向量检索可自举 | 检索复用自举评估 | 有审计检索复利 | 共识 10 三级溯源 + 沙盒防伪 |

拒绝项：5 条分别对应 prompt 安全、单一预算、无校准语义裁决、无治理扩张、仿真等同成功。

### 2.2 architecture.md — 10 决议 5 延期

| 决议 | 主题 | 归一取舍 |
|------|------|---------|
| 01 七阶段状态机 | 三/五/七阶段分法归一为七阶段 | 写作与审稿合并为 review 内小循环 |
| 02 单一可变区文件契约 | 四文件分离 | pre-run.sh 禁写校验 |
| 03 固定墙钟预算赛马 | 300-900 秒可配置，git keep/discard | 文献类用 token 预算 |
| 04 eval 持久内核与局部修复 | hot_run 热加载 + local-first 双门控 | 全量重写为降级路径 |
| 05 task 并发与 hub 协调 | 3 并发 + 三频道 + Elo 排序 | 大产物走文件系统 |
| 06 能力最小契约与分面路由 | 三域分面 + 安全 pre_filter | validate/execute 同签名 |
| 07 三段式灵感引擎 | 5 个 + 2 次调用 + PI 门禁 | 单次生成去重后取 top-3 |
| 08 双 keeper 联合裁决 | 数值每轮 + 语义后置 + VLM/FACT 后置 | 阈值默认 6.0 |
| 09 显性推理 trace | 单轮隔离 + 全局追加 + 三级溯源 | FACT 双指标校验 |
| 10 分级验证关卡 | L1 三项必检 + L2 领域校验 + 三层路由 | 验证器与生成器分离 |

延期 5 项：SDL 真机闭环、GFlowNet 与图谱、多租户计费、人类基线对照、联邦调度。激活条件分别量化。

### 2.3 epistemic.md — 11 护栏 5 不确定性

| 护栏 | 主题 | 证据等级 |
|------|------|---------|
| 01 可证伪假设门控 | 三字段缺失阻断 | direct + supported inference |
| 02 可复现执行封存 | 环境代码数据度量同版本封存 | direct + supported inference |
| 03 来源层级与三级溯源 | T0-T4 分级与 FACT 双指标 | direct |
| 04 负结果强制归档 | 双归档与再利用 | direct |
| 05 评估污染隔离 | 泄露检测与 held-out 复测 | direct + supported inference |
| 06 自动化权限分级与安全互锁 | 分级权限与多级互锁 | direct |
| 07 人类复核点与分叉裁决 | nature language 反馈直通 Meta-review | direct |
| 08 跨域迁移显式边界校验 | 不变量缺失降级为探索模式 | direct |
| 09 双 keeper 联合裁决与预算分层 | 双阈值 + 预算分层 | direct + supported inference |
| 10 独立验证层与多样性闸门 | 生成验证分离 + 多样性闸门 | direct + supported inference |
| 11 分层持久记忆与 U 标记 | 三级分层 + U=0/1 标记 | supported inference |

不确定性 5 项：规模化拐点、自主性深度权衡、跨域评估有效性、图谱一致性、激励与成本边界。

---

## 3 Layer 3 双裁判独立性与合议方法

两份裁判独立产生，分工明确。哲学裁判 A 聚焦认识论正确性，运行裁判 B 聚焦单机可运行性。合议方法：逐条对齐，相同处合并，差异处裁决，未决处显式标记风险与验收信号。

| 对齐方式 | 数量 | 处理 |
|---------|------|------|
| 完全一致合并 | 5 条（P01/P02/P04/P05/P11 的前半） | 合并为单一表述，取更具体的机制描述 |
| 互补合并 | 4 条（P02/P03/P07/P08） | 各取一侧长处，指纹、VLM 后置等 |
| 冲突裁决 | 3 条（P09 图谱阈值、P03 预算指纹、P07 keeper 启用范围） | 以运行侧量化阈值为准，作为哲学侧抽象条件的具体化 |
| 运行侧独有增补 | 2 条（task 并发、分层归档） | 增补为注册表独立条目 |

合议裁决标准：跨领域可迁移性、可审计性、可落地性三项。优先级依据地基先行、执行次之、认知与治理随后、领域扩展居后。

---

## 4 逐条合议溯源

| 合议编号 | Layer 1 候选来源 | Layer 2 收敛依据 | Layer 3 裁决来源 | 冲突处置 | 证据等级 |
|---------|----------------|----------------|----------------|---------|---------|
| P01 文件契约 | cs-ml 原则 1, chem 原则 1/2, platform 原则 4 | architecture 决议 02, epistemic 护栏 02 | 哲学 P01 + 运行决议 02 | 无冲突，一致保留 | 高 direct |
| P02 状态机 | platform 原则 4, cs-ml 原则 5 | architecture 决议 01, adversarial 共识 1 | 哲学 P01 后半 + 运行决议 01 | 形态一致，取七阶段 | 高 direct |
| P03 预算 | cs-ml 原则 1, physics 原则 2, chem 原则 5/10, bio 原则 01/08 | adversarial 争议 1, architecture 决议 03, epistemic 护栏 02/09 | 哲学 P02 + 运行决议 03 | 采运行侧四字段指纹 | 高 direct |
| P04 注册表 | platform 原则 1/2, bio 原则 04, chem 原则 1/8 | adversarial 争议 4, architecture 决议 06 | 哲学 P03 + 运行决议 07 前半 | 采哲学 E1/E2 + 运行三域分面 | 高 direct |
| P05 安全门控 | chem 原则 2/3, platform 原则 9, physics 原则 5 | adversarial 争议 5/6, epistemic 护栏 06 | 哲学 P04 + 运行决议 07 后半 | 无冲突，一致为硬门控 | 高 direct |
| P06 可证伪门控 | bio 原则 06/07, cs-ml 原则 05/06/10 | epistemic 护栏 01, architecture 决议 07 门禁 | 哲学 P06 + 运行决议 06 门禁 | 无冲突，三字段阻断 | 高 direct |
| P07 双 keeper | cs-ml 原则 4/5/6/7, bio 原则 06, platform 原则 10 | adversarial 争议 3, epistemic 护栏 05/09, architecture 决议 08 | 哲学 P07 + 运行决议 08 | 采运行分阶段启用 | 中高 |
| P08 分级验证 | physics 原则 2/3/4, chem 原则 8/10, bio 边界 01 | adversarial 争议 8, architecture 决议 10, epistemic 护栏 10 | 哲学 P08 + 运行决议 10 | 无冲突，L1 三项必检一致 | 中高 |
| P09 显性 trace | bio 原则 09, platform 原则 3/8, template 02 §4 | architecture 决议 09, epistemic 护栏 03/04 | 哲学 P05 + 运行决议 09 | 无冲突，FACT 双指标一致 | 高 direct |
| P10 分层记忆 | cs-ml 原则 10, chem 原则 5/7, bio 原则 06, physics 原则 6/7 | adversarial 争议 7, epistemic 护栏 11 | 哲学 P09 + 运行延期 02 | 裁决：首期 pairwise，图谱延后至 50 条 | 中 supported inference |
| P11 人机协同 | bio 原则 01/11, chem 原则 3, physics 原则 9/10, platform 边界 1 | adversarial 争议 9, epistemic 护栏 07, architecture 决议 05 | 哲学 P10 + 运行决议 11 | 无冲突，三类强制介入一致 | 高 direct |
| P12 错误回灌 | cs-ml 原则 2, chem 原则 4, platform 原则 9 | architecture 决议 04, epistemic 护栏 04 | 哲学 P11 + 运行决议 04 | 无冲突，local-first 一致 | 高 direct |

---

## 5 证据等级分布

| 等级 | 数量 | 代表原则 | 说明 |
|------|------|---------|------|
| 高 direct | 8 | P01, P02, P03, P04, P05, P09, P11, P12 | 来源为工作区规格原文、开源代码、运行日志可定位度量，多域独立验证 |
| 中高 direct + supported inference | 3 | P06, P07, P08 | 形态为直接证据，阈值与增益为支持性推断，需 held-out 实测校准 |
| 中 supported inference | 1 | P10 | 形态字段为直接证据，图谱复利量化与共识阈值需运行中统计校准 |
| 推测性外推（已剔除） | — | R01-R05 拒绝项对应 | 跨域外推未经校准的宣称已剔除，列为拒绝项 |

---

## 6 拒绝项溯源

| 拒绝项 | 被拒冲动 | Layer 1 反例 | Layer 2 裁决 | 合议替代 |
|--------|---------|-------------|-------------|---------|
| R01 prompt 安全 | 提示词呼吁替代 pre_filter | chem 原则 3 Coscientist 依赖拒答被标反例 | adversarial 拒绝 1 | P05 硬门控 |
| R02 单一预算统一定价 | 5 min 推广到湿实验 | cs-ml 边界 1, chem 原则 5/10, bio 原则 01/08 | adversarial 拒绝 2 | P03 分层预算 |
| R03 无校准模拟分裁决 | 模拟分独立 keep | cs-ml 边界 2, bio 边界 03, chem 边界 3 | adversarial 拒绝 3 | P07 主次双 keeper |
| R04 无治理扩张注册表 | 百级工具先扩张后补契约 | bio 边界 02, platform 原则 1 失效模式 | adversarial 拒绝 4 | P04 E1/E2 分层 |
| R05 仿真等同成功 | 高分即宣布发现 | chem 边界 2/3, physics 边界 1 | adversarial 拒绝 5 | P08 分层验证 + 原始数据 |

---

## 7 延期项与激活条件溯源

| 延期项 | 来源 | 延期原因 | 激活条件 | 涉及 template |
|--------|------|---------|---------|-------------|
| SDL 真机闭环 | chem 原则 2/3/6/10, physics 原则 9/10, platform 边界 1 | 真实硬件抽象与协议约束，纯软件复刻虚假可执行性 | registry 出现 endpoint: remote 且仿真分支验证通过 | 02-harness |
| GFlowNet 与图谱 | physics 原则 7/8, cs-ml 原则 10, chem 原则 5/7 | reward 建模与图谱一致性成本高，冷启动噪声大 | failed.jsonl > 50 且 mode collapse | 03-inspiration |
| 多租户计费 | platform 原则 6/7, 边界 2 | 本地单机无多租户需求，治理复杂度高于收益 | 多用户共享实例需求出现 | 02-harness |
| 人类基线对照 | platform 原则 10, cs-ml 边界 2 | rubric 维护成本高，需原作者协同 | 连续 5 个 keep 且需对外宣称质量分 | 00-spec |
| 联邦调度 | chem 原则 6, 边界 1/2, physics 边界 2 | 跨站点校准依赖真实硬件数据与权限隔离 | 本地验证通过且需借用云端能力 | 02-harness |

---

## 8 未决风险与观测债务

| 风险 | 关联原则 | 观测债务 | 缓解路径 |
|------|---------|---------|---------|
| 跨硬件指纹可比性未实测 | P03 预算指纹 | device_info 校准参数缺失，跨硬件 delta 虚高 | held-out 复测与指纹对照，Q01 赛道选择后首轮校准 |
| 语义 keeper 校准误差带未公布 | P07 双 keeper | 模拟分与真实接收 gap 未量化 | Q02 决策校准节奏与抽检投入，bench/scores.jsonl 双轨分对照 |
| 图谱共识阈值在小样本下效力不足 | P10 分层记忆 | ≥2 agent 共识在 10-20 样本下统计效力有限 | 运行中积累 50 条后评估，Q03 决策图谱时机 |
| reward 稀疏时多样性退化为随机 | P12 有约束多样性 | distinct_modes 阈值未在工作区实测 | 首期用 0.85 去重与加权排序，延期 02 观察 mode collapse 信号 |
| 仿真外推到大晶胞能力未知 | P08 分层验证 | ≤20 原子预训练外推未验证 | MatterSim 三层路由中 dft 层复核，lab 层原始数据兜底 |
| 人类延迟成瓶颈 | P11 人机协同 | 夜间自治比例与分叉点拦截率未度量 | WATCHDOG.yml 阈值调优，status.md 时延可观测 |

---

## 9 输入文件清单与校验

| 层 | 文件 | 行数 | 状态 |
|---|------|------|------|
| L1 | `debate/layer1/bio.md` | 约 18.6 KB | 已读 |
| L1 | `debate/layer1/chem-materials.md` | 约 18.1 KB | 已读 |
| L1 | `debate/layer1/cs-ml.md` | 约 15.9 KB | 已读 |
| L1 | `debate/layer1/physics-crossdomain.md` | 约 20.8 KB | 已读 |
| L1 | `debate/layer1/platform.md` | 约 21.8 KB | 已读 |
| L2 | `debate/layer2/adversarial.md` | 约 26.6 KB | 已读 |
| L2 | `debate/layer2/architecture.md` | 约 26.5 KB | 已读 |
| L2 | `debate/layer2/epistemic.md` | 约 23.6 KB | 已读 |
| L3 | `debate/layer3/philosophy-a.md` | 约 39.9 KB | 已读 |
| L3 | `debate/layer3/operating-model.md` | 约 39.8 KB | 已读 |
| template | `template/00-spec.md` | 约 13.1 KB | 已读 |
| template | `template/01-workspace-layout.md` | 约 7.6 KB | 已读 |
| template | `template/02-harness-wiring.md` | 约 11.0 KB | 已读 |
| template | `template/03-inspiration-engine.md` | 约 11.4 KB | 已读 |
| channels | `channels/README.md` | 约 11.9 KB | 已读，46 系统索引 |
| derived | `derived-principles/00-design-philosophy.md` | 本次产出 | 已写 |
| derived | `derived-principles/01-principles-registry.md` | 本次产出 | 已写 |
| derived | `derived-principles/02-template-mapping.md` | 本次产出 | 已写 |
| derived | `derived-principles/03-debate-record.md` | 本文件 | 已写 |

验证命令：

```bash
ls debate/layer1/*.md debate/layer2/*.md debate/layer3/*.md template/*.md derived-principles/*.md
grep -c "^## " derived-principles/03-debate-record.md
grep -c "证据等级" derived-principles/03-debate-record.md
```
