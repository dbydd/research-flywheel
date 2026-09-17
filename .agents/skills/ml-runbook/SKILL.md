---
name: ml-runbook
description: runner 跑批工具面手册。开工与交件前加载：measured/environment.json 读数器字段规范、静默失败清单与评测红旗表、评测协议检查项、工具登记簿、长批切片操作法。qa 复核读数有效性时读 ①②③。用户提到跑批、环境记录、读数有效性、静默失败、红旗、held-out 终判、切片、续跑时使用。
---

# 跑批手册（ml-runbook）

定位：服务 runner（主）与 qa（读 `environment.json` 判有效性）。本文件只补操作细节与可对拍字段。功耗纪律、训练槽、uv/lightning/polars/CSVLogger 选型、三约束、held-out 条款一律以仓根 `AGENTS.md` 为准，冲突时以仓根为准。

## ① 读数器规范（`measured/environment.json`）

作用：把预算条与确定性条从散文变成可对拍数字。字段缺项即无有效读数，qa 直退单。

| 键 | 填什么 | 依据 |
|---|---|---|
| `schema_version` | 读数器与校验器共同常量（如 `"1"`） | 常量即契约 |
| `slice_id` `task_id` `pid` `started_at` `finished_at` | 一片一份，时刻用 ISO | 可续跑可追责 |
| `wall_time_s` | 实测秒数，不用步数折算 | 声明步数是下界，不是耗时 |
| `peak_rss_mib` | 进程树峰值内存 | 预算条证据 |
| `memory_model` | `unified_cpu_gpu` 或 `discrete` | Apple silicon 禁把统一内存当独立 VRAM 相加 |
| `thermal` | `pmset -g therm` 原文一行 + `throttled: true|false|null` | 热降频迹象 |
| `limits` | `available_cores` / `effective_capacity_cores` / `quota` / `mem_available_mib`，四类事实分开记 | quota 1.5 是 CPU 时间带宽，不是 1.5 个物理核 |
| `budget_plan` | 计划值，非实测：`suggested_workers` / `threads_per_worker` / `binding_limits[]` / `warnings[]` | 多天花板取最小值；内存未知退到 1 worker 并记 `MEMORY_UNKNOWN` |
| `backend` | `accelerator` + `usability: verified|not_verified` | 管理查询可见 ≠ 有调度权与运行时兼容 |
| `pins` | python 版本、`包@版本` 串、`uv.lock` hash、核对日期 | pin 是与数值同等的断言要素 |
| `seed` | 值 + 作用域（train 与 eval 分开） | 确定性条 |
| 缺观察 | 一律写 `null` | 禁把 unknown 当 unlimited |

写入器规则：
- 序列化 `json.dumps(..., sort_keys=True, allow_nan=False, ensure_ascii=False, indent=2)`，产出字节级可 diff。
- 落盘走 `O_WRONLY|O_CREAT|O_EXCL` + `O_NOFOLLOW` + `0o600` + `fsync`，默认拒绝覆盖；`--force` 才替换，替换在 `run-log.md` 记一行。
- 一份 `environment.json` 写定后不改；多片逐片落 `environment.<slice_id>.json`，`run-log.md` 指过去。
- 输入有界：拒 symlink、拒 URL、拒非 regular file，快照 ≤1 MiB。
- 探针只读：固定 argv 元组、无 shell、无字符串拼接、短超时；禁 stress test、大分配、改 affinity、改时钟功耗。
- 探针失败不得抹掉已有观察，只在 `warnings[]` 记稳定 code 并排序输出。
- 批前后各采一份，diff 忽略时刻字段。packs ② 预算条 = 快照 + 计划 + 实际 wall-time 三件对拍，不接受自述。
- 计划值与实测值分列：`budget_plan.*` 是计划，`limits.*` / `wall_time_s` / `peak_rss_mib` / `thermal` 是实测。`summary.md` 与 packs ② 预算条写成「计划 / 实测 / 差」三列并排，实测槽禁填计划值。

## ② 静默失败清单 + 红旗表

交件前逐条过。每条配一个当场可跑的探针，探针结论写进 `measured/self_checks.json`。

