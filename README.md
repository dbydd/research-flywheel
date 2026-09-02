# Research Flywheel — 全自动科研飞轮工作区模版

> 一句话：`omp` / `pi` 打开工作区，输入一句灵感或空输入，agent 全自动完成建模 → 实验 → 评估 → 写作 → 审稿 → 归档，产出论文草稿或结构化失败结论；灵感亦可在一轮轮 autoresearch 中自动产生，夜间无人值守自转。

## 目录

```
research-flywheel/
  README.md               # 本文件，入口与导航
  channels/               # 各渠道可借鉴点（23 文件，46 系统）
    01-karpathy-autoresearch.md ... 23-misc-university-labs.md
    _index-cs.md / _index-biomed.md / _index-chemmat.md / _index-platform.md / _index-physics-misc.md
    README.md             # 全量 46 条索引总表
  template/               # 工作区规格（可直接 scaffold）
    00-spec.md            # 七阶段状态机、度量契约、失败路径、harness 接线
    01-workspace-layout.md# 目录树、文件契约、读写边界、git keep/discard
    02-harness-wiring.md  # OMP/PI 接线：task/eval/hub/schedule_prompt/trace
    03-inspiration-engine.md # 自动灵感：Sakana / Co-Scientist / Virtual Lab 三式对比
```

## 快速开始（规划）

```bash
bash template/../orchestration/scaffold.sh --idea "gated attention with learned temperature" --budget 300
# 或空灵感触发自动产生
bash orchestration/scaffold.sh --budget 300

# 夜间自转
# schedule_prompt 每 30-45 分钟一轮：取 ideas.jsonl 最高分 → run_once → keep/discard → archive → 晨间 status.md
```

详见 `template/00-spec.md` 验证标准：30 分钟内在 `traces/` 看到 metrics，在 `archive/` 看到 keep 或 failure 归档，`traces.jsonl` 可回放。

## 渠道概览（46 系统）

| 类别 | 代表系统 | 可借鉴核心 |
|------|----------|------------|
| CS 通用 | Karpathy autoresearch, Sakana v1/v2, HKUDS AI-Researcher, CycleReviewer, Dolphin/VirSci | 单文件赛马 + tree search + 双循环偏好训练 + 异常局部修复 |
| 生物医学 | Stanford Virtual Lab, Biomni, Google Co-Scientist, FutureHouse Robin, TxAgent | PI/critic 会议 + 150 工具检索 + Elo 锦标赛 + lab-in-the-loop |
| 化学材料 | Coscientist, ChemCrow, SciAgents, Berkeley A-Lab, Toronto SDL, MatterGen | 18 工具 guard + 图推理 + 机器人闭环 + 扩散生成筛选 |
| 平台基建 | Bohrium+SciMaster, Agent Lab/Rxiv/Claw, Deep Research, Benchmarks | 四层能力注册 + 预印本协作 + 双轨评测 + flywheel 制衡 |
| 物理跨学科 | AutoNumerics/PhysMaster, Denario/Rumi, DigCat/A-Lab, 7 校 SDL | 残差自验证 + GFlowNet 多样性 + 云端分发 + 10x 压缩比 |

全量索引见 `channels/README.md`，分领域汇总见 `channels/_index-*.md`。

## 规格要点

- **七阶段**：inspiration → modeling → experiment → evaluation → writing → review → archive，失败可从 evaluation/review 直达 archive
- **三文件基座**（Karpathy）：`prepare.py` 固定评估，`run.py` 唯一可变，`program.md` 冻结目标
- **三阶段**（Agent Lab）：`navigator/` 文献、`traces/` 实验、`reports/` 写作
- **四层**（Bohrium）：Data / Model / Execution / Orchestration 映射到 `prepare.py+bench/` / `run.py` / `traces/` / `orchestration/`
- **Harness**：`task` 并行探索、`eval` 持久内核、`hub` 协调选举、`schedule_prompt` 定时、`git` keep/discard、`traces.jsonl` 追踪
- **灵感引擎**：Sakana 头脑风暴+查新 / Co-Scientist 辩论+Elo / Virtual Lab PI分配，三式统一为 候选→去重→辩论→Elo→入队

## 来源验证

全部渠道经 `web_search` + `read` 论文/官网/GitHub 交叉验证，详见各 `channels/*.md` 末尾来源节。

## 下一步

1. 按 `template/01-workspace-layout.md` 一键 scaffold 最小可跑工作区
2. 接入首个领域（如单 GPU 语言建模或 PDE 求解）的 `prepare.py` 与 `bench/`
3. 跑首轮夜间循环基线，打通 metrics → keep → report → failure 四门控
