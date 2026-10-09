---
name: onlyne-supervisor
description: Use when operating an Onlyne cluster as _supervisor. Covers starting workspaces, dispatching tasks, reading the ledger, routes, faults, and repair.
---

# Onlyne Supervisor

You own orchestration and recovery. The server routes, queues, records, and enforces ACL.
One narrow automatic rule can move a stale `working` mirror. It acts only after the ledger
row of that task is terminal. The server never settles an open task. Every other recovery
choice belongs to you and to the spec file.

## Mount points

- Admin surface: `onlyne --server-root <root> <verb>` reaches the socket that the daemon
  of that root publishes in the machine-level runtime directory
  (`/tmp/onlyne-<uid>/<digest>.sock`, with `$ONLYNE_RUNTIME_DIR` overriding it) and the
  local trust root (0600). `<root>/.onlyne/run/s` is only the canonical spelling that
  operators print. Your admin sends carry a required `--from _supervisor`, and the admin
  surface stamps `admin = true` on every envelope it relays. Put `admin = true` on your
  own `[[client]]` entry too. That is the standing a client-held supervisor session sends
  with, and the flag the Control-class ACL bypass reads.
- Lifecycle: `onlyne server init|run|status|generate|reload`, the top-level
  `onlyne wait-ready`, `onlyne client run|init|status`, and `onlyne gateway status`. The
  platform verbs that used to sit beside `gateway status` went with the frozen gateway
  crate. The mount vocabulary itself stays in the protocol. Nothing detaches, and there is
  no `start`/`stop`. Both daemons run in the foreground. A supervisor that wants one in
  the background starts `run` itself, in a tab, in `launchd`, or in `systemd`.
- Every request verb prints one JSON line for its answer. `onlyne cluster export-prose`
  prints the prose raw, and `--json` wraps it in an object. Exit codes: 0 ok, 1 failed
  answer, 2 local validation, 3 no socket, 4 refused operator input (`generate`, and
  `skill export` declining to overwrite a file), 5 `client run` found no session host,
  127 missing sibling.

## Current operating facts

- Install the 2.1.1 registry set:

  ```bash
  cargo install --locked onlyne-cli onlyne-server onlyne-client onlyne-testkit
  ```

  The command installs the latest published version of each crate.
  Run `onlyne --version`, `onlyne-server --version`, and `onlyne-client --version` after
  installation. Each command must report `2.1.1`.

- `onlyne version` reports the CLI package, the protocol, and the sibling binary paths.
  Neither testkit command (`onlyne-agent-fake`, `onlyne-gateway-fake`) accepts `--version`.
  Read `onlyne version` for the installed package inventory. The TUI is a verb of the
  `onlyne` binary, and it is not a separate binary.
- `onlyne schema spec` and `onlyne schema client` print the compiled JSON Schema of
  `<server-root>/.onlyne/spec.toml` and `<workspace>/.onlyne/config.toml`. `--pretty`
  indents the same document. The keys, their types, and the required keys come out of the
  build. An installed binary therefore answers the whole vocabulary without a source
  checkout.
- Re-export the role and supervisor handbooks from the installed binary:
  `onlyne skill export --set role --set supervisor --force`.
- The live acceptance shape is completion, then handoff, then client kill. Read the task
  ledger, the session projection, both sequence numbers, and the ghost audit after the
  task settles. The expected readings are `acked`, `exited`, and no new ghost row for that
  task.

## Onboard a cluster

1. `onlyne server init --root <root> --listen 127.0.0.1:<port>` writes the `[server]`
   spec, the server key pair, and a fresh `cert_pin` in it. An existing `spec.toml` stops
   the verb with exit 4 until `--force`. An existing readable key pair keeps its own pin.
