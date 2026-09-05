import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFileSync } from "node:child_process";
import { appendFileSync, cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";

// Research Flywheel worker entry.
// dispatch_role_agent is the worker spawn path.
// Operating context lives in .pi/SYSTEM.md.
// SYSTEM.md loads once as session customPrompt.
// The template root carries no AGENTS.md.
// Worker worktrees still receive their role preset as root AGENTS.md.

function resultOf(response: any): any {
  return response?.result ?? response;
}

function orca(cwd: string, args: string[]): any {
  return JSON.parse(execFileSync("orca", [...args, "--json"], { cwd, encoding: "utf8" }));
}

function roleProfile(cwd: string, role: string): string {
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(role)) throw new Error(`invalid role: ${role}`);
  const path = join(cwd, ".agents", "roles", `${role}.md`);
  if (!existsSync(path)) throw new Error(`role profile not found: .agents/roles/${role}.md`);
  return readFileSync(path, "utf8");
}

function workerName(role: string, requested?: string): string {
  const value = requested ?? `${role}-${Date.now()}`;
  const name = value.replace(/[^A-Za-z0-9._-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 64);
  if (!name) throw new Error("worker name is empty");
  return name;
}

function worktreeOf(response: any): { id: string; path: string } {
  const result = resultOf(response);
  const worktree = result?.worktree ?? result;
  const id = worktree?.id ?? worktree?.worktreeId;
  const path = worktree?.path;
  if (typeof id !== "string" || typeof path !== "string") throw new Error("Orca worktree response is incomplete");
  return { id, path };
}

function terminalOf(response: any): string {
  const result = resultOf(response);
  const handles = [
    result?.handle,
    result?.terminal?.handle,
    result?.startupTerminal?.handle,
    result?.agentTerminalHandle,
    result?.terminalHandle,
    ...(Array.isArray(result?.terminals) ? result.terminals.map((item: any) => item?.handle) : []),
  ];
  const handle = handles.find((value) => typeof value === "string");
  if (typeof handle !== "string") throw new Error("Orca terminal response has no handle");
  return handle;
}

function listWorktrees(cwd: string): any[] {
  try {
    const result = resultOf(orca(cwd, ["worktree", "list"]));
    const worktrees = result?.worktrees ?? result;
    return Array.isArray(worktrees) ? worktrees : [];
  } catch {
    return [];
  }
}

function sleepMs(ms: number): void {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function findWorktreeBySuffix(cwd: string, suffix: string): { id: string; path: string } | null {
  for (const candidate of listWorktrees(cwd)) {
    const path = candidate?.path;
    if (typeof path !== "string" || !path.endsWith(suffix)) continue;
    const id = candidate?.id;
    if (typeof id !== "string") continue;
    return { id, path };
  }
  return null;
}

// Orca materializes the checkout asynchronously: the create call returns
// (or drops) before `worktree list` shows the new entry. Poll until the
// suffix appears instead of trusting a single list call.
function waitForWorktreeByName(cwd: string, name: string, timeoutMs = 120000): { id: string; path: string } | null {
  const base = cwd.split("/").filter(Boolean).pop() ?? "";
  const suffix = `/${base}/${name}`;
  const deadline = Date.now() + timeoutMs;
  for (;;) {
    const found = findWorktreeBySuffix(cwd, suffix);
    if (found) return found;
    if (Date.now() >= deadline) return null;
    sleepMs(1500);
  }
}

function listTerminals(cwd: string, worktreeId: string): any[] {
  try {
    const result = resultOf(orca(cwd, ["terminal", "list", "--worktree", `id:${worktreeId}`]));
    const terminals = result?.terminals ?? result;
    return Array.isArray(terminals) ? terminals : [];
  } catch {
    return [];
  }
}

function closeTerminal(cwd: string, handle: string): void {
  orca(cwd, ["terminal", "close", "--terminal", handle]);
}

function injectContext(source: string, target: string, profile: string): void {
  rmSync(join(target, ".pi"), { recursive: true, force: true });
  rmSync(join(target, ".agents"), { recursive: true, force: true });
  mkdirSync(join(target, ".pi", "extensions"), { recursive: true });
  cpSync(join(source, ".pi", "settings.json"), join(target, ".pi", "settings.json"));
  const npmSource = join(source, ".pi", "npm");
  if (existsSync(npmSource)) cpSync(npmSource, join(target, ".pi", "npm"), { recursive: true });
  cpSync(join(source, ".pi", "extensions"), join(target, ".pi", "extensions"), { recursive: true });
  cpSync(join(source, ".agents", "roles"), join(target, ".agents", "roles"), { recursive: true });
  writeFileSync(join(target, "AGENTS.md"), profile.endsWith("\n") ? profile : `${profile}\n`);
}

// Worker goal and todos are created by the scheduler process, not by the
// worker model. After the worker Pi reaches idle, dispatch sends one
// follow-up user message that instructs the model to call create_goal with
// the exact objective below, then the exact todo list, then do the station
// work. The model fills in evidence and results; it never invents the goal
// or the step list.
function goalObjective(station: string, task: string): string {
  const text = task.replace(/"/g, "'");
  return `[${station}] ${text}`;
}

function todoSeed(station: string, ideaId: string, runDir: string): Array<{ content: string; status: string; activeForm: string }> {
  const steps: Array<[string, string]> = (() => {
    switch (station) {
      case "scout":
        return [
          ["Survey literature and record frontier-notes.md", "Surveying literature"],
          ["Pull local evidence into research/", "Pulling local evidence"],
          ["Design evaluation contract", "Designing evaluation contract"],
          ["Append idea line and write station-result.txt DONE", "Writing idea line"],
        ];
      case "modeling":
        return [
          ["Write natural-language derivation", "Writing derivation"],
          ["Formalize Lean proof and run lean", "Formalizing Lean proof"],
          ["Implement method in experiment/", "Implementing method"],
          ["Write evaluator in evaluation/ and station-result.txt DONE", "Writing evaluator"],
        ];
      case "experiment":
        return [
          ["Run baseline through evaluator", "Running baseline"],
          ["Run candidate through evaluator", "Running candidate"],
          ["Record traces and write station-result.txt DONE", "Recording traces"],
        ];
      case "evaluation":
        return [
          ["Measure every objective and constraint", "Measuring objectives"],
          ["Apply pass rule and write verdict.md plus station-result.txt DONE", "Writing verdict"],
        ];
      case "writing":
        return [
          ["Draft report with traced numbers", "Drafting report"],
          ["Preserve open questions and write station-result.txt DONE", "Preserving open questions"],
        ];
      case "review":
        return [
          ["Check number traceability and verdict match", "Checking traceability"],
          ["Return verdict line plus findings and station-result.txt DONE", "Returning verdict"],
        ];
      case "archive":
        return [
          ["Place paper or archive failure", "Placing paper"],
          ["Append ledger line and write station-result.txt DONE", "Appending ledger"],
        ];
      default:
        return [[`Complete ${station} station`, `Completing ${station}`]];
    }
  })();
  return steps.map(([content, activeForm], index) => ({
    content: `[${ideaId}/${station}] ${content} (${runDir})`,
    status: index === 0 ? "in_progress" : "pending",
    activeForm,
  }));
}

function kickoffMessage(station: string, ideaId: string, runDir: string, objective: string, todos: Array<{ content: string; status: string; activeForm: string }>): string {
  const lines = [
    `Station ${station} for idea ${ideaId}. Run these tool calls first, in order, before any other work.`,
    `1. Call create_goal with objective exactly: ${objective}`,
    `2. Call todo with exactly this JSON array: ${JSON.stringify(todos)}`,
    `3. Do the station work in ${runDir}.`,
    `4. Write station-result.txt with first line DONE or FAILED.`,
    `5. Call update_goal with status complete.`,
    `Do not invent a different goal or step list.`,
  ];
  return lines.join("\n").replace(/"/g, "'");
}

// Production chain: idea id in, full station brief out.
// The scheduler passes idea plus prior station output.
// The plugin reads the idea record and builds the seven-section brief.
const STATION_ROLE: Record<string, string> = {
  scout: "researcher",
  modeling: "implementer",
  experiment: "operator",
  evaluation: "operator",
  writing: "writer",
  review: "reviewer",
  archive: "worker",
};

function readIdeas(cwd: string): any[] {
  const path = join(cwd, ".agents", "ideas.jsonl");
  if (!existsSync(path)) return [];
  return readFileSync(path, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

function findIdea(cwd: string, id: string): any {
  const idea = readIdeas(cwd).find((entry) => entry?.id === id);
  if (!idea) throw new Error(`idea not found: ${id}`);
  if (!Array.isArray(idea.evidence) || idea.evidence.length === 0) throw new Error(`idea ${id} has empty evidence`);
  if (!idea.evaluation?.objectives?.length) throw new Error(`idea ${id} has empty evaluation.objectives`);
  if (!idea.done_when) throw new Error(`idea ${id} misses done_when`);
  return idea;
}

function evaluationSummary(idea: any): string {
  const objectives = (idea.evaluation.objectives ?? []).map((o: any) => `${o.metric} ${o.direction} epsilon ${o.epsilon} baseline ${o.baseline} evaluator ${o.evaluator}`).join("; ");
  const constraints = (idea.evaluation.constraints ?? []).map((c: any) => c.check ?? c.description ?? JSON.stringify(c)).join("; ");
  return `objectives: ${objectives}. constraints: ${constraints || "none"}. pass_rule: ${idea.evaluation.pass_rule ?? "all"}.`;
}

function stationHow(station: string, _idea: any, runDir: string): string {
  switch (station) {
    case "modeling":
      return `1. Read the idea record and every evidence path. 2. Write natural language derivation to ${runDir}/derivation.md. 3. Formalize with lean to ${runDir}/proof.lean and run lean until it passes. 4. Implement the method in experiment/ as named by the idea. 5. Write the evaluator named in the idea evaluation contract into evaluation/.`;
    case "experiment":
      return `1. Read the idea record and modeling output. 2. Run the baseline and candidate through the evaluator. 3. Record raw outputs and traces to ${runDir}/. 4. Report every objective value with baseline and delta.`;
    case "evaluation":
      return `1. Read the idea record and experiment traces. 2. Run the evaluation contract: every objective gets a measured value, every constraint gets pass or fail. 3. Apply the pass rule. 4. Write verdict with numbers to ${runDir}/verdict.md.`;
    case "writing":
      return `1. Read the idea record, derivation, traces, and verdict. 2. Cite every number to its trace file. 3. Write the report to papers/ or ${runDir}/ as named in Prior. 4. Preserve open questions.`;
    case "review":
      return `1. Read the report, every trace, and the idea evaluation contract. 2. Check every number traces to a file. 3. Check method supports conclusion and verdict matches measured values. 4. Return verdict line plus numbered findings.`;
    case "archive":
      return `1. Read the review verdict and Prior artifact paths. 2. On keep, place the paper under papers/ with a fixed name. 3. On failure, move traces and report under .agents/archive/<idea-id>/. 4. Append one ledger line to .agents/ledger.jsonl with idea id, verdict, and artifact paths.`;
    default:
      return `Complete the ${station} station. Write artifacts to ${runDir}/.`;
  }
}

function stationDoneWhen(station: string, runDir: string): string {
  switch (station) {
    case "modeling":
      return `${runDir}/derivation.md exists, lean proof passes, implementation and evaluator exist.`;
    case "experiment":
      return `${runDir}/ traces exist with objective values, baselines, and deltas.`;
    case "evaluation":
      return `${runDir}/verdict.md exists with per-objective values, per-constraint verdicts, and overall verdict.`;
    case "writing":
      return `Report exists at the requested path with every number cited to a trace.`;
    case "review":
      return `Review verdict line plus numbered findings returned, each naming report section and discrepancy.`;
    case "archive":
      return `Paper placed or archive moved, ledger line appended, paths returned.`;
    default:
      return `${runDir}/ artifacts exist.`;
  }
}

function buildStationBrief(cwd: string, station: string, idea: any, prior: string, extra: string): { brief: string; runDir: string } {
  const runDir = join(cwd, ".agents", "runs", idea.id, station);
  mkdirSync(runDir, { recursive: true });
  const relRunDir = `.agents/runs/${idea.id}/${station}`;
  const evidencePaths = [...(idea.evidence ?? []), ...(idea.evaluation?.objectives ?? []).map((o: any) => o.evaluator)].filter(Boolean).join(", ");
  const brief = [
    `Why: Run ${station} station for idea ${idea.id}. ${idea.question}`,
    `Background: Hypothesis: ${idea.hypothesis} Method: ${idea.method} Evaluation: ${evaluationSummary(idea)}`,
    `Prior: ${prior}`,
    `How: ${stationHow(station, idea, relRunDir)}${extra ? ` Extra: ${extra}` : ""} Write ${relRunDir}/station-result.txt with first line DONE plus one-line summary, or FAILED plus cause. Sync-back: copy ${relRunDir}/ artifacts to this worktree ${relRunDir}/ with cp, or report FAILED when nothing was produced.`,
    `Evidence: ${evidencePaths}`,
    `Done when: ${stationDoneWhen(station, relRunDir)} ${relRunDir}/station-result.txt first line starts with DONE. Idea done_when: ${idea.done_when}`,
    `Failure Done: State attempted steps, observed output, cause, and next station or manual flag. Write partial artifacts to ${relRunDir}/.`,
  ].join("\n");
  return { brief, runDir };
}

function buildScoutBrief(direction: string): string {
  return [
    `Why: Seed the flywheel with the first grounded idea for this direction.`,
    `Background: User direction: ${direction} Frontier constraints unknown until scout pulls evidence.`,
    `Prior: No prior run. This is the seed round.`,
    `How: 1. Search current literature with web_search: at least 2 queries on the direction, read at least 2 primary sources (papers, docs, or upstream repos), record URLs plus one-line findings each. 2. Inspect local frontier sources for the direction (code, data, evaluator, contract). 3. Pull all evidence into research/: web findings go to research/frontier-notes.md with URLs, local artifacts are copied or referenced by path. 4. Design the evaluation contract with objectives, constraints, and pass rule. 5. Append one idea line to .agents/ideas.jsonl following .agents/idea-schema.md. Write .agents/runs/scout/station-result.txt with first line DONE plus idea id, or FAILED plus cause. The idea evidence array must include research/frontier-notes.md plus local evidence paths. Sync-back: copy the idea line and any research/ artifacts to the scheduler worktree listed in Evidence, or report FAILED when nothing was produced.`,
    `Evidence: research/ paths created by this station. Scheduler worktree for sync-back is named in the dispatch notice.`,
    `Done when: One idea line exists in .agents/ideas.jsonl with non-empty evidence including research/frontier-notes.md, evaluation.objectives, and done_when. station-result.txt first line starts with DONE.`,
    `Failure Done: State attempted sources (web queries plus local paths), observed gap, cause, and manual flag. No empty idea record.`,
  ].join("\n");
}

function removeUserGuide(cwd: string): void {
  const readmePath = join(cwd, "README.md");
  if (existsSync(readmePath)) rmSync(readmePath);
}

function seedWorktreeForStation(cwd: string, worktreePath: string, station: string, ideaId?: string): void {
  if (station === "scout") return;
  const relRunDir = `.agents/runs/${ideaId}/${station}`;
  mkdirSync(join(worktreePath, relRunDir), { recursive: true });
  const copyInto = (rel: string): void => {
    const src = join(cwd, rel);
    if (!existsSync(src)) return;
    cpSync(src, join(worktreePath, rel), { recursive: true });
  };
  copyInto(`.agents/runs/${ideaId}`);
  const idea = readIdeas(cwd).find((entry) => entry?.id === ideaId);
  for (const p of [...(idea?.evidence ?? []), ...(idea?.evaluation?.objectives ?? []).map((o: any) => o.evaluator), "papers"]) {
    if (typeof p === "string") copyInto(p);
  }
}

function readStationResult(cwd: string, ideaId: string, station: string): { status: string; detail: string } {
  const runDir = join(cwd, ".agents", "runs", ideaId, station);
  if (!existsSync(runDir)) return { status: "missing", detail: `${runDir} absent` };
  const verdictFile = join(runDir, "verdict.md");
  const statusFile = join(runDir, "station-result.txt");
  if (existsSync(statusFile)) {
    const first = readFileSync(statusFile, "utf8").split("\n").find(Boolean) ?? "";
    const status = first.trim().toUpperCase();
    if (status.startsWith("FAILED")) return { status: "failed", detail: first };
    return { status: "done", detail: first || "worker-reported completion" };
  }
  if (existsSync(verdictFile)) {
    const head = readFileSync(verdictFile, "utf8").slice(0, 400);
    return /fail/i.test(head.slice(0, 80)) ? { status: "failed", detail: head } : { status: "done", detail: head };
  }
  return { status: "unknown", detail: `${runDir} exists but carries no verdict` };
}

function dispatchStation(cwd: string, station: string, opts: { idea?: string; prior?: string; direction?: string; extra?: string; name?: string }): object {
  if (!STATION_ROLE[station]) throw new Error(`unknown station: ${station}`);
  const role = STATION_ROLE[station];
  const name = opts.name;
  if (station === "scout") {
    const direction = (opts.direction ?? "").trim();
    if (!direction) throw new Error("scout station needs direction");
    const brief = buildScoutBrief(direction.replace(/"/g, "'"));
    const dispatched: any = dispatchRoleAgent(cwd, role, brief, station, "seed", ".agents/runs/scout", name ?? `scout-${Date.now()}`);
    const { role: _role, ...rest } = dispatched;
    return { station, role, direction, ...rest };
  }
  const ideaId = (opts.idea ?? "").trim();
  const prior = (opts.prior ?? "").trim();
  if (!ideaId) throw new Error(`${station} station needs idea`);
  if (!prior) throw new Error(`${station} station needs prior`);
  const idea = findIdea(cwd, ideaId);
  const { brief } = buildStationBrief(cwd, station, idea, prior.replace(/"/g, "'"), (opts.extra ?? "").replace(/"/g, "'"));
  const dispatched: any = dispatchRoleAgent(cwd, role, brief, station, ideaId, `.agents/runs/${ideaId}/${station}`, name ?? `${station}-${ideaId}`, (worktreePath) =>
    seedWorktreeForStation(cwd, worktreePath, station, ideaId),
  );
  const { role: _role, ...rest } = dispatched;
  return { station, role, idea: ideaId, ...rest };
}

function repoIdOf(cwd: string): string | null {
  try {
    const current = resultOf(orca(cwd, ["worktree", "current"]));
    const id = current?.worktree?.repoId;
    return typeof id === "string" ? id : null;
  } catch {
    return null;
  }
}

function dispatchRoleAgent(cwd: string, role: string, task: string, station: string, ideaId: string, runDir: string, requestedName?: string, setup?: (worktreePath: string) => void): object {
  const trimmed = task.trim();
  if (!trimmed) throw new Error("task is empty");
  for (const section of ["Why:", "Background:", "Prior:", "How:", "Evidence:", "Done when:", "Failure Done:"]) {
    if (!trimmed.includes(section)) throw new Error(`Task brief misses ${section}`);
  }
  const profile = roleProfile(cwd, role);
  const name = workerName(role, requestedName);

  // Stage 1: create the worktree. Orca's runtime drops the response right after
  // materializing the checkout plus a fallback shell terminal, so the JSON call
  // returns ok:false (runtime_unavailable) while the worktree does land. Tolerate
  // that, then adopt the created worktree by path suffix.
  const repoId = repoIdOf(cwd);
  const createArgs = repoId
    ? ["worktree", "create", "--repo", `id:${repoId}`, "--name", name, "--setup", "skip"]
    : ["worktree", "create", "--name", name, "--setup", "skip"];
  try {
    orca(cwd, createArgs);
  } catch {
    /* runtime drop is expected; adopt below */
  }
  const adopted = waitForWorktreeByName(cwd, name);
  if (!adopted) throw new Error(`worktree ${name} did not materialize within 120s`);
  const worktree = { id: adopted.id, path: adopted.path };

  // Stage 2: inject context before any agent starts.
  injectContext(cwd, worktree.path, profile);
  if (setup) setup(worktree.path);

  // Stage 3: start pi in a dedicated terminal, not the fallback shell.
  // The kickoff message carries the exact create_goal objective plus the
  // exact todo list. The worker model executes those tool calls first.
  const objective = goalObjective(station, trimmed);
  const todos = todoSeed(station, ideaId, runDir);
  const kickoff = kickoffMessage(station, ideaId, runDir, objective, todos);
  const terminal = terminalOf(orca(cwd, ["terminal", "create", "--worktree", `id:${worktree.id}`, "--command", "pi --approve"]));
  orca(cwd, ["terminal", "wait", "--terminal", terminal, "--for", "tui-idle", "--timeout-ms", "60000"]);
  orca(cwd, ["terminal", "send", "--terminal", terminal, "--text", kickoff, "--enter"]);

  // Stage 4: close the fallback shell created by worktree create.
  for (const item of listTerminals(cwd, worktree.id)) {
    const handle = typeof item?.handle === "string" ? item.handle : "";
    if (handle && handle !== terminal) closeTerminal(cwd, handle);
  }

  return { role, task: trimmed, worktree, terminal };
}

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_event, ctx) => {
    if (!ctx.hasUI) return;
    const ideasPath = join(ctx.cwd, ".agents", "ideas.jsonl");
    let ideaCount = 0;
    try {
      if (existsSync(ideasPath)) {
        ideaCount = readFileSync(ideasPath, "utf8").split("\n").filter(Boolean).length;
      }
    } catch { /* empty queue reads as zero */ }
    ctx.ui.notify(
      [
        "Research Flywheel ready.",
        `Idea pool: ${ideaCount} queued in .agents/ideas.jsonl.`,
        "Start: /bootstrap — seed the first idea, or resume the flywheel loop.",
      ].join("\n"),
      "info",
    );
  });

  pi.registerCommand("bootstrap", {
    description: "Seed the first idea and start the flywheel",
    handler: async (args, ctx) => {
      const argDirection = (args ?? "").trim();
      if (argDirection) {
        const details: any = dispatchStation(ctx.cwd, "scout", { direction: argDirection });
        removeUserGuide(ctx.cwd);
        ctx.ui.notify(`Scout dispatched. Worktree: ${details?.worktree?.path ?? "unknown"}. Removed README.md (user guide); workspace is now agent-only. After scout writes the idea, run /flywheel <idea-id>.`, "info");
        return;
      }
      if (!ctx.hasUI) {
        ctx.ui.notify("Non-interactive mode: run /bootstrap <direction>.", "error");
        return;
      }
      const field = (await ctx.ui.input("研究领域 / 方向", "例如: 稀疏注意力 kernel 优化"))?.trim();
      if (!field) { ctx.ui.notify("Bootstrap cancelled: no field.", "warning"); return; }
      const question = (await ctx.ui.input("第一个研究问题", "例如: 能否降低 HBM 流量并保持 fp32 数值对齐"))?.trim();
      if (!question) { ctx.ui.notify("Bootstrap cancelled: no question.", "warning"); return; }
      const constraints = (await ctx.ui.input("已知约束（可空，回车跳过）", "例如: 数值必须匹配 fp32 reference"))?.trim();
      const composed = `field: ${field}; question: ${question}; constraints: ${constraints || "none"}`;
      const ok = await ctx.ui.confirm("确认派发 scout", `${composed}\n\n派发 scout 拉证据并写入第一条 idea？`);
      if (!ok) { ctx.ui.notify("Bootstrap cancelled.", "warning"); return; }
      const details: any = dispatchStation(ctx.cwd, "scout", { direction: composed });
      removeUserGuide(ctx.cwd);
      ctx.ui.notify(`Scout dispatched. Worktree: ${details?.worktree?.path ?? "unknown"}. 已移除 README.md（用户向说明），工作区进入纯 agent 运行态。Scout 写入 idea 后运行 /flywheel <idea-id> 推进。`, "info");
    },
  });

  pi.registerCommand("flywheel", {
    description: "Advance one idea through the production chain",
    handler: async (args, ctx) => {
      const ideaId = (args ?? "").trim().split(/\s+/)[0] ?? "";
      if (!ideaId) {
        ctx.ui.notify("Run /flywheel <idea-id>: reports the next station and its prior text.", "info");
        return;
      }
      try {
        const idea = findIdea(ctx.cwd, ideaId);
        const order = ["modeling", "experiment", "evaluation", "writing", "review", "archive"];
        let next = order[0];
        let prior = `Idea record ${idea.id}: ${idea.question} Hypothesis: ${idea.hypothesis} Method: ${idea.method} Evidence: ${(idea.evidence ?? []).join(", ")}.`;
        for (const station of order) {
          const result = readStationResult(ctx.cwd, idea.id, station);
          if (result.status === "done") {
            prior = `Station ${station} done: ${result.detail}. Run dir: .agents/runs/${idea.id}/${station}/.`;
            continue;
          }
          if (result.status === "failed") {
            ctx.ui.notify(`Idea ${idea.id} blocked at ${station}: ${result.detail}`, "error");
            return;
          }
          next = station;
          break;
        }
        ctx.ui.notify(`Idea ${idea.id}: next station ${next}. Prior: ${prior}`, "info");
      } catch (error: any) {
        ctx.ui.notify(`Flywheel advance failed: ${error?.message ?? error}`, "error");
      }
    },
  });

  pi.registerTool({
    name: "dispatch_station",
    label: "Dispatch production station",
    description: "Build a full station brief from an idea record and dispatch it. Scout seeds the idea pool from a direction; modeling, experiment, evaluation, writing, review, archive run in order on an idea id with prior station output.",
    parameters: {
      type: "object",
      properties: {
        station: { type: "string", enum: ["scout", "modeling", "experiment", "evaluation", "writing", "review", "archive"], description: "Production station to run. Scout needs direction. All others need idea and prior." },
        idea: { type: "string", description: "Idea id from .agents/ideas.jsonl. Required for every station except scout." },
        direction: { type: "string", description: "User research direction, required for scout." },
        prior: { type: "string", description: "Prior station output: cause, artifact paths, numbers. Required for every station except scout." },
        extra: { type: "string", description: "Optional extra instructions appended to How." },
        name: { type: "string", description: "Optional Orca worktree name." },
      },
      required: ["station"],
      additionalProperties: false,
    },
    async execute(_toolCallId, input: any, _signal, _onUpdate, ctx) {
      const details = dispatchStation(ctx.cwd, input.station, input);
      return { content: [{ type: "text", text: JSON.stringify(details, null, 2) }], details };
    },
  });

  pi.registerTool({
    name: "station_result",
    label: "Read station result",
    description: "Read one station run dir for an idea and report done, failed, missing, or unknown. Unknown means artifacts exist but no verdict file; treat it as worker drift.",
    parameters: {
      type: "object",
      properties: {
        station: { type: "string", enum: ["scout", "modeling", "experiment", "evaluation", "writing", "review", "archive"], description: "Station to inspect." },
        idea: { type: "string", description: "Idea id from .agents/ideas.jsonl." },
      },
      required: ["station", "idea"],
      additionalProperties: false,
    },
    async execute(_toolCallId, input: any, _signal, _onUpdate, ctx) {
      const result = readStationResult(ctx.cwd, input.idea, input.station);
      return { content: [{ type: "text", text: JSON.stringify({ station: input.station, idea: input.idea, ...result }, null, 2) }], details: result };
    },
  });

  pi.registerTool({
    name: "flywheel_tick",
    label: "Advance the flywheel",
    description: "Read .agents/ideas.jsonl plus one idea run dir, then report the next station to dispatch and its prior. Queued ideas start at modeling after scout produced the record; stations advance only when prior station reads done.",
    parameters: {
      type: "object",
      properties: {
        idea: { type: "string", description: "Idea id to advance." },
      },
      required: ["idea"],
      additionalProperties: false,
    },
    async execute(_toolCallId, input: any, _signal, _onUpdate, ctx) {
      const idea = findIdea(ctx.cwd, input.idea);
      const order = ["modeling", "experiment", "evaluation", "writing", "review", "archive"];
      let next = order[0];
      let prior = `Idea record ${idea.id}: ${idea.question} Hypothesis: ${idea.hypothesis} Method: ${idea.method} Evidence: ${(idea.evidence ?? []).join(", ")}.`;
      for (const station of order) {
        const result = readStationResult(ctx.cwd, idea.id, station);
        if (result.status === "done") {
          prior = `Station ${station} done: ${result.detail}. Run dir: .agents/runs/${idea.id}/${station}/.`;
          continue;
        }
        if (result.status === "failed") {
          return { content: [{ type: "text", text: JSON.stringify({ idea: idea.id, blocked: station, detail: result.detail }, null, 2) }], details: { blocked: true } };
        }
        next = station;
        break;
      }
      return { content: [{ type: "text", text: JSON.stringify({ idea: idea.id, next, prior }, null, 2) }], details: { next } };
    },
  });

  pi.registerTool({
    name: "station_ledger_append",
    label: "Append ledger line",
    description: "Append one JSON line to .agents/ledger.jsonl with idea id, station, verdict, and artifact paths.",
    parameters: {
      type: "object",
      properties: {
        idea: { type: "string", description: "Idea id." },
        station: { type: "string", description: "Station name." },
        verdict: { type: "string", description: "done or failed plus short reason." },
        artifacts: { type: "string", description: "Comma-separated artifact paths." },
      },
      required: ["idea", "station", "verdict"],
      additionalProperties: false,
    },
    async execute(_toolCallId, input: any, _signal, _onUpdate, ctx) {
      const line = JSON.stringify({ idea: input.idea, station: input.station, verdict: input.verdict, artifacts: input.artifacts ?? "", at: new Date().toISOString() });
      appendFileSync(join(ctx.cwd, ".agents", "ledger.jsonl"), `${line}\n`);
      return { content: [{ type: "text", text: line }] };
    },
  });

  pi.registerTool({
    name: "dispatch_role_agent",
    label: "Dispatch role agent",
    description: "Create an Orca worktree, inject .agents/roles/<role>.md as AGENTS.md, and start Pi there with a fixed station goal plus todo list. The task brief carries Why, Background, Prior, How, Evidence, Done when, Failure Done. Section headers are required.",
    parameters: {
      type: "object",
      properties: {
        role: { type: "string", description: "Role profile name under .agents/roles" },
        task: { type: "string", description: "Full worker brief: Why, Background, Prior with cause and artifact paths, How, Evidence paths, Done when, Failure Done. Section headers are required." },
        station: { type: "string", description: "Station name used for the fixed goal objective and todo list." },
        idea: { type: "string", description: "Idea id used for the fixed goal objective and todo list." },
        runDir: { type: "string", description: "Station run dir used for the fixed todo list." },
        name: { type: "string", description: "Optional Orca worktree name" },
      },
      required: ["role", "task", "station", "idea", "runDir"],
      additionalProperties: false,
    },
    async execute(_toolCallId, input: any, _signal, _onUpdate, ctx) {
      const details = dispatchRoleAgent(ctx.cwd, input.role, input.task, input.station, input.idea, input.runDir, input.name);
      return { content: [{ type: "text", text: JSON.stringify(details, null, 2) }], details };
    },
  });
}
