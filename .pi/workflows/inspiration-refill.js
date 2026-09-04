// inspiration-refill — parallel literature-scout evidence lanes, then idea-generator.
//
// Invoke from the workspace root:
//   subagent({ workflowScriptPath: ".pi/workflows/inspiration-refill.js", cwd: <workspace root> })
//
// Preconditions:
//   - Used when archive/ideas.jsonl has fewer than 2 queued ideas (run-loop step 1).
//
// Boundary:
//   - The three scout lanes map 1:1 to the literature-scout contract categories
//     (prior_art / gaps / dead_ends). No query angles are invented here; each
//     scout derives its own retrieval set from navigator/ and archive/ sources.
//   - idea-generator stays the only writer to archive/ideas.jsonl and inspiration.md.

const scoutLane = function (key, focus) {
  return {
    key: key,
    agent: "literature-scout",
    context: "fresh",
    task: [
      "Produce the " + focus + " portion of the literature evidence for this workspace,",
      "exactly per your profile contract: read navigator/ and archive/ sources,",
      "deduplicate against navigator/queries.jsonl, and record the retrieval record.",
      "Return the " + focus + " evidence records as your text output.",
      "Independent judgment only. Do not read or wait on the other scout lanes.",
    ].join("\n"),
  };
};

const lanes = await runs.all([
  scoutLane("scout-prior-art", "prior_art"),
  scoutLane("scout-gaps", "gaps"),
  scoutLane("scout-dead-ends", "dead_ends"),
]);

const categories = ["prior_art", "gaps", "dead_ends"];
const evidence = lanes
  .map(function (result, index) {
    return "## Scout evidence: " + categories[index] + "\n\n" + result.output;
  })
  .join("\n\n---\n\n");

const generation = await runs.run("idea-generator", {
  agent: "idea-generator",
  context: "fresh",
  task: [
    "The idea queue needs a refill. Read archive/ideas.jsonl for the existing set,",
    "then generate new falsifiable candidate ideas per your profile contract,",
    "using the scout evidence below as the only external input.",
    "Run your own dedup pass against existing ideas first.",
    "Then append accepted ideas (status: \"queued\") to archive/ideas.jsonl and",
    "rewrite inspiration.md with a one-line summary per accepted idea.",
    "Each idea must predict a delta on the evaluator's main metric with direction",
    "and magnitude, and must respect the local-only profile constraints.",
    "",
    evidence,
  ].join("\n"),
});

return {
  scouts: {
    prior_art: lanes[0].output,
    gaps: lanes[1].output,
    dead_ends: lanes[2].output,
  },
  idea_generator: generation.output,
  generation_artifacts: generation.artifactPaths ?? null,
};