2. Put role content in `<root>/.onlyne/templates/<topo>/<role>/`. The basename is the
   spec role name. Templates hold `AGENTS.md`, prompts, and `.pi/` settings. They are
   opaque bytes plus a closed set of placeholders:
   `{{role}} {{cluster}} {{server_name}} {{listen}} {{cert_pin}} {{admin}} {{max_sessions}} {{agent_package}}`.
   The coding-agent package travels on the last placeholder. One appearance of it makes
   the package happen. Set `[server].agent_package` to the absolute path of a real
   package, because the spec that `onlyne server init` writes leaves it an empty string.
   Give the template a `.pi/settings.json` that holds
   `{"packages": ["{{agent_package}}"]}`. `generate` then vendors the whole package into
   `<ws>/.onlyne/agent/<pkg-name>/` and renders that entry as
   `../.onlyne/agent/<pkg-name>`. The `../` form is the one that pi 0.85.1 loads. A
   project `packages` path resolves against the directory that holds the settings file.
   A bare `.onlyne/agent/<pkg-name>` lists the package and starts nothing. Anywhere else
   in a template, the same placeholder renders as the workspace-relative
   `.onlyne/agent/<pkg-name>`. A template that uses the placeholder while
   `agent_package` is empty exits 4 with
   `onlyne: agent_package not set in spec.toml [server]`. A template that never names the
   directory gets a workspace with no package at all, and its sessions start with no
   plugin tools registered.
   The workspace skill also comes out of the binary:
   `onlyne skill export --dest <workspace>/.agents/skills --set role` writes
   `onlyne-role`. `--set supervisor` writes `onlyne-supervisor` for your own seat.
   `--set dev` writes `onlyne`. Each one lands as `<dest>/<name>/SKILL.md`. The default
   `<dest>` is `.agents/skills` under the working directory. A file whose bytes already
   match is left alone. A differing file stops the export with exit 4 and
   `onlyne: refusing to overwrite <path>; pass --force` before anything is written.
3. `onlyne server generate --root <root>` renders workspaces under `<root>/.onlyne/ws`
   and prints paste-ready `[[client]]` fragments. If any generated byte embeds an
   absolute path, the verb fails with exit 4 and deletes the output. Move a generated
   directory wherever you want: `mv`, then `onlyne client run --workspace <new-path>` in
   the foreground. Whoever wants it backgrounded starts it that way. That is the whole
   relocation story.
4. Append the fragments to `spec.toml`, then run `onlyne reload`. `onlyne spec-diff`
   shows the pending delta first. The spec file is the only truth. There is no runtime
   config API.

A key that `Spec` does not know is warned about and ignored. The server starts, and the
setting silently keeps its default. A config that looks like it took effect can therefore
do nothing. `onlyne-server run` prints one ``ignoring unknown key `<path>` `` warning per
such key on startup. Read those lines after every spec edit. A key that a release deleted,
such as the v1 `[client.timeout].running_ms`, looks exactly like a key that works.
`onlyne schema spec` prints the field set this build reads.

Two kinds of key are outside that class, and both name the line
(`spec.toml:7: <sentence>`). The first is a real key that holds a wrong value. The second
is a key that v2 retired by name. `backend`, `relay_required`, `relay_required_count`,
and `relay_count` are refused before the schema pass, at the root and inside a
`[[client]]` entry alike, with `BACKEND_IS_GONE` or `RELAY_IS_GONE`. A spec left over
from v1 is therefore told what to delete. `RELAY_IS_GONE` also carries the replacement.
`allowed_targets` is both the permission and the obligation. A role owes each of its
listed targets a delivery before it may report a terminal outcome. A role that owes
nothing leaves the list empty.

The exit number is a property of the door. The merged `onlyne` verbs report 4 for refused
operator input or generation. The daemon binaries `onlyne-server` and `onlyne-client`
report 1 for a failed run. An admin-socket verb asked before the server read the spec
reports 3 for no socket. The sentence is identical in all three doors. Read the sentence,
and read the code after it.

An existing tree carries a store marker. The `state.db` of the server names revision 6,
and the `client.db` of a client names revision 3. A marker that answers another revision
stops that daemon with a sentence naming the revision it found. A legacy workspace stops
`onlyne client init` before it writes anything. Both exit 6 (`EXIT_NEEDS_MIGRATION`).
That code is reserved for a build that will not start on a file from another revision.
There is no `migrate` command. The operator moves the old file aside and starts again.
Exit 2 is a different door: a bad flag, an unknown verb, or a missing supervisor gate
flag.

