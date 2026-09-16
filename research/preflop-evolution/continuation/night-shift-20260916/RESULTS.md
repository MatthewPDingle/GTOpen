# Preflop accuracy and runtime: night-shift checkpoint

Updated 2026-09-16T20:08:24.177010+00:00.

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

## Local range sensitivity

A label-free diagnostic perturbed 24 training contexts in 288 small, prescribed ways. The candidate has roughly four to five times the median value response of Balanced, with much of that response already present in its linear base. This motivates testing smoother fitting, but higher sensitivity can be legitimate and does not establish causation for the observed convergence gap. No model was changed by the diagnostic.

[Detailed response measurements](../range-sensitivity-20260916/RESULTS.md).

## Less reactive fitting (N22)

A separately prespecified CPU training screen adds a sensitivity penalty to the linear fit, then refits the same small nonlinear correction. It uses only training/development families and keeps the inference architecture unchanged. It must preserve N15 accuracy within 5% in every family, improve at least 5% over the earlier linear control, and lower mean local sensitivity by at least 25%, without worsening any family sensitivity. [Protocol](../smooth-fit-20260916/README.md).

Training screen rejected all fixed strengths. Fresh independent accuracy and GPU/convergence qualification remain separate.

| Penalty | Mean error (% pot) | Worst-family change vs N15 | Sensitivity reduction | Eligible |
|---|---:|---:|---:|---|
| 0 | 6.284 | +0.00% | 0.00% | No |
| 0.0001 | 6.306 | +2.02% | 2.84% | No |
| 0.001 | 6.333 | +8.65% | 14.84% | No |
| 0.01 | 6.515 | +14.88% | 37.22% | No |

The zero-penalty control reproduced the existing N15 training validation exactly. No failed tolerance was changed and no rejected smoother was sent to the GPU.

## Lightly weighted range-diversity data (N23)

The unchanged N15 architecture was fitted with the 36 synthetic training contexts at fixed weights .05 and .2, while retaining original contexts at weight1 and excluding entire validation families. The zero-extra-data control reproduced N15 exactly. [Protocol](../weighted-expanded-20260916/README.md).

| Extra-context weight | Mean error (% pot) | Worst-family change vs N15 | Sensitivity reduction | Eligible |
|---|---:|---:|---:|---|
| 0 | 6.284 | +0.00% | 0.00% | No |
| 0.05 | 6.392 | +11.58% | 20.59% | No |
| 0.2 | 6.562 | +11.69% | 24.00% | No |

No fixed weight passed all requirements; the extra-data variants were not promoted. Positive-mass labels were independently verified in all 62 training contexts.

## Changed-policy validation

### N20: passed the unchanged four-context gate

| Context | Balanced error | Previous predictor | Candidate error |
|---|---:|---:|---:|
| original-bb-call-0 | 6.788 | 5.892 | 3.745 |
| original-bb-call-1 | 6.342 | 6.843 | 3.095 |
| candidate-bb-call-0 | 6.287 | 6.464 | 3.546 |
| candidate-bb-call-1 | 6.838 | 5.586 | 3.819 |

Errors are percent of pot. Every context must improve at least 15% versus Balanced and regress at most 10% versus the previous predictor. These are fresh boards on changed ranges in a familiar scenario, not untouched-scenario validation or a full-game convergence certificate.

All **200 references** passed the provenance and solve-quality audit. Physical prediction bounds passed in the changed contexts. These diagnostics do not alter the fixed accuracy gate.

## Hand-group and position diagnostic

The pooled N15 result improves over Balanced in all seven hand groups, but this hides position-specific weaknesses. OOP suited-broadway error is 6.141% of pot versus 3.813% for Balanced; IP premium pairs still have 16.612% error and -11.234% signed bias. These descriptive groups did not participate in fitting or acceptance and do not change the gates. OOP/IP describe postflop position, not a breakdown by individual preflop seat.

[Full pooled and position tables](../shrunk-residual-20260916/HAND-GROUPS.md).

## Isolating the card-accounting change (N24)

The N20 path changes compatible-card accounting as well as hand values. A separately frozen control keeps the same interface but disables the learned predictor, using the previous Balanced continuation values. It compares equal150/500iteration snapshots. [Protocol](../chance-control-20260916/README.md).

| Iteration | Path | Summed frozen-value gap (bb) |
|---|---|---:|
| 150 | ordinary | 0.065835 |
| 150 | paired_balanced | 0.026543 |
| 150 | learned | 0.188129 |
| 500 | ordinary | 0.004809 |
| 500 | paired_balanced | 0.006646 |
| 500 | learned | 0.090492 |

