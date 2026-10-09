---
name: onlyne-supervisor
description: Use when you operate an Onlyne cluster as _supervisor. Covers the admin surface, spec keys, gates, dispatch, hooks, faults, repair verbs, session scopes, and the TUI board.
---

# Onlyne Supervisor

You own orchestration and recovery. The server routes, queues, records, and enforces ACL. The core detects. You decide. One narrow automatic rule can move a stale `working` mirror row, and it runs only after the task ledger row reached a terminal state. The server never settles an open task.

## Mount points

- Reach the daemon of one root with `onlyne --server-root <root> <verb>`. The socket sits in the machine runtime directory at `/tmp/onlyne-<uid>/<digest>.sock`. `$ONLYNE_RUNTIME_DIR` overrides the directory. `<root>/.onlyne/run/s` is only the spelling operators print. Trust root mode is 0600.
- Your admin sends carry `--from _supervisor`. The admin surface stamps `admin = true` on every envelope it relays. Put `admin = true` on your own `[[client]]` entry too. That is the standing a client-held supervisor session sends with, and the flag the Control-class ACL bypass reads.
- Lifecycle verbs: `onlyne server init|run|status|generate|reload`, `onlyne wait-ready`, `onlyne client run|init|status`, and `onlyne gateway status`. Nothing detaches. There is no `start` or `stop`. Both daemons run in the foreground. A supervisor that wants one in the background starts `run` itself, in a tab, under `launchd`, or under `systemd`.
- Every request verb prints one JSON line. `onlyne cluster export-prose` prints prose raw, and wraps it in an object under `--json`.
- Exit codes: `0` ok. `1` failed answer. `2` local validation. `3` no socket. `4` the operator input was refused, as with `generate` or `skill export` declining an overwrite. `5` `client run` found no session host. `127` missing sibling.

## Operating facts

- Install the four registry crates at one version and track the release channel:

  ```bash
  cargo install --locked onlyne-cli onlyne-server onlyne-client onlyne-testkit
  ```

  Run `onlyne version` after installation. It must report `protocol: 1` and the paths of both sibling binaries. The testkit installs `onlyne-agent-fake` and `onlyne-gateway-fake`. Neither accepts `--version`. Read `onlyne version` for the package inventory. The TUI is a verb of the `onlyne` binary.
- `onlyne schema spec` and `onlyne schema client` print the compiled JSON Schema for `<server-root>/.onlyne/spec.toml` and `<workspace>/.onlyne/config.toml`. `--pretty` indents the document. Keys, types, and required fields come out of the build, so an installed binary answers without a source checkout.
- Re-export the shipped handbooks with `onlyne skill export --set role --set supervisor --force`.
- The live acceptance shape is a completion, then a handoff, then a client kill. After the task settles, read the task ledger, the session projection, both sequence numbers, and the ghost audit. Expect `acked`, `exited`, and no new ghost row for that task.

## Read the spec refusals

- A key the `Spec` type does not know is warned about and ignored. The server starts, and the setting keeps its default. A config that looks applied can do nothing. `onlyne-server run` prints one `ignoring unknown key \`<path>\`` line per such key. Read those lines after every spec edit. A key a release deleted, as v1 deleted `[client.timeout].running_ms`, looks exactly like a key that works. `onlyne schema spec` prints the field set this build reads.
- Two key classes refuse by name, and both name the line, as `spec.toml:7: <sentence>`. One class is a real key with a wrong value. The other is the keys v2 retired: `backend`, `relay_required`, `relay_required_count`, and `relay_count`. The loader refuses them at the root and inside a `[[client]]` entry with `BACKEND_IS_GONE` or `RELAY_IS_GONE`. A v1 spec learns what to delete. `RELAY_IS_GONE` carries the replacement: `allowed_targets` is both the permission and the obligation. A role owes each listed target one delivery before it may report a terminal outcome. A role that owes nothing leaves the list empty.
- Exit codes name the door. The merged `onlyne` verbs report `4` for refused operator input. The daemons `onlyne-server` and `onlyne-client` report `1` when the run fails. An admin verb before the server read the spec reports `3` for no socket. The sentence is the same in all three. Read the sentence, and read the code.

## Store revisions

- A tree from another build carries a store marker. The server `state.db` names revision 6. The client `client.db` names revision 3. A marker from another revision stops the daemon, and the sentence names the revision it found. A legacy workspace stops `onlyne client init` before it writes. Both exit `6`, the code for "this build will not start on a file from another revision".
- There is no `migrate` command. Move the old file aside and start again.

