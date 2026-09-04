#!/bin/sh
# Research Flywheel scaffold — POSIX shell, stdlib only, safe for existing workspaces.
# Python via uv-first helper: prefers 'uv run --directory "$WORKSPACE" --frozen python' when uv and uv.lock exist, then python3, then python.
# Preserves existing files and python3/python bootstrap fallback for portability.
# No file writes happen outside the workspace root.
# Runs from any cwd. Preserves existing user files. Handles existing Git baseline.
# Resolve workspace from script location — works from any cwd without relying on BASH_SOURCE
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
WORKSPACE="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"

# uv-first python helper — prefers uv when lock exists, falls back to python3/python
run_python() {
  if [ -f "$WORKSPACE/uv.lock" ] && command -v uv >/dev/null 2>&1; then
    uv run --directory "$WORKSPACE" --frozen python "$@"
  elif command -v python3 >/dev/null 2>&1; then
    python3 "$@"
  elif command -v python >/dev/null 2>&1; then
    python "$@"
  else
    return 127
  fi
}

IDEA=""
while [ $# -gt 0 ]; do
  case "$1" in
    --idea)
      if [ $# -lt 2 ]; then
        echo "scaffold.sh: --idea requires an argument" >&2
        exit 1
      fi
      IDEA="$2"
      shift 2
      ;;
    --idea=*)
      IDEA="${1#--idea=}"
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--idea \"text\"]" >&2
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "scaffold.sh: unknown option: $1" >&2
      exit 1
      ;;
    *)
      echo "scaffold.sh: unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

# 1) Create required directories (idempotent, never deletes)
for d in \
  archive \
  archive/papers \
  bench/tasks \
  capabilities \
  evaluation \
  experiment \
  navigator/evidence \
  orchestration/hooks \
  reports/figures \
  research \
  runs \
  traces \
  .pi
do
  mkdir -p "$WORKSPACE/$d"
done

# 2) Inspiration — preserve existing unless --idea supplied or file missing
INSPIRE="$WORKSPACE/inspiration.md"
if [ -n "$IDEA" ]; then
  printf "# Inspiration\n\n%s\n" "$IDEA" > "$INSPIRE"
elif [ ! -f "$INSPIRE" ]; then
  cat > "$INSPIRE" <<'INSP_EOF'
# Inspiration

Enter your research idea as a single sentence. Leave empty to trigger auto-inspiration via `python orchestration/inspiration.py --once`.
INSP_EOF
fi

# 3) Reference files — only when absent, never overwrite research docs
if [ ! -f "$WORKSPACE/program.md" ]; then
  cat > "$WORKSPACE/program.md" <<'PROG_EOF'
---
experiment_profile:
  name: reference-linear-regression
  baseline_ref: main
  mutable_paths:
    - experiment/run.py
  integrity_paths:
    - program.md
    - evaluation/prepare.py
    - capabilities/registry.json
  stages:
    probe:
      requested:
        cost_type: compute
        resource_class: cpu
        count: 1
      deadline_seconds: null
    full:
      requested:
        cost_type: compute
        resource_class: cpu
        count: 1
      deadline_seconds: null
  evaluation:
    evaluator: evaluation/prepare.py
    metric: mse
    direction: lower
    epsilon: 0.0001
    baseline_artifact: traces/baseline-metrics.json
  evidence_ladder:
    - tier: proxy
      evaluator: evaluation/prepare.py
      escalation: run deterministic smoke check
      success_language: "proxy result"
    - tier: modeled
      evaluator: evaluation/prepare.py
      escalation: clean reproduction matches the recorded metric
      success_language: "modeled result"
    - tier: independently_reproduced
      evaluator: evaluation/prepare.py
      escalation: fresh process repeats the committed experiment
      success_language: "independently reproduced result"
  authorization_boundary:
    workspace: current repository
    tools: [read, write, edit, bash, eval, task]
    endpoints: [local]
    compute: local cpu
    data_access: synthetic data in evaluation/prepare.py
    data_exfiltration: none
    lifecycle_envelope: profile-managed
    authorized_external_actions: []
    authorization_source: user task and this program
