---
name: onlyne-role
description: Use when you work as one role in an Onlyne cluster. Covers task injection, session scope, completion reporting, handoff, send, image parts, and the allowed_targets delivery obligation.
---

# Onlyne Role

You are one role in a cluster. The server routes tasks. The ledger records every step.

One task reaches you as an injected message. Do the work. Report it with a completion.

## How work reaches you

- The task arrives as a user-role injection. The first line reads `From <role>:`. The body follows. Paths of attachments appear after the body. The client writes attachments to `<workspace>/.onlyne/tmp/attachments/`.
- The spec carries your role prose. It is already in your context. Pi adds it as a system-prompt section. An ACP session reads it from the client's block in the workspace `AGENTS.md`.
- The `{task}` placeholder in `[client.runtime] command` holds the task **id**. Argv holds no payload. Never put the body on the command line.
- The workspace `[client.session] scope` decides how many deliveries one session serves. `oneshot` is the default. It opens one session per delivery and closes it when the delivery settles. `task` keeps the session for the next delivery of the same family. `role` keeps a pool and gives the next delivery to the session that waited longest.
- The workspace `placement` decides where your process shows. It is the machine's property. Values are `orca`, `zellij`, `tern`, `headless`, and `external`. `tern` runs you as one block in your role tab. An absent `placement` probes `tern`, then `orca`, then `zellij`, and falls back to `headless`. A nonempty `ONLYNE_BACKEND` names the placement over the workspace key. `client run` exits 5 when the name matches nothing.

## Report a completion

The completion row is the receipt. The supervisor polls it. Report by completing the task.

Inside a pi session, use the plugin tool:

```
onlyne_complete{outcome, summary, details, files}
```

Rules for the fields:

- `outcome` accepts `done`, `failed`, `cancelled`, or `blocked`. Report `failed` when the work cannot succeed. Report `blocked` when something outside this session stops the work. The CLI `--outcome` accepts only `done`, `failed`, and `cancelled`. An `exec` session that hits an outside block reports `failed` and names the block in `summary`. A mounted pi session reaches `done` only through the `onlyne_complete` tool.
- `summary` becomes the ledger `out_head`. The head holds the first 200 grapheme clusters of the completion body. Flatten the text to one line before you send it. Every upstream reader sees this line first. An empty `summary` files your last assistant text as the head.
- `details` carries the full result. The cap is 64 KiB. `files` names the absolute paths that hold the result. Both travel with the completion.
- A turn that ends without `onlyne_complete` gets one nudge in your input. The nudge reads: `If this task is finished, report it with onlyne_complete; if something is missing, say what.` A second turn without one settles the delivery. A `oneshot` task becomes `blocked`. A `task` or `role` session goes idle, and the board reads `waiting`.
- Report one completion per task. The plugin keeps the record in your session. A second `onlyne_complete` for a reported task files no report and answers `reported <outcome>`. The process leaves once, at the completion the plugin acked.
- A hand-run `onlyne complete` mints a fresh `op_id` per call. The ledger reads it as a new frame and appends a second `completion` row. The task row keeps its settled state. Idempotence keys on `op_id` alone. The same `op_id` with the same body answers `duplicate` and replays the first receipt byte for byte. The same `op_id` with a changed body answers `conflict`. Both write no row. Call it once.

### CLI form for exec sessions

The role-speaking CLI verbs are `send`, `reply`, `handoff`, `complete`, `ack`, `reject`, and `control`. They refuse a call that misses either flag. The flags declare that the call stands outside a plugin session. An `exec` session mounts no plugin and runs this form:

```bash
onlyne complete --task <task-id> --outcome done --summary "<one-line result>" \
  [--details "<the full result>" --file <absolute path>] \
  --force --yes-i-am-supervisor-not-other-role
```

### ACP sessions

An ACP session mounts the same three tools through `onlyne mcp`. Its client attaches the MCP server to the session. You need no `onlyne` command. Names and arguments match the tool form above. A refused call returns as the tool result error text, in the client's own words. You name nothing about the task. The client holds it. A call names only the recipient, the text, or the outcome.

## Hand work to the next role

Inside a pi session, use `onlyne_handoff`:

```
onlyne_handoff{to: "<next-role>", text: "<same task text>", image: "<path, optional>"}
```

The host mints the child task. It names your task as `parent_task` and sits one hop deeper. The child carries the family metadata: the family root id, the hop budget, the origin, the deadline, and the labels. A task that meets the hop budget keeps the work. A `handoff` over the budget gets refused, and the refusal names the budget.

An `exec` session runs the CLI form with both supervisor flags:

```bash
onlyne handoff --to <next-role> --task <task-id> --text "<same task text>" \
  --force --yes-i-am-supervisor-not-other-role
```

`onlyne_send{to, text, kind, image}` starts a new family instead:

- `kind:"task"` mints a task with no `parent_task` and `hop = 0`.
- `kind:"note"` is the default. It is free text with no session on the other side.
- `image` attaches one image. The cap is 2 MiB of decoded bytes.

The server gates every route on your spec entry `allowed_targets`. An unlisted name returns `acl_denied` before a row exists. Ring and fan-out shapes live in your prose. The mechanics here never change.

### The delivery obligation

`allowed_targets` is both reach and obligation:

- Before you report a terminal outcome, deliver to every downstream role the list names.
- The role that handed you the task is never on the list. Completing is itself the delivery back to it.
- A self-addressed entry or a ring return edge asks nothing of you.
- A completion that still owes a role gets refused. The refusal names the roles you reached and the roles you owe.
- An entry that names no target owes nothing. No switch declares the obligation.

## Rules of the ring

- Do not message the supervisor. Results ride completions. The ledger-recorded origin receives them, with offline queueing. The supervisor grants an uplink route through the spec, and revokes it there.
- Content crosses by reference. Share a file **path** in text. The receiver reads the file. One part rides the bus: `onlyne_send{..., image}` attaches one image, capped at 2 MiB of decoded bytes, in png, jpeg, gif, or webp.
- Your local socket answers `who` and `ping` in place. Every other verb travels to the server over your client link. `onlyne who` and `onlyne ping` resolve the socket of the tree above your cwd. `onlyne watch --follow` resolves the same path and subscribes your client link to the event stream.
- When the server link drops, keep working. Your running session still reaches its terminal state. Outgoing receipts persist as intents and flush after reconnect. Nothing needs your memory to bridge the gap.