## Dispatch flows downhill

```bash
onlyne --server-root <root> send --from _supervisor --to <role> --text "RING=... K=1 TOTAL=10" \
  --force --yes-i-am-supervisor-not-other-role
```

- Seven verbs require both flags: `send`, `reply`, `handoff`, `complete`, `ack`, `reject`, and `control`. Each writes a role's own voice on the wire. The pair declares that the call stands outside that role's plugin session. The refusal names the plugin tool that answers for a role, as `onlyne_send` for `send`, `onlyne_handoff` for `handoff`, and `onlyne_complete` for `complete`. A call missing a flag exits `2` before it opens a socket.
- These verbs carry no flag: `repair *`, `ledger`, `sessions`, `roles`, `faults`, `watch`, `history`, `reload`, and `status`. There is no `shutdown` verb. Both daemons run in the foreground, and the terminal host owns stopping them.

### Material moves by path

A delivery template can render a block that quotes an upstream role result. Nothing in the tree fills it. That is a decision, and Onlyne does not take on the file system. A role that wants the next role to have something writes it where both can reach it and names the path in the `handoff` text. A file that must ride the envelope rides in `attachments`, and the client has written it by the time the text names it. A fifteen-page digest goes as a path in the handoff. A small result that belongs in the conversation goes in the handoff body.

### Family metadata

- `--hop-budget <n>` records the hops the family may spend.
- `--label <k=v>` records metadata beside the ledger. Repeat the flag up to eight times.
- `--deadline <rfc3339>` records the wall-clock bound for the whole run.

Every handoff inherits all of it: the family root id, the budget, the origin, the deadline, and the labels. The hop that meets the budget keeps the work. The figures ride `Causality`, so `onlyne ledger` prints `family` and `hop_budget` off the row. The delivery a role model reads names neither. A `handoff` over the budget is refused before the child is minted, and the refusal names the budget. The counters are read off the ledger, never out of the task text.

### The ledger carries the state

```bash
onlyne --server-root <root> ledger --task <task-id>       # queued|in_flight|acked|rejected|expired
onlyne --server-root <root> sessions --task <task-id>     # lifecycle projection
onlyne --server-root <root> watch --follow --tier durable  # live stream; tiers: durable|advisory
```

- Roles answer by completing the task. The receipt lands in the ledger as `out_head`: the first 200 grapheme clusters of the completion body, flattened to one line. `onlyne complete --summary` carries that line, truncated to 200 characters. `--head-from ledger` reads the head back off the task row. `--details` carries the whole result to the next hop and the originator. The ceiling is 64 KiB. `--file` names an absolute path the result points at. A details body over the ceiling is refused before anything is sent.
- A receipt for a task your role dispatched reaches you with no receiver grant. It waits in `queued` until your role holds a live session. Those rows are your pull inbox. `ledger` reads the backlog. Your own client drains the queue as it pulls.
- Your sends need no receiver grant. Leave `allowed_targets` off your own entry, and every registered role is reachable. Name a list there, and the reach is exactly that list. The receiver `allowed_senders` is read on no row of yours.

### Your inbox is _supervisor

- `_supervisor` is a logical signature node. Its `command` is empty, so no client dials it, no session opens for it, and it reads `offline` for the life of the cluster. That is not a broken role. It is your inbox.
- A backlog is what an inbox is for. Your seat outlives the swarm. The ledger is durable, `onlyne --server-root <root> ledger` reads the whole backlog, and `queued: N` on the role reads "N items wait for me". Drain it first on every start, before you dispatch.
- A supervisor that runs as a client, with a real `command` naming a runtime, drains those rows into its own session. That is the right shape when you want the work delivered. It is the wrong shape when your lifetime is the user's to manage, because a client-held inbox holds only what its own process was there to take.
- Nothing wakes you. There is no resident process. Timeliness belongs to a hook: bind `[[hook]]` to `ledger_state`, and filter the event on `data.to.role.role == "_supervisor"` to learn the moment work lands. Let the script carry it to whatever runs. The worker set is read at server start, so a `[[hook]]` change needs a restart.
- The one thing that can shorten your inbox is a TTL you set. `requeue_ttl_secs` under `[server]` defaults to `0`, which expires nothing. Set it positive, and `_supervisor`, permanently disconnected, has every queued receipt eligible for expiry once the TTL passes. The clock reaches your inbox whether you meant it or not. `--ttl` is read only on a `--note` send, so a dispatched task carries no deadline of its own, and a row that was handed out and returned is owned by its requeue gate.
- Completion receipts for a task you dispatched always reach you, with offline queueing. The ledger origin is the path, and it needs no standing edge. A role completing work it was handed from another role is a different path: that one reads `allowed_targets`, so keep `_supervisor` in the `allowed_targets` of the roles whose receipts you want to collect.