## Dispatch flows downhill

```bash
onlyne --server-root <root> send --from _supervisor --to <role> --text "RING=... K=1 TOTAL=10" \
  --force --yes-i-am-supervisor-not-other-role
```

Seven verbs require both flags: `send`, `reply`, `handoff`, `complete`, `ack`,
`reject`, and `control`. Each verb writes the voice of a role on the wire. The pair is
your declaration that the call stands outside the plugin session of that role. The
refusal names the plugin tool that answers for a role where one exists (`onlyne_send`
for `send`, `onlyne_handoff` for `handoff`, `onlyne_complete` for `complete`). A call
missing either flag exits 2 before it opens a socket. `repair *`, `ledger`, `sessions`,
`roles`, `faults`, `watch`, `history`, `reload`, and `status` carry no such flag. There
is no `shutdown` verb. Both daemons run in the foreground, and the terminal host owns
stopping them.

**Material moves by path, and it does not move through the envelope.** A delivery template can render an optional block that quotes the result of an upstream role. Nothing in the tree fills that block. That is a decision. Moving material between roles is the
business of the roles, and Onlyne does not take on the file system. A role that wants the
next one to have something writes it where both roles reach it, and names the path in its
`handoff` text. That text is a body any reader can open. A file that rides the envelope
rides in `attachments`, and the client has already written it by the time the text names
it. A digest fifteen pages long therefore goes over as a path in the handoff. A small
result that belongs in the conversation goes in the `handoff` body itself.

A task family carries its own metadata, and you set it where the run starts. `onlyne ...
send --hop-budget <n>` records the hops the family may spend. `--label <k=v>` records
whatever a script of yours reads beside the ledger, and you can repeat the flag up to
eight times. `--deadline <rfc3339>` records the wall-clock bound for the whole run. Every handoff inherits all of it. The child carries the root task id of the family, its budget, its origin, its deadline, and its labels. The origin is the role that sent the root. The hop that
meets the budget is therefore the hop that keeps the work. The figures ride `Causality`,
so `onlyne ledger` prints `family` and `hop_budget` off the row without a script that
rebuilds them from `parent_task` links. The delivery that a role model reads names
neither. A `handoff` that would sit over the budget is refused before the child is
minted. The counters are read off the ledger, never out of the task text.

- Roles answer by completing the task. The receipt lands in the ledger as `out_head`:
  the first 200 grapheme clusters of the completion body (`head_preview` in
  `crates/onlyne-store/src/server.rs`). The `onlyne_complete` tool of a pi session
  flattens its text to one line before it goes. `onlyne complete --summary` carries that
  line truncated to 200 characters (`HEAD_CHARS` in `crates/onlyne-cli/src/verbs.rs`),
  and `--head-from ledger` reads the head back off the row of the task. `--details`
  carries the whole result to the next hop and to the originator, capped at the
  `details` ceiling of the protocol, and `--file` names an absolute path that the result
  points at. A details body over the cap is refused before anything is sent. A receipt
  for a task your role dispatched reaches you with no receiver-side grant, and waits in
  `queued` until your role has a live session. Those rows are your pull-inbox. `ledger`
  reads the backlog, and the queue drains as your own client pulls.
- The ledger carries the state. Poll it for proof.

```bash
onlyne --server-root <root> ledger --task <task-id>       # queued|in_flight|acked|rejected|expired
onlyne --server-root <root> sessions --task <task-id>     # lifecycle projection
onlyne --server-root <root> watch --follow --tier durable  # live stream; tiers: durable|advisory
```

- Your sends need no receiver grant. Leave `allowed_targets` off your own entry, and
  every registered role is reachable. Name a list there, and the reach is exactly that
  list. The receiver's `allowed_senders` is read on no row of yours. Dispatch and repair
  therefore start at `send`, with no spec edit first.
