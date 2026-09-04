// candidate-pipeline — run-loop steps 4–6 (model → execute → audit) as an
// orchestration skeleton, gated stage by stage.
//
// Invoke from the workspace root:
//   subagent({ workflowScriptPath: ".pi/workflows/candidate-pipeline.js", cwd: <workspace root> })
//
// Preconditions:
//   - A commitment.json exists for the current run (run-loop step 2) and the
//     baseline (git SHA + integrity hashes) is captured (run-loop step 3).
//
// Documented deviation from AGENTS.md step 5:
//   Patch, compile/smoke gates, the candidate run, and the clean reproduction
//   happen inside ONE isolated modeler task (fresh uv-managed python subprocesses per
//   eval-state discipline), because a raw workflowScript cannot run host
//   commands itself. The supervisor remains free to run steps 4–6 manually.
//
// HARD BOUNDARY — the workflow stops before the deterministic keeper gate
// (run-loop step 7). It never writes terminal states, never dispatches
// paper-writer or the review panel, and never waives any gate: every gate
// failure returns the structured evidence and ends the pipeline.

//
// Gate 0 (pre-research): no modeling starts without a frontier evidence
// packet. literature-scout builds it (papers + cloned code + a baseline that is
// measured or commandable); critical-advisor audits it for toy-work, missing
// pre-research, and minimal-progress stalls. Only substantial_pass advances.
//
const preflight = await runs.run("literature-scout", {
  agent: "literature-scout",
  context: "fresh",
  task: [
    "Gate 0 pre-research for the claimed idea and this run's commitment.json.",
    "Per your profile: search the frontier (arxiv/primary sources), clone and",
    "read the relevant open-source implementations, and state the competitive",
    "baseline as a measured number or an exact reproducible command. Write the",
    "evidence packet to traces/<run_id>/preflight.md. A prose citation list is a",
    "stall, not a packet.",
  ].join("\n"),
  outputSchema: {
    type: "object",
    properties: {
      packet_written: { type: "boolean" },
      cloned_repos: { type: "array", items: { type: "string" } },
      papers_count: { type: "number" },
      baseline_state: { type: "string", enum: ["measured", "commanded", "none"] },
      preflight_path: { type: "string" },
      gaps: { type: "string" },
    },
    required: ["packet_written", "cloned_repos", "papers_count", "baseline_state", "preflight_path", "gaps"],
    additionalProperties: false,
  },
});

const pre = preflight.structuredOutput;
if (!pre || !pre.packet_written || pre.baseline_state === "none") {
  return {
    pipeline_state: "preflight_missing",
    preflight: pre ?? null,
    handoff: preflight.artifactPaths ?? null,
  };
}

const advisor = await runs.run("critical-advisor", {
  agent: "critical-advisor",
  context: "fresh",
  task: [
    "Gate 0 audit of the pre-research packet at " + pre.preflight_path,
    "Per your profile: the packet must contain papers with arxiv ids and method",
    "takeaways, open-source code cloned and read with file-level notes, and a",
    "baseline that is measured or exactly commandable. Verdicts: substantial_pass,",
    "send_back (numbered amendments), reject_toy.",
  ].join("\n"),
  outputSchema: {
    type: "object",
    properties: {
      verdict: { type: "string", enum: ["substantial_pass", "send_back", "reject_toy"] },
      findings: { type: "string" },
      required_amendments: { type: "string" },
    },
    required: ["verdict", "findings", "required_amendments"],
    additionalProperties: false,
  },
});

const adv = advisor.structuredOutput;
if (!adv || adv.verdict !== "substantial_pass") {
  return {
    pipeline_state: adv && adv.verdict === "reject_toy" ? "preflight_rejected_toy" : "preflight_send_back",
    preflight: pre,
    advisor: adv ?? null,
    handoff: preflight.artifactPaths ?? null,
  };
}

const modeling = await runs.run("modeler", {
  agent: "modeler",
  context: "fresh",
  worktree: true,
  task: [
    "Claimed idea → candidate patch, per your profile contract:",
    "0. Read traces/<run_id>/preflight.md (Gate 0 packet) and commitment.json first;",
    "   no packet means preflight: not_passed, stop.",
    "1. Read the highest-priority queued idea and commitment.json for this run.",
    "2. Implement the idea's preregistered method COMPLETELY inside mutable_paths only (scope is bounded by mutable_paths, not by patch size);",
    "   write mutation.json and gate on its integrity result.",
    "3. Compile gate in a fresh uv-managed python subprocess:",
    "   compile(source, 'run.py', 'exec') over your patched file.",
    "4. Smoke check in another fresh uv-managed python subprocess via evaluation.prepare.evaluate.",
    "5. Run the candidate per the experiment profile, then the clean reproduction",
    "   in its own fresh subprocess. Record cost.json and the state manifest.",
    "At most ONE repair round per your contract; a second failure stops the pipeline.",
    "Return the structured gate states exactly; run_root is the directory holding",
    "verification.json for this run.",
  ].join("\n"),
  outputSchema: {
    type: "object",
    properties: {
      verdict: { type: "string", enum: ["gates_passed", "gate_failed", "mutation_rejected"] },
      compile: { type: "string", enum: ["pass", "fail", "not_run"] },
      smoke: { type: "string", enum: ["pass", "fail", "not_run"] },
      execution_state: { type: "string", enum: ["completed", "failed", "not_run"] },
      reproduction_state: { type: "string", enum: ["passed", "failed", "not_run"] },
      run_root: { type: "string" },
      notes: { type: "string" },
    },
    required: ["verdict", "compile", "smoke", "execution_state", "reproduction_state", "run_root", "notes"],
    additionalProperties: false,
  },
});

const m = modeling.structuredOutput;
if (!m || m.verdict !== "gates_passed") {
  return {
    pipeline_state: "modeling_gate_failed",
    modeling: m ?? null,
    handoff: modeling.artifactPaths ?? null,
  };
}
if (m.execution_state !== "completed") {
  return {
    pipeline_state: "execution_error",
    modeling: m,
    handoff: modeling.artifactPaths ?? null,
  };
}
if (m.reproduction_state !== "passed") {
  return {
    pipeline_state: "reproduction_failed",
    modeling: m,
    handoff: modeling.artifactPaths ?? null,
  };
}

const audit = await runs.run("analyst", {
  agent: "analyst",
  context: "fresh",
  task: [
    "Audit verification.json for the completed run produced in the isolated worktree.",
    "Run root: " + m.run_root,
    "Per your profile contract: verdict audit_pass or audit_fail with a numbered",
    "finding list; on audit_fail cite the exact field and observed value.",
    "Report discrepancies; never silently repair anything.",
  ].join("\n"),
  outputSchema: {
    type: "object",
    properties: {
      verdict: { type: "string", enum: ["audit_pass", "audit_fail"] },
      findings: { type: "string" },
    },
    required: ["verdict", "findings"],
    additionalProperties: false,
  },
});

const a = audit.structuredOutput;
return {
  pipeline_state: "audit_" + (a ? a.verdict : "unknown"),
  modeling: m,
  audit: a,
  handoff: modeling.artifactPaths ?? null,
};
