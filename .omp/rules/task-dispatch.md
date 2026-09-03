---
description: Task dispatch protocol for the flywheel supervisor
alwaysApply: false
condition: "task\\(|call_task|agent:"
---

# Task Dispatch Protocol

- Dispatch phase work with the `task` tool, passing `agent: "<project-agent-name>"`. Available project agents: literature-scout, idea-generator, modeler, analyst, paper-writer, reviewer-methodology, reviewer-skeptic, reviewer-reproducibility, meta-reviewer.
- Give each subagent the full context it needs in the prompt: run_id, idea record, trace paths, and the exact output contract from its `.omp/agents/<name>.md` definition. Subagents start blank; they never see this chat.
- `modeler` always runs with `isolated: true`. Reviewers run in parallel (one `tasks[]` batch). Never serialize independent reviews.
- Skip formatters and project-wide test suites inside subagents; the runtime gates (compile/smoke/reproduction) are the verification. One integration owner: you.
- Large artifacts stay in files; task prompts carry paths, never blobs.
