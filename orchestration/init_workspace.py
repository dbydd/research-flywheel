"""Initialize the repository baseline and first run evidence for the reference profile.

This script does not pretend to be an OMP tool. It is the human/scaffold step that:

1. Initializes a Git repository when missing.
2. Records the integrity-path hashes that the contract requires.
3. Captures the baseline evaluator result for delta calculations.
4. Seeds `archive/ideas.jsonl` with one exploratory idea.
5. Writes `status.md` for human review.

Run from the workspace root:

    python orchestration/init_workspace.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
INTEGRITY_PATHS = [
    "program.md",
    "evaluation/prepare.py",
    "capabilities/registry.json",
]
ARTIFACT_PATHS = [
    ".omp/config.yml",
    "AGENTS.md",
    "QUEST.md",
    "evaluation/prepare.py",
    "experiment/run.py",
    "capabilities/registry.json",
    "program.md",
]


def run(cmd: list[str], cwd: Path) -> str:
    completed = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def hash_file(relative: str) -> str:
    digest = hashlib.sha256(WORKSPACE.joinpath(relative).read_bytes()).hexdigest()
    return f"sha256:{digest}"


def ensure_repo() -> None:
    if (WORKSPACE / ".git").exists():
        return
    run(["git", "init", "--initial-branch=main"], WORKSPACE)
    run(["git", "config", "user.email", "research-flywheel@local"], WORKSPACE)
    run(["git", "config", "user.name", "Research Flywheel"], WORKSPACE)


def record_baseline() -> dict:
    ensure_repo()
    integrity = {path: hash_file(path) for path in INTEGRITY_PATHS}
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "git": {
            "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"], WORKSPACE) or "main",
            "head": run(["git", "rev-parse", "HEAD"], WORKSPACE),
        },
        "integrity_paths": INTEGRITY_PATHS,
        "integrity_hashes": integrity,
    }


def commit_baseline() -> None:
    run(["git", "add", *ARTIFACT_PATHS, "orchestration/init_workspace.py"], WORKSPACE)
    run(["git", "commit", "-m", "chore: scaffold research flywheel reference workspace"], WORKSPACE)


def run_evaluator(reference_run: str) -> dict:
    sys.path.insert(0, str(WORKSPACE))
    from evaluation.prepare import evaluate, load_data

    data = load_data()
    targets = [target for _, target in data]
    predictions = [float(target) for _, target in data]
    metrics = evaluate(predictions, targets)
    return {
        "run_id": reference_run,
        "metric_main": metrics,
        "metric_aux": {"samples": len(data), "description": "identity baseline"},
    }


def write_status(run_id: str, baseline: dict) -> None:
    status = WORKSPACE / "status.md"
    status.write_text(
        f"""# Research Flywheel Status

## Latest run
- run_id: {run_id}
- phase: archive
- outcome: keep
- profile: reference-linear-regression
- recorded_at: {baseline['captured_at']}

## Pending actions
- None.

## Open questions
1. First production domain profile and its native evaluator.
2. External-report and major-route human sampling strategy.
3. Long-running checkpoint granularity and runtime deadline design.
4. Real-remote-endpoint data-exfiltration authorization wording.
5. Maintenance cost of derived indexes when enabled.

## Recovery order
1. Read this status, `AGENTS.md`, and `QUEST.md`.
2. Read `program.md` and choose the active profile.
3. Read the active run journal under `runs/<run_id>/journal/`.
4. Read the run evidence under `traces/<run_id>/`.
5. Use the research ledger `research/ledger.jsonl` for cross-run facts.
6. Apply P10 four-layer recovery if OMP session continuity exists.
"""
    )


def write_idea() -> None:
    ideas_path = WORKSPACE / "archive" / "ideas.jsonl"
    if ideas_path.exists() and ideas_path.read_text().strip():
        return
    ideas_path.parent.mkdir(parents=True, exist_ok=True)
    idea = {
        "id": "idea-reference-001",
        "title": "Identity baseline keeps determinism obvious",
        "hypothesis": "An identity mapping produces zero MSE on the validation set and proves the harness contract without instrumenting model variants.",
        "method": "Pass target values directly as predictions.",
        "expected_delta": "mse == 0.0",
        "risk": "No generalisation evidence; only proves the contract.",
        "refs": [],
        "status": "queued",
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with ideas_path.open("w") as handle:
        handle.write(json.dumps(idea) + "\n")


def main() -> int:
    baseline = record_baseline()
    commit_baseline()
    (WORKSPACE / "traces").mkdir(exist_ok=True)
    reference_run = "reference-bootstrap"
    baseline_metrics = run_evaluator(reference_run)
    (WORKSPACE / "traces" / "baseline-metrics.json").write_text(
        json.dumps(baseline_metrics, indent=2) + "\n"
    )
    write_idea()
    write_status(reference_run, baseline)
    print(json.dumps({"baseline_sha": baseline["git"]["head"], "reference_run": reference_run}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