## Operator policy lives outside the core

The events you most need to hear about are recorded by the client that witnessed them and published onto the server stream. What to do is your policy, and the spec carries it:

```toml
[[hook]]
on = ["delivery_blocked", "turn_end_without_complete"]
run = ["./hooks/notify-supervisor.sh"]
timeout = "10s"
```

- `on` names classes from a closed set: `ledger_state`, `session_state`, `fault`, `role_presence`, `gateway_presence`, `spec_reloaded`, `turn_end_without_complete`, `delivery_blocked`, and `handoff`. A class outside the set refuses the whole load by name with `spec.toml:<line>`. That is a hard refusal. Unknown keys carry past with one warning line each.
- The server spawns `run` for each matching event, with the event as one JSON object on stdin. The object carries `seq`, `type`, `data`, and `created_at`. `ONLYNE_SOCKET` points at the admin socket, so the script can `onlyne send` in the same step. A slow script delays nothing: an event reaches every subscriber without waiting on any hook worker.
- Delivery is at-least-once per hook. The last handled `seq` is recorded, and a restart resumes from there. A script that must not act twice deduplicates on `seq`.
- A nonzero exit or a timeout records fault `hook_failed` once for that event and leaves the event untouched. The hook returns to it, so a broken script holds only its own backlog, and the stream and every other hook carry on.
- The worker set is read at server start. Editing `[[hook]]` needs a restart, and a `reload` that changes the set names it in the log.

## Faults and repair

```bash
onlyne --server-root <root> faults --open-only            # what the core detected
onlyne --server-root <root> repair inspect --task <id>    # read the stored facts
onlyne --server-root <root> repair retry|close --task <id> [--reason <text>]
onlyne --server-root <root> repair fail --task <id> --reason <text>
onlyne --server-root <root> repair adopt --task <id> --backend <name> --reason <text>
onlyne --server-root <root> repair rebind --task <id> --session-id <id> --backend <name> --reason <text>
onlyne --server-root <root> repair ack --fault-id <n> --reason <text>
```

- The core detects and records. Recovery is your call. `repair retry` puts eligible `queued` or `in_flight` work back in the queue. A task whose rows are settled returns `conflict`. `repair fail` settles the task failed and rejects its undelivered rows. `repair close` settles it cancelled the same way. `repair adopt` re-points the row desired backend binding without touching its generation. `repair rebind` moves the row to another session id and bumps its generation. `repair inspect` prints the session projection with every fault recorded against the task. The `kind=task` row is authoritative for the task outcome. A `kind=completion` row records receipt transport and `out_head`, and its state never reopens a rejected task.
- Client and server `(generation, seq)` values are per-writer watermarks. Compare the terminal outcome, the lifecycle, the resource, and the generation. Do not require equal sequence numbers.
- Task control runs beside repair: `onlyne control recycle|probe|snapshot|cancel|focus --task <id> --from <role> --force --yes-i-am-supervisor-not-other-role`. `recycle` and `cancel` carry a required `--reason`. `probe`, `snapshot`, and `focus` take none, and a `--reason` on `probe` is refused by the parser. `focus` brings the task live session to the front of its host.
- A client at `max_sessions` pulls with `control_only`, so those commands reach the session that holds the last slot. Work for that role waits until a slot frees.
- `DeliveryState::Exhausted` is terminal. Retry only after an explicit decision here.
- A command on this surface speaks as a role. `control` and the four message verbs name it with `--from <role>`. The reads resolve everything from the row they name and take no such flag. `control` needs no `--to` on this surface: the task session row names the role the op must reach, the CLI reads that row, and an explicit `--to <role>` still wins. A task no session owns is refused before anything is written, and the refusal names `--to`.
- `recycle` and `cancel` end the task on your word. The client asks the plugin for its ending and closes the host resource, and the plugin report settles the task. A word the plugin never answers is settled by this client after three heartbeat intervals, so a cancel that lands before the agent wrote anything still ends its task. The delivery row the client still holds is refused with `operator cancel` or `operator recycle`.

