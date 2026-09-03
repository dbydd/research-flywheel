---
globs: ["experiment/**/*.py", "evaluation/**/*.py", "orchestration/**/*.py"]
description: Python evidence discipline for flywheel experiment and runtime code
---

# Python Evidence Discipline

- The deterministic profile runs on stdlib only. Adding an import of anything outside the standard library in `experiment/` or `evaluation/` counts as an execution error (`import` class), a feature for failure drills, a bug anywhere else.
- Portable Python is `>=3.11` (`pyproject.toml:requires-python`, `.python-version` `3.11`). `uv.lock` is committed; `fingerprint.environment.package_lock_hash` is `sha256:<uv.lock digest>` when present, otherwise `"unlocked"`. Keep the portability comments in shell entrypoints intact — they mark reversible choices.
- Shell entrypoints (`reproduce.sh`, `orchestration/hooks/*.sh`) prefer `uv` when `uv` and `uv.lock` exist (`uv run --frozen python ...`), with `python3`/`python` fallback for bootstrap portability. Formal gates (compile/smoke/keeper reproduction) always run as fresh `uv run --frozen python` subprocesses and never require a configured OMP persistent kernel. OMP `eval` remains an optional exploration acceleration only; a metric from a contaminated eval cell is invalid evidence.
- Documentation and templates call `uv sync --frozen` once and then `uv run --frozen python ...` for every Python invocation. No prompt may require a persistent kernel.
- Runtime scripts are concurrency-safe by contract: idea claims and run-id reservations go through the existing `fcntl` lock helpers (`locked()`, `.lock` files). A new writer of `archive/ideas.jsonl` or `traces.jsonl` reuses `atomic_append`/`append_jsonl`; raw `open(...,'w')` on a shared JSONL is a bug.
- Error envelopes follow `template/02-harness-wiring.md`: `error_class` ∈ syntax|import|runtime|timeout|resource|assert, with `raw_stdout_ref`/`raw_stderr_ref` pointing at preserved logs. Never truncate stderr to save space.
