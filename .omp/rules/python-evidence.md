---
globs: ["experiment/**/*.py", "evaluation/**/*.py", "orchestration/**/*.py"]
description: Python evidence discipline for flywheel experiment and runtime code
---

# Python Evidence Discipline

- The deterministic profile runs on stdlib only. Adding an import of anything outside the standard library in `experiment/` or `evaluation/` counts as an execution error (`import` class), a feature for failure drills, a bug anywhere else.
- Prefer `python3`; fall back to `python` in shell entry points (`reproduce.sh`, `orchestration/hooks/*.sh`). Keep the portability comments intact — they mark reversible choices.
- Runtime scripts are concurrency-safe by contract: idea claims and run-id reservations go through the existing `fcntl` lock helpers (`locked()`, `.lock` files). A new writer of `archive/ideas.jsonl` or `traces.jsonl` reuses `atomic_append`/`append_jsonl`; raw `open(...,'w')` on a shared JSONL is a bug.
- Error envelopes follow `template/02-harness-wiring.md`: `error_class` ∈ syntax|import|runtime|timeout|resource|assert, with `raw_stdout_ref`/`raw_stderr_ref` pointing at preserved logs. Never truncate stderr to save space.