These are separate approximate games and this is one diagnostic run. It isolates one possible contributor; it does not prove a particular learned feature caused the difference or establish full-game exploitability. At 500 iterations the card-accounting control has a much smaller remaining gap than the learned path; card accounting alone does not reproduce the large learned gap. [Input and snapshot audit](../chance-control-20260916/result-audit.json).

## Practical strategy stability (N19)

| Path | Stability signal met | Additional learning time, 500 to 1500 (s) |
|---|---|---:|
| original | Yes | 780.4 |
| candidate | No | 1090.9 |

The fixed signal requires both consecutive 500-iteration intervals to have <=1 percentage point aggregate-action and weighted per-hand change at every inspected node, with frozen-value gap <=0.005 bb. Absent arriving ranges do not count as stable. This limited diagnostic does not establish full-game convergence. If either arm misses the signal, no comparative time-to-stability claim is made.

| Path | Gap at 1000 (bb) | Gap at 1500 (bb) |
|---|---:|---:|
| original | 0.001266 | 0.000617 |
| candidate | 0.078152 | 0.078407 |

The candidate took **39.8% more learning time** for these additional 1000 iterations and failed the settling signal. These are single observed spans, not repeated runtime medians or time-to-convergence measurements. The short repeated benchmark therefore does not establish approximately maintained end-to-end performance. The candidate charts changed little in the final interval, but its frozen-value gap plateaued. [Snapshot and input audit](../policy-stability-20260916/result-audit.json).

## Wider flop-menu sensitivity (N21)

Separately frozen before its outcomes: the same model and four changed-policy contexts, 20 unused matched boards, and 160 references comparing half-pot-only flop bets with a nested 33%/50%/75% menu. Turn/river menus remain fixed. No fitting or automatic deployment. [Protocol](../flop-menu-20260916/README.md).

The fixed eight-context/menu accuracy gate passed.

| Context / menu | Balanced error | Previous error | Candidate error |
|---|---:|---:|---:|
| original-bb-call-0-control | 8.992 | 7.875 | 6.169 |
| original-bb-call-0-expanded | 9.176 | 8.062 | 6.313 |
| original-bb-call-1-control | 8.800 | 8.651 | 5.694 |
| original-bb-call-1-expanded | 8.989 | 8.848 | 5.772 |
| candidate-bb-call-0-control | 8.150 | 7.911 | 5.474 |
| candidate-bb-call-0-expanded | 8.313 | 8.116 | 5.557 |
| candidate-bb-call-1-control | 9.002 | 7.264 | 5.210 |
| candidate-bb-call-1-expanded | 9.152 | 7.342 | 5.231 |

Errors are percent of pot. Twenty boards provide a limited conditional estimate; this does not establish unrestricted-tree or untouched-context accuracy.

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

## Fixed pairwise values (N25)

A separately frozen training-only experiment learns hand-versus-hand payoffs, with opposite player corrections that conserve the pot. This removes own-range dependence from each hand value but is less expressive than full postflop play. It must retain accuracy before any GPU work. [Protocol](../pairwise-values-20260916/README.md).

Training eligibility: **False**. Training eligibility alone does not qualify a model for deployment.

| Ridge strength | Mean family error (% pot) | Eligible |
|---|---:|---|
| 0.01 | 14.048 | False |
| 0.1 | 12.582 | False |
| 1.0 | 12.761 | False |

All three numerical checks passed. A NumPy boolean prevented the initial result from being written; a separate output-only adapter reran the unchanged deterministic fitting code. No frozen source, model, grid or gate changed. [Repair provenance](../pairwise-values-20260916/output-repair.json).

## Own-range value response (N26)

All 432 fixed training-input perturbations completed without reference labels or fitting. Raw and Balanced hand values stayed invariant to own-range changes. The candidate and its older linear base both showed systematic shifts in values assigned to existing hands. This is not unique to the neural correction. Smaller perturbations gave larger normalized responses; zero-weight hands, entropy features and clipping preclude treating these finite differences as a stable smooth derivative. Own-range dependence can be legitimate, so this is neither an accuracy test nor proof of the settling cause. [Detailed results and limitations](../own-range-drift-20260916/RESULTS.md).

## Latest versus averaged strategies (N28)

At the same 17 inspected decisions after 1500 iterations, the largest weighted latest/average hand-strategy variation was 0.211 percentage points for the candidate and 0.285 for ordinary Balanced. There is no large hidden separation at these decisions at this checkpoint. Deeper nodes and temporal trajectories remain unmeasured; no latest-policy convergence metric was substituted. [Read-only audit](../current-policy-20260916/RESULTS.md).

