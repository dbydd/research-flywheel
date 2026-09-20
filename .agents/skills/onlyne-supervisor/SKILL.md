---
name: onlyne-supervisor
description: Use when operating an Onlyne cluster as _supervisor — dispatching tasks, polling the ledger, reading faults, and repairing deliveries.
---

# Onlyne Supervisor

You run the cluster. The server makes no decisions of its own: routing, the ledger,
queueing, and ACL are mechanics. Every call is yours, together with the spec file.

## Mount points

- Admin surface: `onlyne --server-root <root> <verb>` reaches the served admin socket.
  Resolve order: `--socket` > `ONLYNE_SOCKET` > `--server-root` > `--workspace`/cwd walk.
  A directory owns a surface when `.onlyne/run/s` or `.onlyne/run/socket` answers. Canonical
  `<root>/.onlyne/run/s` binds while the path fits 103 bytes; past the bound the daemon binds
  `<temp>/onlyne-<16hex>/s` and writes the served path to `<root>/.onlyne/run/socket` (0600).
  Your sends carry `--from _supervisor`, and your spec entry needs `admin = true`.
- Lifecycle you touch at runtime: `onlyne --server-root <root> status|roles|sessions|ledger|faults|watch|history`,
  `onlyne --server-root <root> control|repair|send|handoff|reply|complete|reload|spec_diff|cluster|tui`.
  A client process never detaches and carries no `start`/`stop`: whoever runs one has it in a
  visible foreground tab.

## Cluster facts

- The spec file is the only truth. There is no runtime config API.
- `onlyne spec_diff --server-root <root>` previews the pending delta, `onlyne reload
  --server-root <root>` applies it.
- A workspace directory is relocatable. Move it with `mv`; the client resolves everything it
  needs from `--workspace`, and its intents and cursors travel inside `.onlyne/`.
- Every verb prints one JSON line. Exit codes: 0 ok, 1 failed answer, 2 local validation,
  3 no socket, 4 refusal, 5 no supported host, 127 missing sibling.

## Dispatch flows downhill

```bash
onlyne --server-root <root> send --from _supervisor --to <role> --text "RING=... K=1 TOTAL=10"
```

- Roles answer by completing the task. The receipt lands in the ledger as `out_head` — the
  one-line, 200-character summary copied verbatim from the role's `onlyne_complete` text. A
  root receipt addressed to `_supervisor` queues (`state = queued`) by design: those rows
  are your pull-inbox. `ledger` reads the backlog, and the queue drains when your own client
  attaches.
- The ledger carries the state. Poll it for proof.

```bash
onlyne --server-root <root> ledger --task <task-id>       # queued|in_flight|acked|rejected|expired
onlyne --server-root <root> sessions --task <task-id>     # lifecycle projection
onlyne --server-root <root> watch --follow --tier durable  # live stream; tiers: durable|advisory
```

- Keep `allowed_targets` on ring and worker edges only. A role that can message
  `_supervisor` turns you into a work queue. When one task genuinely needs a live uplink,
  add `_supervisor` to that role's `allowed_targets`, run `reload`, then drop the edge once
  the task settles — grants are per task.
- Completion receipts always reach the role the ledger records as origin, offline queueing
  included. Reporting upward needs no standing edges at all.

## Faults and repair

```bash
onlyne --server-root <root> faults --open-only            # what the core detected
onlyne --server-root <root> repair inspect --task <id>    # read the stored facts
onlyne --server-root <root> repair retry|close|fail --task <id> [--reason ...]
onlyne --server-root <root> repair ack --fault-id <n> --reason ...
```

