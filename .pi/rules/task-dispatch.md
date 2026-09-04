---
description: Task dispatch protocol for the flywheel supervisor
alwaysApply: false
condition: "task\\(|subagent|agent:"
---

# Task Dispatch Protocol

- Dispatch phase work with the subagent `task` tool, passing `agent: "<project-agent-name>"`. Available project agents: literature-scout, idea-generator, modeler, analyst, paper-writer, reviewer-methodology, reviewer-skeptic, reviewer-reproducibility, meta-reviewer.
- Give each subagent the full context it needs in the prompt: run_id, idea record, trace paths, the literature-scout evidence index for the idea, and the exact output contract from its `.pi/agents/<name>.md` definition. Subagents start blank; they never see this chat.
- **Investigation before work（调查前置）.** Dispatch literature-scout before idea-generator/modeler whenever the method domain lacks evidence under `research/`. Then dispatch critical-advisor (Gate 0) to audit the packet — only `substantial_pass` advances; `send_back` returns numbered amendments; `reject_toy` kills the idea. Never dispatch modeler without the evidence index in the prompt.
- `modeler` always runs with `isolation: "worktree"`. Reviewers run in parallel (one batched dispatch). Never serialize independent reviews.
- **Verification duty (not optional).** Runtime gates (compile/smoke/reproduction) are the FLOOR of verification, not its totality. Every dispatched task whose output changes behavior must include behavior-level checks over the changed code, and the dispatcher includes the deliverable definition (`.pi/rules/flywheel-hard-constraints.md` clause 11) in the prompt. A subagent that returns "done" without its deliverable is rejected and re-dispatched with the gap named.
- **Gate 2 before keep.** After a candidate completes and the analyst audit passes, critical-advisor audits the keeper candidate (toy-work / minimal-progress / unrelated submission / fake progress → `reject_toy` blocks keep). Then run `orchestration/flywheel.py --resolve-review <run_id>` so the runtime deterministically enforces the panel verdict.
- Large artifacts stay in files; task prompts carry paths, never blobs.
