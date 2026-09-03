---
globs: ["reports/*.md", "runs/*/journal/*.md", "traces/*/reasoning.md"]
description: Report writing rules for flywheel keepers and failure records
---

# Report Writing Rules

- Every quantitative claim cites a file under `traces/<run_id>/`. An uncited number is a defect; a reviewer rejects for it.
- State results in the evaluator's own units and direction (`higher_is_better` field). Never reframe a worse metric as a win ("converged faster", "more stable") — the profile decision rule is the only interpretation.
- `reports/report.md` exists for keepers only. `reports/failure.md` is the terminal artifact for discard/inconclusive/execution_error and is generated from the evidence envelope, not from imagination.
- Next-hypotheses sections feed `idea-generator`. Write them implementable: a patch direction on `mutable_paths`, an expected delta, a risk. A vague "explore further" line wastes a night cycle.
- Write plainly: direct declarative sentences. No contrastive rhetoric ("not X but Y", "however", "其实/而是") in any agent-authored file in this workspace.
