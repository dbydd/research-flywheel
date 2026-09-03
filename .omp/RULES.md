# Flywheel Hard Constraints

These constraints hold for every agent, every phase, every schedule prompt. They are sticky on purpose: they must stay in force after a long night session.

1. Never bypass the keeper gate. Keep requires execution completed + evaluation completed + clean reproduction passed + |delta| > epsilon in the profile direction + analyst `audit_pass`. A review panel may reject a keeper; no agent may pass a candidate the gate failed.
2. Never edit `evaluation/prepare.py`, `program.md`, `capabilities/registry.json`, or any `integrity_paths` entry during candidate work. These files define the measurement; changing them voids every comparison.
3. Modeling edits happen only inside an isolated task view, only on `experiment_profile.mutable_paths`. The parent checkout stays at the baseline.
4. `traces/`, `runs/`, `traces.jsonl`, `research-ledger.jsonl`, `terminal.json` are runtime-owned and append-only for agents. Never rewrite or delete evidence; a wrong record gets a corrective append, never an edit.
5. Every terminal outcome is archived before a candidate branch is deleted: keep → papers + report; discard/inconclusive/execution_error → `archive/failed.jsonl` + failure record.
6. A metric from a contaminated eval cell (no `reset` before formal comparison) is invalid evidence. Re-run clean before any keep decision.
7. Stay inside `program.md` `authorization_boundary`. An action outside it requires a `pending-actions.jsonl` record and a journal checkpoint first; then continue runnable work.
8. No real-world side effects: no network endpoints outside the boundary, no purchases, no deletions outside the workspace, no credential access. The reference profile is local-only by design.
