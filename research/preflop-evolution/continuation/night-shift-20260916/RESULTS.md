# Preflop accuracy and runtime: night-shift checkpoint

Updated 2026-09-16T12:37:34.058413+00:00.

The scheduled research window ends at **20:49:02 UTC on 16 September** (06:19 Adelaide on 17 September). This document is a checkpoint, not a completion or deployment claim.

## Decision so far

Accuracy and speed are separate requirements. A candidate that improves the average but materially worsens one family is rejected. A speed improvement to a rejected predictor does not qualify that predictor for use. No research runner in this study deploys to the app on port 56708.

## New reference data

| Partition | Saved references / planned | Purpose |
|---|---:|---|
| range-bridges / training | 242 / 720 | New training range and stack examples |
| range-bridges / evaluation | 0 / 400 | N03 fixed-model accuracy test |
| expanded-validation / prospective | 0 / 400 | Fresh evaluation of any eligible N06b/N08 models |

Counts indicate saved files; the study audit separately validates their numerical quality. N03 adds 36 synthetic contexts, not 36 independent real-player populations. Original plus development plus new contexts total 62 training cases.

## Prospective accuracy: targeted blind-call data (N01)

This completed experiment failed its fixed accuracy screen. It improved on the previous learned predictor at both tested cases, but one case became worse than ordinary Balanced.

| Case | Balanced error | Previous predictor | N01 predictor | Change vs Balanced |
|---|---:|---:|---:|---:|
| test-seven-straddle-00 | 5.092 | 8.481 | 5.714 | -12.2% |
| test-eight-open-01 | 15.661 | 5.228 | 4.236 | +72.9% |

Errors are mean absolute hand-value errors as a percentage of the starting pot. Positive change means lower error. [Full N01 result and uncertainty](../policy-refinement-20260916/RESULTS.md).

## Training-family screens

These scores select models for later evaluation; they are not independent evidence of poker-strategy accuracy. Each validation family is excluded from fitting. Fixed candidate sets are retained, including failures.

| Experiment | Best attempted error (% pot) | Mean gain | Worst family error ratio | Eligible |
|---|---:|---:|---:|---|
| N02 curvature | 6.697 | +2.80% | 1.050329 | No |
| N02 hand offsets | 6.752 | +1.99% | 1.043477 | No |
| N05 projected fitting | 7.274 | -5.58% | 1.064916 | No |
| N06 nonlinear | 6.423 | +6.77% | 1.050442 | No |
| N06b nonlinear + new data | Pending | — | — | Pending |
| N08 precision weighting | Pending | — | — | Pending |
| N03 range diversity | Pending | — | — | Pending |

N03 uses the original 24 validation cases. Other rows use the original 26 including the two development cases, so do not rank N03 against them using raw error. N06b/N08 gains and ratios list the expanded-data and original-data controls respectively; both must pass. Eligibility requires at least 5% lower mean error and no family more than 5% worse. Printed values never determine the gate: full-precision values do.

The label-precision diagnostic found appreciable variation between 20-flop subsets and the 100-flop training estimates. Exact rank-event controls reduced that variation by 6–21%, but failed the fixed all-family 20% requirement. The original labels were retained. This diagnostic is not an estimate of error against exact poker values.

## Later prospective accuracy checks

Pending eligibility and fresh reference generation. No later evaluation gain is claimed.

## Speed and unchanged-result checks (N04)

Removing overwritten terminal work passed the independent 12-case action-value oracle, the ordinary CPU test suite and 21 GPU regression tests. The repeated benchmark additionally requires equality of every saved regret and accumulated strategy value.

**Timing is pending. No speed gain is claimed yet.**

This benchmark retains the old predictor, which failed an accuracy screen. Any newly qualified predictor still needs its own implementation, timing and changed-policy checks.

## Remaining limitations

- Fixed zero-rake, heads-up postflop references use a restricted bet menu. They are not complete preflop game solves.
- Small average solve gaps do not guarantee every rare-hand training value is accurate.
- Fresh-board evaluation reuses historical case identities from held-out source families; it is not untouched-context validation.
- The larger preflop interface still approximates multiway card removal and ignores folded-card bunching.
- Bootstrap intervals condition on fitted models and cached equities. Value accuracy and frozen-value best-response gaps do not certify full-game exploitability.

See the [plan and invariants](README.md), [experiment ledger](ledger.json) and individual study artifacts for hashes, protocols and detailed results.

## Hand-level reference diagnostic

Snapshot at 2026-09-16T12:37:33.790854+00:00, covering 242 / 720 planned training references. Hands with more than 1% pot remaining best-response gain account for **0.0042%** of hand mass when averaging completed references and players equally. The largest observed individual gain is 3.143% of pot. This diagnoses remaining solve error, not model prediction error or a rigorous per-hand value-error bound. A partial snapshot is not a final all-flop estimate.

[Hand-level audit details](../range-bridges-20260916/partial-hand-quality.json).