- `_supervisor` is your inbox, and a backlog is what an inbox is for. The entry is a
  logical signature node with `command = []`. No client ever dials it. No session is ever
  opened for it. It reads `offline` for the life of the cluster. That is not a broken
  role, a leak, or dirty data. Your seat is yours to start and stop, and it is
  longer-lived than the swarm it supervises. Whatever arrived while you were gone is
  therefore exactly what you came back for. The ledger is durable.
  `onlyne --server-root <root> ledger` reads the whole backlog. `queued: N` on the role
  reads as N items waiting for me. Drain it first on every start, before you dispatch
  anything new.
- A supervisor that runs as a client names a real `command` for a runtime. It drains
  those same rows by pulling them into its own session. That is the right shape when you
  want the work delivered to you. It is the wrong shape when your lifetime is the user's to manage. A client-held inbox only holds what its own process was there to take. A row that sits at `queued` for an hour is a message that arrived safely and is
  still waiting.
- Nothing wakes you. There is no resident process and no "deliver to me and I start".
  Timeliness therefore belongs to a hook, and it does not belong to the queue. Bind
  `[[hook]]` to `ledger_state`, and filter the event on
  `data.to.role.role == "_supervisor"` to learn the moment work lands. Let the script
  carry it to whatever is actually running. The worker set is read at server start, so
  changing `[[hook]]` needs a restart.
- One thing can shorten an inbox: a TTL you set yourself. `requeue_ttl_secs` under
  `[server]` defaults to `0`, which expires nothing. A queued receipt for a role with no
  live connection then waits indefinitely. Set it positive, and every queued receipt to
  `_supervisor` is eligible for expiry once that TTL passes, because `_supervisor` is
  permanently disconnected. The clock then reaches your inbox whether you meant it or
  not. That one setting is the whole of it. `--ttl` is read only on a `--note` send, so a
  dispatched task carries no deadline of its own. A row that was already handed out and
  returned is owned by its own requeue gate, and the TTL does not own it.
- Completion receipts for a task you dispatched always reach you, offline queueing
  included. The recorded origin in the ledger is the path, and it needs no standing
  edge. A role completing work it was handed from another role is a different path, and
  that path reads `allowed_targets`. Keep `_supervisor` in the `allowed_targets` of the
  roles whose receipts you want to collect.

## Operator policy lives outside the core

The events you most need to hear about are recorded by the client that witnessed them
and published onto the stream of the server. The two examples are a turn that ended
without a completion and a delivery that came back `blocked`. What to do about them is
your policy, and the spec carries it:

```toml
[[hook]]
on = ["delivery_blocked", "turn_end_without_complete"]
run = ["./hooks/notify-supervisor.sh"]
timeout = "10s"
```

- `on` names classes from a closed set: `ledger_state`, `session_state`, `fault`,
  `role_presence`, `gateway_presence`, `spec_reloaded`, `turn_end_without_complete`,
  `delivery_blocked`, and `handoff`. A class outside the set refuses the whole load by
  name, with `spec.toml:<line>`. That is a hard refusal. The unknown keys described
  above pass with one warning line each, and this refusal is different from them.
- The server spawns `run` for each matching event. The event arrives as one JSON object
  on stdin with `seq`, `type`, `data`, and `created_at`, and `ONLYNE_SOCKET` is set to
  the admin socket. The script can therefore `onlyne send ...` in the same step. A slow
  script delays nothing: an event reaches every subscriber without waiting on any hook
  worker.
- Delivery is at-least-once per hook. The last handled `seq` is recorded, and a restart
  resumes from there. A script that must not act twice deduplicates on `seq`. A nonzero
  exit or a timeout records fault `hook_failed` once for that event and leaves the event
  untouched. The hook returns to that event instead of skipping ahead. A broken script
  therefore holds only its own backlog, while the stream and every other hook carry on.
- The worker set is read at server start. Editing `[[hook]]` needs a restart. A
  `reload` that changes the set names it in the log.

`docs/operations.md`, section "Event hooks", carries the full table and a worked script.

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

