# Research Flywheel — 全自动科研飞轮工作区模版

> 一句话：`pi` 打开工作区，输入一句灵感或空输入，agent 全自动完成建模 → 实验 → 评估 → 写作 → 审稿 → 归档，产出论文草稿或结构化失败结论；灵感亦可在一轮轮 autoresearch 中自动产生，夜间无人值守自转。

## 目录

```
research-flywheel/
  README.md               # 本文件，入口与导航
  pyproject.toml          # Python >=3.11，uv 管理，package=false
  uv.lock                 # 已提交锁文件；指纹 package_lock_hash = sha256:<uv.lock digest>，缺失时为 "unlocked"
  .python-version         # 3.11
  channels/               # 各渠道可借鉴点（23 文件，46 系统）
    01-karpathy-autoresearch.md ... 23-misc-university-labs.md
    _index-cs.md / _index-biomed.md / _index-chemmat.md / _index-platform.md / _index-physics-misc.md
    README.md             # 全量 46 条索引总表
  template/               # 工作区规格（可直接 scaffold）
    00-spec.md            # 七阶段状态机、度量契约、失败路径、harness 接线
    01-workspace-layout.md# 目录树、文件契约、读写边界、git keep/discard
    02-harness-wiring.md  # pi 接线：subagent task / uv fresh process / schedule_prompt / trace
    03-inspiration-engine.md # 自动灵感：Sakana / Co-Scientist / Virtual Lab 三式对比
```

## 环境要求（可移植默认）

- **Python `>=3.11`**（仓库固定 `.python-version` 为 `3.11`，`pyproject.toml:requires-python` 一致）
- **uv**（已提交 `uv.lock`；`[tool.uv] package=false`，无依赖时亦保持锁文件可复现）
- POSIX shell + Git（`task` 隔离与归并依赖 Git baseline）

指纹契约：`metrics.json:fingerprint.environment.package_lock_hash` 为 `sha256:<uv.lock digest>`（`uv.lock` 存在时）或 `"unlocked"`（缺失时）。`evaluation.evaluator_hash` 与 `fingerprint` 完整才参与 keeper 判定。

## 快速开始（uv 默认，零持久内核）

> 默认路径在普通 shell 中即可跑通。`uv` + `uv.lock` 存在时用 uv，缺失时 shell 入口回退到 `python3`/`python` 以便 bootstrap。

```bash
# 1) 一次性同步（冻结锁文件）
uv sync --frozen

# 2) 建仓（或空灵感触发自动产生）
bash orchestration/scaffold.sh --idea "gated attention with learned temperature"
# 或
bash orchestration/scaffold.sh

# 3) 单轮执行（fresh uv 子进程，默认路径）
uv run --frozen python orchestration/flywheel.py

# 4) 复现最新 keep（shell 入口内部优先 uv，回退 python3/python）
bash reproduce.sh

# 5) 自动灵感（uv 管理）
uv run --frozen python orchestration/inspiration.py --once
```

夜间自转：`schedule_prompt` 每 30-45 分钟一轮 — 取 `archive/ideas.jsonl` 最高分 → `run_once`（uv fresh process）→ keep/discard → archive → 晨间 `status.md`。运行时机仅自动执行 `hardware_dependency_level == 0` 且未命中 `WATCHDOG.yml` human gate 的任务。

详见 `template/00-spec.md` 验证标准：`uv sync --frozen` 后 30 分钟内在 `traces/` 看到 metrics，在 `archive/` 看到 keep 或 failure 归档，`traces.jsonl` 可回放。


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
- **Harness**：subagent `task` 并行探索（worktree 隔离）、`uv run --frozen python` fresh 进程为默认且唯一正式执行路径、`schedule_prompt` 定时、`git` keep/discard、`traces.jsonl` 追踪
- **灵感引擎**：Sakana 头脑风暴+查新 / Co-Scientist 辩论+Elo / Virtual Lab PI分配，三式统一为 候选→去重→辩论→Elo→入队
- **可移植 Python**：`pyproject.toml`（`>=3.11`，`package=false`）、`uv.lock`（`sha256` 指纹）、`.python-version`（`3.11`）随模版分发；`uv sync --frozen` 一次，之后均用 `uv run --frozen python ...`

## 来源验证

全部渠道经 `web_search` + `read` 论文/官网/GitHub 交叉验证，详见各 `channels/*.md` 末尾来源节。

## 下一步

1. `uv sync --frozen` 后按 `template/01-workspace-layout.md` 一键 scaffold 最小可跑工作区
2. 接入首个领域（如单 GPU 语言建模或 PDE 求解）的 `prepare.py` 与 `bench/`
3. 跑首轮夜间循环基线，打通 metrics → keep → report → failure 四门控（全程 `uv run --frozen python ...` fresh 进程）