| # | 静默失败（数字看着正常，读数其实无效） | 探针 |
|---|---|---|
| 1 | LR schedule 没真被应用 | 每步打印实际 LR，首步值必须等于 hparams 声明值 |
| 2 | 数据未 shuffle / 批内相关 | 连打两个 batch 的 label 直方图，批样本哈希对拍 |
| 3 | train/val 泄漏 | 缩放、插补、编码、特征选择、alpha 选择全在 Pipeline 内且 per-fold refit；split 先于一切学出来的变换 |
| 4 | 分组/时序用错切分 | 同族样本走 group-aware，时间前后部署走 time-respecting；违规即泄漏 fail |
| 5 | 推理侧预处理与训练不一致 | 复用同一 transform 对象，禁手写第二份 |
| 6 | 标签错 | 噪声检查（cleanlab 类）先在小切片上跑 |
| 7 | tokenizer 与预训练权重不匹配 | 打印 vocab size 与特殊 token id 对拍 |
| 8 | NaN / 发散 | 七查：LR 降 3–10×、梯度裁剪、输入含 inf/nan、logit soft-cap、QK-norm、输出投影 zero-init、梯度累积下 loss 是否除过 `grad_accum_steps`（最后一条是常见假 NaN） |
| 9 | 影子模块 | 项目脚本不得与被安装包同名（`sklearn.py`、`umap.py`）；用 `find_spec` 当场验 |
| 10 | 外来 checkpoint | 只 hash + 分类，不 `torch.load`、不反序列化；复现评测禁 `latest`，写具体 hash |
| 11 | 计时读数无效 | 异步设备先同步再计；kernel 时间与端到端延迟分开报 |

反直觉读数带（别把成功判成失败）：GRPO 的 loss 从 0 开始上升才正常，它是相对初始策略的 KL。看三条带：`reward` 上升、`reward_std` 保持 >0、`kl` 温和增长。报警阈：`reward_std`→0 是模式坍缩；`kl`>0.5 是过冲，降 LR；`reward` 平直是 reward 函数过苛或容量不足。
监控四项：梯度范数尖峰先于 loss 尖峰、逐层激活统计、死神经元（>50% 零激活）、每步 LR。
调试次序：先在单个 batch 上过拟合，过不上就是有 bug；此关未过不谈正则与调参。

红旗表（出现即停手，在 `run-log.md` 记一行；禁当战果入账）：

| 读数现象 | 判读 |
|---|---|
| 全任务 ≈ 随机水平 | 没训好，或评测解析器没吃进输出 |
| 生成任务恰好 0% | 格式/解析 bug，不是能力为零 |
| 跨 seed 方差巨大 | 种子或采样设置未固定 |
| 样样超已发表最强基线 | 大概率数据污染：先查训练数据里有无基准样本 |
| 提升落在噪声内 | 已到分辨极限，报不可辨，不写方向 |

## ③ 评测协议检查（held-out 终判的机械面）

条款本体在仓根（主度量切一份 held-out，verdict 用冻结候选跑一次出终判，失败禁回炉再优化）。这里只给 runner 可核对项。

- 冻结：终判前把候选 checkpoint 的 sha256 写进 `environment.json`，终判只跑该 hash。
- 单次：held-out 只允许一次评测调用；多跑一次即在 `run-log.md` 记事故，第二次数字不进稿、不进 packs。
- 选点：落成布尔字段 `checkpoint_selected_without_eval_feedback`、`deterministic_policy_pass`、`learning_disabled`、`report_per_seed_and_aggregate`，任一为 false 即评测泄漏或读数不可比。
- 调参面：选层、选阈值、选 prompt、选 checkpoint 只能读训练面或 inner fold；报性能走 outer loop。同 fold 选参又报性能即泄漏 fail。
- 报数：few-shot 档、多 seed 的 mean±std、全超参、基线来源（配置/种子/切分，缺一即无效基线）。
- 度量语义对表：分数方向是否 higher-is-riskier、输入形状是概率矩阵还是风险分、排序判别类指标不得当校准证据、归因图不得当性能证据（其报告须留 seed、背景样本、评测预算）。
- 自检断言好形状：可加性检查、分位数单调性、短序列输出 `np.isnan(...).any()`、`terminated` 与 `truncated` 不得混。

## ④ 工具登记簿（名字 + 一句话 + 何时用；安装一律走 uv）

