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
