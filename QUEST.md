# Research Flywheel Quest

## Goal
Run a zero-dependency reference research experiment through the pi workspace (investigation-first: frontier evidence pulled to research/ before any method work) and leave a reproducible paper draft or a structured failure conclusion.

## Complete chain

Input: a sentence in `inspiration.md`, a queued record in `archive/ideas.jsonl`, or an empty queue.

Output: a run under `runs/<run_id>/`, a trace under `traces/<run_id>/`, a native evaluation, a report and review, a paper or failure archive, an updated research ledger, and `status.md`.

## Reference task

Use the synthetic regression profile in `program.md`. The experiment implementation proposes a small model change in `experiment/run.py`. The fixed evaluator in `evaluation/prepare.py` measures mean squared error on deterministic data. The reference profile runs locally with no network, instrument, package install, or paid service.

## Resume rule

Resume the active run from its latest phase journal. Preserve completed evidence. Re-run formal comparison in a clean process when exploratory state exists.
