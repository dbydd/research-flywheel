---
name: onlyne-role
description: Use when acting as a role inside an Onlyne cluster — a session assigned a task by the server, needing the correct handoff, completion, and reporting discipline.
---

# Onlyne Role

You are one role in an Onlyne cluster. A task arrives as an injected message, and your
session exists for that one task. Do the work, then report in the form the ledger reads.

## How work reaches you

- The task body arrives in your session as a user-role injection:
  `[onlyne] task <task-id> from role:<sender> (kind task)`. Your role prose comes from the
  cluster spec through `welcome`, and is already in your context.
- The `{task}` placeholder in your spawn command is the task **id**, never the body. Argv
  holds no payload.
- Your session serves this task. Finish it here. A new task gets a fresh session.

## Reporting: completion is the receipt

Report upward by completing the task. The completion row is what the supervisor polls.

```bash
onlyne complete --task <task-id> --outcome done --head-from local --text "<one-line result>"
```

or, inside a pi session, the `onlyne_complete{outcome, text}` tool.

- `--head-from` is required on the CLI: `local` truncates your `--text` into `out_head`,
  `ledger` reads back the head already stored for the row.
- Your `--text` becomes the ledger `out_head`, verbatim: one line, whitespace-collapsed,
  capped at 200 characters. Put the whole answer there. It is the only upward channel.
- `--outcome done|failed|cancelled`. Provable impossibility → `failed`, with the reason in
  `text`. The report path depends on your host. A mounted pi session answers through the
  `onlyne_complete` tool, and if you fall silent there the plugin files a fallback receipt
  from your last assistant text — so name the result in that text. A plain `exec` session
  carries no plugin and no fallback: `onlyne complete` is yours to run before you stop.
- A `backend = "acp"` session mounts nothing and needs no `onlyne` command. Its prompt
  ends with an absolute report path the client prepared under the workspace
  (`<workspace>/.onlyne/out/<task-id>.md`); the last action before you stop is one line
  in that file — `hop-done: <the result in one line>` or `hop-failed: <why it failed, one
  sentence>` — written via a temp name in the same directory then renamed into place.
  The client reads that file once at turn end and deletes it. Missing file keeps the old
  behavior (head from the last streamed line). `hop-done` replaces `out_head`. `hop-failed`
  settles Failed. A file that fails the contract settles Cancelled, with a fault reason
  opening `acp payload invalid:`. This flywheel template's `session_command` is pi; the
  ACP file contract stays dormant until a workspace sets `backend = "acp"`.
- From onlyne-client 1.2.1, a settled task with no result line still files its
  `completion` receipt, with empty text. The next hop waiting on that receipt proceeds.
- One completion per task. Inside your session the plugin keeps that record: a second
  `onlyne_complete` for a task it already reported answers `duplicate`, files no report, and the
  process exits once. Call it once.

## Passing work sideways

```bash
onlyne handoff --to <next-role> --task <task-id> --text "<same task text>"
```

The handoff reads your task's ledger row, mints a child task under `parent_task`, and sets
`hop = parent + 1`. Targets come from your spec entry's `allowed_targets`; any other name
returns `acl_denied` before a row exists. Ring and fan-out shapes live in your prose. The
mechanics here never change.

`onlyne_send{to, text, kind}` covers the same ground from inside a pi session:
`kind:"task"` mints a fresh family, while `kind:"note"` (the default) is free text that
rides an already-live session on the receiving role — a role that is offline, or online
with every session settled, refuses it with `recipient_offline`. Follow-up instructions
for your own in-flight task are notes; new work is a task.

This tree's handoff convention `> hop-failed: <环节> <一句话>` is body text on the
relay, a different object from the ACP payload-v1 file prefix `hop-failed:`.

## Rules of the ring

- Do not message the supervisor. Results ride completions: the origin recorded in the
  ledger receives them automatically, even from offline queueing. The supervisor grants an
  uplink route for a specific task through the spec, and revokes it the same way.
- Content crosses by reference. Share a file **path** in text; the receiver reads the file.
  Workspace bytes never ride the bus.
- Your local socket answers `who`, `ping`, `watch` from inside the workspace:
  `onlyne who`, `onlyne watch --follow`. Resolve order: `--socket` > `ONLYNE_SOCKET` >
  cwd walk of `.onlyne/run/s` or `.onlyne/run/socket`. The client injects `ONLYNE_SOCKET`
  into the session it spawns.
- When the server link drops, keep working: your running session still reaches its terminal
  state, and outgoing receipts persist as intents and flush after reconnect. Nothing needs
  your memory to bridge a gap.
- Your pane sits in the operator's session host, addressed as a herdr workspace labelled
  `onlyne:<cluster>` plus a tab named for your role. The operator points the backend at the
  workspace they use by renaming it before sessions spawn: `herdr workspace rename
  <WORKSPACE_ID> onlyne:<cluster>`, then `herdr tab rename <TAB_ID> <role>`. A label that
  differs yields a second workspace, and the client logs a warning naming the label and the
  workspace it created.
- A finished session takes its host resource with it. An idle pane that stays open means
  `reuse` kept the agent attached for the next task.