The core detects and records. Recovery is your call. `repair retry` handles eligible
`queued` or `in_flight` work. A task whose rows are settled returns `conflict`.
`repair fail` settles the task `failed` and rejects its undelivered rows. `repair close`
settles it `cancelled` the same way. `repair adopt` re-points the desired backend
binding of the row. `repair rebind` moves the row to another session id and bumps its
generation. `repair inspect` prints the session projection with every fault recorded
against the task. The `kind=task` row is authoritative for the task outcome. A
`kind=completion` row records receipt transport and `out_head`, and its state never
reopens a rejected task. Client and server `(generation, seq)` values are per-writer
watermarks. Compare the terminal outcome, the lifecycle, the resource, and the
generation, and do not require equal sequence numbers. Task control runs beside repair:
`onlyne control recycle|probe|snapshot|cancel|focus --task <id> --from <role> --force
--yes-i-am-supervisor-not-other-role`. `recycle` and `cancel` carry a required
`--reason`, and the other three take none. A `--reason` on `probe` is refused by the
parser. `focus` brings the live session of the task to the front of its host. A client
holding `max_sessions` sessions pulls with `control_only`, so those commands reach the
session that holds the last slot. Work for that role waits until a slot frees.
`DeliveryState::Exhausted` is terminal. Retry it only after an explicit decision here.
A command on this surface speaks as a role, so `control` and the four message verbs name
it with `--from <role>`. The reads resolve everything from the row they name and take no
such flag. `control` needs no `--to` on this surface, because the session row of the task
names the role the op has to reach. The CLI reads that row and addresses the op there.
An explicit `--to <role>` still wins. A task that no session owns is refused before
anything is written, and the refusal names `--to`.

`recycle` and `cancel` end the task on your word. The client asks the plugin for its
ending and closes the host resource, and the own report of the plugin settles the task.
A word the plugin never answers is settled by this client after three heartbeat
intervals. A cancel landing before an agent has written anything therefore still ends
its task, and leaves no row for a sweep to take. The delivery row the client still holds
is refused with `operator cancel` or `operator recycle`.

Heartbeat faults carry the liveness verdict, and the row keeps its state through them.
`heartbeat_missing` says the pane beats stopped and the role link stayed up. The row is
`working`, `onlyne sessions` answers `heartbeat_stale` on it, and the TUI shows
`working+stale`. Check the pane first. A dead process answers `control recycle`. A live
one resumes beating inside ten seconds and clears the flag on its own.
`heartbeat_after_complete` says a session kept talking after its completion landed.
`control recycle` ends the straggler, and the history of the row keeps the settled
completion either way. Both kinds open once per task and stay open until you
`repair ack` them. The fault table therefore doubles as your to-do list.

`stalled` is the own report of the client. A session whose projection tuple froze for
`stall_report_secs` (1800 default, 0 disables) faults once per episode. No-op beats keep
the row beating. `stalled` is the progress verdict beside the liveness one. The verdict
means real silence on live work. The client checks the stored lifecycle at the scan and again at the send boundary. So a session that already completed has its progress clock retired before any fault fires. Run `control probe` first, then `control recycle` or
`repair retry` as the answer demands.

`stale_working` covers the owner that left. A row that the mirror still reads `working`,
whose role has been offline past 600 seconds, records this fault once. The own observer
of the server writes it. `[server].stale_watch_secs` (60 default) is the scan cadence
for both observers.

A row that no client will ever write again is the work of the ghost sweep. A mirror row
still reading `working`, whose task ledger row has already reached a terminal state, is
rewritten by the server on its own interval. `[server].ghost_sweep_secs` (60 default, `0`
disables the pass) sets the interval. When the mirror has no outcome, the task ledger
supplies it: `acked` settles `done`, and `rejected` and `expired` settle `failed`. An
outcome already present in the mirror is preserved. The sequence advances, a
`session_state` event travels, and one row lands in `ghost_sweeps`. The row names the
session, both sequences, the outcome, and the evidence it acted on, such as
`task_settled:acked`. `onlyne ghosts [--limit N]` reads that audit, newest first. One
class stays out of its reach: a `working` row whose owner role is offline while the task
is still open. An ending there would decide live work and swallow the requeue that the
work is owed. `stale_working` remains the only output for that class, and its recovery
stays yours through the `repair` verbs.

