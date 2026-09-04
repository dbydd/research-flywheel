 The Harness Playbook — Stencil Stencil Blog 

 PLAYBOOK Link preview The Harness Playbook Can Bölük 2026-09-02 Before anything else: a thank you. Hundreds of thousands of you have used omp, reported what broke, suggested what was missing, and shaped what it became. This post and omp² itself exist because of you. Upon hearing about omp², many of you jumped to ask, "but why?" A while loop around a fetch sounds simple, but there's a reason OpenCode, Pi, OpenClaw and omp are all
concurrently working on a complete refactor: this class of software did not exist before, and only by starting
with the simple version, we could see the cracks to work towards a better one. Unavoidable complexity needs an owner. At the moment, the conservation of complexity 
tips toward extensions and users, making it impossible to write reliable software on top of omp or Pi. I can already hear
the "whaaat, it is so simple and pleasant to extend." Give me a few chapters to change your mind. Dijkstra wrote that "simplicity is prerequisite for
reliability" , and yet he is known for
algorithmically solving pathfinding. Why not just brute force? He was not, at all, making the claim
we now repeat as simple good, complex bad . The advice was to help implementers reason. We
shamefully use it to excuse the implementer from reasoning. Ousterhout gives the missing half in the notes of his Stanford lectures. He tells module writers to
 "embrace
suffering" .
Take on hard problems, solve them completely, and make the result easy for everybody else to use.
Push complexity down into the module. Let a few implementers carry it instead of making every caller
carry a smaller, slightly different copy. I am sure many readers remember the wave of memes from the tweet comparing Claude Code to a game
engine. The comparison sounds far-fetched, but if you list the responsibilities of a harness, putting rendering aside, it does match quite well. It maintains an authoritative world, journals changes, runs untrusted actions, replicates state to
multiple views, schedules actors, interprets commands, adapts incompatible protocols, and renders a
real-time interface. Sounds familiar? It seems game engines have spent decades owning the same categories of complexity. What follows is both a postmortem and a playbook: 
 What omp taught us names failures we met in a system people actually used. 
 What omp² changes describes the replacement architecture—some of it already built, some still
being worked through. 
 Contents 9 chapters · 2 appendices 01 The design envelope 02 The state 03 The runtime 04 The control plane 05 The inference 06 The tool surface 07 The interface 08 The stack 09 Closing notes A State failures in the official examples B Elastic Speculative Slots The design envelope Choose the operating modes first; every subsystem must survive all of them. Before discussing any subsystem of an agentic harness, imagine that four very different products
will depend on it: 
 Multiplexed workspace 
 A local environment with multiple agents and subagents in the same folder. 
 Remote driver 
 A remote client driving a cloud agent—or the machine under their desk—from a phone. 
 Spectator 
 A web client watching a Claude agent work. 
 Factorio 
 An automated software factory using the SDK against untrusted input. 
 These are not market personas. They are architecture tests. Together they vary the dimensions that
make a harness stop being a chat loop: Test Local or remote Interactive or autonomous Trust boundary Concurrency Multiplexed workspace local interactive mostly trusted many agents, one workspace Remote driver remote interactive split host/client one or many agents Spectator remote view observational untrusted presentation input many viewers Factorio remote or fleet autonomous hostile repository and tool input many jobs A design that only works for the first case tends to smuggle the controller into the TUI, keep
state in closures, let extensions execute in the engine process, and assume a human can recover from
an unbounded call. A design that survives all four is forced into better boundaries. The rest of the book follows five consequences: 
 One authoritative session. Rewind, fork, resume, replication, and inspection must all derive
from the same journaled state. 
 A trusted control plane. Policy and session ownership stay on the host; sandboxes receive only
bounded execution requests. 
 Bounded work. Tool calls, subagents, and background jobs are all cancellable streams with
central limits and observability. 
 Explicit compatibility. Model and provider quirks are structured knowledge, not branches
scattered through call sites. 
 Views are projections. The TUI, web client, remote client, and subagent inspector render the
same state instead of becoming additional authorities. 
 Those constraints are connective tissue for everything that follows. When a later section proposes
a DOM, a convar, a Director, a tiny VM stub, or a component renderer, it is solving one of these
five requirements—not introducing a clever subsystem for its own sake. The first requirement is the foundation: before deciding where code runs or how it is rendered, the
harness needs to know what is true. The state If authoritative state cannot be derived from the journal, rewind, fork, and resume are lies. What must survive If you want something to be durable, rewindable, crash-tolerant, and forkable, you have three
choices: 
 Preserve the history that produces it. 
 Preserve the changes in the properties you care about. 
 Preserve the machine itself. 
 The Source Engine uses a variant of the second option for networking. omp and Pi currently use...
none of them consistently. There are events, but state is not really sourced from those events,
violating the first principle of event sourcing: state must be derivable from the events alone . What omp taught us: two authorities π · two authorities 1 · never a delta — but it IS state 2 · rewind cannot reach it OUTSIDE THE TREE todo · retry · subagents · streaming closures · prompts · tools · settings · MCP authoritative, not derived UNIT OF CHANGE message · custom · custom_message covers the tree only SOURCE OF TRUTH message tree ids and messages only ON DISK · .jsonl the tree, and nothing else REPLAY move leaf pointer replay(.jsonl) ≠ original rewind · fork · resume all lie Source engine · single authority never a delta — fine, it is derived OUTSIDE THE ENTITY LIST client prediction derived, never authoritative UNIT OF CHANGE { Δ entity … } covers every field SOURCE OF TRUTH entity list rules · plugins · globals — all of it ON DISK · .dem all of the state REPLAY seek tick, re-derive replay(.dem) == original nothing outside left to leak One authority versus two: everything in Source is an entity delta, so replay(.dem) == original . Pi's journal covers the message tree only, while authoritative state lives outside it—rewind, fork, and resume all lie. There were understandable reasons to arrive here. Repeating the system prompt and AGENTS.md in
every log would be wasteful; that can be solved by hashing the template and storing its variables.
And this style of state modeling is not common in TypeScript, which does not actually have runtime
types. The result, however, is still two sources of truth: Source Engine Pi-style harness source of truth entity list , that is it. The server simulates; the client predicts. message tree plus todo state, retry counters, subagent registry, streaming flags, and other state invisible to persistence unit of Δ { Δ entity ... } , covering every field because every delta is an entity delta message / custom / custom_message , with no engine-owned fold; every extension hand-rolls derivation globals CCSGameRules is a singleton entity . No special cases. three tiers, one of which works plugin state plugins write entity fields, so state is networked and replayed by default module-level closures: let turnCount = 0 , new Map() , new Set() replay load .dem , seek to a tick, and re-derive load .jsonl ; the leaf pointer moves while the other authorities reset or survive arbitrarily The globals row is where it gets funny. Source does not have session globals; they are simply
properties of an entity. Ours have their own hierarchy: journaled as tree entries journalable via custom entries not journaled at all is this fact in the tree? A ✓ the blessed ~3 model_change · thinking_level_change session_info · label replays correctly B ~ hand-rolled every extension writes its own derive ≈15 lifecycle bugs, see below C ✗ outside history AGENTS.md · extension set · tool roster settings · provider config · MCP servers edit AGENTS.md → the replay uses today's copy. the session you recorded is gone. header line = (version, id, timestamp, cwd) no parentid → not in the tree → can't branch, can't rewind The three tiers of session globals, one of which works. Source did not get its correctness by writing a careful reconciler or excellent documentation. It
made non-replayable state unrepresentable . Correctness comes from that constraint , not from
every extension author remembering to register two hooks and define an update shape. The evidence: correctness is optional in the API We looked at the 78 official Pi extension examples. Sixty were stateless; among the 17 with state, only two
were correct. Example State that escaped authority User-visible failure git-checkpoint.ts checkpoint refs owned by a transient Map /fork runs after agent_settled has already cleared the checkpoint plan-mode/index.ts plan mode restored from the whole file, not the selected branch rewind leaves restrictions active; resume can resurrect a dead branch status-line.ts turn count in a closure rewind from turn 3 to turn 1 produces turn 4; resume starts at zero dynamic-tools.ts live extension registry a tool survives rewind, then disappears after resume snake.ts restore scans abandoned branches a save from a dead branch returns bookmark.ts “last” means last in file order a hidden assistant message on an abandoned branch gets bookmarked kimi-deferred-tools.ts active tool roster is not re-derived Calculator stays active before its discovery point auto-commit-on-exit.ts shutdown conflates process exit with session switch /new , /resume , or /fork commits the worktree tic-tac-toe.ts live writes and restore reads use different entry types a crash can make the user's move disappear You can find the details in Appendix A , but the important
point is that documentation would not repair this distribution of bugs. The engine needs one place
where state can exist. tic-tac-toe.ts : play X, crash before O replies, resume, and X is gone. Live writes and restore reads use different entry types. What omp² changes: one materialized session What if the whole session materializes as one DOM ? Of course you can also use a ECS system with serialization, or any other
representation format you wish, I mainly chose XML as it makes the state very easy to compose, inspect and debug. < meta > 
 < todo >…</ todo > <!-- persistent components, journal-derived --> 
 < jobs >…</ jobs > 
 </ meta > 
 < body > <!-- the live chain, entries as elements --> 
 < user id = "e12" >…</ user > 
 < ai id = "e13" >…</ ai > 
 < Read id = "e14" status = "ok" > 
 < input path = "src/main.rs:1-80" /> 
 < result lines = "80" >…</ result > 
 </ Read > 
 </ body > 
 < queues > 
 < steering >...</ steering > 
 < prompts >...</ prompts > 
 </ queues > Its events are a property-change stream: : todo.done 
 event: patch@1 
 by: e41 
 data: {"ops":[["set",412,"status","completed"],["set",415,"status","in_progress"]]} The tree is the authority; the journal stores its incremental changes. Runtime objects may cache or
index it, but they do not become a second place where truth lives. At any journal point, the harness
can materialize—and therefore snapshot—the whole session. What one authority buys With state and transcript in one tree, several hard problems reduce to the same operation. Rewind is a DOM diff. Diff the current materialization against the target state. A <subagent> 
element disappeared? Terminate it by destroying the element. One appeared? Resume or spawn it by
creating the element. The delta itself is the complete lifecycle work list. 
 Adding a stateful feature never adds a call site to rewind, fork, resume, or replication. 
 Prompts become projections. There is no 100-line state object passed into every template. The
system prompt reads the same tree as everything else: - {{ count(select("todo item[status!=completed]")) }} open items Replication becomes subscription. We already have the application and the derivation. A remote
client consumes the patch stream instead of tailing a file. The remote-driver and spectator cases no
longer require separate state plumbing. Rendering becomes projection. A component registry can render Read , Bash , a message, or a
subagent from the same element state. Streaming arguments mutate <input> ; streaming output mutates
 <result> . Chapter seven turns this into a typed interface rather than another bespoke renderer. Controller and actor This separation also makes subagents inspectable. Pi's views read live session state directly—the
footer calls sessionManager.getEntries() —so adding “inspect subagent” means plumbing controller
state through UI internals. Keep controller and actor completely separate: the controller owns session state; actors only
render its snapshot and patch stream. The TUI, remote client, and subagent inspector become peers.
Inspecting a child means pointing the same actor at the child's state. A truthful state model is the foundation, but it can still be undermined if untrusted code owns the
policy that mutates it. The next chapter draws the runtime boundary. The runtime Keep policy on the trusted host; put only a bandwidth-bounded execution stub inside the sandbox. The state chapter established what the harness believes. The runtime chapter decides who may change
it, where untrusted work runs, and what a “tool call” means once execution can last hours, stream
output, or ignore a polite request to stop. The sandbox should execute, not decide Start with the Factorio case from the design envelope. Suppose we clone roboomp, ask gpt spark to replace every mention of its name with CodeWhatever,
and start charging people thousands for our magic technique. Who runs the tools? The VM, duh.
Yeah, right. Here is what happens when we put the executor in the VM: TOOLS ARE COMPLICATED DRIVER trusted harness trust boundary VM untrusted: code exec, web content WHERE DOES EACH TOOL LIVE? 1) TODO harness state 2) FILE R/W which side? 3) IMAGE-GEN output lands here 4) PY-EVAL exec state needs secret PROGRAMMATIC TOOL USAGE CONFLICT! ? Hmm, well that doesn't work. Because: 
 Programmatic tool usage requires access to all tools; so we can't arbitrarily split harness-state
tools and environment-state tools 
 We'd need to build a duplex gateway, allowing the VM to call host tools; which,

 Defeats the purpose (either you enable DoS; or you need to rate-limit your own VM with certain
actions) 
 Just made this even more complicated, no thank you. 

 Okay, let's put the driving app, in the VM! WHAT IF THE DRIVER LIVES IN THE VM? VM (untrusted) DRIVER app source + prompts now you have to build & host THIS LLM GATEWAY proxy — key stays out here (a) conn error (b) OOM kamikaze outside can't tell which! ? untrusted prompt app source leaks out ! moved the boundary, kept the pain 
 Now we're leaking app prompts as well as internal source, unless we move our app outside the VM, and
connect to the harness via a network RPC, as well as move the session storage outside 
 But, session storage being outside, means we'd need to grant write access to the VM, which again,
gets us back to Problem #1 & #2 together. 
 The solution is to put a single, obedient, stub inside the VM, and be very very careful, limiting