### Liveness verdicts

- `heartbeat_missing` says the pane beats stopped and the role link stayed up. The row is `working`, `onlyne sessions` answers `heartbeat_stale` on it, and the TUI shows `working+stale`. Check the pane first. A dead process answers `control recycle`. A live one resumes beating inside ten seconds and clears the flag on its own.
- `heartbeat_after_complete` says a session kept talking after its completion landed. `control recycle` ends the straggler. The row history keeps the settled completion either way.
- Both kinds open once per task and stay open until you `repair ack` them. The fault table doubles as your to-do list.
- `stalled` is the client own report: a session whose projection tuple froze for `stall_report_secs`, default 1800, `0` disables, faults once per episode. No-op beats keep the row beating. `stalled` is the progress verdict beside the liveness one. The client checks the stored lifecycle at the scan and again at the send boundary, so a session that already completed has its progress clock retired before any fault fires. Answer with `control probe` first, then `control recycle` or `repair retry` as the evidence demands.
- `stale_working` covers the owner that left: a row the mirror still reads `working`, whose role has been offline past 600 seconds, records this fault once. The server observer writes it. `[server].stale_watch_secs`, default 60, is the scan cadence for both observers.

### Ghosts and dead sessions

- A row no client will ever write again is the ghost sweep work. A mirror row still reading `working`, whose task ledger row already reached a terminal state, is rewritten by the server on its own interval. `[server].ghost_sweep_secs`, default 60, `0` disables, sets the cadence. With no outcome in the mirror, the task ledger supplies it: `acked` settles `done`, `rejected` and `expired` settle `failed`. An outcome already present is preserved. The sequence advances, a `session_state` event travels, and one row lands in `ghost_sweeps` with the session, both sequences, the outcome, and the evidence, as `task_settled:acked`. `onlyne ghosts [--limit N]` reads that audit, newest first.
- One class stays out of reach: a `working` row whose owner role is offline while the task is still open. An ending there would decide live work and swallow the requeue that work is owed. `stale_working` remains that class only output, and its recovery stays yours through `repair *`.
- A task-bound unsettled session is retired after either arm fires: a dropped connection exceeds `[client] reconnect_grace_secs`, default 60, `0` disables that arm, or an attached transport accepts no frame for three heartbeat intervals. Both arms settle the task `failed`, refuse the held delivery with reason `session_dead`, close the host resource, and publish the exit. That refusal is terminal. Create a new task to run the work again. `repair retry` only requeues eligible queued or in-flight rows and returns `conflict` for a settled task.

### Accept gate and redelivery

- A delivery that arrives with the client accept gate closed is left unanswered. The row stays `in_flight`, and the next `hello` that does not claim it puts it back on the queue.
- A refusal, `accepted: false`, is kept for work this client can never serve: an assignment the plugin declines, `assign rejected`, or a session the operator word retired with its delivery in hand, `operator cancel` or `operator recycle`.
- A restarted client declares no live sessions, so the server requeues every unacknowledged row of the roles it reconnects as, and the next pull hands them out again. `onlyne ledger --task <id>` shows the rows that came back.
- Automatic re-delivery rides two spec gates. `[server].requeue_max_attempts`, `0` unlimited, lands a returned in-flight row as `rejected` with reason `requeue_exhausted`. `[server].requeue_ttl_secs`, `0` off, lands returned rows as `expired` with reason `requeue_ttl`. The TTL also expires never-pulled task, completion, and control rows while the recipient role has no live connection. `repair retry` always rides outside the gates. A reconnecting client declares its live sessions at `hello`, so a link flap leaves a running task row `in_flight` and un-duplicated. A claimed session that dies without completing is requeued the moment the client reports it exited, and `repair inspect` keeps the whole trail either way.

### Settlement reasons on the ledger

`onlyne ledger` prints the row it holds, and a settled row carries its `reason`. The key is one of the eight the CLI recognizes: `msg_id`, `task`, `state`, `reason`, `out_head`, `body`, `family`, `hop_budget`. A row carries the key only where it has a value. A clean `acked` row omits it, and the bytes match what the same row printed before the column existed. The TUI task panel appends `reason=<text>` to the row tail under the same rule.

Six settlement doors write a value there:

