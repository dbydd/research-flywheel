// review-panel — parallel review panel for a keeper run, then meta-reviewer aggregation.
//
// Invoke from the workspace root:
//   subagent({ workflowScriptPath: ".pi/workflows/review-panel.js", cwd: <workspace root> })
//
// Preconditions:
//   - reports/report.md exists for a keeper run (paper-writer already completed).
//
// Boundary:
//   - Aggregates panel verdicts only. It never touches the deterministic keeper
//     gate, terminal states, or archive — those belong to the flywheel runtime.

const reportPath = "reports/report.md";

const panel = await runs.all([
  {
    key: "methodology",
    agent: "reviewer-methodology",
    context: "fresh",
    task: [
      "Read " + reportPath + " and the evidence it references in this workspace.",
      "Produce your methodology-perspective verdict exactly per your profile contract:",
      "a verdict line, then numbered findings with report section references.",
      "Independent judgment only. Do not read or wait on the other panel members.",
    ].join("\n"),
  },
  {
    key: "skeptic",
    agent: "reviewer-skeptic",
    context: "fresh",
    task: [
      "Read " + reportPath + " and the evidence it references in this workspace.",
      "Produce your adversarial-perspective verdict exactly per your profile contract:",
      "a verdict line, then numbered findings with report section references.",
      "Independent judgment only. Do not read or wait on the other panel members.",
    ].join("\n"),
  },
  {
    key: "reproducibility",
    agent: "reviewer-reproducibility",
    context: "fresh",
    task: [
      "Read " + reportPath + " and the evidence it references in this workspace.",
      "Produce your reproducibility-perspective verdict exactly per your profile contract:",
      "re-run the reference command, compare against the reported result, and give",
      "a verdict line plus numbered findings. Independent judgment only.",
    ].join("\n"),
  },
]);

const lanes = ["methodology", "skeptic", "reproducibility"];
const verdicts = panel
  .map(function (result, index) {
    return "## Panel: " + lanes[index] + "\n\n" + result.output;
  })
  .join("\n\n---\n\n");

const meta = await runs.run("meta-reviewer", {
  agent: "meta-reviewer",
  context: "fresh",
  task: [
    "Three independent reviewer verdicts for " + reportPath + " follow below.",
    "Aggregate them per your profile contract: write reports/review.md and produce",
    "the final review verdict plus the Elo-style review_vote.",
    "You may downweight unsupported findings, but never invent findings that no",
    "reviewer raised, and never overturn a verdict without citing the specific",
    "panel text it contradicts.",
    "",
    verdicts,
  ].join("\n"),
});

return {
  panel: {
    methodology: panel[0].output,
    skeptic: panel[1].output,
    reproducibility: panel[2].output,
  },
  meta: meta.output,
  meta_artifacts: meta.artifactPaths ?? null,
};