the max amount of data streamed back (you don't want a 2GB response to a misused Read tool): THE STUB STAYS IN, EVERYTHING ELSE STAYS OUT HOST (trusted) DRIVER <git> HARNESS LLM GATEWAY keys live here SESSION STORAGE single writer typed RPC the only door VM (untrusted) if popped: attacker gets a stub, python, and grep EXECUTOR STUB py + rg mirrored <git> RO overlay that's it. nothing else. minimum viable prisoner The diagrams lead to one boundary: 
 The host owns session state, inference, policy, tool routing, approval, limits, and journaling. 
 The sandbox owns environment execution through a small, obedient protocol. 
 Every stream crossing back is bounded before the untrusted side can exhaust host memory or context. 
 That arrangement satisfies Factorio without making local use worse. The same host can point the stub
at a local process, a container, a VM, or a remote machine. Subagents cross the same boundary Placement is not only host versus VM. Subagents need the same boundary at the filesystem layer:
worktrees isolate tracked files only, while pi-iso gives each child a copy-on-write view of the
whole workspace using APFS, btrfs, ZFS, overlayfs, ProjFS, or a copy fallback. The child diverges;
the parent receives a diff. The child receives a view and returns changes. It does not share the parent's mutable authority.
That is the filesystem form of the same host/sandbox rule. What omp taught us: one call, three disconnected APIs Okay, but how do we define a tool? We'll go into the changes we made initially later on, but we
mostly kept the core contract identical: export const myCustomTool : ToolDefinition = { 
 name : "my_tool" , 
 parameters : mySchema , 

 // 1. Called during argument streaming & before execute() 
 renderCall ( args , theme , context ) { 
 if ( context . argsComplete ) { 
 // Trigger async preview computation 
 } 
 return new Text ( "Pre-execution preview UI..." , 0 , 0 ); 
 }, 

 // 2. Main execution 
 async execute ( _id , params ) { 
 /* ... -> string */ 
 }, 

 // 3. Called after execute() settles 
 renderResult ( result , options , theme , context ) { 
 return new Text ( "Final execution result UI" , 0 , 0 ); 
 }, 
 }; This contract looks pleasantly small, but it splits one operation into three unrelated phases. The
preview, execution, model result, human result, diagnostics, streaming updates, cancellation, and
journal record all describe the same call. The API makes them pretend otherwise. The callback split duplicates work First, splitting the renderer path makes reactivity opt-in. Even when the rendered tool does not
“snap” into a new shape, the author has to duplicate much of the presentation logic. The larger problem is how execute works. Take Edit as an example: 
 renderCall will open the file, hopefully caching the read parts somewhere (where?), apply the
edits, and render a diff 
 execute will then open the file again, applying all, writing, and returning a diff in a
model-friendly format 
 renderResult then gets this diff, but has to parse whatever format we decided on! Why? Because
a human wants to see colorized and highlighted version of course, maybe with nicer line numbers. 
 This led to an instinctual implementation that: 
 wasted I/O time: file opened twice 
 wasted CPU time: application was calculated not once, not twice, but each time a character
changed, all over (renderCall is not a coroutine!) 
 unnecessary ser/de over arbitrary format: we had to parse model output to implement renderResult
(or pass bits in details, duplicating the data journaled) 
 In order to make this efficient, you need to implement a coroutine that you drive outside this
definition, find a place to store its handle, and you will still have to implement the whole result
deserialization business. The problem is not merely duplicated code. The contract has no authoritative object whose state
moves from “arguments streaming” through “running” to “settled.” Every implementation invents a
side channel for that lifecycle. What omp² changes: execution is a state stream Tool execution is a bounded, cancellable stream of state—not an async function that returns text. There is also no general way to add structured warnings, diagnostics, or truncation notices. Most
Pi tool implementations end up doing something like: text += ` \n ${ theme . fg ( "warning" , `[Truncated: ${ truncation . outputLines } lines shown ( ${ formatSize ( truncation . maxBytes ?? DEFAULT_MAX_BYTES ) } limit)]` ) } ` ; The model then has to guess where tool data ends and harness commentary begins. Because execute 
is not a generator, streaming output requires yet another protocol over the update channel. The DOM model removes both special cases: 
 streaming output mutates the <result> body; 
 adding a warning creates <diag severity="warn"> . 
 While execution is ongoing, clients receive patches to this state. Once it settles, the final diff
against the previous state is journaled. In the unified session model, a call is an element with structured children: < Edit id = "e41" status = "running" version = "3" > 
 < input i = "Update the parser without changing the public API" >…</ input > 
 < result >…streaming structured state…</ result > 
 < diag severity = "warn" >…</ diag > 
 < usage tokens = "0" elapsed-ms = "842" /> 
 </ Edit > The executor mutates this element while it runs. The model, user, journal, remote client, and test
harness observe different projections of the same state. Settling freezes the final diff; no client
has to parse a result string to recover the richer object that existed before serialization. Limits are part of the primitive A Pi tool has no limits: return 1 MB of text and it is forwarded to the model verbatim. That is too
low-level a primitive to expose. Bound output once Pi faced this itself with Bash and Read , and answered with a truncation utility exported for
implementations to share. omp extended that utility with an artifact system so the model can read
the preserved full output back, but left the responsibility where Pi left it: on each
implementation. Sending 1 MB to the model may be a capability worth keeping, but it should be an opt-out—one central
implementation and an explicit notrunc property—rather than truncation being an opt-in to good
design. Leaving the helper optional fails in two ways. Most tools need some truncation, so an opt-in helper guarantees uneven coverage: 
 authors who do not know the helper exists roll their own, each with a slightly different notice; 
 authors who never imagined a huge result roll nothing. 
 Truncating inside the tool implementation, rather than at the conversation-rendering layer, breaks
Code mode: 
 the agent can never rely on a tool's output inside Eval ; every use has to parse harness notices
out of the data first; 
 the Eval result may itself be truncated, so each invocation stacks N+1 independent truncation
layers around the same data. 
 Bound blocking time once Backgrounding anything , and capping how long a call may block, belong to the library layer as
well—not to each tool that happens to run long. The first reason is caching and UX. An unexpectedly long call otherwise leaves the agent unable to
notice and adjust, the user returning to a stuck session, autonomous jobs waiting forever, and the
provider's KV cache expiring before the call returns. The second reason, which omp got wrong too, is duplication. When every tool grows its own
backgrounding, every tool also grows its own spawn, poll, message, kill, and list helpers. Take
this diagram Claude drew around its own Task and Bash tools: Background Bash Interface Subagent Bash run_in_background: true Spawn Task prompt, subagent_type BashOutput poll by bash_id Stream out system-reminder async agent notification stdin no tool exposed Message in SendMessage agent_id, message KillShell shell_id Stop interrupt cancel_queued: true exit code + tail final BashOutput Result tool_result Task result block /bashes running shells List ListAgents running agents claude's map of its own tools Both converge on the interface of a process: signal + stream in + stream out . A backgrounded
shell, a subagent, a dev-server daemon, a remote function, and an ordinary call that ran past its
budget are all the same object—a job with stdin, stdout, an exit status, and a signal handle. One
stdio-shaped job primitive should encapsulate all of them. Then the blocking budget is enforced in
one place, output spills to one artifact path, and inspecting, messaging, or killing any of them is
one surface instead of a per-tool copy. Observability expectations converge the same way. Users who want to see subagent state also want
to see backgrounded shells. Agents that message peers across harness instances also want to see
the daemons those peers run, so that N agents in one directory share a single HMR bun dev 
instead of launching N copies on N ports. Cancellation requires a kill boundary Extensions—and therefore custom tools—sharing the engine's JavaScript isolate leads to disaster.
Proper hot reload becomes nearly impossible, and a tool call cannot be forcibly stopped once it has
escaped cooperative cancellation. JavaScript and Go expose cancellation through AbortSignal and context.Context : useful protocols,
but not enforced ones. Forget to pass the signal, call a dependency that does not accept it, run
synchronous work, or enter an infinite retry loop, and a timeout only tells the agent to continue;
the work itself may keep burning resources in the background. A safe host therefore needs an execution unit it can actually terminate—a process, worker,
subinterpreter, VM request, or equivalent boundary whose death cannot take session authority with
it. Cancellation belongs to the runtime contract, not to every tool author's good behavior. Make the mandatory boundary pleasant A deliberately dumb sandbox stub creates one final SDK problem: extension authors now see two
filesystems. A custom edit function might otherwise have to read a file on one side, transfer it in
full, and write it back on the other. This is why omp² chose Python for extensions. Python can inspect its own AST using the standard
library, package the source needed by a function, and submit it to another runtime; a @remote 
attribute can turn a local-looking function into an RPC. It is the same property that makes remote
functions feel natural in systems such as Modal's Python SDK. Bringing the Python runtime also makes Eval dependable rather than contingent on whichever
interpreter happens to be installed. Two birds with one stone. Once work has a trusted owner and a cancellable execution primitive, the harness still needs a
coherent way to control values and multi-turn behavior. That is the control plane. The control plane The runtime owns two different kinds of control. Values answer which model, tier, theme, or
policy is active. Behaviors answer whether the agent may yield, must take another turn, or
temporarily needs a capability. Both become incoherent when every caller owns a private setter or
flag. Values: declare policy with the setting Scope, persistence, inheritance, and replication belong in each setting's declaration—not in setter call sites. The configuration system also became a minefield, with dirty tracking and several levels of
configuration (global, session-level, ephemeral...). Most get/set operations were routed through
the AgentSession type, as they were in Pi, because changes have to be persisted to the JSONL. Do you know what configuration system solved all of these problems years ago? Yes, Source Engine! What's especially remarkable is that most people who have touched a Valve game know what sv_cheats 
does off the top of their head. Despite all these years of people customizing their setup, I can't
recall a single unhappy user. Can you remember any other configuration of any other software? A convar is a typed variable with a name, a
default, a help string, and a bitfield of flags , declared once, at the definition site: ConVar sv_gravity ( "sv_gravity" , "800" , FCVAR_REPLICATED | FCVAR_NOTIFY , "World gravity." ); Persistence, ownership, scope, replication, even replay-honesty: all properties of the variable ,
stated where it is born. Nobody routes a set through a god object, nobody hand-rolls dirty
tracking. FLAGS, NOT PLUMBING ConVar("sv_gravity", "800", REPLICATED | NOTIFY , "World gravity.") SERVER (one authority) sv_cheats 0 sv_gravity 800 mp_friendlyfire 0 sv_password ••• REPLICATED NOTIFY REPLICATED NOTIFY REPLICATED PROTECTED CLIENT (every player) sv_cheats 0 sv_gravity 800 cl_interp 0.031 r_drawothermodels 1 name "can" read-only read-only ARCHIVE CHEAT USERINFO locked unless sv_cheats = 1 REPLICATED forced onto every client USERINFO · sent up .dem every change stamped into the demo, replay stays honest config.cfg ARCHIVE vars written to disk, everything else is ephemeral NOTIFY = change announced to every player       PROTECTED = value never leaves the server set() through a god object + dirty tracking   ->   flags where the variable is born one store. flags decide the rest. One authoritative server store, mirrored to every client. REPLICATED pushes values down, USERINFO sends client-owned vars up, CHEAT locks vars behind sv_cheats , ARCHIVE decides what reaches config.cfg — and every change is stamped into the .dem . A convar is not a second settings database beside the session DOM. A session-scoped convar is one
more journaled node in the authoritative tree; its flags declare how it participates in resume,
rewind, spawn, replication, and archival. Inheritance should not require a second setting Today in omp, service tier (i.e. /fast ) has a separate setting just for the subagent. tier : 
 openai : priority 
 subagent : inherit # separate setting In convar land, ai_fastmode is one variable, flagged SESSION : journaled with the session, so
resuming restores the value. Inheritance needs no flag at all: a spawned child seeds every 
variable from the parent's live values, by default. There is nothing to opt into. Want children pinned instead? One line: # subagent.cfg — auto-exec'd for every spawn 
 ai_fastmode 0 

 # sonic.cfg — auto-exec'd when a sonic spawns, class config 
 ai_model @smol 
 ai_thinking low config.cfg for the main session, any number of user cfgs as profiles, subagent.cfg auto-exec'd
on every spawn, <agent>.cfg layered on top, also solving the god object with a thousand
properties. TF2 knew the way to go! One value now describes the main session and its children. The inheritance rule lives where the
value is defined instead of becoming another property on a growing session god object. Profiles and keybindings stay in-band And once cfgs exist, binds make it even better — bind , toggle , and alias are console commands
too, so every input pattern we keep inventing schemas for stays in-band. User wants a keybind to
hide thinking? bind ctrl+t "cl_showthinking 0" # careful — one-way; the second press still writes 0 
 bind ctrl+t "toggle cl_showthinking" # there we go; toggle also cycles value lists 

 alias +thinkhud "cl_showthinking 1" # fires on key-down... 
 alias -thinkhud "cl_showthinking 0" # ...and on key-up 
 bind ctrl+h +thinkhud # hold to peek at the thinking stream That's what our keybinding layer should be: not a bespoke schema with its own defaults table! The command stream is the connective tissue: cfg files, console input, aliases, binds, remote
administration, and journal replay all speak the same language over the same declared variables.
Customization stops multiplying one-off schemas. Behaviors: the loop-shaped hole Anything that can keep control across turns belongs in one composable, agent-owned Director primitive. Another topic of concern is extensibility. Now I'd argue Pi actually has a great extension layer,
but it does have a "loop" shaped hole. Now I went ahead and installed the most popular Plan and Goal implementations in Pi. Trying to
activate both gives you: Okay! That's interesting, but there's no "workflow" API. How would that work? The implementations
define their own: export const WORKFLOW_MUTEX_CHANNEL = "workflow:mutex:v1" ; 
 export const AGENT_WORKFLOW_GROUP = "agent-workflow" ; 

 export class WorkflowMutex { 
 private session : object | undefined ; 
 private readonly heldGroups = new Map < string , WorkflowMutexOwner >(); 
 private generation = 0 ; 
 private readonly pi : Pick < ExtensionAPI , "events" >; 

 constructor ( pi : Pick < ExtensionAPI , "events" >) { 
 this . pi = pi ; 
 pi . events . on ( WORKFLOW_MUTEX_CHANNEL , ( payload ) => { 
 this . answer ( payload ); 
 }); 
 } Aha! Both implementations came from the same author, who had faced this problem and built a
solution that works across that plugin suite. The complexity of introducing a system to encapsulate this behavior was passed down to the plugin
authors, who can only build a system that works among their own extensions. omp has a similar problem: // modes/interactive-mode.ts — the exclusivity "system", in its entirety 
 if ( this . goalModeEnabled || this . goalModePaused ) { this . showWarning ( "Exit goal mode first." ); return ; } 
 if ( this . vibeModeEnabled ) { this . showWarning ( "Exit vibe mode first." ); return ; } 
 // …restated by hand at six other entry points The missing abstraction becomes visible as soon as independently written behaviors meet. A private
mutex can keep one author's Plan and Goal plugins from colliding, but it cannot make arbitrary
extensions compose. omp's hand-written mode checks have the same limitation. Two decisions follow: name the loop-owning primitive—a Director —and move more built-in behavior
onto the public extension surface so holes in that surface become impossible to ignore. Directors own candidate yields The agent has a loop. Things increasingly want to direct that loop: plan wants another turn until a
plan exists, goal wants another turn until the goal is complete, /force wants to alter the next
inference, the todo reminder wants one last chance to object before we yield. So give the agent layer one object which owns that decision: a stack of Directors. By "stack" we mean one live subtree in the session DOM, not a Python array that we promise to
serialize later. The DOM is the authority; the runtime only walks it. candidate yield flows this way ────────────────────────────────┐ 
 ▼ 
 Base → TodoReminder → Goal → Plan → ForceTool(write) 
 parent child/top The loop stays very boring: while True : 
 request = directors. prepare_inference (base_request) # outside → inside 
 turn = await inference (request) 
 await execute_tools (turn) 

 if turn.has_tool_calls: 
 continue 

 decision = await directors. on_yield (turn) # inside → outside 
 match decision: 
 case Continue (): continue 
 case Yield (): return prepare_inference walks the stack from the outside in, so the innermost behavior may refine the
request its parent was about to make. on_yield walks back out. Each Director may: 
 Pass — let the next Director inspect the candidate yield. 
 Continue — consume the yield and run another turn. 
 Yield — consume it and actually yield to the user. 
 Push — put a child Director on top of itself. 
 Done — pop itself, then offer the same candidate yield to its parent. 
 Fail — pop with an error. 
 Consequently, rewind removes Directors, resume restores them, and a remote inspector can see which
behavior currently owns the candidate yield. Plan mode, completely Say plan mode is active and the model tries to yield without writing the plan file. Plan sees that
candidate yield before any outer behavior does: class Plan ( Director ): 
 async def on_yield ( self , agent , turn ): 
 if not turn. wrote ( self .plan_file): 
 return agent. force_tool ( 
 "write" , 
 until = lambda turn : turn. wrote ( self .plan_file), 
 reminder = "Write the plan file before yielding." , 
 retries = 3 , 
 ) 

 if not turn. called ( "ask" ) and not turn. proposed_plan (): 
 return agent. force_tool ( 
 "required" , 
 until = lambda turn : turn. called ( "ask" ) or turn. proposed_plan (), 
 reminder = "Propose the plan, or ask the user what is missing." , 
 retries = 3 , 
 ) 

 return Yield () Now force_tool("write") , in its soft mode, pushes a small built-in Director that contributes the capability to the next inference request: class ForceTool ( Director ): 
 def prepare_inference ( self , request ): 
 return request. with_tool_choice ( self .tool) 

 async def on_yield ( self , agent , turn ): 
 if self . until (turn): 
 return Done () # pop; offer the yield back to Plan 
 if self .retries_left: 
 return Continue ( self .reminder) 
 return Fail ( "tool requirement exhausted" ) Plan already has another Director below it on the stack: Base → TodoReminder → Plan A candidate yield reaches Plan first. While Plan is active, Plan either continues, pushes a child,
or yields directly to the user. It does not Pass , so the outer TodoReminder never sees that yield. Extensions use the exact same interface: await agent. direct ( VerifyBeforeYield ( ... )) < directors > 
 < todo-reminder id = "d1" > 
 < plan id = "d2" plan-file = "local://auth-plan.md" > 
 < force-tool id = "d3" tool = "write" attempts = "1" max-attempts = "3" /> 
 </ plan > 
 </ todo-reminder > 
 </ directors > This is a full composition rather than another special mode. Plan owns the yield, temporarily pushes
ForceTool, receives the same candidate yield back when the child is done, and either continues or
returns it to the user. Hooks, Directors, and inference 
 A hook observes or edits one inference or turn. 
 A Director can keep control across turns and intercept yielding. 
 Directors meaningfully stack, nest, finish, and resume their parent. 
 That is enough for plan, goal, vibe, autoresearch, reminders, and external verification behaviors to
use the same agent-layer primitive—without teaching each one the private flags of every other one. ForceTool expresses a semantic request: “the next successful turn must call write .” It does not
know whether the selected provider has native tool_choice , whether forcing destroys a cache, or
whether a local model needs an extra prompt. That translation belongs to the inference layer. The control plane can now say what should happen. The next chapter makes that request mean the same
thing across incompatible models and providers. The inference Model compatibility is structured knowledge with explicit precedence—not provider-name branches scattered through code. The control plane asks for semantic behavior: stream this model, force that capability, enforce this
shape, count these tokens. The inference layer has to translate those requests into whatever this
exact model, on this exact host, through this exact API can actually do. What omp taught us: quirks become architecture This one is easy to explain because there's already a before/after commit on omp v1. Before dd57045396 , OpenAI compatibility lived in one 880-line file centered on a giant builder. Open it and you were greeted with this: const isCerebras = modelMatchesHost ( hostModel , "cerebras" ); 
 const isZai = modelMatchesHost ( hostModel , "zai" ); 
 const isKimiModel = isKimiModelId ( spec . id ); 
 const isMoonshotKimi = isKimiModel && isMoonshotNative ; 
 const isAnthropicModel = 
 modelMatchesHost ( hostModel , "anthropic" ) || 
 isClaudeModelId ( spec . id ) || 
 isAnthropicNamespacedModelId ( spec . id ); 
 // …then DeepSeek, Qwen, MiMo, Grok, Mistral, OpenCode, local servers Then those booleans feed other booleans, several nested ternaries, and finally one giant compat 
object. Is Kimi allowed to force a tool while thinking? Depends which Kimi, on which host, through
which API. Does this loopback URL mean llama.cpp, or LiteLLM proxying something else? Better add
another carve-out. There is nothing wrong with any individual branch! Each one fixed a real provider bug. The problem
is that the same knowledge ended up encoded in several places: 
 compat/openai.ts : 880 lines 
 model-thinking.ts : 977 lines 
 variant-collapse.ts : 1,776 lines 
 separate Bedrock, Anthropic, and Devin compatibility builders 
 more name detection in discovery and provider serializers 
 What replaced them? taxonomy/ "what model is this string?" 
 classes/ "what is true of this model lineage?" 
 providers/ "what does this host change?" So Anthropic thinking now reads like this: class "anthropic" { 
 on "anthropic" "amazon-bedrock" "google-vertex" { 
 family "sonnet" { 
 revision ">=3.7 <4.6" { thinking-mode "budget" } 
 } 
 revision ">=4.7" { 
 thinking-mode "anthropic-adaptive" 
 } 
 } 
 } That's the actual knowledge we were trying to express! Sonnet revisions before 4.6 use budget
thinking; Anthropic 4.7+ uses adaptive thinking; only claim this on hosts where we checked it. KDL itself is not magic. The compiler is what saved us from rebuilding the mess in a prettier
format: 
 Unknown directive or value? Error. 
 Two equally specific rules setting the same thing? Error — file order does not secretly win. 
 No matching rule? Unknown, not "false". 
 Did this make providers less weird? Of course not. We still have compatibility axes named
 requires-mistral-tool-ids , qwen-preserve-thinking , strip-deepseek-special-tokens , and ten
ways to spell "turn reasoning off". Look at the names and weep. What it saved us from was expressing the next quirk as another branch in four different functions.
Now it's one rule, in the place that owns the fact, with a compiler yelling if its precedence is
ambiguous — and the inference layer can finally answer: what does this exact model, on this exact
host, actually support? The win is not fewer quirks. It is one owner for each fact, explicit precedence, and an unknown 
state when the library has not established an answer. The rest of the harness stops rediscovering
model identity through provider-name branches. A provider is more than stream This was almost guaranteed to come back and haunt me the second I implemented my Pi plugin for
web-search. In fact, the same pressure hit the minimalist origins of the repository too, as you can see
with Pi's new image
models 
implementation. Pi models providers as stream and streamSimple and that's more or less it! Great for standing up a
provider quickly, however not great for building more and more on top of it because: 
 What about Anthropic's token-counting interface? 
 or, Codex's WebRTC voice endpoint & remote compaction? 
 or, Anthropic/OpenAI web-search? 
 or, embeddings? 
 or, image/video generation? 
 or, tokenization? 
 or, usage query? 
 or, model discovery? 
 Do you think every extension that does one of these also implements synchronized OAuth refresh
and retries correctly? Beyond that, having access to the bleeding-edge controls that the inference provider supports is a
major win, some examples: 
 Constrained sampling 
 Text verbosity options for OpenAI 
 Google's context filter options 
 Forced tool calls 
 Developer role 
 Mid-session system prompts 
 ... 
 Authentication refresh, retries, token counting, search, generation, discovery, and provider-native
controls are shared infrastructure. Leaving them to extensions guarantees several partial
implementations of the same protocol. Capability policy: forced tool calls A forced tool call shows why “supporting a flag” is not enough: 
 Error on unsupported providers: no harness-native feature can use it without excluding a large
part of the model roster. 
 Silently drop it: callers receive an unexpected best-effort path and have to invent their own
enforcement loop. 
 Pass it through blindly: provider side effects become product bugs; Anthropic, for example,
can turn the forced call into a cache miss over the conversation. 
 Do not expose it: informed callers hack around the library and recreate all three failure modes. 
 An ideal harness implementation: 
 Always inject a soft prompt telling the model that it must invoke the tool on its next turn.
This is worth doing unconditionally: hosted APIs like OpenAI quietly prepend this nudge for you,
but open-source inference engines don't, so a model behind vLLM gets a hard constraint it was
never told about, and flails when reasoning is enabled. The soft prompt levels that field. 
 Set the native flag only when it's free. If the provider supports forced tool calls without
side effects, pass it through. If it carries a penalty, skip the flag and rely on the soft prompt
alone. 
 Escalate on non-compliance. If the model doesn't call the tool, retry a bounded number of
times; as a last resort, set the native flag even where it costs something. Correctness wins over
the cache once persuasion has failed. 
 No Yes, side-effect free Yes, but costly (e.g. Anthropic cache miss) Yes No Yes No Extension requests forced tool call Inject soft prompt: "you must call tool X next turn" Provider supports native forcing? Run turn with soft prompt only Set native tool_choice flag Run turn Model called the tool? Done Retries left? Retry — escalate: set flag despite drawbacks Surface failure to caller The forced call starts as a soft prompt; the native flag goes on only when the provider supports it without side effects, and if the model still doesn't call the tool, bounded retries escalate to setting the flag despite its cost before surfacing failure to the caller. This is the provider-side implementation of the Director from the previous chapter. ForceTool 
states the invariant; inference chooses the cheapest honest way to satisfy it and escalates when the
model does not comply. Tool schemas are model-facing protocols A tool's parameters field strictly defines its argument shape. That would be ideal for a human API;
models are not generic API clients. Their mistakes are often specific to the tool name and the
harnesses represented in training. RL-maxxed agents may call a familiar tool using another harness's schema. Composer models sometimes
emit Grep with their expected shape even when no Grep tool exists. Codex may see
 paths: string[] and send one string delimited by ; or , , according to the mood of the day. The library should therefore validate and correct. Be strict about the tool's semantic contract,
but charitable about the model's dialect: repair paths: "a,b" into a list when the mapping is
unambiguous; otherwise return a structured, retryable error. A raw JSON Schema validator cannot own
this layer by itself. Strict sampling needs budgets and dialects Constrained sampling was one of the first features we added to Pi: + strict?: boolean; 
 + customFormat?: { syntax: "lark" | "regex"; definition: string }; 
 + customWireName?: string; Pi followed a few months later with LARK and strict support, but exposed it as an opaque structure
for the provider layer to pass through. Two system-wide constraints make that insufficient: 
 Strict-schema capacity is a shared budget. Many providers cap the number of strict schemas.
Enough independently authored extensions can therefore make the provider reject every request.
The user should not have to binary-search and patch plugins to recover the harness. 
 Grammar dialect is provider-specific. Passing a LARK grammar to every provider can itself be
invalid. An extension cannot maintain the compatibility map because users may route the same
model through native hosts, proxies, or custom providers. 
 That is why the apparently “complicated” implementation belongs in the inference layer: No Yes No Yes, and priority wins Yes No Extension declares tool as strict Provider supports grammar enforcement? Ship JSON Schema only; unconstrained sampling + charitable client-side repair Budget remaining? Normalize schema per provider dialect Inject grammar constraint on the wire Run turn Output valid? Done Repair client-side, surface structured error to model Model retries with correction signal What honoring strict actually takes: provider capability, a strict-schema budget with priorities, per-dialect normalization, and a client-side repair path—none of which an opaque pass-through struct can provide. The extension declares intent—strictness, grammar, priority. The inference layer owns capability,
budgets, dialect normalization, fallback, repair, and the final wire format. Corrective inference Inference libraries also need to: 
 repair malformed JSON; 
 detect repetition loops in models such as Gemini and DeepSeek; 
 parse each model's output dialect and synthesize canonical tool_call and think blocks when
structured output leaks into text. 
 A leaked tool call rendered as prose because the dialect was not parsed into a tool_call block. You can read my prior post about the
tool-calling side of this subject. Supporting a provider or model requires handling its individual
quirks alongside wiring up a URL. A provider adapter is not complete when it can open a stream. It is complete when the rest of the
harness receives one canonical turn despite malformed JSON, repetition, leaked reasoning, or a
model-specific tool-call dialect. Compaction is scheduled, not triggered Start the summary before the limit, from a journal snapshot; at the limit, commit it only if the snapshot still describes the branch. The naive design turns out to also offers the worst UX here.The user waits for the largest request of the session at the exact moment they are most invested. Beyond using methods like Snapcompact there is still a lot of room for improvement here. Even the frontier lab ships the naive design. What one should do instead is, speculatively kick-off the compaction process ~10% before the limit is reached. You essentially make the conversation branch into
two concurrent versions, one where the user, and the model, continue working; the other where the model is compacting the conversation. See the layer icon showing when the speculative compaction triggers? Once you receive the response, you then splice it inside the other branch, which also lets you preserve the momentum of the work as the model will not get confused by a handoff
message standing as the only message in the history, but instead, will see all the progress it should have done anyway. Beyond the prompt, other methods worth considering include: 
 Remote compaction : The provider doing it server-side. OpenAI's API returns an opaque state
blob as a result, but since it has access to decrypted thinking, it can significantly improve the loss of context. 
 Handoff : Instead of asking for a summary, try asking the model to "handoff" the work instead. 
 Shake : Completely local, you can simply trim the heavy tool results from the history. 
 Note that this is also something you should consider in your UI rendering vs. request rendering abstraction, as the user would expect all messages to remain as they are when looking at the history, but for the
model, none of those messages will exist; hence you should model each entry in the prompt history as a "fold" when creating the request fn(this, req) -> req , handling it within the <Handoff> implementation of it. Use small local models for harness work Tiny local models are super useful! Even if you really only work with the frontier models, I
recommend you implement some embedded tiny model (esp. check out LiquidAI models) as this will
save you a lot of latency+money for classification tasks, as well as small tasks like generating a
title, translation, or judging how happy the user is with the way the conversation is going.
Another use case of course is TTS/STT where you can already get SoTA performance locally. This is not a second “agent.” It is a cheap internal capability for small tasks that should not
pay frontier latency or cost. Once compatibility and repair are centralized, the permanent tool surface can stay small. The next
chapter is about what deserves a schema on every request—and what emphatically does not. The tool surface Every permanent tool taxes every turn; keep the roster small and make its primitives deep. The runtime chapter defined how work executes. The inference chapter defined how schemas survive
models and providers. We can finally ask the product question: which operations deserve to occupy
the model's permanent grammar? Every schema has a tax The best way to present most tools to the model is to not put them in the permanent tool roster at all . A while back, I got a complaint about how omp was slower than codex on the same task, not token
wise, but when you measure wall-clock. I fully expected this to be a nothing-burger, but to my
surprise, it was true, almost two times even! MEDIAN WALL, SECONDS (sol:med) PREFIX, K TOKENS 0 s 20 s 40 s 60 s 80 s omp · stock, no fixes 23 defs · 12–16 turns 86.2 s 25.1k tok omp · todo-batched 23 defs, r9 · 6–8 turns 59.5 s 25.1k tok ↓ −26.7s · todo-batching fix omp · /xdev default 15 defs, r11 · 6–8 turns 45.4 s 20.6k tok ↓ −14.1s · 23→15 wire defs omp · lean floor 5 tools, r11 · 4–6 turns 36.6 s 15.1k tok ↓ −8.8s · essential-5 only codex-cli 0.144 (reference) 3 tools · 4 turns 42.2 s 9.6–12.3k tok pi (reference) ~5 tiny-schema tools · 6 turns 37.0 s 5.6k tok Median wall (thick bar, seconds) and request prefix (thin bar, k tokens) per variant · task sol , median of 6 runs, fresh session each · cyan = omp variants, grey = external references · annotations are deltas vs the row above. The culprit was the tool roster. Limit it to five essential tools and you get 36.6s , ahead of Codex's
 42.2s and Pi's 37.0s . Why? Tool grammar! Even if it's just a text description to the model, it
is something that actively contributes to token generation with most frontier model providers, as it
affects the token generation process, driving them to always give you valid JSON (on top of the
tokens used to describe it). A tool is not some free win, just in case the model needs it; this is the idea about dynamic tool
discovery. But this dynamic approach comes with a cache invalidation as soon as you change the tool
roster, which is why we aren't a big fan of it. Pi got one part right, and we always agreed with it: MCPs are horribly designed and do not belong
in the permanent tool layer. So how do we satisfy both the user who wants a Figma MCP and the
inference constraints? Dynamic tool discovery avoids the permanent grammar cost but invalidates the cache whenever the
roster changes. The better target is a stable, tiny grammar with a long tail reachable through
ordinary composition. Put the long tail behind stable surfaces Meet the dyn CLI! This is not a real CLI of course, but a builtin exposed by our Bash
implementation, giving the model a stable discovery protocol, and a convenient way to use it through
Bash, or through Eval as a Python function. dyn 
 dyn --q github 
 dyn github/list_prs --state open | jq '.[] | .title' 
 cat query.sql | dyn database/query - --params limit=5 
 dyn image_gen "blueprint of a frog" > result.json Once it finds an interesting tool, just like tool search, it can use --help to get the details: $ dyn github/create_pr --help
dyn github/create_pr <title> [OPTIONS]

Arguments:
 <title>

Options:
 -d, --draft / --no-draft
 -r, --reviewers <TEXT>[,…] (repeatable)
 -p, --pr-meta.priority <INTEGER>
 -m, --pr-meta.notify / --no-pr-meta.notify
 -j, --json <JSON>
 -h, --help
 This is synthesized from the JSON schema of course, which is all you need to generate a nice CLI
mapping already. Large inputs are where this becomes especially nice: dyn database/query "SELECT 1" # literal 
 dyn database/query @query.sql # file contents 
 cat query.sql | dyn database/query - # stdin One edge case to handle: what about image-returning tools? Well, how does omp display images to you?
Sixel or the Kitty protocol, right? Why not parse the same output in the Bash tool and attach the images!
Now you also get to look at remote images through ssh, sweet. There is a second option when all those operations belong to one API: expose a code surface.
Browser keeps open / run / close and runs code against a persistent tab; Computer exposes
 desktop , wait , and assert in a persistent session. One stable schema, operations composed
inside one call. Bounded operation set: schema. Open-ended operation set: code surface. The two forms serve different shapes of API. A bounded operation set can remain a schema; an
open-ended operation set wants a code or command surface where several operations compose inside one
call. Neither requires changing the permanent roster after discovery. Contract hygiene: intent and version One small change to the contract is worth calling out: every tool gets an i intent argument.
It arrives while arguments stream, so renderCall can show what the model thinks it is doing before
the call completes. The journal gets a readable summary too, without every tool inventing
 reason / purpose . People should version their tools . It makes traces much easier to use: you can parse a frequently changed tool's I/O and evaluate its
success rate over time without guessing which contract produced each call. Name, version, intent, input, output, diagnostics, and usage are protocol data. Once traces are used
for evaluation or repair, guessing any of them becomes avoidable technical debt. Deep builtins A small roster only works when its primitives are broad for a semantic reason—not because unrelated
features were dumped into one switch statement. omp's builtins are useful examples. Read: materialize a resource The most boring tool in omp actually packs what would be 20 tools in others. 
 You can read directories, no need for Ls . 
 Instead of an additional ReadNotebook tool, you get nice output by default when you read an
 .ipynb file. 
 .pdf , .docx , .pptx , .xlsx , .epub ? You get extracted markdown. 
 .cpuprofil, .sample.txt ? You guessed it! You get a bottleneck summary. 
 .sqlite , .sqlite3 , .db , .db3 ? You can list tables, inspect schemas, rows, or even query. 
 Images return either the image or metadata without vision. To preview an SVG, add :img . 
 Archives can be addressed without unpacking them—not only ZIP and TAR, but JARs, wheels, and ASAR. 
 The same projections work for an online resource at http://... , with ranges read on demand;
ordinary web pages become markdown, just like web_fetch . 
 This isn't really polymorphism for the sake of being clever. These are all the same operation from
the model's perspective: 
 Materialize this resource into the most useful representation I can reason about. 
 For code, it can also return a structural summary, replacing large declaration bodies with an
ellipsis. The model need not pull an entire large file into context merely to find class X . :raw bypasses the projections when the bytes matter. :conflicts gives one line per unresolved
merge-conflict block instead of making the model hunt through the whole file. Ranges can be open-ended, length-based, or disjoint: :50 
 :50- 
 :50-200 
 :50+150 
 :5-16,960-973 
 :raw:50-100 
 :50-100:raw Then there are the non-web URLs: artifact://<id> 
 agent://<id> 
 history://<id> 
 issue://123 
 pr://123/diff/2 
 skill://react 
 rule://foo 
 memory://... 
 local://... 
 vault://... 
 security://... 
 omp://... 
 xd://browser 
 ssh://host/path 
 mcp://... Repository information, MCP resources, subagent transcripts, skills, memory, local scratchspace,
omp documentation, and even remote machines over SSH all fit the same internal URL subsystem. We
recommend this design. Read also handles less visible recovery: resolving an incorrect absolute path from a unique
workspace suffix, expanding ~ on Windows, and avoiding other turn-wasting path errors. Could this have been: return await Bun . file ( path ). text (); Yes. Extension authors would then implement their own readers, or the model would find shell
workarounds, while the harness exposed similarly shaped functionality under separate names such as
 web_fetch . That is not less complexity. It is the same complexity, copied into shell commands, prompts,
extensions, and failed tool calls, where nobody owns it and everybody implements 30% of it slightly
differently. Read is complicated so reading isn't. The complexity has one owner. The operation stays stable while resource-specific projection moves
behind it. Bash: a policy-aware command language The Bash tool should not simply shell out to Bash. This sounds unhinged. omp ships a complete bash parser, interpreter, as well as a full set of coreutils, in-process; this
has been a good choice for simple reasons: 
 You keep the model's muscle memory. It can reach for grep ; because omp is the interpreter, we
can intercept the command and route suitable arguments to our ripgrep engine. Nobody spends
context begging the model to use rg in AGENTS.md . 
 Platform neutrality comes almost for free. No WSL or Git Bash: omp can execute most Bash
invocations in-process on Windows. Nuff said. 
 The console remains stateful across calls, including variables, exit codes, $! , and so on. 
 The more interesting advantage appears when Claude calls it with something like this: INC = "…/10.0.22621.0" ; declare -A R 
 for d in um shared ucrt ; do while IFS = read -r f ; do b = "${ f ##*/ }" ; R[ "${ b ,,}" ] = " $f " ; done \ 
 < <( find " $INC / $d " -maxdepth 1 -type f -name "*.[hH]") ; done 
 n = 0 
 while IFS = read -r ref ; do case " $ref " in * / * ) continue ;; esac ; r = "${ R [${ ref ,,}] :- }" ; \ 
 [ -n " $r " ] || continue ; rd = "${ r %/* }" ; rn = "${ r ##*/ }" ; \ 
 if [ " $ref " != " $rn " ] && [ ! -e " $rd / $ref " ]; then ln -s " $rn " " $rd / $ref " ; n =$(( n+1 )); fi ; \ 
 done < <( grep -rhoiE "#[[:space:]]*include[[:space:]]*<[^>]+>" " $INC /um" " $INC /shared" " $INC /ucrt" \ 
 | sed -E "s/.*<([^>]+)>.*/\1/" | sort -u) Can you tell me what this is doing within 5 seconds? (If you said yes, you're lying) Whatever your opinion on tool approval, this is horrible: nobody will read it. Anthropic's recent
research points the same way, with auto mode—another Claude reading the command—beating humans by
quite far. When omp interprets the command itself, it can ask at the moment execution reaches ln ; everything
before that is read-only. It can skip even that prompt when the user has already allowed writes to
the directory. This shifts the harness from being the TSA screen of “Bash” to being a capability approver:
“May I use Git to push?” Common commands such as find , cat , and ln run in-process, query the
access model just in time, and inherit the user's existing read/write policy. Because the host interprets common commands, approval can occur at the capability boundary that
matters— git push , a write outside the workspace, a network request—not at the unreadable shell
string boundary. The runtime policy from chapter three becomes enforceable without discarding the
model's shell muscle memory. AutoQA: give agents a bug-report path We added this tool a month into our fork, before Anthropic added an equivalent to theirs. You know how you usually provide a way for users to report their issues with your product somewhere?
This is the equivalent of that, but for the agents. This lets you collect, fully autonomously,
information about what they liked about a tool, what they found confusing, and what they saw act
erroneously. Now the quality of the reports is not quite great , Codex for instance, loves to complain about
external edits to files by blaming the Read or LSP tool when it doesn't rename things
properly ( not my fault man, ask the TypeScript guys ), but, it is very easy to filter them out, and
once you do, you get a tremendous amount of signal about which tool fails and how it can be
improved. AutoQA closes the loop between tool design and deployed behavior. It is noisy, but once obvious
misattributions are filtered, it reveals which operation confuses models, which projection hides
needed data, and which repair belongs in the harness. Tools now have a bounded runtime, a stable discovery surface, and structured state. The user should
not need every tool author—often Claude—to become a terminal rendering and security expert merely to
show that state safely. The interface 267s → 90ms render time, one session 13% of profiled CPU in one .includes 98.7s spent re-wrapping in wrapAnsi 0 images in that session An ANSI-escaped array of strings and render() do not make a good rendering primitive. The session DOM and tool state stream give every client the same facts. They do not, by themselves,
produce a safe, fast, consistent interface. A renderer can still turn those facts into re-parsed
strings, extension-specific styling conventions, and irreversible scrollback bugs. What omp taught us: strings compound This was in fact the topic of one of my first PRs to
 pi-mono . Before the change, if you went ahead and
profiled Pi for the duration of a task, and looked at the CPU usage, the list would be entirely
occupied by, you guessed it, the renderer! Renderer-dominated CPU profile of a Pi session — treemap of self time. String scanning (red) alone burns a fifth of the session. · hover a tile for the code it profiles. Being a TypeScript CLI makes some of this inevitable (the fact that strings are UTF-16 internally alone
means you go through a relatively expensive transcoding step on every single frame, unless you're
passing around Uint8Arrays to represent text like a maniac). But it's the contract itself that makes this expense compound. You want to embed a child component?
Now you have to deal with: 
 Sanitizing said string & discarding or decoding-past ANSI escapes 
 Dealing with padding, truncation, and calculation of every line 
 This also doesn't get any better with the fact that images can be passed, along one of these lines,
as base64 text. The .includes check for whether a line is an image line alone accounted for 20% of
the total CPU cycles spent in a session. That's a steep bill (and this session didn't even have any
images!). This is only the graph of the JS side of the business. The rendering pipeline under this setup is a
heap grooming machine: you keep allocating, decomposing and throwing away strings and arrays of
strings—concatenated, split, truncated, padded, again and again, every single step of the way. Not
gud. The same contract also leaves extensions without a shared design language. If you have used any 
Pi extension, you know there is no way to make them follow a common guideline beyond asking Clawd
to restyle each one—and then maintaining the result. There is no contract for whether or not you should use curved borders, whether or not Nerd Font icons
are OK to use, whether or not it will use the colors you like for conveying the semantics of what it
is doing. You will find that: 
 99% of the time, it will do the bare minimum (i.e. truncate/line-wrap text), and all your tools
will be indistinguishable gray rectangles. 
 1% of the time, it will try so hard to look fancy, that it will look out of context,
when the rest of your setup is minimalist. 
 A community renderer from the Pi catalog shows what this contract does to the
things that reach a user: if ( cq . sources . length > 0 ) { 
 lines . push ( "" ); 
 for ( const s of cq . sources ) { 
 const domain = s . url . replace ( / ^ https ? :\/\/ / , "" ). replace ( / \/ . * $ / , "" ); 
 const title = s . title . length > 50 ? s . title . slice ( 0 , 47 ) + "..." : s . title ; 
 lines . push ( theme . fg ( "muted" , ` \u25b8 ${ title } ` ) + theme . fg ( "dim" , ` \u00b7 ${ domain } ` )); 
 } 
 } 
 lines . push ( "" ); 
 } else { 
 const textContent = result . content . find (( c ) => c . type === "text" )?. text || "" ; 
 const preview = textContent . length > 500 ? textContent . slice ( 0 , 500 ) + "..." : textContent ; 
 for ( const line of preview . split ( " \n " )) lines . push ( theme . fg ( "dim" , line )); 
 } 

 if ( details ?. fetchUrls ?. length ) { 
 if ( details . curated ) { 
 lines . push ( theme . fg ( "muted" , `Fetching ${ details . fetchUrls . length } URLs in background` )); 
 } else { 
 lines . push ( theme . fg ( "muted" , "Fetching:" )); 
 for ( const u of details . fetchUrls . slice ( 0 , 5 )) { 
 const display = u . length > 60 ? u . slice ( 0 , 57 ) + "..." : u ; 
 lines . push ( theme . fg ( "dim" , " " + display )); 
 } 
 if ( details . fetchUrls . length > 5 ) lines . push ( theme . fg ( "dim" , ` ... and ${ details . fetchUrls . length - 5 } more` )); 
 } 
 } There is quite a bit wrong here: 
 It's slicing text by codepoints rather than visible width, so it will break out of its line and
