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