The core detects and records; recovery is your call. `retry` re-dispatches, `close` ends the
session, `rebind`/`adopt` point a task at a live pane, `fail` marks the row. `close` and
`fail` also file a `Cancel` for the owning role. Task control runs beside repair:
`onlyne control recycle|probe|snapshot|cancel|focus --task <id>` (`focus` raises the
task's live session in its host tab).
`DeliveryState::Exhausted` is terminal — retry only after an explicit decision here.

Heartbeat faults carry the liveness verdict, and the row keeps its state through them.
`heartbeat_missing` says the pane's beats stopped while the role link stayed up: the row is
`working`, `onlyne sessions` answers `heartbeat_stale` on it, and the TUI shows `working+stale`.
Check the pane first. A dead process answers `control recycle`, and a live one resumes beating
inside ten seconds and clears the flag on its own. `heartbeat_after_complete` says a session
kept talking after its completion landed; recycle ends the straggler, and the row's own history
keeps the settled completion either way. Both kinds open once per task and stay open until you
`repair ack` them, so the fault table doubles as your to-do list.

`stalled` is the client's own report: a session whose projection tuple froze for
`stall_report_secs` (1800 default, 0 disables) faults once per episode. No-op beats keep the
row beating; `stalled` is the progress verdict beside the liveness one. The verdict means real
silence on live work: the client checks the stored lifecycle at the scan and again at the send
boundary, so a session that already completed has its progress clock retired before any fault
fires. `control probe` first, then `recycle` or `repair retry` as the answer demands.

A finished session takes its host resource with it. The client closes the pane, tab, zellij
session, or exec child once that session holds no task and its agent has detached, and the
client log records the closure with `retiring idle session resource`. An idle pane still open
in front of you means its agent remains attached — the `reuse` case — or the owning client is
down.

Automatic re-delivery rides two spec gates: `[server].requeue_max_attempts` (0 unlimited) lands
a starving row as `rejected` with reason `requeue_exhausted`, and `[server].requeue_ttl_secs`
(0 off) lands it as `expired` with reason `requeue_ttl`. `repair retry` always rides outside
the gates. A reconnecting client also declares its live sessions at `hello`, so a link flap
leaves a running task's row `in_flight` and un-duplicated; a claimed session that dies without
completing gets its row requeued the moment the client reports it exited, and `repair inspect`
keeps the whole trail either way.

A role at `max_sessions` keeps pulling with `control_only = true`, so `focus`/`recycle`/`cancel`
still land while work rows stay `queued`.

From onlyne-client 1.2.1 a settled task with no result line still files its `completion`
receipt, body empty. A next hop waiting on that receipt proceeds. ACP payload-v1
(`hop-done:` / `hop-failed:` one line in `<ws>/.onlyne/out/<task-id>.md`) is the
`backend = "acp"` report path only; this template's `session_command` is pi.

`onlyne ledger` prints `reason` among the row keys when the row has one. A pane backend
refuses a protocol `session_command` (`--mode rpc`, `--acp`) with a ledger reason naming
`exec` or `acp` as the matching workspace backend.

## Errors you will see

`acl_denied` → the edge is missing from the spec. `unauthorized` → the key is not
registered. `recipient_offline` → a `note` found nothing to wake: its role was
offline, or online with no session running while `note_queue` stays off. The
message says which. `duplicate` → the same `op_id` again; its `data` is the
original receipt, byte for byte.
`conflict` → same `op_id`, different body. `not_admin` → a non-admin role sent with
`--from`. Every reject writes no ledger row and leaves no sender intent. A queued
note's `--ttl` deadline sits on its ledger row, so the sweep answers `expired` after
a server restart too.

## Watching with the TUI

`onlyne tui --server-root <root>` opens the two-page board: page 1 the role network
(serpentine grid, `●` busy, `◐` in flight, orthogonal hops), page 2 the ledger. `hjkl`
walks edges, `l` follows one, `e` reveals your dispatch spokes, `a` filters to active,
arrows pan.

## Clusters under clusters

Your own client connects to a parent server as a plain `[[client]]` entry marked
`aggregate`. Tasks flow in, completions flow out, and no child role name ever appears in
the parent ledger. Hand the parent operator your interface text with
`onlyne cluster export-prose`. The protocol contains zero federation code, so there is
nothing to break.
