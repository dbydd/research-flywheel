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
