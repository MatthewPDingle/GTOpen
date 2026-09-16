# Preflop accuracy and runtime: night-shift checkpoint

Updated 2026-09-16T17:22:04.704414+00:00.

The scheduled research window ends at **20:49:02 UTC on 16 September** (06:19 Adelaide on 17 September). This document is a checkpoint, not a completion or deployment claim.

## Decision so far

Accuracy and speed are separate requirements. A candidate that improves the average but materially worsens one family is rejected. A speed improvement to a rejected predictor does not qualify that predictor for use. No research runner in this study deploys to the app on port 56708.

## New reference data

| Partition | Saved references / planned | Purpose |
|---|---:|---|
| range-bridges / training | 720 / 720 | New training range and stack examples |
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
| N06b nonlinear + new data | 7.379 | +4.07% / -7.10% | 0.995294 / 1.107302 | No |
| N08 precision weighting | 7.100 | +7.69% / -3.06% | 0.949357 / 1.126007 | No |
| N03 range diversity | 7.970 | -14.39% | 1.236920 | No |
| N13 matchup-distribution moments | 6.929 | -0.58% | 1.082122 | No |
| N15 conservative nonlinear correction | 6.284 | +8.79% | 1.021217 | Yes; evaluation still required |

N03 uses the original 24 validation cases. Other rows use the original 26 including the two development cases, so do not rank N03 against them using raw error. N06b/N08 gains and ratios list the expanded-data and original-data controls respectively; both must pass. Eligibility requires at least 5% lower mean error and no family more than 5% worse. Printed values never determine the gate: full-precision values do.

The label-precision diagnostic found appreciable variation between 20-flop subsets and the 100-flop training estimates. Exact rank-event controls reduced that variation by 6–21%, but failed the fixed all-family 20% requirement. The original labels were retained. This diagnostic is not an estimate of error against exact poker values.

## Cheap pairwise-prior recalibration (N09)

The fixed training screen passed. Mean error was **10.223% of pot**, versus 14.998% for Balanced (31.8% lower). The worst family ratio was 1.004837. It also had to improve at least 5% on unchanged priors under the same compatible-pair calculation, with no family more than 5% worse against either baseline.

The conditional predictor remains more accurate on training-family checks. N09 is considered because its pairwise matrices can be cached. GPU correctness and performance require the separate checks below. Its frozen candidate was registered before N03 evaluation outcomes existed, permitting shared future reference computation under a separate prospective protocol. [Full N09 result](../recalibrated-priors-20260916/RESULTS.md).

## Cached additive pair values (N10)

The fixed training screen failed. Mean error was **10.351% of pot**, compared with 10.223% for N09. The worst family ratio versus N09 was 1.259211. This tests a different cheap pair-table model that can represent value from future bets. Its independent algebra, accounting and synthetic recovery checks passed, but those checks do not establish accuracy on real reference values. [Full N10 result](../pair-value-adjustments-20260916/RESULTS.md).

## Fixed correction to cached priors (N11)

The fixed two-stage screen failed. Mean error was **10.382% of pot**, versus 10.223% for N09. The worst family ratio versus N09 was 1.106549. Both fitting stages excluded the validation family, and all 26 N09 control errors reproduced. [Full N11 result](../corrected-pair-priors-20260916/RESULTS.md).

## Depth-dependent cached priors (N12)

The fixed training screen failed. Mean error was **9.809% of pot**; improvement over the original-data N09 control was 4.05%. The complete controls and family checks determine eligibility, without rounded thresholds. [Protocol and evidence](../depth-pair-priors-20260916/README.md).

## Depth-dependent cached priors (N12b)

The fixed training screen failed. Mean error was **10.695% of pot**; improvement over the original-data N09 control was -4.62%. The complete controls and family checks determine eligibility, without rounded thresholds. [Protocol and evidence](../depth-priors-expanded-20260916/README.md).

## Later prospective accuracy checks

### N09: failed the fixed accuracy screen

| Held-out family | Balanced error | Previous predictor | Candidate | Improvement vs Balanced, 90% interval |
|---|---:|---:|---:|---:|
| test-eight-open | 10.727 | 8.585 | 12.338 | -41.2% to -0.7% |
| test-seven-straddle | 14.947 | 7.034 | 11.382 | +20.7% to +25.0% |