A task-bound unsettled session is retired after either a dropped connection exceeds
`[client] reconnect_grace_secs` (60 default, 0 disables that arm), or an attached
transport accepts no frame for three heartbeat intervals. Both arms settle the task
`failed`, refuse the held delivery with reason `session_dead`, close the host resource,
and publish the exit. That refusal is terminal. Create a new task to run the work again.
`repair retry` only requeues eligible `queued` or `in_flight` rows, and returns
`conflict` for a settled task.

A delivery that arrives with the accept gate of the client closed is left unanswered.
The row stays `in_flight`, and the next `hello` that does not claim it puts it back on
the queue. A refusal (`accepted: false`) is kept for work this client can never serve.
The examples are an assignment the plugin declines (`assign rejected`) and a session the
word of the operator retired with its delivery still in hand (`operator cancel`,
`operator recycle`).

A finished session takes its host resource with it. The client closes the pane, tab,
tern block, zellij session, or exec child once that session holds no task and no plugin
connection is attached. The client log records the closure with
`retiring idle session resource`. An idle pane still open in front of you means the
owning client is down.

**A scope that keeps sessions overrides the rule above.** It overrides it by making the
runtime hold on. `[client.session] scope = "task"` or `"role"` promises a session that
outlives the delivery it served. That session is therefore not closed when the work
lands. A `role` pool hands the next delivery to a member that is still there. The client
never reclaims a member on its own. A task-free session is exempt from the
three-heartbeat silence sweep by name. A session whose connection is still attached is
exempt from the reclamation sweep. What ends a member is the runtime leaving, in one of
two ways. Both reach the same log line above:

- Its process exits or its socket ends. That starts `[client] reconnect_grace_secs`
  (60 default), and the session is retired when that window passes.
- It sends `detach`. A session holding no task is retired **at once**. The protocol has
  no other way to read "I am leaving" from a session with nothing left to serve. A
  graceful goodbye is therefore taken as a final one.

So a `role` pool needs a runtime in one of exactly two shapes. **Resident**: the process
and its socket stay, and it does not `detach` when it runs out of work. That is what
`idle_close = 0` asks for. **Resumable**: the runtime declares `resume`, so a non-zero
`idle_close` suspends it instead. The conversation stays in the own store of the runtime,
and the next delivery resumes that conversation rather than starting a new one.
`suspend` is the frame that asks for the release. A runtime declaring neither simply
waits for its agent to leave.

**`pi` reads the scope and acts on it.** Each `assign` carries the scope of the role.
The plugin ends its own process under `oneshot` and stays under `task` or `role`. A
`role` pool in front of it therefore holds its member, and the same conversation takes
the next delivery. A `oneshot` session leaves and takes its pane with it. That second half is a load-bearing detail. The client retires a session while its agent is still reachable, because that exemption is what keeps a pool member alive. A runtime that
stayed under `oneshot` would hold its pane open forever. The leave also has to be the
own leave of the runtime, because the teardown of the client is a pane kill. A runtime
killed mid-teardown loses what it had not yet written. pi flushes its session file as it
shuts down.

`pi` declares `register`, `report`, `inject`, and `recycle` with no `resume`. The other
door is therefore shut to it. There is no setting that releases its process and brings
the conversation back, and `idle_close` has to stay `0`. It must not name a bound.
Nothing in `spec.toml` can assert that half either. It is the agent to keep it.

The tell that a pool is not being reused is a `role` role whose `onlyne sessions` shows
a new `session_id` per delivery and none left standing. A pool that works looks like one
row reading `lifecycle=idle` with `resource=attached` between deliveries. The client log
carries `the delivery joined the session its scope keeps for it` once per reuse.

