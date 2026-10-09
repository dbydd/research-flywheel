---
name: onlyne-role
description: Use when acting as one role inside an Onlyne cluster. A task arrives as a delivery, you do the work, then you report one completion and hand work on through the edges your spec names.
---

# Onlyne Role

You are one role in an Onlyne cluster. A delivery arrives in your session, and the work it
carries belongs to that task. Do the work. Report it with a completion. Hand work on only
through the targets your spec entry names.

## How work reaches you

- The delivery arrives as a user-role injection. The first line is `From <role>:` and names
  the sender. The body follows byte for byte. Attachment paths, when the sender attached an
  image, point into `<workspace>/.onlyne/tmp/attachments/`.
- Your role prose comes from the cluster spec. It is already in your instruction layer: pi
  takes it as a system-prompt section, and an ACP session reads it from the client's block in
  the workspace `AGENTS.md`.
- The `{task}` placeholder in the role's `[client.runtime] command` is the task id. The body
  never travels in argv.
- Which deliveries one session serves is the workspace's `[client.session] scope`. `oneshot`
  is the default: one session per delivery, closed when the delivery settles. `task` keeps
  one session for the whole family. `role` keeps a pool and gives each delivery to the
  session that has waited longest.
- Where your process is displayed is the workspace's `placement`. The machine owns it. An
  absent placement probes tern, then orca, then zellij, and falls back to headless. A
  nonempty `ONLYNE_BACKEND` names the placement and wins over the config file. `client run`
  exits 5 when that name matches nothing.

## Report with a completion

The completion row is your receipt. Everything upstream reads that row.

Inside a pi session, the plugin tool is the path:

```
onlyne_complete{outcome, summary, details, files}
```

- Your `summary` becomes the ledger `out_head`: the first 200 grapheme clusters of the body,
  flattened to one line. It is the display line the supervisor reads. Put the result there.
  A summary that carries nothing files your last assistant text as the head instead.
- `outcome` is `done`, `failed`, `cancelled`, or `blocked`. A provable impossibility is
  `failed`, with the reason in `summary`. A stop outside this session is `blocked`.
- `details` carries the full result, at or under 64 KiB. `files` names the absolute paths the
  result rests on. Both travel with the completion as they stand.
- A mounted pi session answers through the tool. The tool is the only path to `done`. A turn
  that ends with no completion gets one nudge in your input. A second turn with no completion
  settles the delivery: a `oneshot` task becomes `blocked`, and a `task` or `role` session
  goes idle.
- One completion per task. A second `onlyne_complete` for a reported task files no report and
  answers the same `reported <outcome>` line. Idempotence keys on `op_id`: the same `op_id`
  with the same body answers `duplicate`, and with a changed body answers `conflict`. Call
  the tool once.

## Deliver what your edges owe

Your spec entry's `allowed_targets` is one list with two effects. The server reads it as the
permission: a send to any other name returns `acl_denied` before a row exists. The client
reads it as the obligation: before you report a terminal outcome, your session must have
delivered to every downstream role on the list.

- The role that handed you the task is never one of them. Your completion is itself the
  delivery back to it. A self-addressed entry and a ring's return edge therefore ask nothing
  of you.
- A completion that still owes a role is refused. The refusal names the roles you have not
  reached and the ones you have.
- An entry that names no target owes nothing. There is no switch to declare.

## Hand work sideways

Inside a pi session, `onlyne_handoff` hands this task on:

```
onlyne_handoff{to: "<next-role>", text: "<task text for the next hop>", image: "<path, optional>"}
```

The host mints the child. It names this task as `parent_task`, sits one hop deeper, and
carries the family metadata: the family root id, the hop budget, the origin, the deadline,
and the labels. A handoff over the family's hop budget is refused, and the refusal names the
budget it would break. The hop that meets the budget keeps the work.

`onlyne_send{to, text, kind, image}` starts a fresh family instead. `kind:"task"` mints a
task with no parent and `hop = 0`. `kind:"note"`, the default, is free text with no session
on the other side; a note to an offline role answers `recipient_offline`. `image` attaches
one image, capped at 2 MiB of decoded bytes.

## Speak for a role from a shell

The CLI verbs that speak for a role are `send`, `reply`, `handoff`, `complete`, `ack`,
`reject`, and `control`. Each writes a role's own voice on the wire. A verdict written from a
shell answers for a session the plugin is still serving, so every one of these verbs refuses
a call that misses either `--force` or `--yes-i-am-supervisor-not-other-role`.

An `exec` session mounts no plugin. It runs the CLI form and declares itself with both flags:

```bash
onlyne complete --task <task-id> --outcome done --summary "<one-line result>" \
  --force --yes-i-am-supervisor-not-other-role
```

The CLI `--outcome` accepts only `done`, `failed`, and `cancelled`. An `exec` session that
hits an outside block reports `failed` and gives the reason in `summary`. An ACP session
mounts the same three tools through `onlyne mcp` and needs no `onlyne` command of its own.

## Rules of the ring

- Do not message the supervisor. Results ride completions: the origin recorded in the ledger
  receives them automatically, even from offline queueing.
- Content crosses by reference. Write a file path in the text; the receiver reads the file.
  The one exception is the `image` field, which carries a single image at 2 MiB of decoded
  bytes in png, jpeg, gif, or webp.
- Your local socket answers `who` and `ping` in place. Every other verb travels on to the
  server through your client's link. `onlyne watch --follow` resolves the socket above your
  cwd and subscribes your client's own link to the event stream.
- When the server link drops, keep working. Your running session still reaches its terminal
  state. Outgoing receipts persist as intents and flush after reconnect in order.
