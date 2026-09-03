# Reasoning — 20260903-050000-a1b1

- idea: idea-006 — Intercept shift toward residual mean variant 1
- hypothesis: Shifting intercept toward the mean residual corrects bias and lowers MSE without touching the evaluator.
- candidate: slope 1.8 intercept 1.0 via experiment/run.py (project root import)
- baseline mse: 0.0
- candidate mse: 0.2400000000000002
- delta: -0.2400000000000002
- epsilon: 0.0001 direction: lower
- execution: completed reproduction: completed
- outcome: discard keep: False
- verification: integrity True backend isolated-candidate-dir
- evidence: traces/20260903-050000-a1b1/raw-result.json, traces/20260903-050000-a1b1/run.log, traces/20260903-050000-a1b1/verification.json