## Heads-up settling without a multiway reset (N27)

All twelve snapshots completed in two prespecified heads-up fixtures with one legal-pair context anchored at the root. The learned gap at 40 bb stayed near 0.00048 bb between 500 and 1500 iterations. At 100 bb it rose from 0.00358 to 0.00551 bb. Both baseline paths improved strongly. The effect can occur without a multiway reset, although it is much smaller here. Two fixtures do not establish general causality or full-postflop accuracy. [Complete comparison](../heads-up-settling-20260916/RESULTS.md).

## Remaining one-action deviations (N29)

At the same seventeen N19 decisions, the largest learned one-action improvement is 0.00063855 bb, versus 0.00001068 bb for ordinary Balanced. These selected improvements are small relative to the learned full frozen-value gap, but they overlap and must not be added as a full-gap decomposition. Uninspected branches and successive deviations remain unresolved. [Detailed values](../late-frontier-20260916/RESULTS.md).

## Targeted own-mean response regularization (N30)

The three fixed training settings all failed the unchanged joint accuracy/response screen. The mild setting improved mean error 0.94% but reduced targeted response only 0.14%. The strongest reduced response 30.78% but worsened its weakest accuracy family 11.81%. All twenty-six N15 controls reproduced; two numerical checks passed. No candidate was promoted. [Training results](../own-drift-fit-20260916/RESULTS.md).

## Zero-reach model switching (N31)

The full terminal scan found 446 learned large-case terminal/player combinations with zero current own range but positive opponent reach. These use the older Balanced continuation during current-strategy evaluation; averaged ranges remain positive at every eligible leaf. No such switch occurs in either small heads-up fixture at this checkpoint, so it cannot explain their residual gaps. All 17 selected prefix checks agree exactly with N28; source hashes remained unchanged. This is a hypothesis diagnostic, not additive gap attribution. [Full scan and caveats](../zero-reach-20260916/RESULTS.md).

## Zero-own-range continuation control (N32)

A separate kernel changes only the zero-own-range guard, using the existing uniform combo prior to retain learned values. Positive-range predictions stay unchanged. Two 500-step continuations start from the exact same N19 checkpoint, after N21 releases the GPU. This tests one possible contributor; the uniform prior is an assumption and no deployment follows automatically. Completed gap ratio versus the original guard: 1.0092. [Frozen protocol](../zero-fallback-20260916/README.md).

## Conservative paired-accounting blend (N33–N35)

The first blend attempt (N33) stopped at its conservation check: the historical ordinary comparator uses independent opponent weights, unlike the learned legal-pair values. Its frozen failed attempt is retained. N34 explicitly uses the paired Balanced formula, reproduces all 26 full-model controls, and conserves the weighted pot without post-hoc adjustment.
The smallest preregistered qualifying learned share is 25%. Training-family mean error improves 21.14% over paired Balanced, but is 1.876 times full N15's error. This is an explicit accuracy/settling tradeoff, not a superior standalone predictor. N35 separately prepares GPU linearity checks and a same-start continuation comparison; no GPU settling or fresh accuracy outcome is implied by the training screen. [Training results](../paired-blend-20260916/RESULTS.md) · [Frozen GPU protocol](../paired-blend-gpu-20260916/README.md).

## Conditional fresh blend validation (N36)

Registered before N35 results: only run if its settling and <=10% learning-time overhead screens pass. Saved references: **0/80**. No completed accuracy result. The twenty unused flops are shared by four fixed control/blend range contexts. Partial output cannot pass the screen. [Frozen plan](../paired-blend-prospective-20260916/README.md).

## Wider-menu hand groups (N21)

Every positive-weight class was observed across its twenty boards. The post-evaluation group breakdown still finds a small regression for out-of-position suited connectors/gappers (about 4.94% of range mass): error 5.368 versus 5.272% pot on the control menu and 5.628 versus 5.531% on the expanded menu. No subgroup uncertainty or population claim is inferred from this descriptive breakdown. [All groups and coverage](../flop-menu-20260916/HAND-GROUPS.md).

## Positive-hand reference coverage

The completed N15 and N20 coverage audits found observations for every positive-weight hand class across their 400 and 200 references. This rules out completely missing positive-weight classes in those tests; it does not establish precise values or coverage of unseen situations. Weighted board counts are descriptive, not independent sample sizes or confidence guarantees. [N15 coverage](../shrunk-residual-20260916/COVERAGE.md); [N20 coverage](../policy-transfer-optimized-20260916/N20/COVERAGE.md).

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