**A pool that empties and a tab that never closes have one cause, and it reads like
neither.** The scope rides the assignment as `assign.scope`. A runtime can act on it
only when the **client binary** stamps it, and re-vendoring the plugin is a different
install. A client too old to stamp it sends a frame with no scope. The runtime reads
that as `oneshot` by design, and every session then leaves on completion. The signature
is unmistakable in the client log: `stays idle`, followed three to seven seconds later
by `retiring idle session resource`, for every delivery, with the tab going away each
time. A pool that empties and a tab that closes together mean the binary is behind. The
two problems did not cancel each other.

The same log line is how a reclaimed resource looks from the outside. `idle_close`
non-zero on a runtime that declares no `resume` suspends a session that cannot be
brought back. That reads as a pool member vanishing for no stated reason. When a `role`
pool misbehaves, read those two lines before reading anything else.

### Orca and Tern sessions

Orca creates one new terminal for each task. `attach` refreshes a persisted terminal
handle. It does not relay into an arbitrary existing session. Spawning requires a
running Orca app, an `orca` CLI that resolves to and reaches that app, and a client
launched from the intended Orca tab with the matching worktree environment
(`ORCA_WORKTREE_ID` under the host policy). A `[single-instance]` CLI error is the
immediate spawn refusal. The exact `session_dead` rejection comes later, from the
retirement sweep of the client after a slot exists.

Tern runs each session as a block inside the tab of the role. One Tern session serves one cluster, and one tab serves one role. The block is retired when the session ends. Set it with
`placement = "tern"` in the `config.toml` of the role workspace, or with
`ONLYNE_BACKEND=tern`. An absent `placement` probes `tern`, `orca`, and `zellij` in that
order and falls back to `headless`. A machine with Tern therefore uses it without a line
of config. The `onlyne` board that watches your clusters inside Tern ships in this
repository at `integrations/tern-plugin`. `tern plugin install integrations/tern-plugin`
installs it. `tern plugin link integrations/tern-plugin` loads that directory in place
and reloads on every save. It is a supervisor face. It runs the same admin verbs this
document names (`status`, `roles`, `sessions`, `faults`, `control`, `repair`) as
one-shot `onlyne` processes against each root.

Automatic re-delivery rides two spec gates. `[server].requeue_max_attempts`
(0 unlimited) lands a returned in-flight row as `rejected` with reason
`requeue_exhausted`. `[server].requeue_ttl_secs` (0 off) lands returned rows as
`expired` with reason `requeue_ttl`. The TTL also expires never-pulled task, completion,
and control rows while their recipient role has no live connection. `repair retry`
always rides outside the gates. A reconnecting client declares its live sessions at
`hello`. A link flap therefore leaves the row of a running task `in_flight` and
un-duplicated. A claimed session that dies without completing gets its row requeued the
moment the client reports it exited. `repair inspect` keeps the whole trail either way.

A restarted client declares no live sessions. The server then requeues every
unacknowledged row of the roles it reconnects as, and the next pull hands them out
again. `onlyne ledger --task <id>` shows the rows that came back.

Both gates leave their mark where you can read it. `onlyne ledger` prints the row it
holds, and a settled row carries its `reason`. The key is among the eight the CLI
recognizes on a ledger answer: `msg_id`, `task`, `state`, `reason`, `out_head`, `body`,
`family`, `hop_budget` (`ROW_FIELD_KEYS` in `crates/onlyne-cli/src/ledger.rs`). A row
carries the key only where it has a value. A clean `acked` row simply omits it, and the
bytes match what the same row printed before the column existed. The page-2 task panel
of the TUI appends `reason=<text>` to the tail of the row under the same rule. Six
settlement doors write a value on the column. `requeue_exhausted` and `requeue_ttl` come
from the two gates above. `expired` comes from the deadline sweep on a queued note past
its `--ttl`. The refusal of the receiving client carries its own word there:
`session_dead` when the reconnect sweep buries the delivery of a dead session,
`assign rejected` when the plugin declines an assignment, `operator cancel` and
`operator recycle` when the client settles a session the word of the operator retired
while it still held the delivery, whatever `onlyne reject --reason <text>` names, and
the literal `rejected` as the fallback. The own `onlyne repair fail --task <id> --reason
<text>` and `onlyne repair close --task <id> --reason <text>` of the operator write that
text onto every undelivered row of the task, and the close falls back to
`operator close`. The ack side stays out of it. `onlyne ack --msg-id <id> --reason
<text> --force --yes-i-am-supervisor-not-other-role` settles the row through
`mark_acked` and keeps a reason the row already carried. `onlyne repair ack --fault-id
<n> --reason <text>` writes its reason on the fault row alone. Both run against a role
workspace or client socket, and both require `--reason`.