Candidate SHA-256: `7c324ecf383dc24cf9e95024851f9fed7b6b11aad545741f98e0c6a78383eb4b`.

The gate also checks every individual case against the previous predictor. Passing this value-error screen alone does not authorize deployment.

### N15: passed the fixed accuracy screen

| Held-out family | Balanced error | Previous predictor | Candidate | Improvement vs Balanced, 90% interval |
|---|---:|---:|---:|---:|
| test-eight-open | 14.388 | 10.587 | 9.041 | +27.9% to +40.5% |
| test-seven-straddle | 14.682 | 7.281 | 5.080 | +48.7% to +68.3% |

Candidate SHA-256: `6b5aea3edb28044b6d9f81df0f5121d455daebdbe4e1adba27448136694def43`.

The gate also checks every individual case against the previous predictor. Passing this value-error screen alone does not authorize deployment.

## Cached-prior GPU checks (N09)

The isolated cached-matrix source passes offline CUDA compilation. This verifies source compilation only; it does not establish execution correctness or speed.

Execution oracle and repeated timing remain pending; they run only after prospective accuracy passes.

## Nonlinear predictor GPU preparation (N15)

The physical-value sanity check passed across 26 training contexts. Predictions are checked against the pot and remaining stack, with negative future-play values allowed inside those bounds. This is not an accuracy estimate.

The physical-value sanity check passed across 8 prospective contexts. Predictions are checked against the pot and remaining stack, with negative future-play values allowed inside those bounds. This is not an accuracy estimate.

Both double-precision implementations pass offline CUDA compilation: ordinary range summaries and parallel range summaries. Four CPU checks cover the emitted neural arithmetic, standardization and execution guards. GPU execution is allowed only after N15 passes its registered accuracy screen. Compilation is not evidence of accuracy or runtime performance.

Both implementations passed the independent GPU oracle and their mutual action-value comparison.

No N15 GPU speed result is available yet.

## Lower-cost neural arithmetic (N16)

Three CPU checks and both offline compilations pass. The model is unchanged: only neural accumulations use float32, with feature standardization and range centering retained in double precision. No GPU execution or speed gain is implied. [Protocol](../shrunk-mixed-gpu-20260916/README.md).

## Parallel pair bookkeeping (N17)

The rank-incidence shortcut matches physical card-combination counts in CPU checks. Both source variants compile offline. N17 parallelizes pair normalization and correction centering in double precision; its optional mixed variant also incorporates N16. Compilation alone supplies no GPU execution or timing evidence. [Protocol](../pair-reductions-20260916/README.md).

Both GPU variants passed all 12 independent action-value oracle cases each, including zero-reach hands and multiway configurations. This verifies the implementation against its specified model; it does not make the multiway approximation exact.

The mixed implementation failed its fixed consistency limit: maximum inspected strategy difference **0.201470**, player EV difference **0.002220 bb**. Both limits were 0.001. The joint benchmark stopped after its first repeat; no completed runtime pass is claimed. Full precision is evaluated separately under N20 with the same frozen source and model.

## Retained full-precision implementation (N20)

N20 retains the exact N17 double source after rejecting mixed arithmetic. It adds action-value comparisons on actual solved policies, then runs three fresh original/candidate timing pairs. No failed tolerance is relaxed. [Protocol](../full-precision-20260916/README.md).

The additional check on two actual solved policies passed across **20,618 action values**. Maximum difference versus the original validated double implementation: **0 bb**.

Candidate median **1.1780 s/iteration**; overhead versus original **+5.93%**. Runtime target passed. Changed-policy qualification remains separate.

| Path | Median setup / compilation (s) | Median whole process (s) |
|---|---:|---:|
| original | 1.00 | 166.06 |
| candidate | 1.08 | 180.96 |

Whole-process time includes setup, 50 warm-up iterations, 100 measured iterations and final evaluation/save. It is a fixed-work measurement, not time to convergence.

The explicit additional interface arrays total **5.72 MiB**, calculated from the saved plan and the six allocations in the frozen Rust implementation. The ordinary equity cache remains allocated. This excludes CUDA modules, compiler spills and allocator overhead; total device-memory peak was not measured. The raw run logs also retain the original solver memory-budget estimate.