- `requeue_exhausted` and `requeue_ttl` come from the two gates above.
- `expired` comes from the deadline sweep on a queued note past its `--ttl`.
- The receiving client refusal carries its own word: `session_dead` when the reconnect sweep buries a dead session delivery, `assign rejected` when the plugin declines an assignment, and `operator cancel` or `operator recycle` when the client settles a session the operator word retired while it still held the delivery.
- Whatever `onlyne reject --reason <text>` names, and the literal `rejected` as the fallback.
- The operator `onlyne repair fail --task <id> --reason <text>` and `onlyne repair close --task <id> --reason <text>` write that text on every undelivered row of the task, and the close falls back to `operator close`.

The ack side stays out of it. `onlyne ack --msg-id <id> --reason <text> --force --yes-i-am-supervisor-not-other-role` settles the row through `mark_acked` and keeps a reason the row already carried. `onlyne repair ack --fault-id <n> --reason <text>` writes its reason on the fault row alone. Both run against a role workspace or a client socket, and both require `--reason`.

### Session scopes keep or close the host resource

- A finished session takes its host resource with it. The client closes the pane, tab, tern block, zellij session, or exec child once the session holds no task and no plugin connection is attached. The client log records the closure with `retiring idle session resource`. An idle pane still open in front of you means the owning client is down.
- A scope that keeps sessions overrides that rule by making the runtime hold on. `[client.session] scope = "task"` or `"role"` promises a session that outlives the delivery it served, so the session is not closed when the work lands. A `role` pool hands the next delivery to a member that is still there. The client never reclaims a member on its own. A task-free session is exempt from the three-heartbeat silence sweep by name. A session whose connection is still attached is exempt from the reclamation sweep. What ends a member is the runtime leaving in one of two ways, and both reach the same log line above: its process exits or its socket ends, which starts `[client] reconnect_grace_secs`, or the runtime sends `detach`.
- A `role` pool needs a runtime in one of exactly two shapes. **Resident**: the process and its socket stay, and it does not `detach` when it runs out of work. That is what `idle_close = 0` asks for. **Resumable**: the runtime declares `resume`, so a nonzero `idle_close` suspends it instead, the conversation stays in the runtime own store, and the next delivery resumes that conversation. `suspend` is the frame that asks for the release. A runtime that declares neither simply waits for its agent to leave.
- `pi` reads the scope and acts on it. Each `assign` carries the scope. The plugin ends its own process under `oneshot` and stays under `task` or `role`. A `role` pool in front of it holds its member, and the same conversation takes the next delivery. A `oneshot` session leaves and takes its pane with it. That second half matters: the client retires a session while its agent is still reachable, and that exemption is what keeps a pool member alive. A runtime that stayed under `oneshot` would hold its pane open forever. The leave must be the runtime own, because the client teardown is a pane kill, and a runtime killed mid-teardown loses what it had not yet written. Pi flushes its session file as it shuts down.
- `pi` declares `register`, `report`, `inject`, and `recycle` with no `resume`. The other door is shut to it. No setting releases its process and brings the conversation back, and `idle_close` has to stay `0` rather than name a bound. Nothing in `spec.toml` can assert that half. It is the agent to keep.
- The tell that a pool is not reused is a `role` role whose `onlyne sessions` shows a new `session_id` per delivery and none left standing. A pool that works looks like one row reading `lifecycle=idle` with `resource=attached` between deliveries, and the client log carries `the delivery joined the session its scope keeps for it` once per reuse.
- A pool that empties and a tab that never closes have one cause, and it reads like neither. The scope rides the assignment as `assign.scope`, so a runtime can act on it only when the **client binary** stamps it. Re-vendoring the plugin is not the same install. A client too old to stamp it sends a frame with no scope. The runtime reads that as `oneshot` by design, and every session leaves on completion. The signature is unmistakable in the client log: `stays idle`, then `retiring idle session resource` three to seven seconds later, for every delivery, with the tab going away each time. A pool that empties and a tab that closes together means the binary is behind, and the two problems did not cancel.
- The same log line shows a reclaimed resource from the outside. An `idle_close` nonzero on a runtime that declares no `resume` suspends a session that cannot be brought back, which reads as a pool member vanishing for no stated reason. When a `role` pool misbehaves, read those two log lines before anything else.

### Orca and Tern sessions

