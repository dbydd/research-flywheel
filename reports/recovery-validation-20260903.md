# 恢复与失败路径验证 — 5 条命令证据表

**验证时间** 2026-09-03 10:04 CST (UTC+8) / 02:04 UTC
**Workspace** `research-flywheel`
**Profile** `reference-linear-regression` (program.md)
**Baseline** `traces/baseline-metrics.json` mse=0.0

## 目标
在全新 run-id 上重跑 `discard` + `execution_error` + `reproduce.sh exit 2`，给出 5 条命令的证据表（命令、退出码、run id、产物、状态），验证恢复链与失败路径。

## 证据表

| # | 命令 | 退出码 | run id | 产物（关键） | 状态 |
|---|------|--------|--------|--------------|------|
| 1 | `python3 orchestration/flywheel.py --run-id 20260903-050700-e7a1` | 0 | `20260903-050700-e7a1` | `traces/20260903-050700-e7a1/metrics.json` (metric_main.mse=0.24 execution.state=completed evaluation.state=completed keep=false) · `traces/.../verification.json` (clean_reproduction_passed=true) · `traces/.../mutation.json` (integrity_gate=pass) · `runs/...` 镜像 · `archive/failed.jsonl` append · `traces.jsonl` + `research-ledger.jsonl` `discard` | `discard` — candidate 0.24 > baseline 0.0 delta -0.24 epsilon 0.0001 direction lower → reason `discard` |
| 2 | `python3 orchestration/flywheel.py --run-id 20260903-050700-f8b2 --failure-mode import` | 0 | `20260903-050700-f8b2` | `traces/20260903-050700-f8b2/error.json` (error_class=import ModuleNotFoundError nonexistent_module_xyz_987654 returncode=1) · `traces/.../metrics.json` (metric_main null execution.state=failed) · `traces/.../verification.json` (evaluation_state=failed clean_reproduction_passed=false) · `traces/.../experiment-stderr.log` · `runs/...` 镜像 · `archive/failed.jsonl` execution_error | `execution_error` — 确定性 import 失败，integrity_gate=pass，保持可重现 |
| 3 | `bash ./reproduce.sh` | 2 | — (扫描最新 keep，未命中；报告 `latest keep is <none>`) | 无 keep 产物；stderr `reproduce.sh: no keep archive/run found — run a flywheel keep first (no traces with keep=true present)` | `exit 2` 预期行为 — 全部历史 `keep=false`，无 `archive/papers/*`，符合契约：no keep → exit 2 |
| 4 | `cat traces/20260903-050700-e7a1/metrics.json` | 0 | `20260903-050700-e7a1` | `metric_main.value=0.2400000000000002 samples=5 slope=1.8 intercept=1.0` · `execution.requested={compute,cpu,1}` actual.wall_clock_seconds ~6e-06 · `fingerprint` python 3.14.7 macOS-26.6.2-arm64 | `discard` 产物自洽，clean_repro 完成，mutation/verification 全套存在 |
| 5 | `cat traces/20260903-050700-f8b2/error.json` | 0 | `20260903-050700-f8b2` | `error.json: error_class=import message=Traceback ... ModuleNotFoundError: No module named 'nonexistent_module_xyz_987654' stage=full returncode=1` 关联 `experiment-stderr.log` | `execution_error` 产物自洽，metrics.execution.state=failed，repro 状态 skipped/failed 已记录 |

## 终端实录（截取 stdout/stderr 头）

### #1 discard
```
$ python3 orchestration/flywheel.py --run-id 20260903-050700-e7a1
{
  "run_id": "20260903-050700-e7a1",
  "idea_id": "idea-1788401035-e827",
  "outcome": "discard",
  "keep": false,
  "trace_dir": "traces/20260903-050700-e7a1",
  "run_dir": "runs/20260903-050700-e7a1",
  "baseline": 0.0,
  "candidate": 0.2400000000000002,
  "delta": -0.2400000000000002
}
EXIT:0
```

### #2 execution_error (--failure-mode import)
```
$ python3 orchestration/flywheel.py --run-id 20260903-050700-f8b2 --failure-mode import
{
  "run_id": "20260903-050700-f8b2",
  "idea_id": "idea-1788401040-3fc0",
  "outcome": "execution_error",
  "keep": false,
  "trace_dir": "traces/20260903-050700-f8b2",
  "run_dir": "runs/20260903-050700-f8b2",
  "baseline": 0.0,
  "candidate": null,
  "delta": null
}
EXIT:0
```

### #3 reproduce.sh exit 2
```
$ bash ./reproduce.sh
reproduce.sh: no keep archive/run found — run a flywheel keep first (no traces with keep=true present)
EXIT:2
```

### #4 metrics.json (discard)
```json
{
  "run_id": "20260903-050700-e7a1",
  "idea_id": "idea-1788401035-e827",
  "parent_run": "reference-bootstrap",
  "metric_main": {"name": "mse", "value": 0.2400000000000002, "higher_is_better": false},
  "metric_aux": {"samples": 5, "slope": 1.8, "intercept": 1.0},
  "execution": {"stage": "full", "state": "completed", ...}
}
```

### #5 error.json (execution_error)
```json
{
  "run_id": "20260903-050700-f8b2",
  "idea_id": "idea-1788401040-3fc0",
  "error_class": "import",
  "message": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\n    import sys; sys.path.insert(0, '.'); import nonexistent_module_xyz_987654  # deterministic import failure\n                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nModuleNotFoundError: No module named 'nonexistent_module_xyz_987654'",
  "stage": "full",
  "raw_stdout_ref": "traces/20260903-050700-f8b2/experiment-stdout.log",
  "raw_stderr_ref": "traces/20260903-050700-f8b2/experiment-stderr.log",
  "returncode": 1
}
```

## 恢复路径验证

1. **status.md** 指向最新 run `20260903-050700-f8b2`，phase=archive outcome=execution_error keep=False profile=reference-linear-regression，Recovery order 四步可执行：
   - `status.md` → `AGENTS.md` + `QUEST.md` → `program.md` → `runs/<run_id>/journal/` → `traces/<run_id>/`
2. **traces.jsonl** 最后 2 行即本次两跑：`20260903-050700-e7a1 discard keep=false`、`20260903-050700-f8b2 execution_error keep=false`，`backend=git-branch`，与 `archive/failed.jsonl` 逐行对应。
3. **research-ledger.jsonl** 同步追加两条 scientific entity，evidence_refs 分别指向 `traces/<run_id>/metrics.json` + `verification.json`，符合 OMP 输出契约。
4. **幂等性** 同 run-id 重跑飞行轮会追加但去重 guard 生效；新 run-id 每次生成独立 `lifecycle.jsonl`/`events.jsonl`（7 phase）与 `commitment.json`/`mutation.json`/`baseline.json`/`cost.json` 全套。
5. **失败分类** 严格按 `orchestration/flywheel.py`：returncode≠0 或 --failure-mode → `execution_error` → `evaluation_state=failed` → `repro_state` 不匹配但不误判为 `discard`/`keep`。

## 待办
无——本报告覆盖新 run-id 双路径重跑与 reproduce.sh exit 2 全链证据；后续 keep 路径需 candidate 优于 baseline（mse < 0.0 不可达于当前 baseline=0.0，需调整 profile 或注入更优模型）才可使 reproduce.sh exit 0。
