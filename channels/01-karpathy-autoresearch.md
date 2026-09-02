# 01 — Karpathy Autoresearch：五分钟硬循环

## 元信息
- **机构 / 作者**：Andrej Karpathy（前 Tesla AI Director、OpenAI 联合创始人），个人项目，社区协作 fork 扩展
- **发布时间**：2026-03 首个 repo 公开，X 上两条主贴说明设计意图，官网 autoresearch.lol 同步上线
- **论文 / 载体**：无传统论文，以 GitHub repo 为载体，配 `program.md` 作为可编程研究组织接口
- **核心 URL**：
  - Repo：https://github.com/karpathy/autoresearch
  - 官网：https://autoresearch.lol
  - 设计说明推文：https://x.com/karpathy/status/2029701092347630069 与 https://x.com/karpathy/status/2031135152349524125
  - Red Hat 规模化复现：https://developers.redhat.com/articles/2026/04/07/autoresearch-on-red-hat-openshift-ai-198-experiments-zero-intervention
  - 入门解读：https://thenewstack.io/karpathy-autonomous-experiment-loop

## 时间线
- 2026-03：Karpathy 发布 autoresearch，定位为单 GPU 上 nanochat 的自动训练实验机
- 2026-04：Red Hat 在 OpenShift AI 上跑通 198 次实验零干预流水线，验证云端夜跑可行性
- 2026-04 至今：社区 fork 涌现，`miolini/autoresearch-macos` `trevin-creator/autoresearch-mlx` `jsegov/autoresearch-win-rtx` 等覆盖 macOS / Windows / AMD

## 循环形态（文字图）
```
[ Human 编写 program.md ] ──► [ Agent 读取 program.md + train.py + prepare.py ]
        ▲                                  │
        │                          mutate train.py (单文件)
        │                                  ▼
        │                          uv run train.py — 固定 5 min wall-clock
        │                                  │
        │                          读 val_bpb（bits per byte，越低越好）
        │                                  │
        │                     ┌──── keep（metric 提升）──── commit
        │                     │                         │
        │                     └──── discard（未提升）── revert
        │                                                  │
        └──────────── 下一轮迭代（12 次/小时，100 次/夜）◀──┘
```
关键约束：`prepare.py` 固定不动（数据、tokenizer、dataloader、评测逻辑），只有 `train.py` 可改；训练时长固定为真实 5 分钟，确保不同架构/超参/优化器改动在可比时间预算下竞争；越睡越强的夜跑是显式产品目标。

## 智能体架构
- **单 Agent 极简设计**：默认 `program.md` 定义一个 agent，职责为读现状、提假设、改代码、跑实验、判结果、写日志
- **人机边界**：人负责“研究组织代码”（`program.md`），Agent 负责“实验代码”（`train.py`）；人通过改 `program.md` 来编程团队工作方式，后续可扩展为多智能体 swarm（Karpathy 在 README 中指明这是下一步）
- **无内置多角色**：不设 reviewer / PI / critic 分工，评审由 val_bpb 数值自动完成；社区已有实践在 `program.md` 上叠加 planner / executor / analyst 分层

## 工具链
- **训练底座**：PyTorch 单 GPU 闭环，模型、优化器（Muon + AdamW）、训练循环全在 `train.py` 内暴露给 Agent
- **运行器**：`uv` 管理依赖，`prepare.py` 一次性下载数据并训练 BPE tokenizer
- **度量单一度量**：`val_bpb`，与词表大小无关，允许 Agent 自由改 vocab / 架构
- **版本控制即记忆**：git keep/discard 是唯一状态机，progress.png 可视化收敛曲线
- **平台**：官方要求单张 NVIDIA H100，社区 fork 适配 MPS / CPU / 其他加速器

## 评测方式
- **在线度量**：每次 5 分钟跑完立即读 val_bpb，与 baseline 比较决定保留
- **离线分析**：`analysis.ipynb` 回放所有实验日志，画进步曲线与参数敏感度
- **外部复现报告**：Red Hat 记录 198 实验全程零人工干预，作为稳定性证据；社区报告在 TinyStories 等低熵数据集上小模型亦可观察到单调下降

## 开源与复现成本
- **开源状态**：MIT，Star 95k+（截至 2026-04 统计），Fork 13k+，Issue 194
- **复现成本**：单张 H100 可跑；夜跑 8 小时约 96 次实验；CPU/Mac 需配合社区 fork 并调参（见 README 建议：改用 TinyStories、vocab 4096/2048/256、MAX_SEQ_LEN 降至 256、EVAL_TOKENS 缩减、DEPTH 降至 4、WINDOW_PATTERN 改为 "L"、TOTAL_BATCH_SIZE 降至 2^14）
- **依赖极轻**：仅 PyTorch 及少量包，无分布式、无复杂配置

## 可借鉴点（落地到 harness 机制）
1. **单文件变异 + git keep/discard 状态机**：harness 限定可写集合（类似 `train.py`），其余文件只读；每次迭代自动 `git diff` → 跑 → `git commit` 或 `git checkout --`，保证可回滚与可审计；落地时在 `prepare.py` 等价物中加只读校验钩子。
2. **固定时间预算赛马**：harness 强制 `timeout: 300s` wall-clock，无论模型大小都同预算竞争，避免“大模型刷步数”作弊；实现为外层 runner 设硬超时并在超时后立即采 val_bpb，最后一步不完整则丢弃。
3. **program.md 作为可编程研究组织**：把 agent 行为从代码中抽到一份 Markdown skill 文件，人通过改 prompt 即可改团队拓扑；harness 模板可提供 `template/program.md` 预设单 agent / 双 agent reviewer / 多 agent swarm 三档。
4. **单一度量驱动**：选一个词表无关、硬件无关的标量（val_bpb）作为唯一 keeper，简化自动决策；harness 中为每个赛道定义 `METRIC` 与方向（越低越好/越高越好），并在 runner 统一采集。
5. **夜跑与可视化闭环**：`progress.png` + `analysis.ipynb` 让人在早晨一眼判断是否值得继续烧卡；harness 可复用为 `channels/<id>/progress.png` 与每日 `log.md` 自动追加。

## 坑 / 局限
- **固定预算导致跨硬件不可比**：在 H100 上的 5 分钟结果无法与 A100 / Mac 直接对比，论文式报告需注明硬件指纹；harness 需记录 `device_info` 与 `budget_seconds` 两列。
- **单文件作用域限制探索空间**：数据管线、评测逻辑、tokenizer 均被锁死，无法发现需要跨文件协同的创新；扩展时需设计分级解锁（先单文件，后白名单目录）。
- **无语义评审，易过拟合 val_bpb**：数值提升可能来自微调噪声或验证集泄露，缺乏 rubric 或 reviewer；引入轻量 rubric（随机 seed 复测 + held-out 校验）可降低误判。

## 复现指引（最小）
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv run prepare.py   # ~2 min
uv run train.py     # ~5 min 单次验证
# 随后把 Claude/Codex 指向 program.md 启动自治循环
```
