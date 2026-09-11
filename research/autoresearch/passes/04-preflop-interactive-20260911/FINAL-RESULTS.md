# Pass04 results — draft awaiting final integration and remaining runs

The demonstrated improvement is earlier access to an unchanged full-reference strategy: in the paired API-c test, a navigable/exportable spot became available in12.266 seconds instead of299.078 seconds, **24.38x earlier**. This exposes the solve's current work without waiting for its normal final publication. It does **not** make that early strategy accurate24.38x sooner.

**No10x improvement in qualified time to accuracy has been demonstrated.** Compressed models and conditional refinement produced useful research results, but their failures and unverified scope prevent that claim. This document does not mark the research goal, production validation, deployment, or GitHub publication complete. Root will replace pending entries with terminal evidence.

## Original objective and what changed

[program.md](program.md) asked for a usable interactive Preflop Lab, approximately an order of magnitude faster than the already optimized`ff54279` reference. It separated cheaper continuation values, early strategy publication, and independent decision-quality measurement. The baseline is that optimized implementation, not the earlier slow implementation.

The strongest candidate for installation is **exact early publication with detached GPU work**. Users can navigate an actual completed snapshot while the next iteration computes. Measured accuracy is labeled separately from the displayed iteration, so an early snapshot is not mistaken for a converged solve. Model arithmetic, default full1024 values, native format and precision stay unchanged in the curated production scope. Its final production binary and session-preserving installation still require root's completion record.

## Experiment outcomes, including failures

| Experiment | Measured result | What it establishes / remaining failure |
|---|---|---|
| API-c exact Reference publication |All4 API cases pass. Export299.078→12.266s; preview has iteration2 with accuracy unmeasured. Reference on/off native header, both full arenas, final gaps/EV/iterations match exactly.|24.38x earlier availability on this fixture. Both finish50 at gap1.49551663 and iteration limit, not target0.005. No faster-convergence claim.|
| Frozen32-v2 continuation |Core/BB checks pass; independent overlap worst error8.5864pp versus full3.8714pp; additional mean1.6000pp.|Rejected for general preview: exceeds both overlap guards. The supplementary nine-way AA pass does not cancel this failure.|
| Frozen64 continuation |Large1000 global relative gates pass in470.559s total, but physical overlap additional mean1.14470pp, propagated interval[1.05802,1.19339] against limit1pp.|Rejected as a generally qualified cheap model. Local small-tree failures persist. API-c64 export4.0s remains an unqualified early result.|
| Frozen128 physical model |Training-only selection; reserved new physical corpus passes unchanged core/BB/relative-stress gates, with uncertainty checks.|Supports further native testing. It inherits full latent-model limitations; full and128 still have substantial absolute premium-overlap error.|
| Native128 small primary |Development global pass from10; adaptive from30. Fixed/frozen100 fails excess0.0235723>0.02 and mean positive loss0.0102495>0.01.|100-iteration constrained result is not accepted. Several original-continuation local gates fail, including after supplemental500.|
| Native128 large50 |First snapshot4.623s, solver47.356s,total55.180s. Global excess1.35941,mean0.079743,max0.123430.|All candidate global gates fail. Historical full50 fixed-work solver ratio6.39x is not time to quality.|
| Native128 large1000 |Solver728.126s,total734.919s; global excess0.00264499,mean0.00026127,max0.00117942 pass; exact native roundtrip.|Passes only these global comparison gates. Own gap0.00614523 and full-evaluated0.00742875 exceed absolute0.005. Large local tails unmeasured; small failures persist.|
| Full-payoff conditional refinement from64 |Six tested BB cases; five retain improved conditional gaps, one correctly retains its better baseline. Three-case runs4.899s/4.777s including load/audits.|Promising bounded continuation repair. Every source restores exactly, but prefix remains unvalidated and original-continuation tail failures are not waived.|
| Small development warm starts |Scale0.01 plus50 full iterations improves two local paths; rare SB limp path still fails. Larger scales0.1/1 have additional early local failures.|A limited initializer result, not a generally accepted strategy or end-to-end10x result.|
| Large warm start from64 source50, scale0.01 |All five native checkpoints verify exactly. Fresh full100 gap0.42837396;780.451s through audit, excluding source creation.|Fails0.005 accuracy and0.02 excess-gap gate. No matched fresh full100 timing comparison.|
| Large warm start from64 source1000, scale0.01 |All five native checkpoints verify exactly. Fresh full100 gap0.51658592;772.057s through audit, excluding source creation.|Also fails accuracy and excess-gap gates. The previously passing source average policy does not qualify this fresh-regret conversion or its resulting policy.|

The paired Reference API-c cache has20,000 samples, unlike API-a's accidentally regenerated1,024-sample cache. API-a remains in the evidence with its limitation; it is not mixed into current numerical comparisons. The exact Reference publication pair ends with the same strategy; their early and late strategies are naturally different stages of learning. See [API-c summary](proposals/early-preview/preview-api-c-summary.json) and [cache discrepancy resolution](proposals/early-preview/BENCH-API-DISCREPANCY.md).