---

# Reference Research Program

## Objective

Test whether a small change in the experiment implementation lowers mean squared error on the fixed deterministic validation set.

## Research question

Can a candidate linear model improve the fixed evaluator result while preserving the evaluator and data integrity paths?

## Commitment rule

Ideas remain exploratory until a run commitment records the falsifiable statement, observed metric, decision rule, negation criterion, and requested resources. The reference run uses a deterministic synthetic regression experiment.

## Plan

`inspiration → modeling → experiment → evaluation → writing → review → archive`

## Profile notes

The reference profile is local and dependency-free. It demonstrates the harness contract. Domain profiles provide their own evaluator, evidence ladder, success language, and resource fields.
PROG_EOF
fi

if [ ! -f "$WORKSPACE/evaluation/prepare.py" ]; then
  cat > "$WORKSPACE/evaluation/prepare.py" <<'PREP_EOF'
"""Deterministic, dependency-free reference evaluator."""

from __future__ import annotations

from typing import Iterable


_DATA = (
    ((0.0,), 1.0),
    ((1.0,), 3.0),
    ((2.0,), 5.0),
    ((3.0,), 7.0),
    ((4.0,), 9.0),
)


def load_data() -> tuple[tuple[tuple[float, ...], float], ...]:
    """Return the fixed validation set."""
    return _DATA


def evaluate(pred: Iterable[float], target: Iterable[float]) -> dict[str, float | str]:
    """Return the native evaluator result."""
    predictions = tuple(pred)
    targets = tuple(target)
    if len(predictions) != len(targets):
        raise ValueError("prediction and target lengths differ")
    if not predictions:
        raise ValueError("evaluation requires at least one prediction")
    mse = sum((actual - expected) ** 2 for actual, expected in zip(predictions, targets)) / len(targets)
    return {"name": "mse", "value": mse, "higher_is_better": False}
PREP_EOF
fi

if [ ! -f "$WORKSPACE/experiment/run.py" ]; then
  cat > "$WORKSPACE/experiment/run.py" <<'RUN_EOF'
"""Dependency-free reference experiment implementation."""

from __future__ import annotations

import json
import time
from pathlib import Path

from evaluation.prepare import evaluate, load_data


