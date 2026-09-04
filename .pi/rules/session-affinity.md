---
description: Session affinity policy — when dispatch reuses an agent session vs opens a fresh one
alwaysApply: true
---

# Session Affinity Policy

**Principle: the workspace files are the authoritative memory; sessions are caches.** Every agent must be able to oneshot into the correct state from files alone (traces/, preflight.md, journal/, research/, ideas.jsonl). If a fresh agent with the full file contract cannot oneshot, fix the files and the contract — never paper over it with a longer-lived session. A long-lived session is a second authority: not replayable, not forkable, invisible to the evidence envelope.

## Default: fresh

- **Phase boundaries always open a new session**: scout → idea → model → execute → audit → write → review → aggregate. Downstream conclusions are already serialized (preflight.md, mutation.json, traces/); the next phase needs the conclusions, not the previous agent's chat memory — and cutting the chat memory also cuts preference contamination (the scout's tastes must not steer the modeler).
- **Independence boundary (no exceptions)**: reviewer-methodology, reviewer-skeptic, reviewer-reproducibility, analyst, critical-advisor are ALWAYS fresh sessions and MUST NEVER resume or steer a session that belongs to a writer/modeler or to each other. Anchoring is not a tuning problem; it is a validity problem.

## Resume (notify the old session) — only three cases

1. **Iterative loop inside one phase**: the modeler's sanctioned repair round, the scout amending a packet after a `send_back` with numbered amendments. Resume keeps tacit context and avoids re-reading the whole library.
2. **Consecutive small steps in one run**: same agent, no rejected output since the last resume, same run_id.
3. **Incremental deepening of one investigation**: the scout asked to go one level deeper on the same topic (e.g. a second implementation clone for the same packet).

Anything else → fresh. "Saving tokens" is not a reason to resume across a phase boundary.

## Deadlock clause (the stuck-in-a-rut trigger)

- Same agent + same artifact + **2 consecutive** send_back / reject / failed repairs → the next attempt **must** be a fresh session with a re-framed prompt: file paths only, plus an explicit dead-end list from the failed attempts. Resuming the old session for attempt #3 is forbidden — the old session's framing is the disease at that point.
- The re-frame requirement is not optional: "same prompt, new session" is NOT a valid retry; the prompt must name what was tried and demand a different approach.

## Dispatch ledger (make the decision auditable)

The supervisor appends one line to `runs/<run_id>/sessions.jsonl` for EVERY dispatch:

```json
{"ts": "<iso>", "agent": "<name>", "mode": "fresh|resume", "reason": "<one clause>", "prior_session_ref": "<runId or null>", "artifact": "<path or null>"}
```

- resume without a valid clause-1/2/3 reason is a defect critical-advisor can cite at Gate 0/Gate 2.
- A third attempt without a session switch after 2 rejects is a blocking finding.

## Mechanics

- pi subagents: fresh = `context: "fresh"`; resume = re-invoke with the prior runId and a follow-up message (steer/resume). Workflows keep `context: "fresh"` on all phase agents per this policy.
- The ledger file is supervisor-owned and append-only, same discipline as the journal.
