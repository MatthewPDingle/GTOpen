# Next research after completed coverage and runtime checks

Updated 2026-09-28 18:29 Adelaide. Collector, pipeline, supplemental analysis
and full-bank speed qualification are terminal and successful. Do not restart.
See BOARD-RIVER-DEAL-COVERAGE-STATUS.md for process identities and evidence.

Both scientific descriptive gates passed. Read BOARD-RIVER-DEAL-COVERAGE-REVIEW.md
for interpretation and mixed subgroup results. Shared preparation also passed
full-bank output equality and timing checks: 1.761x faster preparation/inference,
0.376 seconds/case saved excluding guard time. Future registered collectors may
reuse that exact helper with per-bank validation and unchanged inference order.
Never rewrite completed registered sources.

## Next bounded work

1. Read BOARD-RIVER-TARGET-INTEGRATION-NOTES.md and inspect the native traversal,
   proposal/reach treatment, weighted reservoir and training objective. Derive a
   complete estimator and identify exactly which randomness is reduced.
2. Freeze a synthetic correctness plan before execution. Enumerate small games
   with asymmetric policies, unequal deal proposals, zero-probability own actions,
   rare opponent histories, ties, rake and raises. Verify complete action-update
   expectations and ancestor returns. Include deliberately wrong weighting and
   conditioning as negative controls.
3. Retain sampled residual corrections when using learned baselines. The current
   output1-output0 regressor is a Fold/Call contrast against averaged fixed
   opponents; it cannot replace all action values or the per-iteration policy.
4. If synthetic checks pass, qualify a narrow native bridge and measure variance
   reduction per elapsed second. Use qualified shared preparation where its
   contract applies. Bound time, data and resources before starting a pilot.
5. Only then register bounded self-play and fresh full-policy evaluation. Prior
   final sets are spent. Preserve all seeds/failures without picking winners
   from favorable subgroups after scoring.

The estimator design and native pilot are not yet implemented or tested.
Stack/rake/sizing inputs remain separate requirements (STACK-CONTEXT-PLAN.md);
the current features/context hash do not generalize across stack depths.
The broader accuracy goal remains active. No production deployment, archive
deletion, broad GitHub push or Jev integration follows from these results.
