# Reasoning — 20260903-101500-smoke

- idea: idea-011 — Residual-weighted prediction smoothing variant 2
- hypothesis: Averaging neighbouring targets smooths the synthetic sequence and trims squared error.
- candidate: slope 1.8 intercept 1.0 via experiment/run.py (project root import)
- baseline mse: 0.0
- candidate mse: 0.2400000000000002
- delta: -0.2400000000000002
- epsilon: 0.0001 direction: lower
- execution: completed reproduction: completed
- outcome: discard keep: False
- verification: integrity True backend git-branch
- evidence: traces/20260903-101500-smoke/raw-result.json, traces/20260903-101500-smoke/run.log, traces/20260903-101500-smoke/verification.json