def main(run_context: dict) -> dict:
    """Fit the deterministic reference model and return native metrics."""
    started = time.perf_counter()
    data = load_data()
    slope = 1.8
    intercept = 1.0
    predictions = [slope * features[0] + intercept for features, _ in data]
    targets = [target for _, target in data]
    metrics = evaluate(predictions, targets)
    actual = {
        "wall_clock_seconds": round(time.perf_counter() - started, 6),
        "cpu_seconds": round(time.process_time(), 6),
        "tokens": 0,
        "material_cost": 0,
    }
    result = {
        "run_id": run_context["run_id"],
        "metric_main": metrics,
        "metric_aux": {"samples": len(data), "slope": slope, "intercept": intercept},
        "actual": actual,
    }
    trace_dir = Path(run_context["trace_dir"])
    trace_dir.mkdir(parents=True, exist_ok=True)
    (trace_dir / "raw-result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
RUN_EOF
fi

if [ ! -f "$WORKSPACE/capabilities/registry.json" ]; then
  cat > "$WORKSPACE/capabilities/registry.json" <<'REG_EOF'
{
  "manifest_version": "1.0",
  "capabilities": [
    {
      "id": "reference.evaluator",
      "version": "1.0.0",
      "purpose": "Evaluate deterministic synthetic regression predictions",
      "input_schema": {"predictions": "array<number>", "targets": "array<number>"},
      "output_schema": {"name": "string", "value": "number", "higher_is_better": "boolean"},
      "endpoint": "local",
      "approval": "none",
      "documentation": "evaluation/prepare.py",
      "common_failures": ["length mismatch", "empty input"]
    },
    {
      "id": "reference.experiment",
      "version": "1.0.0",
      "purpose": "Run the dependency-free reference experiment",
      "input_schema": {"run_id": "string", "trace_dir": "path", "stage": "string"},
      "output_schema": {"metric_main": "object", "metric_aux": "object", "actual": "object"},
      "endpoint": "local",
      "approval": "none",
      "documentation": "experiment/run.py",
      "common_failures": ["import failure", "runtime failure"]
    }
  ]
}
REG_EOF
fi

if [ ! -d "$WORKSPACE/.pi/agents" ]; then
  mkdir -p "$WORKSPACE/.pi/agents" "$WORKSPACE/.pi/rules" "$WORKSPACE/.pi/workflows" "$WORKSPACE/.pi/prompts"
  # pi project agents/rules/workflows are scaffolded from this template repository's .pi/ tree.
  TEMPLATE_PI="$(cd "$(dirname "$0")/.." && pwd)/.pi"
  if [ -d "$TEMPLATE_PI/agents" ]; then
    cp -R "$TEMPLATE_PI/agents/." "$WORKSPACE/.pi/agents/"
    cp -R "$TEMPLATE_PI/rules/." "$WORKSPACE/.pi/rules/"
    cp -R "$TEMPLATE_PI/workflows/." "$WORKSPACE/.pi/workflows/"
    cp -R "$TEMPLATE_PI/prompts/." "$WORKSPACE/.pi/prompts/"
  fi
fi

if [ ! -f "$WORKSPACE/pyproject.toml" ]; then
  cat > "$WORKSPACE/pyproject.toml" <<'PYPROJ_EOF'
[project]
name = "research-flywheel"
version = "0.1.0"
description = "Portable research-flywheel workspace template"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[tool.uv]
package = false
PYPROJ_EOF
fi

if [ ! -f "$WORKSPACE/.python-version" ]; then
  printf "3.11\n" > "$WORKSPACE/.python-version"
fi

# Create/update uv.lock through uv when available (preserve existing lock if uv absent)
if command -v uv >/dev/null 2>&1; then
  uv lock --directory "$WORKSPACE" >/dev/null 2>&1 || true
fi

# append-only logs — create empty if absent, never truncate existing
for f in archive/ideas.jsonl navigator/queries.jsonl traces.jsonl research/ledger.jsonl archive/failed.jsonl; do
  if [ ! -f "$WORKSPACE/$f" ]; then
    mkdir -p "$(dirname "$WORKSPACE/$f")"
    : > "$WORKSPACE/$f"
  fi
done

# 4) Delegate baseline initialization safely — never overwrite existing user files or recommit without need
INIT="$WORKSPACE/orchestration/init_workspace.py"
if [ -f "$INIT" ]; then
  # Check if python available via uv-first helper probe
  if run_python -c "import sys; sys.exit(0)" >/dev/null 2>&1; then
    NEED_INIT=0
    if [ ! -f "$WORKSPACE/traces/baseline-metrics.json" ]; then
      NEED_INIT=1
    fi
    if [ ! -d "$WORKSPACE/.git" ]; then
      NEED_INIT=1
    fi
    if [ "$NEED_INIT" -eq 1 ]; then
      # Run init but tolerate already-committed or dirty workspace — never delete work
      if ! run_python "$INIT" 2>&1; then
        echo "scaffold.sh: init_workspace.py reported an issue — workspace dirs still valid, check git status" >&2
      fi
    else
      echo "scaffold.sh: baseline present — skipping init_workspace.py (use uv run --frozen python orchestration/init_workspace.py to refresh)" >&2
    fi
  else
    # No python — ensure bare git repo if git available
    if [ ! -d "$WORKSPACE/.git" ] && command -v git >/dev/null 2>&1; then
      git -C "$WORKSPACE" init --initial-branch=main >/dev/null 2>&1 || true
      git -C "$WORKSPACE" config user.email "research-flywheel@local" >/dev/null 2>&1 || true
      git -C "$WORKSPACE" config user.name "Research Flywheel" >/dev/null 2>&1 || true
      echo "scaffold.sh: initialized bare git repo (no python available for full baseline)" >&2
    fi
  fi
fi

echo "scaffold: workspace ready at $WORKSPACE"
if [ -n "$IDEA" ]; then
  echo "scaffold: inspiration set from --idea"
fi
