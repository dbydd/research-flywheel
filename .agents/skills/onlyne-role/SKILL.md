---
name: onlyne-role
description: Use when you act as one role inside an Onlyne cluster. Covers task intake, completion reporting, handoff, send, and the rules of the ring.
---

# Onlyne Role

You are one role in an Onlyne cluster. The server injects each task into your session
as a message. The work you receive belongs to that task. Do the work. Then report it
with a completion.

## How work reaches you

- A task arrives as a user-role injection. Its first line names the source:
  `From <role>:`. The body follows. The injection then lists the paths of the
  attachments that the client wrote for you under
  `<workspace>/.onlyne/tmp/attachments/`.
- Your role prose comes from the cluster spec and is already in your context. pi takes
  that prose as a system-prompt section. An ACP session reads it from the client block
  in the workspace `AGENTS.md`.
- The `{task}` placeholder in the `[client.runtime] command` of your role holds the
  task id. It never holds the body. Argv holds no payload.
- The workspace `[client.session] scope` sets how many deliveries your session serves.
  `oneshot` is the default. It opens one session per delivery and closes it when that
  delivery settles. `task` keeps the session for the next delivery of the family.
  `role` keeps a pool and hands the next delivery to the session that has waited
  longest. An idle session keeps its row. The client may release its process and bring
  it back for the next delivery.
- The workspace `placement` decides where the host shows your process: `orca`,
  `zellij`, `tern`, `headless`, or `external`. The placement is the machine's property.
  It is not yours to set. `tern` runs you as one block in the tab of your role. An
  absent `placement` probes `tern`, `orca`, and `zellij` in that order. Then it falls
  back to `headless`. A machine with Tern therefore needs no line of config to put you
  there. A nonempty `ONLYNE_BACKEND` names the placement over the workspace key. If
  that name matches nothing, `client run` exits 5 and names the value.

## Reporting: completion is the receipt

Report upward by completing the task. The supervisor polls the completion row.

Inside a pi session the plugin tool is the path:

```
onlyne_complete{outcome, summary, details, files}
```

The CLI verbs that speak for a role are `send`, `reply`, `handoff`, `complete`, `ack`,
`reject`, and `control`. Each refuses a call that misses either `--force` or
`--yes-i-am-supervisor-not-other-role`. That door stands outside a plugin session. A
verdict written there answers for a session the plugin is still serving. An `exec`
session mounts no plugin. It runs the CLI form and declares itself with both flags:

```bash
onlyne complete --task <task-id> --outcome done --summary "<one-line result>" \
  [--details "<the full result>" --file <absolute path>] \
  --force --yes-i-am-supervisor-not-other-role
```

- Your `summary` becomes the ledger `out_head`. That head is the first 200 grapheme
  clusters of the completion body (`head_preview` in
  `crates/onlyne-store/src/server.rs`). The ledger flattens it to one line. It is the
  display line everything upstream reads. Put the result there. If `summary` carries
  nothing, the ledger files your last assistant text as the head instead.
- `outcome` on the `onlyne_complete` tool is `done`, `failed`, `cancelled`, or
  `blocked`. Report `failed` for a provable impossibility, and put the reason in
  `summary`. Report `blocked` when something outside this session stops the work. The
  CLI `--outcome` accepts only the first three. So an `exec` session that hits a block
  from outside reports `failed` and says why in `summary`. A mounted pi session
  answers through the `onlyne_complete` tool. That tool is the only path to `done`.
- `details` carries the full result. Keep it at or under 64 KiB. `files` names the
  absolute paths the result rests on. Both travel with the completion as they stand.
- A plain `exec` session carries no plugin. Run `onlyne complete` before you stop. Use
  both supervisor flags above.
- An ACP session mounts the same three plugin tools through `onlyne mcp`. Its client
  attaches that MCP server to the session. The session needs no `onlyne` command of
  its own. The tool names and arguments are the ones above. A refused call comes back
  as the error text of the tool result, in the client's own words. Nothing about the
  task is yours to name. The client holds the task. A call names only the recipient,
  the text, or the outcome.
- If a turn ends without `onlyne_complete`, one nudge arrives in your input:
  `If this task is finished, report it with onlyne_complete; if something is missing, say what.`
  A second turn without one settles the delivery. A `oneshot` task becomes `blocked`.
  A `task` or `role` session goes idle, and the board reads "waiting".
- Complete each task once. Inside your session, the plugin keeps that record. If you
  call `onlyne_complete` again for a task it already reported, it files no further
  report. It answers the same `reported <outcome>` line. The process leaves once, at
  the completion the plugin acked.
- A hand-run `onlyne complete` carries a fresh `op_id` each call. The ledger reads it
  as a new frame and appends a second `completion` row beside the first. The row of
  the task keeps the state it settled in. Idempotence keys on `op_id` alone. If the
  same `op_id` carries the same body, the server answers `duplicate` and replays the
  first receipt byte for byte. If the same `op_id` carries a changed body, it answers
  `conflict`. Each answer writes no row. Call it once.

## Passing work sideways

Inside a pi session, `onlyne_handoff` hands this task on:

```
onlyne_handoff{to: "<next-role>", text: "<same task text>", image: "<path, optional>"}
```

The host mints the child task. It names this task as `parent_task`. The child sits one
hop deeper. It carries the family metadata: the family root id, the hop budget, the
origin, the deadline, and the labels. The task that meets the hop budget keeps the
work. If a `handoff` would sit over the budget, the server refuses it. The refusal
names the budget it would break.

An `exec` session runs the CLI form of the same step, with both supervisor flags:

```bash
onlyne handoff --to <next-role> --task <task-id> --text "<same task text>" \
  --force --yes-i-am-supervisor-not-other-role
```

`onlyne_send{to, text, kind, image}` starts a fresh family instead. `kind:"task"`
mints a task with no `parent_task` and `hop = 0`. `kind:"note"` is the default. It is
free text with no session on the other side. `image` attaches one image. The cap is
2 MiB of decoded bytes. The server gates the target of every route on the
`allowed_targets` of your spec entry. If the name is not on that list, the server
returns `acl_denied` before a row exists. Ring and fan-out shapes live in your prose.
The mechanics here never change.

**That one list is your reach and your obligation.** Before you report a terminal
outcome, deliver to every *downstream* role the list names. The role that handed you
the task is never one of them. Completing is itself the delivery back to it. So a
self-addressed entry, or the return edge of a ring, asks nothing of you. If your
completion still owes a role, the server refuses it. The refusal names the roles you
have not reached and the ones you have. An entry that names no target owes nothing.
There is no separate switch to declare.

## Rules of the ring

- Do not message the supervisor. Results ride completions. The origin recorded in the
  ledger receives them automatically. An offline origin still receives them from the
  queue. The supervisor grants an uplink route for a specific task through the spec.
  The supervisor revokes it the same way.
- Content crosses by reference. Share a file path in the text. The receiver reads the
  file. One part rides the bus: the `image` field of `onlyne_send` attaches one image.
  The cap is 2 MiB of decoded bytes. The formats are png, jpeg, gif, and webp.
- Your local socket answers `who` and `ping` in place. Every other verb it carries
  travels on to the server through your client link. `onlyne who` and `onlyne ping`
  resolve the socket of the tree above your cwd. `onlyne watch --follow` resolves that
  same path. It subscribes your client link to the event stream.
- If the server link drops, keep working. Your running session still reaches its
  terminal state. Outgoing receipts persist as intents. They flush after reconnect.
  Nothing needs your memory to bridge a gap.
