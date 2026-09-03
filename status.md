# Research Flywheel Status

## Initial state
- status: ready
- profile: reference-linear-regression
- queue_depth: 5 ideas queued in archive/ideas.jsonl
- baseline: main branch, deterministic identity MSE 0.0

## Quick start
- Run single iteration: `python3 orchestration/flywheel.py --once`
- Verify reproduction: `bash reproduce.sh`
- Unattended cron: register `orchestration/schedule.json` via `schedule_prompt`