- 训练：PyTorch Lightning（fit/Trainer 单入口 + CSVLogger 主账，本树默认）· scikit-learn（Pipeline 与 CV 反泄漏的标准写法）· TRL GRPO 家族（post-training，读数带见 ②）· pufferlib / stable-baselines3（RL 环境与算法；其多进程采样默认不采纳）。
- 评测：lm-evaluation-harness（60+ 基准、HF/vLLM 后端、few-shot 对齐、逐 checkpoint 追踪；先读「解读结果」节再用）· NeMo Evaluator（容器化多后端多基准，当评测面目录查）· bigcode-evaluation-harness（pass@k，生成与执行分离）。
- 可解释：TransformerLens（activation patching，clean/corrupted × layer×position 扫描，电路与 induction head）· SAELens（SAE 分解多义特征，L0/CE-recovery/dead-features/EV 四读数）· pyvene（声明式因果干预，把机制断言改写成可执行 interchange）· nnsight（PyTorch 内部读取）。
- 数据与资源：polars（本树表格默认）· dask（只在超内存时上，先小数据同步调度器、再 threads、最后 distributed）· get-available-resources 模式（① 的出处）。
- 外发红线：托管日志（W&B、Neptune）、远算（NDIF）、托管索引（Neuronpedia）、联网检索 MCP 均涉数据外发，默认不用；确需先披露并单独批准，主账仍是 `measured/` 文件。
- 领域包（transformers、torch-geometric、aeon、timesfm、statsmodels、pymc、shap、umap-learn）按需查官方 API，不继承其默认工程习惯：`filterwarnings('ignore')`、多进程采样、静默换版本，一律不带进来。
- 版本口径：查包文档先认「最低要求」与「实测版本 + 日期」两句是否分开写，只有实测点可进 `pins`。

## ⑤ 长批切片操作法（片长、进程数、锁语义见仓根；此处只给步骤）

1. 抢槽：按仓根 `.train-slot` 协议原子抢占并写 holder；槽被活 pid 占时先干不需槽的活。
2. 定片预算：起跑前读 ① 的快照与 `budget_plan`，按实测吞吐倒推 45 min 内可完成步数，写死每片步数上限，到点自行退出；被 kill 的片没有完整读数。
3. 落账：每片末写 `environment.<slice_id>.json`、追加 metrics（CSVLogger 主账）、`run-log.md` 一行（slice_id、起止、wall-time、下一步数、异常）。
4. 续跑：下一片从上一片记录的 checkpoint hash 起，`measured/run.log` 的片进度是唯一续跑指针。
5. 让机：片间留散热间隔，同刻训练/拟合进程 ≤1，调度冲突宁可晚出数。
6. 失败三分类，`run-log.md` 记类别 + 失败命令 + 日志路径：`crash`（崩且可修）、`timeout`（超片预算，缩片）、`invalid_reading`（数字在但不可信，回 ② 探针重跑）。
7. 冷启动可重跑：相对路径、以项目目录为准、无交互输入、无手建 venv；全量前先在真数据最小闭环对拍一次。
8. 交活断言三类：文件存在、计数、关键字段在场；自跑自验后在 `run-log.md` 记一行。

## Sources

