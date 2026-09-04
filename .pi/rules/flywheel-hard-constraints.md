# Flywheel Hard Constraints

These constraints hold for every agent, every phase, every schedule prompt. They are sticky on purpose: they must stay in force after a long night session.

## Measurement integrity (existing, confirmed correct)

1. Never bypass the keeper gate. Keep requires execution completed + evaluation completed + clean reproduction passed + |delta| > epsilon in the profile direction + analyst `audit_pass`. A review panel may reject a keeper; no agent may pass a candidate the gate failed.
2. Never edit `evaluation/prepare.py`, `program.md`, `capabilities/registry.json`, or any `integrity_paths` entry during candidate work. These files define the measurement; changing them voids every comparison.
3. Modeling edits happen only inside an isolated worktree, only on `experiment_profile.mutable_paths`. The parent checkout stays at the baseline.
4. `traces/`, `runs/`, `traces.jsonl`, `research-ledger.jsonl`, `terminal.json` are runtime-owned and append-only for agents. Never rewrite or delete evidence; a wrong record gets a corrective append, never an edit.
5. Every terminal outcome is archived before a candidate branch is deleted: keep → papers + report; discard/inconclusive/execution_error → `archive/failed.jsonl` + failure record.
6. A metric from a contaminated cell (no fresh process before formal comparison) is invalid evidence. Re-run clean before any keep decision.
7. Stay inside `program.md` `authorization_boundary`. An action outside it requires a `pending-actions.jsonl` record and a journal checkpoint first; then continue runnable work.
8. No real-world side effects: no purchases, no deletions outside the workspace, no credential access. Investigation pulls (see constraint 9) and literature fetches are explicitly authorized; experiment runtime is local-only by design.

## Investigation-first obligations（调查前置） (added 2026-09-04, see derived-principles/04-constraint-audit.md)

9. **调查前置（No work without investigation）.** Before idea generation or modeling on any nontrivial method domain, the literature-scout must have investigated the frontier AND pulled real evidence to `research/` (repos, code, papers, with provenance). Paraphrase-only "evidence" does not satisfy this clause; evidence = artifacts pulled locally to `research/` (拉取到本地的真实物料，纯文字转述不算). Agents must refuse task-skip pressure: receiving a task with no investigation evidence → report `investigation_missing`, do not improvise.
10. **无中生有禁令（Nothing from thin air）.** Every artifact an agent produces must trace to the active idea's hypothesis/method and its recorded evidence. An off-task artifact (a script unrelated to any idea, a generic demo) is an execution_error, not a contribution.
11. **任务量下限（Task-size floor）.** Completion is defined by deliverables, not by elapsed time or number of checks run. Each phase's deliverable: idea = falsifiable hypothesis with cited evidence; model = method implemented completely within mutable_paths; verification = assertions over the changed behavior; report = every number cited to its trace file. Doing less than the deliverable and calling it done is laziness, and laziness is a defect, not a style.
12. **真实检查（Real checks only）.** Verifying means asserting the changed behavior (compile gate, smoke evaluate, behavior-level checks recorded in `mutation.json:behavior_checks`). Environment probes (interpreter versions, tool presence, directory listings) are setup steps, never verification results, and must never be reported as gate outcomes.
13. **诚实升级（Honest escalation）.** On gate failure: at most one repair round, then report the structured error. Silent workarounds, weakened assertions, or "checks" chosen to pass are findings of the highest severity.