smash everything below it once you resize under 40 columns 
 There is no awareness of the terminal width, so even if you have space, you get an ellipsis! 
 Most importantly, it ignores the first rule of Pi components & does not sanitize external input,
meaning the thing it's fetching can just feed it the right ANSI escapes and replace your entire
UI with a picture of a duck.
 Definitely 
 nothing 
 else 
 can be done with this! 
 This sort of thing is natural when you push the complexity down onto the unsuspecting developer —
often Claude. An LLM is not going to remember every internal detail of your harness each time it is asked to "make
tool UI pls". Hell, I don't really want to either sometimes, and the smoke test will pass as usable. The performance, security, and consistency problems have the same cause: an already-rendered string
is being used as layout tree, style tree, content, transport, and terminal program at once. What omp² changes: a one-pass primitive The lowest-level consumers (i.e. not you, unless you make a PR) push RichText 
 (Style, String) into the abstract pipeline (&mut impl Out) handed to them. This cuts the 267 seconds of render time to 90ms: RENDER ONCE, REPLAY FOREVER before render(): string[] string[] string[]' string[]'' string[]''' parent string[] parse wrap pad concat alloc alloc alloc alloc N components × M transforms — every buffer re-parsed, re-measured, thrown away. Every frame. after push run(style, &str) into a sink markdown latex · syntax decompose(ansi) external text, parsed once .wrap(w) .clip(w,'…') .restyle(f) single pass · no intermediate row buffers Frame diff stdout ANSI written here, once .tee(cache) RichText pool: String runs: [(Style, ..end)] rows: [(run_end, width)] clear() keeps capacity — streaming re-renders allocate nothing replay() next frame, no re-render N + N·M buffers per frame   ->   O(cache) Before: render(): string[] — N components × M transforms, every buffer re-parsed, re-measured, and re-allocated, every frame. After: RichText runs stream through the abstract pipeline in a single pass into the frame diff. The temporaries, the ANSI parsing, the grapheme handling: ENTIRELY GONE from every layer below the