## Errors you will see

`acl_denied`: the edge is missing from the spec. The `allowed_targets` of the sender and
the `allowed_senders` of the receiver have to name each other. Your own sends read
`allowed_targets` alone. A denial on one means that list is non-empty and omits the
target. `unauthorized`: the handshake refused the peer. The causes are an unregistered
key, an unregistered role, a key registered for another role, or a bad signature.
`recipient_offline`: a `note` found nothing to wake. Its role was offline, or online
with no session running and `note_queue` off. The message says which. `duplicate`: the
same `op_id` again. Its `data` is the original receipt, byte for byte. `conflict`: the
same `op_id` with a different body. `not_admin`: a `cluster:` principal sent without an
admin standing. A role that is neither the administrator nor the task owner gets
`forbidden` on a control frame. Every reject writes no ledger row and leaves no sender
intent. The `--ttl` deadline of a queued note sits on its ledger row, and the server
re-arms every stored deadline at startup. The sweep therefore answers `expired` after a
restart too. A note that was already queued when the server was upgraded carries no
deadline and stays `queued`. Settle it with `repair fail` or `repair close`.

## Watching with the TUI

`onlyne tui --server-root <root>` opens the three-page board in this process, and reads
the admin surface. `1`/`2`/`3` switch pages. `Tab` walks the panes of a page. `↑`/`↓`
step the selected row. `PgUp`/`PgDn` (or `[`/`]`) scroll a pane of lines. `q` or `Esc`
leaves. The cluster page lists every role with its presence, the sessions it holds
(`sess`), how many of them are busy, idle, or suspended, and its queue depth. Beside it
is the board of the selected role, one row per delivery in the five-column reading
(`queued`, `running`, `waiting`, `done`, `failed_or_blocked`). The event tail sits under
both. `Enter` opens the family of the selected card on the task page. That page is the path of the family across roles: every delivery by hop, with its verdict and the receipt it settled with. It sits over the tail of the session serving the selected delivery.
The faults page lists the open faults, the own fields of the selected fault, and the
repair verbs it offers with the key that opens each: `a` `repair ack`, `t`
`repair retry`, `c` `repair close`, `F` `repair fail`, `i` `repair inspect`.

The four operations are forms the board opens on the selection. `s` sends a task with
`from`, `to`, and `body`. `f` focuses with `from`, `to`, and `task`. The target is named
by hand, and it is not read off the selection. `r` reports the verdict of a task with
`from`, `task`, `outcome`, and `head`. The repair keys above open the rest. `Enter`
submits a form. `Esc` cancels it. `Tab` moves the caret between its fields. The second
line of the footer prints what the op answered. `^R` re-reads the snapshot. Nothing
polls: a page moves when the admin stream says the cluster did, and a gap in that
stream leaves the header saying `catching up` while the snapshot is re-read.

`onlyne tui --server-root <root> --once` renders one frame as plain text and exits. The
frame is the cluster page, from one snapshot.

## Clusters under clusters

Your own client connects to a parent server as a plain `[[client]]` entry marked
`aggregate = "<child-cluster>"`. The label is an annotation. It contributes no ACL rows,
the delivery path carries no aggregate branch, and a generated `[[client]]` fragment
drops it. Tasks flow in, completions flow out. Every parent ledger row is written from
the parent-side envelope, so its `from`, `to`, and body name parent-visible roles
alone. Hand the parent operator your interface text with
`onlyne cluster export-prose --role <role>`. It prints the prose raw for pasting into a
TOML multi-line string, and wraps it in an object under `--json`. The protocol contains
zero federation code, so there is nothing to break.