## Equal-work strategy warning

At 500 iterations, the summed frozen-value gap is **0.004809 bb** for ordinary Balanced versus **0.090492 bb** for the candidate. Thus the measured 5.93% per-iteration overhead does not establish comparable time to a settled strategy. Calling decreases in several blind/straddle contexts; wider calling itself is not an accuracy criterion. These remain unconverged, model-dependent comparisons.

[All 17 nodes and KQo probes](../policy-transfer-optimized-20260916/N20/STRATEGY-DIAGNOSTIC.md).

## Changed-policy validation

No completed changed-policy result yet.

## Hand-group and position diagnostic

The pooled N15 result improves over Balanced in all seven hand groups, but this hides position-specific weaknesses. OOP suited-broadway error is 6.141% of pot versus 3.813% for Balanced; IP premium pairs still have 16.612% error and -11.234% signed bias. These descriptive groups did not participate in fitting or acceptance and do not change the gates. OOP/IP describe postflop position, not a breakdown by individual preflop seat.

[Full pooled and position tables](../shrunk-residual-20260916/HAND-GROUPS.md).

## Practical strategy stability (N19)

Prepared and tested, not yet completed. It runs only after the selected implementation passes all preceding gates.

## Wider flop-menu sensitivity (N21)

Separately frozen before its outcomes: the same model and four changed-policy contexts, 20 unused matched boards, and 160 references comparing half-pot-only flop bets with a nested 33%/50%/75% menu. Turn/river menus remain fixed. No fitting or automatic deployment. [Protocol](../flop-menu-20260916/README.md).

Prepared with three checks passed; no completed wider-menu accuracy result. N19 has execution priority.

## Half-width nonlinear model (N18)

The fixed training screen failed. Mean error was **6.472% of pot**, 6.07% lower than the linear control. Relative to N15, mean error changed by +2.99% and the worst family by +13.33%. The fixed screen permits at most 5% regression in any family versus N15. No speed claim follows from using fewer hidden units. [Protocol](../compact-residual-20260916/README.md).

## Speed and unchanged-result checks (N04)

Removing overwritten terminal work passed the independent 12-case action-value oracle, the ordinary CPU test suite and 21 GPU regression tests. The repeated benchmark additionally requires equality of every saved regret and accumulated strategy value.

| Path | Median seconds / iteration |
|---|---:|
| original | 1.1122 |
| control | 1.4216 |
| filtered | 1.4165 |

Speedup versus the identical unoptimized predictor: **1.004×**. Overhead versus ordinary Balanced: **+27.4%**. The operational speed target is no more than 10% overhead.

## Parallel range summaries (N14)

A separately specified experiment distributes each serial range-summary calculation over 32 GPU threads. It retains the old predictor and double precision but changes summation order. [Protocol and required tolerances](../warp-summary-20260916/README.md).

Prepared; no speed result is claimed until the independent oracle and repeated benchmark complete.

This benchmark retains the old predictor, which failed an accuracy screen. Any newly qualified predictor still needs its own implementation, timing and changed-policy checks.

## Remaining limitations

- Fixed zero-rake, heads-up postflop references use a restricted bet menu. They are not complete preflop game solves.
- Small average solve gaps do not guarantee every rare-hand training value is accurate.
- Fresh-board evaluation reuses historical case identities from held-out source families; it is not untouched-context validation.
- The larger preflop interface still approximates multiway card removal and ignores folded-card bunching.
- Bootstrap intervals condition on fitted models and cached equities. Value accuracy and frozen-value best-response gaps do not certify full-game exploitability.

See the [plan and invariants](README.md), [experiment ledger](ledger.json) and individual study artifacts for hashes, protocols and detailed results.

## Hand-level reference diagnostic

Snapshot at 2026-09-16T16:59:02.388770+00:00, covering 720 / 720 planned training references. Hands with more than 1% pot remaining best-response gain account for **0.0048%** of hand mass when averaging completed references and players equally. The largest observed individual gain is 4.023% of pot. This diagnoses remaining solve error, not model prediction error or a rigorous per-hand value-error bound. All planned training references are included.

[Hand-level audit details](../range-bridges-20260916/partial-hand-quality.json).
