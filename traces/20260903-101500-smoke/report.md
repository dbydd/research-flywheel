# Report — 20260903-101500-smoke

## Hypothesis
Averaging neighbouring targets smooths the synthetic sequence and trims squared error.

## Method
Candidate slope 1.8 intercept 1.0 vs identity baseline.

## Metrics
- baseline mse: 0.0
- candidate mse: 0.2400000000000002
- delta: -0.2400000000000002

## Outcome
discard — discard: mse baseline 0.0 -> candidate 0.2400000000000002 delta -0.2400000000000002 epsilon 0.0001

## Evidence
- traces/20260903-101500-smoke/metrics.json
- traces/20260903-101500-smoke/verification.json
- traces/20260903-101500-smoke/raw-result.json
## Success language
independently reproduced result: mse 0.2400000000000002