## Why passing the global comparison is not enough

A whole-game average can hide a bad decision on a rarely reached branch. Native128 development500 passes the global gates, yet one SB path assigns100% to an action worse by more than0.1bb under the original reference continuation for a relevant hand. Another path retains about45.6% such probability. Those failures stay visible even where their contribution to whole-game error is tiny.

Conditional refinement solves the future of the selected branch under full payoffs and can improve that branch's self-play gap quickly. It does not prove that the approximate strategy reached the branch with the correct ranges. It also changes future play, so its low conditional gap is not the same test as choosing one action and then following the original future strategy. The retained result flags remain `prefix_unvalidated:true` and `quality_qualified:false`.

Next evidence needed: qualify local decisions and modeled/frozen-seat cases at adequate iteration budgets; validate arriving ranges and representative branches; measure complete initialization/refinement cost against the same passed quality condition. More accurate physical deal modeling remains separate from matching the full latent reference. Do not promote compressed models merely because their terminal computations or first screens are fast.

## Remaining runs and explicit unrun entries

These are pending placeholders, not successful outcomes. Read only completed terminal records before replacing them.

| Follow-up | Current evidence status in this draft |
|---|---|
| Large warm start from64 source50, scale0.01 |Completed successfully as an experiment, but failed accuracy/excess-gap gate at100. Unilateral/local audits unmeasured; see completed result above.|
| Large warm start from64 source1000, scale0.01 |Completed successfully as an experiment, but failed accuracy/excess-gap gate at100. Unilateral/local audits unmeasured.|
| Large warm-start scales0.1 and1 |Unrun on large fixture in evidence reviewed; small development measurements are separate.|
| Adaptive large128 fixed500 plus full global audit |Source-only prepared; unrun in evidence reviewed. Explicitly adaptive after50 failure/1000 success.|
| Adaptive fixed/frozen128 fixed500 plus quality100/500 |Source-only prepared; unrun in evidence reviewed. Requires new100 nativeSHA to match prior100 before extended-trajectory interpretation.|
| Large128 local action tails / generally validated prefix |Unverified. Global audit did not measure them.|
| Matched fresh full1000 time to the same accepted quality |Unavailable. The existing full1024 reference has resumed timing history.|

See [adaptive protocol](proposals/quality-gates/HERDING128-ADAPTIVE-FOLLOWUP.md). Missing runs remain unrun if the deadline or production validation takes priority; no threshold moves to compensate.

## Completion checklist for root

- [x] Register independent physical and native policy gates, preserve frozen candidates and seen/held-out labels.
- [x] Retain32/64 physical rejections,128 local/constrained failures, incomplete accuracy outcomes, and historical timing limitations.
- [x] ResearchH frozen suite:272passed,0failed,26existingignored across37 executables after correcting package working directory. The initial two missing-fit failures and corrected repeat are both retained. [H checks](H-CHECKS.md).
- [x] Paired API-c exact Reference publication/arena/metadata checks pass; final-stage convergence is not claimed.
- [x] Curated Reference-only production implementation proposed in an isolated worktree; no compressed-model default or research model format import. [Integration checklist](proposals/early-preview/PRODUCTION-INTEGRATION-CHECKLIST.md).
- [x] Curated source 53ce9dec08de9fa2f93f246d7f5efcccc8c22c68, staged GPU runtime SHA 7de6c8aaaef5daf840411218a27e13bfda41017571537fac26b76f3414f87bdc: 232 production tests passed, 0 failed, 5 intentional manual performance/stress tests ignored, 90 filtered. Includes full non-GPU solver/server tests, both GPU integration suites and the detached exactness test. All 47 build/test jobs exited 0. JS helper/syntax checks passed at source preparation. See [production qualification](PRODUCTION-QUALIFICATION-REPORT.md). Final API/UI remains pending.
- [ ] Root append final UI/browser and Reference-only API/lifecycle checks, including blocked mutation/stop/resume/export provenance.
- [ ] Root append completed large warm-start and optional adaptive follow-up outcomes, or explicitly record them unrun.
- [ ] Root verify current live work, back up both native sessions, complete session-preserving installation/rollback checks if qualified, and record restored state.
- [ ] Root record final GitHub push/commit status and remaining limitations. This draft does not assert publication or deployment.

Detailed evidence: [physical128](proposals/quality-gates/RESULTS-HERDING128.md), [32/64 rejection](proposals/quality-gates/RESULTS-32-AND-AA-SUPPLEMENT.md), [native128 small and conditional](proposals/quality-gates/RESULTS-NATIVE128-AND-CONDITIONAL.md), [large128](proposals/quality-gates/RESULTS-LARGE128.md), [warm starts](proposals/continuation-ensemble/WARMSTART-RESULTS.md). Original raw records remain authoritative; this draft changes none of them.

Completed and pending large warm-start cases are tracked separately in [large warm-start results](proposals/continuation-ensemble/WARMSTART-LARGE-RESULTS.md).