frame renderer, obviously! Why would we pad your component and pass it down when we can just... stream the padding, and then one
of your lines, and repeat? Why would we make you render a 255 line diff in full color and then
 .slice(0, 3) just to truncate that into another array of string buffers when we can just... drop
your stream after the ellipsis, or break it into lines as a part of the transformation ourselves? The low-level primitive owns measurement and transformation once. Higher layers should never parse
ANSI to discover the structure they themselves emitted. A typed component model Next, the string[] will be replaced by a proper component model. The higher-level consumers will
simply stack boxes and enjoy their LSP showing them the way: element inside is flagged: elements are not allowed inside " loading="lazy"> The markup is typed: nesting an element inside <text> is a lint error at edit time, not a mangled frame at run time. Markup in, frame out: <box> , <row> / <col> , an <ico:new/> icon, a horizontal magenta..cyan gradient, and a live-rendered ½ from $$ \frac{1}{2} $$ . Now, I may not like working with the frontend, but damn do I like a good abstraction. (Element, Props, Children) is literally all you need, coupled with a layout engine, to make this wonderful in
comparison. The DOM chapter promised that a tool element could be rendered by any actor. This is the concrete
shape of that promise: This is what the Read component looks like. Not half bad, is it? < box bc = muted > 
 < row kind = title gap = 1 > 
 < text >•</ text > 
 < text bold >Read</ text > 
 < a href = {input.path} >{input.label}</ a > 
 {#if status=error}< badge tone = error >exit {code}</ badge >{/if} 
 </ row > 
 {#if result.head}< pre lang = {result.lang} wrap = word start = {result.start} >{result.head}</ pre >{/if} 
 {#if @expanded} 
 {#if result.blob}< pre lang = {result.lang} numbers start = {result.start} blob = {result.blob} ></ pre >{/if} 
 {/if} 
 {#each diag as d}< callout tone = {d.severity} >{d.msg}</ callout >{/each} 
 {#if result.src} 
 < hr title = "Output" /> 
 < row gap = 1 fg = muted > 
 < text >⟨Resolved path:</ text > 
 < text >{result.src}⟩</ text > 
 </ row > 
 {/if} 
 {@render usage} 
 </ box > The tool author describes structure and semantics. The TUI, web client, snapshot test, and remote
inspector decide how that structure is laid out on their own surface. Presentation policy belongs to the renderer The component model buys two useful properties for free: 
 <ico:new/> gives every plugin a convenient icon while respecting the user's ASCII, Unicode, or
Nerd Font choice. Borders work the same way. 
 Semantic colors no longer require a theme object threaded through every renderer. Claude can ask
for info instead of choosing a literal color and hoping it fits the user's theme. 
 border=round bc="info" resolves to the theme's semantic color; fg="red..blue" is a gradient. No theme object threaded anywhere. You also need to own the pace of the text stream. Claude and Codex emit chunks at very different
cadences—one a few words at a time, the other a few characters. Smoothing those differences changes
how responsive the harness feels: steady motion reads as progress; bursts followed by stalls do not.
Heh. Semantic icons, borders, colors, truncation, and stream pacing now have one owner. Extensions ask for
 info , error , or <ico:new/> ; they do not thread a theme object through every function or choose
a Nerd Font glyph on behalf of every user. Verification is part of the interface In the current "meta", the biggest ROI investment that also costs you nothing is asking the agent
to implement a debug protocol for any kind of interactive TUI / GUI. If "how to verify" is unknown
and unspecified, the agent will side-channel a look-alike, meaning it will create a test file that
doesn't really check anything in most cases. By defining what "verification" means and giving it a convenient shape in advance, you drop the
friction by a considerable amount, which means it becomes an active part of the development loop. The shape is not really important, and can always be updated: it could be a custom tool, a Python
package, or an API, but it's an absolute must to provide a non-destructive, off-screen,
multi-instance thing that prevents the agent from redefining (and usually downgrading) the
definition of success. In other words, the debug protocol becomes the machine-readable definition of what the UI is—not
merely a test helper. The transcript is a protocol The actual impossible part of the TUI is having 0 GH issues about how it's broken. People are
idealistic creatures about what they don't know, and unfortunately many do not know that the perfect
TUI experience they want is impossible (every component fully up to date no matter the location,
dynamically mutated). Blocks We define the canonical transcript as a list of blocks. A block produces rows of text and moves
through a lifecycle: active → finalized → committed While alive, block i shows a current snapshot, W i , which is an array of rows. Upon
finalization, it freezes to an immutable snapshot, F i . Blocks come in two modes: 
 Mutable: each new snapshot may replace the previous one wholesale (spinners, progress).
Snapshots are speculative and never become history; only F i does. 
 Append-only: snapshots only grow: every snapshot is a prefix of the next, and the last
snapshot is a prefix of F i (streaming text). 
 The distinction matters when a block outgrows its viewport allocation. A mutable snapshot cannot
enter history early because a later update might replace it; we would have to yank already-scrolled
rows. An append-only block such as assistant thinking only extends a stable prefix, so that prefix
can begin committing immediately. Terminal A terminal at width W and height H has two buffers: 
 V : the viewport, of H visible rows 
 S : native scrollback, unbounded, append-only 
 Technically, we could clear and write over the scrollback, but this leads to behavior users often
complain about; so it is now an invariant. Wrapping, wrap W , turns logical rows into physical rows and depends on the current
width. There is no addressable area below the viewport. Writing past its bottom scrolls the terminal
and pushes the top rows into S irreversibly. The logical history L is kept in unwrapped rows, so it is width-independent: committed finals, in
block order, each exactly once plus however much of the currently streaming block has already been
let through. With c the last committed block and j = c+1 : L = F 1 · F 2 ⋯ F c · W j [1..e j ] where e j counts the rows the streaming head has already emitted into history
( e j = 0 unless block j is an append-only block mid-stream). Therefore: 
 committed finals occur exactly once, consecutively, in block order; 
 mutable speculative snapshots never enter L ; 
 an append-only head may enter L row by row while still streaming; 
 finalization writes nothing; 
 commitment appends only the rows of F j not yet emitted 
 Resize Resize changes nothing logical: every W i , every F i , and c survive
unchanged. Only wrapping and viewport allocation are recomputed. Rows already in native scrollback
cannot be rewritten, so resize needs one explicit policy for them: 
 Preserve: keep the emulator-wrapped history as-is. 
 Append: append a re-rendered history, possibly duplicating physical rows. 
 Rebuild: start a new physical epoch and replay history into it. 
 These rules separate three things that are easy to conflate: mutable presentation in the viewport,
width-independent logical history, and irreversible native terminal rows. Once they are named,
resize and streaming become policy choices instead of folklore. Specify the impossible part Now why did I put you through all this "math"? Because this is a very complicated algorithm to
verify the sanity of; in the previous iteration, we had to write a fuzzer to get to a stable point,
and this time I'd like to avoid that. Instead, we modeled the behavior in TLA+ as described, and asked for iterative changes to how the
commit and finalization of these blocks are handled until the clearly specified invariants were all
met. Now, if we do want to make a change, say, yolo commit partials, or not allow block truncation, we
have a reference to update and an extremely easy way to know whether or not it will work, with a
counterexample presented on failure. The paper and the full ElasticSlots.tla source live in Appendix B . What this unlocks Obligatory flex, and we can move on! Now if someone complains about how TUI is broken, I can give
them a formal proof of why it cannot be fixed, great. The omp² TUI mid-task: command palette over live parallel shards, session rail with per-file diff stats, and an inline image thumbnail — every element a component on the same streaming pipeline. The TUI, web client, and remote inspector can differ in layout without differing in truth. Tool
authors describe semantic state; the component system owns presentation; the transcript protocol
owns exactly-once history. That is the same design move repeated again: push the hard invariant down into the layer that can
enforce it. The implementation stack should reinforce those invariants rather than invite every
contributor—and every coding agent—to invent a local style. The stack Choose languages whose constraints steer agents toward the codebase you want to maintain. The previous chapters are architecture. Language choice decides how much friction the codebase puts
between that architecture and the next “helpful” local exception. This matters more when a large
share of the implementation is produced by agents trained on the defaults and pathologies of each
ecosystem. Language choice is architecture TypeScript is an awful choice at the moment unless you have no choice but to interact with
frontend code. One of the most impactful decisions you can make when starting a project right now is: picking the
right tool. Now if I saw an article starting like this 3 years back, I'd have started ranting,
but... If you don't believe me, try giving Claude the exact same prompt describing a widget you want
to build. Now swap macOS (Swift) -> Linux (Qt/JS). The former will get you a glassmorphic widget that looks
like it belongs with the OS, the latter will get you a rectangle with overlapping UI elements and
questionable UX choices, making you feel like you just finished reading up on the XML schema
required to define a UI and this is your first time compiling it. Now sure, the way you prompted plays a role here, and you could indeed have gone into more detail,
but after a while you will notice that no matter what you do, one will outperform the other almost
effortlessly. One thing macOS historically did well is forcing developers into one consistent design
style, and it goes just the same with LLMs. The point is not that Swift contains taste and JavaScript does not. It is that defaults, standard
libraries, canonical project shapes, compiler feedback, and ecosystem conventions act as a prior
for generated code. A language that permits twenty equally normal local styles asks the model to
make twenty decisions before it reaches the product problem. TypeScript becomes your language The one thing I loved about TypeScript, unfortunately, was that it always ended up becoming
 your language: 
 to camelCase or snake_case ? or perhaps just name your lib $ 
 to write generics that span 200 lines, or to not even have a single one? 
 to use Buffer or Uint8Array ? 
 to use Zod or Typebox? 
 to use Array<T> or T[] ? 
 to use ESM or CJS? (wb the extension? .ejs, .cjs, .mjs, .js? ) 
 to use TypeScript or JSDoc? 
 to use Class, or to stay with objects (or hell, new function())? 
 to export as default or not? 
 to use star re-exports, or name each? 
 to use private foo or #foo ? 
 to use module/index.ts or module.ts ? 
 to use const x = () => .. or function x() { ? 
 to use function x(args) or function x(...args) ? 
 if latter, to use ...args: any[] or ...args: unknown[] ? 
 to use const X = 1 , enum E { X = 1 } , or const enum E { X = 1 } ? 
 Now see, having spent 10 years of my life with the biggest write-only language aka C++, I do find
joy in this. However, when forced to choose between Zod and Typebox, your junior friend will just
roll what we call an isRecord . Why use generics when you can just union the types? Why make sure
every branch works for both of the types mentally, when you can specialize with a little typeof? Why
use classes, it's just objects and prototypes, no? It could be the sheer amount of bad JS code out there, or it could be the fact that they probably
swallowed a pile of minified code along the way, but I am tired of it. Considering the same junior
can find Linux 0-days, if I were you, I'd stop hoping for the right model or the right
code-quality tool and stop jumping through hoops. Perhaps EffectJS will change that, IMO Go will be the winner here at the end of the day (esp. when GC proposal for WASM finalizes) for
similar reasons to why Swift wins at design (especially with compilation speed and the ease of
cross-compilation), although some cases demand a lower-level systems language, so we chose Rust here. They still have to be steered quite frequently, taking the shortest path to the goal; allocating copies over dealing with intricate borrows,
passing errors as strings instead of using thiserror , but they have most of what's necessary for them to work in the std coupled with
the serde ecosystem, and the compiler provides a decent amount of safety, so that was that. Python for extensions The next decision was whether to invite TS back for extensibility. We said no, mainly because: 
 Agents output decent Py => Decent extensions, by extension 
 A spec-compliant JS runtime is basically impossible in a small footprint (thank you, Locale) &
without the ecosystem, we might as well run Lua 
 Extensions don't even make up 1% of the run time, so we don't really need JIT 
 With a full Py runtime embedded we can also guarantee the eval tool works out of the box,
instead of asking the user to install py3 and never being able to rely on it in the
flows we ship. 
 Python code can inspect its own AST out of the box. This is what makes the runtime chapter's @remote design possible. 
 The runtime chapter introduced the @remote boundary. Python's introspection and attribute model are
what make that boundary ergonomic: the SDK can inspect a function, package the relevant source, and
execute it in the sandbox runtime without asking every extension author to hand-write an RPC. Bringing the runtime also makes Eval a dependable builtin rather than a feature that works only
when the user happened to install a compatible Python. Closing notes An agent harness is systems software—not a while loop around a fetch. “But why?” was the opening question. The direct answer is that every chapter above is a category of
software with decades of prior art: replication, sandboxing, configuration, scheduling, protocol
compatibility, real-time rendering, and language/runtime design. omp² is still being built against this document in states ranging from shipped to still being thought
through; but we sincerely thank each and every one of you for giving it a try and sharing with us
all kinds of awesome ways you tried to use omp, from making it operate a software factory,
to asking it to build itself a camera app on the very same phone. View this post on X You have shaped omp and we expect nothing less interesting from the future! Appendix A: state failures in the official examples The state chapter summarizes these failures by category. This appendix keeps the original evidence:
source links, minimal code excerpts, and reproduction videos. The claim was not theoretical. We looked at 78 official extension examples: 60 were stateless;
among the 17 with state, only two were correct. 1. The checkpoint is cleared before /fork can use it: git-checkpoint.ts source :
missing durable checkpoint ownership; /fork is invoked while idle, after agent_settled has
already emptied the only map of stash refs. const checkpoints = new Map < string , string >(); 
 // … 
 pi . on ( "agent_settled" , async () => { 
 checkpoints . clear (); 
 }); 2. Tree navigation does not restore state: plan-mode/index.ts source :
missing session_tree and getBranch() ; rewinding leaves plan mode and its tool restrictions
active, while resume can resurrect a dead branch's snapshot. const entries = ctx . sessionManager . getEntries (); 
 const planModeEntry = entries 
 . filter (( e ) => e . type === "custom" && e . customType === "plan-mode" ) 
 . pop (); 3. The counter cannot count history: status-line.ts source :
missing branch derivation; rewind from turn 3 to turn 1 and the next turn says 4, while resume
starts again at zero. let turnCount = 0 ; 
 // … 
 pi . on ( "turn_start" , async ( _event , ctx ) => { 
 turnCount ++; 4. A dynamically added tool survives rewind, then disappears after resume: dynamic-tools.ts source :
 /add-echo-tool echo_branch writes only to the live extension registry; /tree does not restart
that registry, so rewind keeps the tool, but --continue starts a new registry and the tool
disappears. const registeredToolNames = new Set < string >(); 
 // … 
 registeredToolNames . add ( name ); 
 pi . registerTool ({ 5. A save returns from an abandoned branch: snake.ts source :
restore scans the whole session file; save on branch A, rewind before it, open /snake , and the
dead save returns. const entries = ctx . sessionManager . getEntries (); 
 for ( let i = entries . length - 1 ; i >= 0 ; i --) { 
 const entry = entries [ i ]; 
 if ( entry . type === "custom" && entry . customType === SNAKE_SAVE_TYPE ) { 6. "Last message" means last in the file: bookmark.ts source :
missing getBranch() ; after rewind, /bookmark can label an assistant message on an abandoned
branch the user cannot see. const entries = ctx . sessionManager . getEntries (); 
 for ( let i = entries . length - 1 ; i >= 0 ; i --) { 
 const entry = entries [ i ]; 
 if ( entry . type === "message" && entry . message . role === "assistant" ) { 7. Calculator stays active after rewinding before discovery: kimi-deferred-tools.ts source :
 tool_search activates Calculator , but no session_tree handler derives the active roster again;
after navigating to a point before discovery, Calculator is still active. const active = pi . getActiveTools (); 
 const added = active . includes ( "Calculator" ) ? [] : [ "Calculator" ]; 
 if ( added . length > 0 ) pi . setActiveTools ([... active , ... added ]); 
 // Missing: session_tree → derive active tools from selected branch. 8. Switching sessions commits the worktree: auto-commit-on-exit.ts source :
missing an exit-only boundary; /new , /resume , and /fork fire session_shutdown , which stages
and commits the dirty worktree. pi . on ( "session_shutdown" , async ( _event , ctx ) => { 
 // … 
 await pi . exec ( "git" , [ "add" , "-A" ]); 
 await pi . exec ( "git" , [ "commit" , "-m" , commitMessage ]); 
 }); 9. Live and restored state disagree: tic-tac-toe.ts restore ;
 user
move :
reconstruction accepts only tool results, but user moves are custom entries; crash after X and
before O, and X disappears. if ( entry . type !== "message" ) continue ; 
 if ( msg . role !== "toolResult" ) continue ; 
 // User moves take a different path: 
 pi . appendEntry ( SAVE_TYPE , getBoardDetails ()); Appendix B: Elastic Speculative Slots The interface chapter keeps the protocol and conclusions in the main reading path. This appendix
contains the paper and the complete TLA+ model used to check the transcript invariants. "Elastic Speculative Slots" — the paper: the three-layer contract, the safety theorem, and the conditional progress results, one-to-one with the full spec below. · Click through for the full PDF. ElasticSlots.tla — the full spec ---- MODULE ElasticSlots ---- 
 \* ========================================================================= 
 \* Elastic Speculative Slots: a formally verified rendering protocol for 
 \* streaming concurrent output blocks through a bounded terminal viewport 
 \* into append-only scrollback. 
 \* 
 \* Three decoupled layers, related by invariants (see ELASTIC_SLOTS2.tex): 
 \* 1. semantic block state (phase/mode/want/final/emitted per block) 
 \* 2. logical history ledger (`history`: width-independent, exactly-once) 
 \* 3. physical native rows (`native`: width-rendered, source-tagged) 
 \* ========================================================================= 
 EXTENDS Naturals, Sequences, FiniteSets, TLC 
 \* Naturals: arithmetic; Sequences: <<>>/Len/SubSeq/\o; FiniteSets: 
 \* Cardinality/IsFiniteSet; TLC: model-checking utilities. 

 CONSTANTS N, H, MaxResizes, MaxLive, RowValues, SnapshotValues, 
 NoFinal, Placeholder, Blank, OverflowMarker 
 \* N : number of block identities (blocks are 1..N, in commit order) 
 \* H : maximum viewport (live transcript) height, in rows 
 \* MaxResizes : bound on resize events (keeps the state space finite) 
 \* MaxLive : uncommitted-block count that constitutes "pressure" 
 \* RowValues : finite row alphabet (what a semantic line of output "is") 
 \* SnapshotValues: finite universe of block contents (sequences of rows) 
 \* NoFinal : sentinel "this block has no final snapshot yet" 
 \* Placeholder : synthetic viewport row shown for an empty slot 
 \* Blank : synthetic viewport row for unused screen space 
 \* OverflowMarker: synthetic viewport row summarizing hidden older blocks 

 ASSUME 
 ∧ N ∈ ℕ \ {0} \* at least one block 
 ∧ H ∈ ℕ \ {0} \* viewport can be nonempty 
 ∧ MaxResizes ∈ ℕ \* zero resizes is allowed 
 ∧ MaxLive ∈ ℕ \ {0} \* pressure threshold >= 1 
 ∧ IsFiniteSet(RowValues) \* finite row alphabet 
 ∧ RowValues ≠ {} \* ... and nonempty 
 ∧ IsFiniteSet(SnapshotValues) \* finite snapshot universe 
 ∧ SnapshotValues ⊆ Seq(RowValues) \* snapshots are row sequences 
 ∧ ⟨⟩ ∈ SnapshotValues \* the empty snapshot exists 
 ∧ (∃ snapshot ∈ SnapshotValues : Len(snapshot) = 1) \* a length-1 snapshot exists 
 ∧ (∃ snapshot ∈ SnapshotValues : Len(snapshot) > 1) \* a longer one exists too 
 ∧ NoFinal ∉ SnapshotValues \* sentinel distinct from real data 
 ∧ Placeholder ∉ RowValues \* synthetic rows are not 
 ∧ Blank ∉ RowValues \* ... confusable with 
 ∧ OverflowMarker ∉ RowValues \* ... semantic rows, 
 ∧ Placeholder ≠ Blank \* and are pairwise 
 ∧ Placeholder ≠ OverflowMarker \* distinct from 
 ∧ Blank ≠ OverflowMarker \* each other. 

 Blocks ≜ 1‥N \* the block identities 
 ModelRows ≜ {"row-a", "row-b"} \* tiny concrete row alphabet for TLC 
 ModelSnapshots ≜ \* a richer snapshot universe (unused by the shipped cfg) 
 {⟨⟩, \* empty block 
 ⟨"row-a"⟩, \* one-liner 
 ⟨"row-b"⟩, \* one-liner, other row 
 ⟨"row-a", "row-b"⟩, \* two distinct rows 
 ⟨"row-b", "row-a"⟩, \* order matters 
 ⟨"row-a", "row-b", "row-a"⟩} \* length three, with repeat 
 SmallModelSnapshots ≜ {⟨⟩, ⟨"row-a"⟩, ⟨"row-a", "row-b"⟩} \* the cfg's universe: lengths 0, 1, 2 

 WidthValues ≜ {"Wide", "Narrow"} \* two-point abstraction of terminal width 
 ResizeModes ≜ {"Preserve", "Append", "Rebuild"} \* policy chosen at a width-changing resize 
 ReplayModes ≜ {"None", "Append", "Rebuild"} \* pending replay (None = no replay in flight) 
 BlockModes ≜ {"Undeclared", "Mutable", "AppendOnly"} \* presentation contract, fixed at Create 
 Phases ≜ {"Absent", "Queued", "Active", "Finalized", "Committed"} \* block lifecycle, monotone left-to-right 
 StopReasons ≜ {"Running", "Graceful", "Detach", "WriteFailure"} \* why the host stopped (Running = it hasn't) 
 NativeSources ≜ {"Append", "Retire", "Replay", "Resize", "FailedWrite", "Exit"} \* provenance tag on every native row 
 CellRows ≜ RowValues ∪ {Placeholder, Blank, OverflowMarker} \* what a viewport cell may display 
 Cells ≜ [owner : 0‥N, row : CellRows] \* a viewport cell: owning block (0 = chrome) + row 
 TaggedRows ≜ [owner : Blocks, row : RowValues] \* a ledger row: semantic, width-independent 
 NativeRows ≜ [source : NativeSources, owner : 0‥N, row : CellRows, width : WidthValues] 
 \* a native row: provenance source, owner, rendered row, and the width it was rendered at 

 SnapshotLengths ≜ {Len(snapshot) : snapshot ∈ SnapshotValues} \* set of occurring snapshot lengths 
 MaxSnapshotLength ≜ \* L_max: the longest snapshot length 
 CHOOSE maximum ∈ SnapshotLengths : \* (CHOOSE is fine here: the maximum 
 ∀ length ∈ SnapshotLengths : length ≤ maximum \* of a finite set is unique) 
 MaxFailureRows ≜ 2 * N * MaxSnapshotLength \* K_max: upper bound on one physical write batch 
 \* (factor 2 = worst-case Narrow doubling) 

 BlankCell ≜ [owner ↦ 0, row ↦ Blank] \* the unused-screen-space cell 
 OverflowCell ≜ [owner ↦ 0, row ↦ OverflowMarker] \* the "N older blocks hidden" summary cell 

 \* ------------------------------------------------------------------------- 
 \* State variables (one tuple entry per column of Table 1 in the paper). 
 \* ------------------------------------------------------------------------- 
 VARIABLES c, phase, mode, want, final, emitted, alloc, target, 
 history, native, width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason 
 \* c : commit frontier -- blocks 1..c are committed (retired) 
 \* phase : lifecycle phase per block 
 \* mode : Mutable / AppendOnly contract per block 
 \* want : current speculative snapshot per block 
 \* final : frozen final snapshot per block (NoFinal until finalized) 
 \* emitted : rows of the head block already streamed into history 
 \* alloc : painted slot height per block (rows on screen now) 
 \* target : requested slot height per block (animation target) 
 \* history : the logical ledger (layer 2) 
 \* native : the physical scrollback of the current epoch (layer 3) 
 \* width, height : current terminal geometry 
 \* resizes : how many resizes happened (bounded by MaxResizes) 
 \* epoch : display epoch; Rebuild resets native and bumps this 
 \* replayMode : pending replay policy (None / Append / Rebuild) 
 \* replayCursor : first committed block to replay (invariantly 1 while replaying) 
 \* replayEnd : last committed block to replay (= c at replay start) 
 \* replayPartial : how many stable head rows to replay 
 \* replayPrepared : replay frame computed and cut fixed (gates the scheduler) 
 \* replayCut : rows of the replay frame that must scroll into native 
 \* flush : explicit "retire everything" request (never reset) 
 \* shutdown : graceful shutdown initiated 
 \* running : host still alive; every action requires it 
 \* stopReason : why we stopped (Running while alive) 

 vars ≜ ⟨c, phase, mode, want, final, emitted, alloc, target, 
 history, native, width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ 
 \* the full variable tuple, used for stuttering ([Next]_vars) and UNCHANGED 

 Maximum(left, right) ≜ IF left ≥ right THEN left ELSE right \* max of two naturals 

 \* ------------------------------------------------------------------------- 
 \* Width rendering: the two-point abstraction of soft-wrap reflow. 
 \* ------------------------------------------------------------------------- 
 RECURSIVE DoubleRows(_) 
 DoubleRows(snapshot) ≜ \* Narrow rendering: 
 IF Len(snapshot) = 0 THEN ⟨⟩ \* empty stays empty; 
 ELSE ⟨Head(snapshot), Head(snapshot)⟩ ∘ DoubleRows(Tail(snapshot)) 
 \* every semantic row occupies TWO physical rows (models a wrapped line) 

 Render(snapshot, wx) ≜ IF wx = "Wide" THEN snapshot ELSE DoubleRows(snapshot) 
 \* rho_omega: Wide = identity, Narrow = row doubling; prefix-monotone by construction 

 Tag(i, snapshot) ≜ \* tg_i: stamp each row with its owner 
 [j ∈ 1‥Len(snapshot) ↦ [owner ↦ i, row ↦ snapshot[j]]] 

 SnapshotSlice(snapshot, lo, hi) ≜ \* s[lo..hi], empty when lo > hi 
 IF lo > hi THEN ⟨⟩ ELSE SubSeq(snapshot, lo, hi) 

 TagSlice(i, snapshot, lo, hi) ≜ Tag(i, SnapshotSlice(snapshot, lo, hi)) \* owner-tagged slice 

 NativeTag(source, i, snapshot, wx) ≜ \* ntg: render at width wx, then tag 
 [j ∈ 1‥Len(Render(snapshot, wx)) ↦ \* one native row per RENDERED row 
 [source ↦ source, owner ↦ i, \* provenance + owner 
 row ↦ Render(snapshot, wx)[j], width ↦ wx]] \* rendered row + width it used 
 NativeTagSlice(source, i, snapshot, lo, hi, wx) ≜ \* native-tag a semantic slice 
 NativeTag(source, i, SnapshotSlice(snapshot, lo, hi), wx) 

 NativeCells(source, cells, wx) ≜ \* lift screen cells to native rows 
 [j ∈ 1‥Len(cells) ↦ \* (used when the emulator itself 
 [source ↦ source, owner ↦ cells[j].owner, \* pushes viewport rows into 
 row ↦ cells[j].row, width ↦ wx]] \* scrollback, e.g. on resize/exit) 

 PrefixOf(sequence, count) ≜ [j ∈ 1‥count ↦ sequence[j]] \* first `count` elements 

 \* ------------------------------------------------------------------------- 
 \* The logical ledger as a FUNCTION of state (invariant ECH says 
 \* `history` always equals CommittedRows(c, final) \o PartialHeadRows). 
 \* ------------------------------------------------------------------------- 
 RECURSIVE CommittedRows(_, _) 
 CommittedRows(k, finals) ≜ \* C(k): finals of blocks 1..k, 
 IF k = 0 THEN ⟨⟩ \* tagged, concatenated in 
 ELSE CommittedRows(k - 1, finals) ∘ Tag(k, finals[k]) \* block (= commit) order 

 RECURSIVE TaggedRange(_, _, _) 
 TaggedRange(lo, hi, finals) ≜ \* tagged finals of blocks lo..hi 
 IF lo > hi THEN ⟨⟩ \* (empty range allowed) 
 ELSE Tag(lo, finals[lo]) ∘ TaggedRange(lo + 1, hi, finals) 

 RECURSIVE NativeRange(_, _, _, _, _) 
 NativeRange(source, lo, hi, finals, wx) ≜ \* same, but width-rendered and 
 IF lo > hi THEN ⟨⟩ \* source-tagged for `native` 
 ELSE NativeTag(source, lo, finals[lo], wx) 
 ∘ NativeRange(source, lo + 1, hi, finals, wx) 

 RetirementRows(lo, hi, finals, firstEmitted) ≜ \* logical retirement batch: 
 IF lo > hi THEN ⟨⟩ \* head block lo contributes only 
 ELSE TagSlice(lo, finals[lo], firstEmitted + 1, Len(finals[lo])) \* its UNstreamed suffix, 
 ∘ TaggedRange(lo + 1, hi, finals) \* later blocks contribute in full 

 NativeRetirementRows(source, lo, hi, finals, firstEmitted, wx) ≜ 
 IF lo > hi THEN ⟨⟩ \* physical twin of RetirementRows: 
 ELSE NativeTagSlice( \* the same rows, 
 source, \* provenance-tagged 
 lo, \* (Retire on success, 
 finals[lo], \* FailedWrite on failure), 
 firstEmitted + 1, \* starting after the already- 
 Len(finals[lo]), \* streamed head prefix, 
 wx \* rendered at the current width 
 ) 
 ∘ NativeRange(source, lo + 1, hi, finals, wx) \* then full later finals 

 FinalizedRange(lo, hi) ≜ \* "blocks lo..hi are all Finalized" 
 ∀ i ∈ lo‥hi : phase[i] = "Finalized" \* (a retirement batch precondition) 

 Unemitted(snapshot, i, emission) ≜ \* U_i(s): the part of s not yet 
 IF mode[i] = "AppendOnly" \* streamed into history -- 
 THEN SnapshotSlice(snapshot, emission[i] + 1, Len(snapshot)) \* suffix for append-only, 
 ELSE snapshot \* everything for mutable blocks 

 \* ------------------------------------------------------------------------- 
 \* Live-viewport geometry: who is presented, who is visible, how much 
 \* space is reserved. All operators take the ambient tuple explicitly so 
 \* that action guards can evaluate them at SUCCESSOR values. 
 \* ------------------------------------------------------------------------- 
 Presented(ph, finals, emission, i, wx) ≜ \* block i occupies viewport iff 
 ∨ ph[i] = "Active" \* it is actively producing, or 
 ∨ ∧ ph[i] = "Finalized" \* it is finalized AND still has 
 ∧ Len(Render(Unemitted(finals[i], i, emission), wx)) > 0 \* unstreamed content to show 

 PresentedSet(ph, finals, emission, wx) ≜ \* the set of presented blocks 
 {i ∈ Blocks : Presented(ph, finals, emission, i, wx)} 
 PresentedCount(ph, finals, emission, wx) ≜ \* pi: how many are presented 
 Cardinality(PresentedSet(ph, finals, emission, wx)) 
 Overflow(ph, finals, emission, wx, hx) ≜ \* ovf: more presented blocks 
 PresentedCount(ph, finals, emission, wx) > hx \* than viewport rows 
 SummaryRows(ph, finals, emission, wx, hx) ≜ \* sigma: one summary row is 
 IF hx > 0 ∧ Overflow(ph, finals, emission, wx, hx) THEN 1 ELSE 0 \* shown iff overflowing (and h>0) 

 NewerPresented(ph, finals, emission, wx, i) ≜ \* how many presented blocks are 
 Cardinality({ \* NEWER (higher index) than i -- 
 j ∈ Blocks : \* used to privilege recency 
 j > i ∧ Presented(ph, finals, emission, j, wx) 
 }) 

 VisiblePresented(ph, finals, emission, wx, hx, i) ≜ \* vis(i): presented AND, under 
 ∧ Presented(ph, finals, emission, i, wx) \* overflow, among the hx-1 
 ∧ IF Overflow(ph, finals, emission, wx, hx) \* newest presented blocks 
 THEN ∧ hx > 0 \* (one row is sacrificed to 
 ∧ NewerPresented(ph, finals, emission, wx, i) < hx - 1 \* the summary marker) 
 ELSE TRUE \* no overflow: presented = visible 

 RECURSIVE AllocationTotal(_, _) 
 AllocationTotal(al, i) ≜ \* sum of painted heights, 
 IF i > N THEN 0 ELSE al[i] + AllocationTotal(al, i + 1) \* blocks i..N 

 RECURSIVE ReservationTotal(_, _, _) 
 ReservationTotal(al, requested, i) ≜ \* Res: each block is charged 
 IF i > N THEN 0 \* max(painted, requested) -- 
 ELSE Maximum(al[i], requested[i]) + ReservationTotal(al, requested, i + 1) 
 \* growth pays up front, shrink keeps its old charge until painted 

 AllocationStateOK(al, requested, ph, finals, emission, wx, hx) ≜ \* A_OK: allocation admissibility 
 ∧ al ∈ [Blocks → 0‥H] \* painted heights in range 
 ∧ requested ∈ [Blocks → 0‥H] \* requested heights in range 
 ∧ ∀ i ∈ Blocks : 
 IF VisiblePresented(ph, finals, emission, wx, hx, i) 
 THEN IF ph[i] = "Active" 
 THEN ∧ al[i] ∈ 1‥H \* visible active: painted >= 1, 
 ∧ requested[i] ∈ 1‥H \* target >= 1 (may differ: animating) 
 ELSE ∧ al[i] ∈ 1‥H \* visible finalized: painted >= 1, 
 ∧ requested[i] = al[i] \* and frozen (no more animation) 
 ELSE ∧ al[i] = 0 \* invisible blocks hold 
 ∧ requested[i] = 0 \* no space at all 
 ∧ ReservationTotal(al, requested, 1) \* reservation invariant: 
 + SummaryRows(ph, finals, emission, wx, hx) ≤ hx \* reservations + summary fit in h 

 CanonicalAllocation(ph, finals, emission, wx, hx) ≜ \* kappa: the safe default -- 
 [i ∈ Blocks ↦ \* one row per visible block, 
 IF VisiblePresented(ph, finals, emission, wx, hx, i) THEN 1 ELSE 0] \* zero otherwise 

 SnapshotHeight(ph, wants, finals, i, wx) ≜ \* dm(i): row demand of block i 
 CASE ph[i] = "Active" → 
 Maximum(1, Len(Render(Unemitted(wants[i], i, emitted), wx))) \* live: >= 1 row 
 □ ph[i] = "Queued" → 
 Maximum(1, Len(Render(Unemitted(wants[i], i, emitted), wx))) \* queued demands space too 
 □ ph[i] = "Finalized" → 
 Len(Render(Unemitted(finals[i], i, emitted), wx)) \* finalized: exactly its unstreamed rows 
 □ OTHER → 0 \* absent/committed demand nothing 

 RECURSIVE FullRows(_, _, _, _, _) 
 FullRows(ph, wants, finals, wx, i) ≜ \* D: total row demand of 
 IF i > N THEN 0 \* blocks i..N 
 ELSE SnapshotHeight(ph, wants, finals, i, wx) 
 + FullRows(ph, wants, finals, wx, i + 1) 

 CreatedCount ≜ Cardinality({i ∈ Blocks : phase[i] ≠ "Absent"}) \* gamma: how many blocks exist 

 PartialHeadExists ≜ \* PH: the head block (c+1) has 
 ∧ c < CreatedCount \* been created, 
 ∧ mode[c + 1] = "AppendOnly" \* is append-only, 
 ∧ phase[c + 1] ∈ {"Active", "Finalized"} \* is live, 
 ∧ emitted[c + 1] > 0 \* and has streamed some rows 

 PartialHeadRows ≜ \* A(c): the head's streamed 
 IF PartialHeadExists \* prefix as tagged ledger rows 
 THEN TagSlice(c + 1, want[c + 1], 1, emitted[c + 1]) \* (prefix of `want`, stable by 
 ELSE ⟨⟩ \* the append-only contract) 

 RowPressure ≜ FullRows(phase, want, final, width, 1) > height \* demand exceeds viewport 
 Pressure ≜ \* pressure = row pressure OR 
 ∨ RowPressure \* too many uncommitted 
 ∨ CreatedCount - c ≥ MaxLive \* blocks piling up 
 RetirementRequested ≜ flush ∨ Pressure \* Req: when retirement may fire 
 Replaying ≜ replayMode ≠ "None" \* a replay is in flight 

 PreviewSource(i) ≜ \* what a slot displays: 
 IF phase[i] = "Active" \* live blocks show their 
 THEN Unemitted(want[i], i, emitted) \* unstreamed speculation, 
 ELSE Unemitted(final[i], i, emitted) \* others their unstreamed final 

 PreviewCell(i, snapshot) ≜ \* the representative cell of a slot: 
 LET rendered ≜ Render(snapshot, width) IN \* render at current width; 
 [owner ↦ i, 
 row ↦ IF Len(rendered) = 0 \* empty content shows the 
 THEN Placeholder \* placeholder row, otherwise 
 ELSE rendered[Len(rendered)]] \* the LAST rendered row (tail view) 

 Repeat(value, count) ≜ [j ∈ 1‥count ↦ value] \* value^count as a sequence 
 Slot(i, snapshot, allocation) ≜ Repeat(PreviewCell(i, snapshot), allocation) 
 \* a slot = its preview cell repeated alloc[i] times (abstracting the real tail window) 

 RECURSIVE PresentedCells(_) 
 PresentedCells(i) ≜ \* all slots, ascending block 
 IF i > N THEN ⟨⟩ \* order (newest at the bottom, 
 ELSE (IF alloc[i] = 0 THEN ⟨⟩ ELSE Slot(i, PreviewSource(i), alloc[i])) \* next to the cursor); 
 ∘ PresentedCells(i + 1) \* zero-alloc blocks contribute nothing 

 Screen ≜ \* Q: the whole viewport, top to bottom: 
 Repeat( 
 BlankCell, \* blank filler first, 
 height - AllocationTotal(alloc, 1) - SummaryRows(phase, final, emitted, width, height) 
 ) \* (exactly the unclaimed rows) 
 ∘ (IF SummaryRows(phase, final, emitted, width, height) = 1 
 THEN ⟨OverflowCell⟩ \* then the overflow summary if any, 
 ELSE ⟨⟩) 
 ∘ PresentedCells(1) \* then the block slots 

 \* ------------------------------------------------------------------------- 
 \* Replay geometry: what a width-changing resize must re-render. 
 \* ------------------------------------------------------------------------- 
 ReplayRows ≜ \* R: the full replay frame -- 
 IF ¬Replaying 
 THEN ⟨⟩ \* nothing when no replay pending 
 ELSE NativeRange("Replay", replayCursor, replayEnd, final, width) \* committed finals 1..c 
 ∘ (IF replayPartial = 0 \* re-rendered at the NEW width, 
 THEN ⟨⟩ \* plus the head's already- 
 ELSE NativeTagSlice( \* streamed stable prefix 
 "Replay", \* (if it had streamed rows 
 replayEnd + 1, \* at resize time) -- 
 want[replayEnd + 1], \* prefix of want, immutable 
 1, \* under the append-only 
 replayPartial, \* contract, so stable while 
 width \* the replay is in flight 
 )) 

 ReplayRoom ≜ \* how many blank rows the 
 Cardinality({j ∈ 1‥height : Screen[j] = BlankCell}) \* viewport can absorb scroll-free 

 RequiredReplayCut ≜ \* cut*: replay rows that do NOT 
 IF Len(ReplayRows) > ReplayRoom THEN Len(ReplayRows) - ReplayRoom ELSE 0 
 \* fit in the blank region and must scroll into native scrollback 

 PreparedReplayTail ≜ \* the part painted bottom-first 
 IF replayPrepared \* into blank rows (no scroll); 
 THEN SnapshotSlice(ReplayRows, replayCut + 1, Len(ReplayRows)) \* only meaningful once 
 ELSE ⟨⟩ \* the frame is prepared 

 Prefix(left, right) ≜ \* left is a prefix of right 
 ∧ Len(left) ≤ Len(right) \* (the partial order behind the 
 ∧ ∀ j ∈ 1‥Len(left) : left[j] = right[j] \* append-only contract) 

 NoEarlierQueued(i) ≜ ∀ j ∈ 1‥(i - 1) : phase[j] ≠ "Queued" \* FIFO admission guard 

 \* ========================================================================= 
 \* Initial state: nothing created, full-height wide viewport, empty 
 \* histories, no replay, host running. 
 \* ========================================================================= 
 Init ≜ 
 ∧ c = 0 \* nothing committed 
 ∧ phase = [i ∈ Blocks ↦ "Absent"] \* no block exists 
 ∧ mode = [i ∈ Blocks ↦ "Undeclared"] \* no contract chosen 
 ∧ want = [i ∈ Blocks ↦ ⟨⟩] \* empty speculation 
 ∧ final = [i ∈ Blocks ↦ NoFinal] \* nothing finalized 
 ∧ emitted = [i ∈ Blocks ↦ 0] \* nothing streamed 
 ∧ alloc = [i ∈ Blocks ↦ 0] \* no slot painted 
 ∧ target = [i ∈ Blocks ↦ 0] \* no slot requested 
 ∧ history = ⟨⟩ \* empty ledger (= CommittedRows(0,...)) 
 ∧ native = ⟨⟩ \* empty scrollback 
 ∧ width = "Wide" \* initial geometry: 
 ∧ height = H \* wide, full height 
 ∧ resizes = 0 \* no resizes yet 
 ∧ epoch = 0 \* first display epoch 
 ∧ replayMode = "None" \* no replay pending 
 ∧ replayCursor = 0 \* replay window empty 
 ∧ replayEnd = 0 
 ∧ replayPartial = 0 
 ∧ replayPrepared = FALSE \* no frame prepared 
 ∧ replayCut = 0 
 ∧ flush = FALSE \* no flush requested 
 ∧ shutdown = FALSE \* not shutting down 
 ∧ running = TRUE \* host alive 
 ∧ stopReason = "Running" \* ... and not stopped 

 \* ========================================================================= 
 \* Actions. Every guard conjoins `running`; most also require ~shutdown. 
 \* ========================================================================= 

 Create(declaration) ≜ \* a new block is declared 
 ∧ running \* host alive 
 ∧ ¬shutdown \* no new work during shutdown 
 ∧ CreatedCount < N \* an identity is still free 
 ∧ phase[CreatedCount + 1] = "Absent" \* blocks are created contiguously 
 ∧ declaration ∈ {"Mutable", "AppendOnly"} \* contract chosen now, forever 
 ∧ phase' = [phase EXCEPT ![CreatedCount + 1] = "Queued"] \* enters the queue 
 ∧ mode' = [mode EXCEPT ![CreatedCount + 1] = declaration] \* contract recorded 
 ∧ UNCHANGED ⟨c, want, final, emitted, alloc, target, history, native, 
 width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ \* pure bookkeeping: no paint, no history 

 Admit(i) ≜ \* a queued block gets a live slot 
 ∧ running \* host alive 
 ∧ ¬shutdown \* not during shutdown 
 ∧ phase[i] = "Queued" \* must be waiting 
 ∧ NoEarlierQueued(i) \* FIFO: no older block still queued 
 ∧ LET newPhase ≜ [phase EXCEPT ![i] = "Active"] \* candidate successor phase, 
 newAlloc ≜ [alloc EXCEPT ![i] = 1] \* with a fresh 1-row slot 
 newTarget ≜ [target EXCEPT ![i] = 1] \* painted and requested 
 IN ∧ ¬Overflow(newPhase, final, emitted, width, height) \* admission may NOT overflow -- 
 ∧ AllocationStateOK(newAlloc, newTarget, newPhase, final, emitted, width, height) 
 \* ... and the new slot must fit the reservation invariant; otherwise the 
 \* block simply stays queued (denied, not summarized) 
 ∧ phase' = newPhase \* commit the candidate state 
 ∧ alloc' = newAlloc 
 ∧ target' = newTarget 
 ∧ UNCHANGED ⟨c, mode, want, final, emitted, history, native, width, height, 
 resizes, epoch, replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ \* repaint only: histories untouched 

 Update(i, snapshot) ≜ \* speculation evolves 
 ∧ running \* host alive 
 ∧ ¬shutdown \* not during shutdown 
 ∧ phase[i] ∈ {"Queued", "Active"} \* only unfinalized blocks change 
 ∧ (mode[i] = "Mutable" ∨ Prefix(want[i], snapshot)) \* THE append-only contract: 
 \* mutable blocks may replace their content arbitrarily; append-only 
 \* blocks may only extend it (old rows are immutable) 
 ∧ snapshot ≠ want[i] \* no stuttering updates 
 ∧ want' = [want EXCEPT ![i] = snapshot] \* the only writer of speculation 
 ∧ UNCHANGED ⟨c, phase, mode, final, emitted, alloc, target, history, native, 
 width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ \* repaint only 

 RequestAllocation(newTarget) ≜ \* the app asks for new slot heights 
 ∧ running \* host alive 
 ∧ ¬shutdown \* not during shutdown 
 ∧ AllocationStateOK(alloc, newTarget, phase, final, emitted, width, height) 
 \* admissible against the CURRENT paint: max(painted, newly-requested) 
 \* must fit, so every later animation frame is pre-paid (dominance) 
 ∧ newTarget ≠ target \* no stuttering requests 
 ∧ target' = newTarget \* targets change; paint doesn't yet 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, emitted, alloc, history, native, 
 width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ \* nothing visible happens yet 

 BridgeHeight(sampled, requested) ≜ \* B(a,t): next painted height 
 IF sampled < requested THEN requested \* growth jumps straight to target; 
 ELSE IF sampled > 2 ∧ requested = 1 THEN 2 \* a deep shrink (>2 -> 1) pauses at 2 
 ELSE requested \* all other shrinks are direct 
 \* the 2-row bridge frame makes deep collapses read as contractions, not snaps 

 ApplyAllocation(i) ≜ \* one animation frame is painted 
 ∧ running \* host alive 
 ∧ ¬shutdown \* not during shutdown 
 ∧ phase[i] = "Active" \* only active slots animate 
 ∧ alloc[i] ≠ target[i] \* something to do 
 ∧ LET nextHeight ≜ BridgeHeight(alloc[i], target[i]) \* bridged next height 
 newAlloc ≜ [alloc EXCEPT ![i] = nextHeight] 
 IN ∧ AllocationStateOK(newAlloc, target, phase, final, emitted, width, height) 
 \* always satisfiable along a bridge: B never raises max(alloc, target) 
 ∧ alloc' = newAlloc \* paint the frame 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, emitted, target, history, native, 
 width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ \* repaint only 

 FinalizeActive(i, snapshot) ≜ \* a live block completes 
 ∧ running \* host alive 
 ∧ ¬shutdown \* not during shutdown 
 ∧ phase[i] = "Active" \* it was producing 
 ∧ (mode[i] = "Mutable" ∨ Prefix(want[i], snapshot)) \* final must honor the contract 
 ∧ LET newPhase ≜ [phase EXCEPT ![i] = "Finalized"] 
 newFinal ≜ [final EXCEPT ![i] = snapshot] \* the final value, frozen forever 
 newAlloc ≜ CanonicalAllocation(newPhase, newFinal, emitted, width, height) 
 IN ∧ phase' = newPhase \* lifecycle advances 
 ∧ want' = [want EXCEPT ![i] = snapshot] \* want converges to final 
 ∧ final' = newFinal \* (invariant: final = want) 
 ∧ alloc' = newAlloc \* ALL slots collapse to canonical 
 ∧ target' = newAlloc \* 1-row previews: finished content 
 ∧ UNCHANGED ⟨c, mode, emitted, history, native, width, height, \* no longer animates 
 resizes, epoch, replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ \* repaint only: nothing retires yet 

 FinalizeQueued(i, snapshot) ≜ \* a block completes WITHOUT ever 
 ∧ running \* having held a slot (finished 
 ∧ ¬shutdown \* before space freed up) 
 ∧ phase[i] = "Queued" \* straight from the queue 
 ∧ (mode[i] = "Mutable" ∨ Prefix(want[i], snapshot)) \* same contract check 
 ∧ LET newPhase ≜ [phase EXCEPT ![i] = "Finalized"] 
 newWant ≜ [want EXCEPT ![i] = snapshot] 
 newFinal ≜ [final EXCEPT ![i] = snapshot] 
 newAlloc ≜ CanonicalAllocation(newPhase, newFinal, emitted, width, height) 
 IN ∧ phase' = newPhase \* note: THIS transition may cause 
 ∧ want' = newWant \* overflow (a hidden block becomes 
 ∧ final' = newFinal \* presented) -- summarization, not 
 ∧ alloc' = newAlloc \* denial, handles it here 
 ∧ target' = newAlloc 
 ∧ UNCHANGED ⟨c, mode, emitted, history, native, width, height, 
 resizes, epoch, replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ \* repaint only 

 AppendStable ≜ \* natural streaming: ONE stable row 
 ∧ running \* of the append-only HEAD block 
 ∧ ¬shutdown \* scrolls into both histories 
 ∧ ¬Replaying \* never interleaves with replay 
 ∧ c < CreatedCount \* a head block exists 
 ∧ mode[c + 1] = "AppendOnly" \* only append-only blocks stream 
 ∧ phase[c + 1] ∈ {"Active", "Finalized"} \* and only while live 
 ∧ RowPressure \* only under ROW pressure: with 
 \* room to spare, stable rows stay in the viewport (still repositionable) 
 ∧ emitted[c + 1] < Len(want[c + 1]) \* a stable row remains to stream 
 ∧ LET next ≜ emitted[c + 1] + 1 \* index of the row to emit 
 newEmitted ≜ [emitted EXCEPT ![c + 1] = next] 
 newAlloc ≜ CanonicalAllocation(phase, final, newEmitted, width, height) 
 IN ∧ history' = history ∘ TagSlice(c + 1, want[c + 1], next, next) \* ledger += 1 semantic row 
 ∧ native' = 
 native 
 ∘ NativeTagSlice("Append", c + 1, want[c + 1], next, next, width) 
 \* native += the same row, rendered (1 or 2 physical rows), tagged Append 
 ∧ emitted' = newEmitted \* the stable frontier advances 
 ∧ alloc' = newAlloc \* layout recanonicalizes (the 
 ∧ target' = newAlloc \* streamed row left the viewport) 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, 
 width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ \* frontier c itself does not move 

 CompleteAppendOnly ≜ \* the fully-streamed head commits 
 ∧ running \* host alive 
 \* (deliberately NO ~shutdown: draining the head stays possible while 
 \* shutting down) 
 ∧ ¬Replaying \* never during replay 
 ∧ c < CreatedCount \* head exists 
 ∧ mode[c + 1] = "AppendOnly" \* head is append-only 
 ∧ phase[c + 1] = "Finalized" \* head is done 
 ∧ emitted[c + 1] = Len(final[c + 1]) \* every row already streamed 
 ∧ LET newPhase ≜ [phase EXCEPT ![c + 1] = "Committed"] 
 newEmitted ≜ [emitted EXCEPT ![c + 1] = 0] \* emitted counter retires with it 
 newAlloc ≜ CanonicalAllocation(newPhase, final, newEmitted, width, height) 
 IN ∧ c' = c + 1 \* frontier advances: PURE 
 ∧ phase' = newPhase \* bookkeeping -- every row is 
 ∧ emitted' = newEmitted \* already in both histories, 
 ∧ alloc' = newAlloc \* so nothing is written 
 ∧ target' = newAlloc 
 ∧ UNCHANGED ⟨mode, want, final, history, native, width, height, 
 resizes, epoch, replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ \* note: history unchanged! 

 BeginFlush ≜ \* someone asks for full retirement 
 ∧ running \* host alive 
 ∧ ¬flush \* idempotent: set once, 
 ∧ flush' = TRUE \* never reset 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, emitted, alloc, target, 
 history, native, width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 shutdown, running, stopReason⟩ \* a pure request: no effect yet 

 RetireSuccess(batchEnd) ≜ \* in-order retirement of a batch 
 ∧ running \* host alive 
 ∧ ¬Replaying \* never during replay 
 ∧ batchEnd ∈ (c + 1)‥N \* batch = blocks c+1 .. batchEnd 
 ∧ FinalizedRange(c + 1, batchEnd) \* ... ALL of them finalized 
 ∧ RetirementRequested \* only under flush or pressure 
 ∧ history' = 
 history ∘ RetirementRows(c + 1, batchEnd, final, emitted[c + 1]) 
 \* ledger += head's unstreamed suffix, then later finals in full 
 \* (emitted[c+1] is the only possibly-nonzero emitted counter) 
 ∧ native' = 
 native 
 ∘ NativeRetirementRows( \* native += the same rows, 
 "Retire", \* tagged Retire, rendered at 
 c + 1, \* the current width; realized 
 batchEnd, \* on a real terminal as ONE 
 final, \* streamed write (paper, 
 emitted[c + 1], \* Lemma "streaming 
 width \* realization") 
 ) 
 ∧ LET newPhase ≜ [i ∈ Blocks ↦ 
 IF i ≤ batchEnd THEN "Committed" ELSE phase[i]] \* batch commits 
 newEmitted ≜ [i ∈ Blocks ↦ 
 IF i ≤ batchEnd THEN 0 ELSE emitted[i]] \* counters reset 
 newAlloc ≜ CanonicalAllocation(newPhase, final, newEmitted, width, height) 
 IN ∧ c' = batchEnd \* frontier jumps to batch end 
 ∧ phase' = newPhase 
 ∧ emitted' = newEmitted 
 ∧ alloc' = newAlloc \* retired slots disappear; 
 ∧ target' = newAlloc \* survivors recanonicalize 
 ∧ UNCHANGED ⟨mode, want, final, width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown, running, stopReason⟩ \* finals themselves are untouched 

 RetireFailure(batchEnd, count) ≜ \* the SAME write, torn partway: 
 ∧ running \* same enabling conditions 
 ∧ ¬Replaying \* as RetireSuccess ... 
 ∧ batchEnd ∈ (c + 1)‥N 
 ∧ FinalizedRange(c + 1, batchEnd) 
 ∧ RetirementRequested 
 ∧ LET rows ≜ 
 NativeRetirementRows( \* the batch that WOULD have 
 "FailedWrite", \* been written, tagged 
 c + 1, \* FailedWrite for forensics 
 batchEnd, 
 final, 
 emitted[c + 1], 
 width 
 ) 
 IN ∧ count ∈ 0‥Len(rows) \* the terminal accepted `count` 
 ∧ native' = native ∘ PrefixOf(rows, count) \* rows: an arbitrary PREFIX -- 
 \* never reordered, never a row from outside the batch 
 ∧ running' = FALSE \* fail-stop: the host halts; 
 ∧ stopReason' = "WriteFailure" \* no retry path exists, so 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, emitted, alloc, target, history, 
 width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, replayPrepared, replayCut, flush, shutdown⟩ 
 \* CRITICAL: c and history do NOT advance -- the ledger never lies about 
 \* what committed, so duplication/reordering after failure is impossible 

 Resize(newWidth, newHeight, resizePolicy, pushed) ≜ \* terminal geometry changes 
 ∧ running \* host alive 
 ∧ ¬shutdown \* not during shutdown 
 ∧ resizes < MaxResizes \* bounded (finite model) 
 ∧ newWidth ∈ WidthValues \* new geometry and the 
 ∧ newHeight ∈ 0‥H \* policy for native history 
 ∧ resizePolicy ∈ ResizeModes 
 ∧ newWidth ≠ width ∨ newHeight ≠ height \* an actual change 
 ∧ pushed ∈ 0‥Len(Screen) \* emulator may scroll 0..h top 
 \* viewport rows into scrollback during the resize (e.g. height shrink) 
 ∧ LET widthChanged ≜ newWidth ≠ width 
 effectiveMode ≜ IF widthChanged THEN resizePolicy ELSE "Preserve" 
 \* height-only resizes never replay: rendered rows are still valid 
 pushedRows ≜ NativeCells("Resize", PrefixOf(Screen, pushed), width) 
 \* rows pushed by the emulator, tagged Resize, at the OLD width 
 beginReplay ≜ effectiveMode ≠ "Preserve" ∧ (c > 0 ∨ PartialHeadExists) 
 \* replay only if there is committed/streamed content to re-render 
 newPhase ≜ phase \* lifecycle is untouched 
 newAlloc ≜ CanonicalAllocation(newPhase, final, emitted, newWidth, newHeight) 
 IN ∧ width' = newWidth \* adopt the new geometry 
 ∧ height' = newHeight 
 ∧ resizes' = resizes + 1 \* burn one resize budget 
 ∧ alloc' = newAlloc \* layout recanonicalizes at 
 ∧ target' = newAlloc \* the new geometry 
 ∧ native' = IF effectiveMode = "Rebuild" 
 THEN ⟨⟩ \* Rebuild: native display is wiped ... 
 ELSE native ∘ pushedRows \* else: record what the emulator pushed 
 ∧ epoch' = IF effectiveMode = "Rebuild" THEN epoch + 1 ELSE epoch 
 \* ... and the display epoch increments (native monotonicity is epoch-scoped) 
 ∧ replayMode' = 
 IF beginReplay THEN effectiveMode \* start a replay, 
 ELSE IF Replaying THEN replayMode ELSE "None" \* or keep/clear the old one 
 ∧ replayCursor' = 
 IF beginReplay THEN 1 \* replay window = committed 
 ELSE IF Replaying THEN replayCursor ELSE 0 \* blocks 1..c 
 ∧ replayEnd' = 
 IF beginReplay THEN c 
 ELSE IF Replaying THEN replayEnd ELSE 0 
 ∧ replayPartial' = 
 IF beginReplay 
 THEN IF PartialHeadExists THEN emitted[c + 1] ELSE 0 \* plus the streamed head prefix 
 ELSE IF Replaying THEN replayPartial ELSE 0 
 ∧ replayPrepared' = FALSE \* ANY resize invalidates a 
 ∧ replayCut' = 0 \* previously prepared frame 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, emitted, history, 
 flush, shutdown, running, stopReason⟩ 
 \* resize logical-neutrality: ledger, frontier, and semantics never move 

 PrepareReplay ≜ \* compute the replay frame 
 ∧ running \* host alive 
 ∧ Replaying \* a replay is pending 
 ∧ ¬replayPrepared \* and not yet prepared 
 ∧ replayPrepared' = TRUE \* freeze the frame NOW: 
 ∧ replayCut' = RequiredReplayCut \* cut = rows that must scroll 
 \* from here the scheduler gate (see Next) admits ONLY the two replay 
 \* writes, so the sampled cut cannot be invalidated by interleaving 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, emitted, alloc, target, 
 history, native, width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 flush, shutdown, running, stopReason⟩ \* pure computation: no write yet 

 ReplaySynchronousSuccess ≜ \* the single buffered write lands 
 ∧ running \* host alive 
 ∧ Replaying \* replay pending 
 ∧ replayPrepared \* frame prepared (gate open) 
 ∧ native' = native ∘ PrefixOf(ReplayRows, replayCut) \* exactly `cut` rows scroll into 
 \* native; the tail was painted into blank rows (no scroll, no history) 
 ∧ replayMode' = "None" \* replay fully drains: 
 ∧ replayCursor' = 0 \* all replay state returns 
 ∧ replayEnd' = 0 \* to its idle shape 
 ∧ replayPartial' = 0 
 ∧ replayPrepared' = FALSE 
 ∧ replayCut' = 0 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, emitted, alloc, target, 
 history, width, height, resizes, epoch, 
 flush, shutdown, running, stopReason⟩ \* logically neutral: ledger untouched 

 ReplaySynchronousFailure(count) ≜ \* the same write, torn partway 
 ∧ running \* host alive 
 ∧ Replaying \* replay pending 
 ∧ replayPrepared \* frame prepared 
 ∧ count ∈ 0‥replayCut \* an arbitrary prefix of the 
 ∧ native' = native ∘ PrefixOf(ReplayRows, count) \* scrolled portion landed 
 ∧ running' = FALSE \* fail-stop, as with 
 ∧ stopReason' = "WriteFailure" \* RetireFailure: halt, no retry 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, emitted, alloc, target, history, 
 width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 flush, shutdown⟩ \* ledger and frontier still truthful 

 BeginGracefulShutdown ≜ \* wind-down begins 
 ∧ running \* host alive 
 ∧ ¬shutdown \* only once 
 ∧ LET newPhase ≜ [i ∈ Blocks ↦ 
 IF phase[i] = "Absent" THEN "Absent" \* never-created stay absent; 
 ELSE IF i ≤ c THEN "Committed" ELSE "Finalized"] \* all live work freezes 
 newFinal ≜ [i ∈ Blocks ↦ 
 IF phase[i] = "Absent" THEN NoFinal \* absent: still no final; 
 ELSE IF i ≤ c ∨ phase[i] = "Finalized" 
 THEN final[i] \* already-frozen finals kept; 
 ELSE want[i]] \* queued/active freeze AT their 
 newAlloc ≜ CanonicalAllocation(newPhase, newFinal, emitted, width, height) 
 IN ∧ phase' = newPhase \* current speculation (f := w) 
 ∧ final' = newFinal 
 ∧ alloc' = newAlloc \* layout collapses to canonical 
 ∧ target' = newAlloc 
 ∧ flush' = TRUE \* permanent flush: everything 
 ∧ shutdown' = TRUE \* must drain, then exit 
 ∧ UNCHANGED ⟨c, mode, want, emitted, history, native, width, height, 
 resizes, epoch, replayMode, replayCursor, replayEnd, replayPartial, 
 replayPrepared, replayCut, 
 running, stopReason⟩ \* nothing retires in this step itself 

 GracefulExit(push) ≜ \* clean exit after full drain 
 ∧ running \* host alive 
 ∧ shutdown \* shutdown was initiated, 
 ∧ ¬Replaying \* replay has drained, 
 ∧ c = CreatedCount \* and EVERY block committed 
 ∧ push ∈ 0‥1 \* optionally scroll one last row 
 ∧ push = 0 ∨ height > 0 \* (only if a viewport row exists) 
 ∧ running' = FALSE \* host stops 
 ∧ stopReason' = "Graceful" \* ... cleanly 
 ∧ native' = IF push = 0 
 THEN native \* either no final scroll, or the 
 ELSE native ∘ NativeCells("Exit", ⟨Screen[1]⟩, width) 
 \* top viewport row scrolls out (restoring the shell prompt), 
 \* tagged Exit 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, emitted, alloc, target, history, 
 width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, replayPrepared, replayCut, flush, shutdown⟩ 

 DetachExit(push) ≜ \* abandon ship: exit NOW, 
 ∧ running \* uncommitted work is dropped 
 ∧ ¬shutdown \* (a detach, not a shutdown) 
 ∧ push ∈ 0‥1 \* same optional final scroll 
 ∧ push = 0 ∨ height > 0 
 ∧ running' = FALSE \* host stops 
 ∧ stopReason' = "Detach" 
 ∧ native' = IF push = 0 
 THEN native 
 ELSE native ∘ NativeCells("Exit", ⟨Screen[1]⟩, width) 
 ∧ UNCHANGED ⟨c, phase, mode, want, final, emitted, alloc, target, history, 
 width, height, resizes, epoch, 
 replayMode, replayCursor, replayEnd, replayPartial, replayPrepared, replayCut, flush, shutdown⟩ 
 \* ECH guarantees `history` holds exactly the committed content at detach 

 \* ------------------------------------------------------------------------- 
 \* Existentially closed action wrappers (for fairness and Next). 
 \* ------------------------------------------------------------------------- 
 RetireSuccessAction ≜ ∃ batchEnd ∈ Blocks : RetireSuccess(batchEnd) \* some batch retires 
 RetireFailureAction ≜ \* some batch write fails at 
 ∃ batchEnd ∈ Blocks : \* some prefix length 
 ∃ count ∈ 0‥MaxFailureRows : RetireFailure(batchEnd, count) 
 ReplaySynchronousFailureAction ≜ \* replay write fails at some 
 ∃ count ∈ 0‥MaxFailureRows : ReplaySynchronousFailure(count) \* prefix length 

 \* ------------------------------------------------------------------------- 
 \* The scheduler gate: once a replay frame is prepared, the ONLY possible 
 \* steps are the replay write landing or failing. This is what the word 
 \* "synchronous" means, and it is what keeps replayCut = RequiredReplayCut 
 \* stable (nothing may repaint in between). 
 \* ------------------------------------------------------------------------- 
 Next ≜ 
 IF replayPrepared 
 THEN ReplaySynchronousSuccess ∨ ReplaySynchronousFailureAction \* gate closed: write or die 
 ELSE ∨ ∃ declaration ∈ {"Mutable", "AppendOnly"} : Create(declaration) \* gate open: 
 ∨ ∃ i ∈ Blocks : Admit(i) \* any protocol 
 ∨ ∃ i ∈ Blocks, snapshot ∈ SnapshotValues : Update(i, snapshot) \* step may fire 
 ∨ ∃ newTarget ∈ [Blocks → 0‥H] : RequestAllocation(newTarget) 
 ∨ ∃ i ∈ Blocks : ApplyAllocation(i) 
 ∨ ∃ i ∈ Blocks, snapshot ∈ SnapshotValues : FinalizeActive(i, snapshot) 
 ∨ ∃ i ∈ Blocks, snapshot ∈ SnapshotValues : FinalizeQueued(i, snapshot) 
 ∨ AppendStable 
 ∨ CompleteAppendOnly 
 ∨ BeginFlush 
 ∨ RetireSuccessAction 
 ∨ RetireFailureAction 
 ∨ ∃ newWidth ∈ WidthValues, newHeight ∈ 0‥H, 
 resizePolicy ∈ ResizeModes, pushed ∈ 0‥H : 
 Resize(newWidth, newHeight, resizePolicy, pushed) 
 ∨ PrepareReplay 
 ∨ BeginGracefulShutdown 
 ∨ ∃ push ∈ 0‥1 : GracefulExit(push) 
 ∨ ∃ push ∈ 0‥1 : DetachExit(push) 

 Spec ≜ 
 ∧ Init \* start in the initial state, 
 ∧ □[Next]_vars \* take Next steps (or stutter), 
 ∧ WF_vars(RetireSuccessAction) \* and don't ignore forever: 
 ∧ WF_vars(PrepareReplay) \* retirement, replay preparation, 
 ∧ WF_vars(ReplaySynchronousSuccess) \* the replay write, 
 ∧ WF_vars(AppendStable) \* head streaming, 
 ∧ WF_vars(CompleteAppendOnly) \* and head commitment. 
 \* Weak fairness: an action enabled forever is eventually taken. Failures 
 \* and exits are NOT fair -- they may happen, but are never forced. 

 \* ========================================================================= 
 \* Invariants (checked by TLC in every reachable state). 
 \* ========================================================================= 

 TypeOK ≜ \* T: every variable in range 
 ∧ c ∈ 0‥N \* frontier within block ids 
 ∧ phase ∈ [Blocks → Phases] \* valid phase per block 
 ∧ mode ∈ [Blocks → BlockModes] \* valid mode per block 
 ∧ want ∈ [Blocks → SnapshotValues] \* speculation from the universe 
 ∧ final ∈ [Blocks → SnapshotValues ∪ {NoFinal}] \* final or the sentinel 
 ∧ emitted ∈ [Blocks → 0‥MaxSnapshotLength] \* emitted counter bounded 
 ∧ alloc ∈ [Blocks → 0‥H] \* painted heights bounded 
 ∧ target ∈ [Blocks → 0‥H] \* requested heights bounded 
 ∧ history ∈ Seq(TaggedRows) \* ledger rows well-formed 
 ∧ native ∈ Seq(NativeRows) \* native rows well-formed 
 ∧ width ∈ WidthValues \* geometry in range 
 ∧ height ∈ 0‥H 
 ∧ resizes ∈ 0‥MaxResizes \* resize budget respected 
 ∧ epoch ∈ 0‥MaxResizes \* epochs only at resizes 
 ∧ replayMode ∈ ReplayModes \* replay state in range 
 ∧ replayCursor ∈ 0‥(N + 1) \* (loose bound; really 0 or 1) 
 ∧ replayEnd ∈ 0‥N 
 ∧ replayPartial ∈ 0‥MaxSnapshotLength 
 ∧ replayPrepared ∈ BOOLEAN 
 ∧ replayCut ∈ 0‥MaxFailureRows \* cut bounded by max batch size 
 ∧ flush ∈ BOOLEAN 
 ∧ shutdown ∈ BOOLEAN 
 ∧ running ∈ BOOLEAN 
 ∧ stopReason ∈ StopReasons 

 LifecycleShape ≜ \* LS: blocks form three bands -- 
 ∧ c ≤ CreatedCount \* can't commit the uncreated 
 ∧ ∀ i ∈ 1‥c : \* band 1: 1..c 
 ∧ phase[i] = "Committed" \* all committed, 
 ∧ mode[i] ∈ {"Mutable", "AppendOnly"} \* with a declared mode 
 ∧ ∀ i ∈ (c + 1)‥CreatedCount : \* band 2: live blocks 
 ∧ phase[i] ∈ {"Queued", "Active", "Finalized"} 
 ∧ mode[i] ∈ {"Mutable", "AppendOnly"} 
 ∧ ∀ i ∈ (CreatedCount + 1)‥N : \* band 3: not yet created 
 ∧ phase[i] = "Absent" 
 ∧ mode[i] = "Undeclared" 

 SnapshotDiscipline ≜ \* SD: finals exist exactly for 
 ∀ i ∈ Blocks : \* finalized/committed blocks, 
 IF phase[i] ∈ {"Finalized", "Committed"} 
 THEN ∧ final[i] ∈ SnapshotValues \* are real snapshots, 
 ∧ final[i] = want[i] \* and equal the last speculation 
 ELSE final[i] = NoFinal \* everyone else: the sentinel 

 EmissionDiscipline ≜ \* ED: streaming is head-only -- 
 ∧ ∀ i ∈ Blocks : 
 ∧ emitted[i] ≤ Len(want[i]) \* never emitted more than exists 
 ∧ (mode[i] ≠ "AppendOnly" ⇒ emitted[i] = 0) \* mutable blocks never stream 
 ∧ (emitted[i] > 0 ⇒ 
 ∧ i = c + 1 \* only the HEAD may have 
 ∧ phase[i] ∈ {"Active", "Finalized"}) \* streamed rows, and only live 
 ∧ (PartialHeadExists ⇒ emitted[c + 1] ≤ Len(want[c + 1])) \* (redundant safety belt) 

 Capacity ≜ AllocationStateOK(alloc, target, phase, final, emitted, width, height) 
 \* CAP: the reservation invariant holds of the ACTUAL alloc/target at all times 

 ExactCommittedHistory ≜ history = CommittedRows(c, final) ∘ PartialHeadRows 
 \* ECH, the central equation: the ledger IS the committed finals in block 
 \* order, plus the head's streamed prefix -- no dupes, no gaps, no reorders 

 NoPrematureHistory ≜ \* every ledger row is owned by 
 ∀ j ∈ 1‥Len(history) : 
 LET owner ≜ history[j].owner IN 
 ∨ ∧ owner ∈ 1‥c \* a committed block, or 
 ∧ phase[owner] = "Committed" 
 ∨ ∧ PartialHeadExists \* the streaming head -- 
 ∧ owner = c + 1 \* speculation NEVER leaks 

 ScreenCapacity ≜ \* the screen is exactly right: 
 ∧ Screen ∈ Seq(Cells) \* well-formed cells, 
 ∧ Len(Screen) = height \* exactly `height` of them, 
 ∧ ∀ i ∈ Blocks : 
 Cardinality({j ∈ 1‥height : Screen[j].owner = i}) = alloc[i] \* each block owns alloc[i] rows, 
 ∧ Cardinality({j ∈ 1‥height : Screen[j] = OverflowCell}) 
 = SummaryRows(phase, final, emitted, width, height) \* the summary row appears iff overflowing, 
 ∧ Cardinality({j ∈ 1‥height : Screen[j] = BlankCell}) 
 = height - AllocationTotal(alloc, 1) 
 - SummaryRows(phase, final, emitted, width, height) \* the rest is blank -- accounts balance 

 ReplayShape ≜ \* RS: replay bookkeeping is sane 
 ∧ (replayMode = "None" ⇒ \* idle: all replay state zeroed 
 ∧ replayCursor = 0 
 ∧ replayEnd = 0 
 ∧ replayPartial = 0 
 ∧ ¬replayPrepared 
 ∧ replayCut = 0) 
 ∧ (replayMode ≠ "None" ⇒ \* in flight: window is 1..replayEnd 
 ∧ replayCursor = 1 
 ∧ replayEnd ∈ 0‥c \* over COMMITTED blocks only, 
 ∧ replayPartial ≤ MaxSnapshotLength 
 ∧ IF replayPrepared 
 THEN ∧ replayCut = RequiredReplayCut \* prepared: the sampled cut is 
 ∧ Len(PreparedReplayTail) ≤ ReplayRoom \* still exact (the gate!) and 
 ELSE replayCut = 0) \* the tail fits the blank region 

 NativeSourceSafety ≜ \* NSS: provenance never lies -- 
 ∀ j ∈ 1‥Len(native) : 
 LET owner ≜ native[j].owner IN 
 ∧ (native[j].source = "Retire" ⇒ \* Retire rows: from blocks that 
 ∧ owner ∈ 1‥c \* really are committed 
 ∧ phase[owner] = "Committed") 
 ∧ (native[j].source ∈ {"Append", "Replay"} ⇒ \* streamed/replayed rows: from 
 ∧ owner ∈ Blocks \* committed blocks or the 
 ∧ (∨ owner ∈ 1‥c \* append-only head -- never 
 ∨ ∧ owner = c + 1 \* from mutable speculation 
 ∧ mode[owner] = "AppendOnly")) 
 ∧ (native[j].source = "FailedWrite" ⇒ stopReason = "WriteFailure") \* failure rows only after failing 
 ∧ (native[j].source = "Exit" ⇒ ¬running) \* exit rows only after exiting 

 \* ========================================================================= 
 \* Temporal (action and liveness) properties. 
 \* ========================================================================= 

 HistoryExtension ≜ Prefix(history, history') \* one step never rewrites the ledger 
 HistoryMonotonicity ≜ □[HistoryExtension]_vars \* ... in ANY step: append-only forever 

 NativeEpochStep ≜ \* per step, native either 
 IF epoch' = epoch 
 THEN Prefix(native, native') \* grows at the end (same epoch) 
 ELSE ∧ epoch' = epoch + 1 \* or is wiped exactly when the 
 ∧ native' = ⟨⟩ \* epoch increments (Rebuild) 
 NativeEpochDiscipline ≜ □[NativeEpochStep]_vars \* holds of every step 

 FinalsStayFixed ≜ \* finals are immutable: 
 ∀ i ∈ Blocks : 
 phase[i] ∈ {"Finalized", "Committed"} ⇒ final'[i] = final[i] 
 FinalImmutability ≜ □[FinalsStayFixed]_vars \* once frozen, frozen forever 

 AppendOnlyPrefixStep ≜ \* the append-only contract as 
 ∀ i ∈ Blocks : \* an action property: 
 (mode[i] = "AppendOnly" ∧ phase[i] ∈ {"Queued", "Active"}) 
 ⇒ Prefix(want[i], want'[i]) \* want only ever extends 
 AppendOnlyMonotonicity ≜ □[AppendOnlyPrefixStep]_vars 

 ResizeKeepsLogicalHistoryStep ≜ \* resize logical-neutrality: 
 (width' ≠ width ∨ height' ≠ height) ⇒ \* a geometry change moves 
 ∧ history' = history \* NONE of the semantic state -- 
 ∧ c' = c \* not the ledger, not the 
 ∧ mode' = mode \* frontier, not modes, 
 ∧ want' = want \* speculation, 
 ∧ final' = final \* finals, 
 ∧ emitted' = emitted \* or streamed counters 
 ResizeKeepsLogicalHistory ≜ □[ResizeKeepsLogicalHistoryStep]_vars 

 FailedWriteStops ≜ □( \* fail-stop: a write failure 
 stopReason = "WriteFailure" ⇒ ¬running \* and a live host never coexist 
 ) 

 StoppedStep ≜ ¬running ⇒ UNCHANGED vars \* a stopped host is frozen: 
 StoppedQuiescence ≜ □[StoppedStep]_vars \* every later step stutters 

 AllFinalized ≜ \* every created block is done 
 ∀ i ∈ 1‥CreatedCount : phase[i] ∈ {"Finalized", "Committed"} 
 AllCommitted ≜ \* everything retired, and the 
 ∧ c = CreatedCount \* ledger is exactly the 
 ∧ history = CommittedRows(c, final) \* committed finals 

 FlushLiveness ≜ \* drain guarantee: finalized + 
 (AllFinalized ∧ flush ∧ shutdown ∧ running ∧ ¬Replaying) \* flushing + shutting down 
 ↝ (AllCommitted ∨ ¬running) \* eventually fully commits (or halts) 

 ReplayLiveness ≜ (Replaying ∧ running) ↝ (¬Replaying ∨ ¬running) 
 \* every replay eventually drains (or the host halts trying) 

 QueuedDemand ≜ ∃ i ∈ Blocks : phase[i] = "Queued" \* someone is waiting for space 
 QueuedPressureRetirement ≜ \* pressure + queued demand 
 ∀ i ∈ Blocks : \* eventually sweeps a finalized 
 (∧ running \* head block into history: 
 ∧ ¬Replaying 
 ∧ c = i - 1 \* i is the head, 
 ∧ phase[i] = "Finalized" \* it is done, 
 ∧ Pressure \* space is scarce, 
 ∧ QueuedDemand) \* and someone needs it 
 ↝ (c ≥ i ∨ ¬running) \* => i eventually commits (or halt) 
 \* NB: this needs MaxLive small enough that queued demand implies 
 \* PERSISTENT count pressure; pure row pressure alone can evaporate 
 \* (see the paper's sharpness remark) 

 ==== STENCIL · 2026 