- 静默失败五条（泄漏、推理侧预处理、标签错、洗牌、tokenizer）、每步打印 LR、监控四项、NaN 七查、单 batch 过拟合优先 → `AI-Research-SKILLs/10-optimization/ml-training-recipes/SKILL.md:280-293` → MIT，改写为探针表。
- GRPO「loss 上升才正常」与 reward/reward_std/KL 三条带及报警阈 → `AI-Research-SKILLs/06-post-training/grpo-rl-training/SKILL.md:349-372` → MIT，事实性读数规则直借、表述改写。
- 评测红旗（随机水平、恰好 0%、跨 run 方差、「样样超 GPT-4」=污染）与最佳实践五条 → `AI-Research-SKILLs/11-evaluation/lm-evaluation-harness/references/benchmark-guide.md:469-482` → MIT，改写；其分数带与 2025 配方属易腐条目，不抄。
- 评测与可解释工具目录（lm-eval-harness、NeMo Evaluator、bigcode、TransformerLens、SAELens、pyvene、nnsight）→ `AI-Research-SKILLs/11-evaluation/*`、`AI-Research-SKILLs/04-mechanistic-interpretability/*` → MIT，只登记名称与用途。
- 读数器写入契约（常量即上限、`sort_keys`、`allow_nan=False`、`O_EXCL`+`O_NOFOLLOW`+`0o600`+`fsync`、拒 symlink/URL、固定 argv 探针、unknown≠unlimited、四类事实分开、Apple silicon 统一内存警告）→ `scientific-agent-skills/skills/get-available-resources/scripts/_common.py:15-87`、`scripts/detect_resources.py:2-7`、`SKILL.md:17-36,84-151` → MIT（该 skill frontmatter `license: MIT`），机制改写。
- `budget_plan` 字段与算法（多天花板取 min、`binding_limits`、`threads_per_worker`、`MEMORY_UNKNOWN` 保守退化、warning 排序）→ `scientific-agent-skills/skills/get-available-resources/scripts/plan_workload.py:85-236` → MIT，字段直借。
- version-scoped 包文档六层写法（底线与实测点分离、日期硬要求、pin 落常量、点名 API 变更、症状→配方陷阱节、Dated sources）→ `scientific-agent-skills/skills/{scikit-learn,pytorch-lightning,transformers,statistical-analysis,scikit-survival}/SKILL.md`（详 `.intake-notes/_frag/ml-runner.md:39-107`）→ MIT，取写法不取条目。
- 反泄漏加严（split 先于学出的变换、per-fold refit、group-aware/time-respecting、outer/inner CV、影子模块禁令、禁 `latest` 与不反序列化外来 checkpoint）→ `scientific-agent-skills/skills/scikit-survival/SKILL.md:137-138,284-287`、`skills/pufferlib/scripts/repro_plan.py:96-100`（全表见 `.intake-notes/_frag/ml-runner.md:236-286`）→ MIT；与三约束重复者只作加严。
- 度量语义限定、可加性/分位数/NaN 自检、异步计时口径、步数是下界 → `scientific-agent-skills/skills/{shap/SKILL.md:18-28,262, timesfm-forecasting/SKILL.md:368-372, pufferlib/SKILL.md:123-126, stable-baselines3/SKILL.md:79-81, optimize-for-gpu/SKILL.md:119-146}` → MIT，改写。
- 失败三分类词表（crash / timeout / 可修崩）→ `AI-Research-SKILLs/10-optimization/ml-training-recipes/references/experiment-loop.md` → MIT，只取分类词。
- 日志字段二分（原始层与标准层互引、批次 ID 跨片一致、模糊信息不猜测写入）→ `nature-skills/skills/nature-experiment-log/SKILL.md:42-84` 与 `references/example-log.md:7-32` → 该目录 frontmatter 标 MIT（仓库根 Apache-2.0，逐目录记出处），只取字段；Obsidian/Dataview/cron/飞书层全弃。

## 与自家条款的接缝

- 功耗纪律与训练槽（单进程、串行、≤45 min 片、`.train-slot` 锁、`pmset -g therm` 采样）正本在仓根 `AGENTS.md`「当前工作模式」节，⑤只补步骤；冲突以仓根为准。
- 三约束：断言清单字段与切分归 `experiment-design`，核验与判词归 qa 及 `evidence-discipline`/`review-discipline`。① 是确定性条与预算条的证据载体，③ 是泄漏条的机械检查，均不改写判词口径。
- raw/derived 二分与命名前缀（`derived_`、`subset_`、七态不合并）正本归 `evidence-discipline` ⑤。① 的「缺观察写 `null`」与其「缺失记 unavailable 而非 0」同向：`null` 与 `unavailable` 是状态标记，不是数值，聚合时不得当 0 吃进。
- 段权：设计段结果节与 `measured/` 流件只增不改。③ 的「多跑一次 held-out」只能作为新增事故记录，不许覆盖原读数。
- 红旗表与 ②③ 的检查项是 qa 出 `rectify` 的触发条件之一；是否成立由 qa 判，runner 不自判通过。
- 路径口径：产物落 `research_project/<项目短名>/measured/`，禁写 `.archive/`；旧 `runs/<run-id>/` 口径已废止。
- 评测器住 `evaluation/`，运行命令原文写进设计段断言清单由 qa 重跑对账；③ 的检查项不替代该命令账。