- Orca creates one new terminal per task. `attach` refreshes a persisted terminal handle. It does not relay into an arbitrary existing session. Spawning needs a running Orca app, an `orca` CLI that reaches that app, and a client launched from the intended Orca tab with the matching worktree environment, `ORCA_WORKTREE_ID` under the host policy. A `[single-instance]` CLI error is the immediate spawn refusal. The exact `session_dead` rejection comes later, from the client retirement sweep after a slot exists.
- Tern runs each session as a block inside the role tab: one Tern session per cluster, one tab per role, and the block is retired when the session ends. Set it with `placement = "tern"` in the role workspace `config.toml`, or with `ONLYNE_BACKEND=tern`. An absent `placement` probes `tern`, `orca`, `zellij` in that order and falls back to `headless`, so a machine with Tern uses it without a line of config. The `onlyne` board that watches clusters inside Tern ships in the source repository at `integrations/tern-plugin`. `tern plugin install integrations/tern-plugin` installs it. `tern plugin link integrations/tern-plugin` loads that directory in place and reloads on every save. It is a supervisor face: it runs the same admin verbs this document names, `status`, `roles`, `sessions`, `faults`, `control`, and `repair`, as one-shot `onlyne` processes against each root.

## Errors you will see

- `acl_denied` — the edge is missing from the spec. The sender `allowed_targets` and the receiver `allowed_senders` must name each other. Your own sends read `allowed_targets` alone, so a denial there means that list is non-empty and omits the target.
- `unauthorized` — the handshake refused the peer: an unregistered key, an unregistered role, a key registered for another role, or a bad signature.
- `recipient_offline` — a `note` found nothing to wake. The role was offline, or online with no session running and `note_queue` off. The message says which.
- `duplicate` — the same `op_id` again. The `data` is the original receipt, byte for byte.
- `conflict` — the same `op_id` with a different body.
- `not_admin` — a `cluster:` principal sent without admin standing.
- `forbidden` — a role that is neither the administrator nor the task owner sent a control frame.

Every reject writes no ledger row and leaves no sender intent. A queued note `--ttl` deadline sits on its ledger row. The server re-arms every stored deadline at startup, so the sweep answers `expired` after a restart too. A note that was already queued when the server was upgraded carries no deadline and stays `queued`. Settle it with `repair fail` or `repair close`.

## Watching with the TUI

`onlyne tui --server-root <root>` opens the three-page board in this process. It reads the admin surface.

- Keys: `1`, `2`, `3` switch pages. `Tab` walks a page panes. `↑` and `↓` step the selected row. `PgUp`, `PgDn`, `[`, `]` scroll a pane of lines. `q` or `Esc` leaves.
- The cluster page lists every role with its presence, the sessions it holds, how many are busy, idle, or suspended, and its queue depth. Beside it sits the selected role board, one row per delivery in the five-column reading `queued`, `running`, `waiting`, `done`, `failed_or_blocked`. Under both is the event tail.
- `Enter` opens the selected card family on the task page: that family path across roles, every delivery by hop with its verdict and the receipt it settled with, over the tail of the session serving the selected delivery.
- The faults page lists the open faults, the selected fault fields, and the repair verbs it offers: `a` opens `repair ack`, `t` `repair retry`, `c` `repair close`, `F` `repair fail`, `i` `repair inspect`.
- The four operations are forms the board opens on the selection. `s` sends a task and asks for `from`, `to`, and `body`. `f` focuses and asks for `from`, `to`, and `task`. The target is named by hand, and the board reads it off no selection. `r` reports a task verdict and asks for `from`, `task`, `outcome`, and `head`. `Enter` submits a form. `Esc` cancels it. `Tab` moves the caret between fields. The footer second line prints what the op answered. `^R` re-reads the snapshot.
- Nothing polls. A page moves when the admin stream says the cluster did. A gap in that stream leaves the header saying `catching up` while the snapshot is re-read.
- `onlyne tui --server-root <root> --once` renders one frame, the cluster page from one snapshot, as plain text, and exits.

## Clusters under clusters

- Your own client connects to a parent server as a plain `[[client]]` entry marked `aggregate = "<child-cluster>"`. The label is an annotation. It contributes no ACL rows, the delivery path carries no aggregate branch, and a generated `[[client]]` fragment drops it.
- Tasks flow in, and completions flow out. Every parent ledger row is written from the parent-side envelope, so its `from`, `to`, and body name parent-visible roles alone.
- Hand the parent operator your interface text with `onlyne cluster export-prose --role <role>`. It prints the prose raw for pasting into a TOML multi-line string, and wraps it in an object under `--json`.
- The protocol contains zero federation code. There is nothing to break.
