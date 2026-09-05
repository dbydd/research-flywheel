Pi is the entry point.
On session start the plugin reports the idea pool and points to `/bootstrap`.
`/bootstrap` is interactive: field, question, constraints, then confirm. `[direction]` skips the prompts.
After scout dispatch the plugin removes README.md. That file is user-facing only; the workspace then runs agent-only.
`/flywheel <idea-id>` reports the next station and its prior text.
`flywheel_tick` is the same advance logic as a tool for agent-driven scheduling.
`station_result` reads one station run dir.
`station_ledger_append` appends one ledger line.
Role presets live in `.agents/roles/<role>.md`.
The Pi tool `dispatch_role_agent` creates a worktree through Orca.
It injects the role preset as that worktree root `AGENTS.md`.
It starts Pi there.
Worker spawn uses `dispatch_role_agent`.
Worker goal tracking uses pi-codex-goal (`create_goal`, `get_goal`, `update_goal`) plus the rpiv-todo `todo` tool.
Station completion is the `station-result.txt` DONE line.

Brief parts order:
- Why: this station exists for this reason
- Background: research background and known constraints
- Prior: prior station output, cause and effect, artifact paths
- How: steps, commands, file ranges
- Evidence: paths the worker must read
- Done when: checkable outputs
- Failure Done: attempted, observed, cause, next

Write the full brief before calling `dispatch_role_agent`.

Worker bootstrapping: after Pi reaches idle the scheduler sends one kickoff message carrying the exact `create_goal` objective plus the exact `todo` list.
The worker executes those tool calls first, then does the station work, writes `station-result.txt`, then calls `update_goal` status complete.
The scheduler reads `station-result.txt` only.

Persistent scheduler state lives in `.agents/`.
The scheduler reads `.agents/ideas.jsonl` and `.agents/ledger.jsonl`.
Workers do not read `.agents/` directly; they read paths named in their brief.

Production chain: scout → modeling → experiment → evaluation → writing → review → archive.
Run `dispatch_station` per idea, station by station, passing prior station output as Prior.
Scout needs direction. The other stations need idea and prior.
The plugin builds each station brief from the idea record.
Station run dirs live under `.agents/runs/<idea-id>/<station>/`.
Archive appends `.agents/ledger.jsonl` and moves kept papers to `papers/`, failures to `.agents/archive/<idea-id>/`.

Modeling uses the host `lean` binary.
The template does not install Lean; the host provides it.
