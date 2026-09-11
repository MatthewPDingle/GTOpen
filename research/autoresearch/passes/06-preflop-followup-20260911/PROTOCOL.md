# Follow-up: preflop speed and conditional convergence

Goal: test all four recommended directions from pass 05 and reach a defensible
research milestone. Preserve the live app on 56708. Push research changes, but
do not deploy experimental solver behavior. No previews count as convergence.

Results and limits are summarized in [FINAL-RESULTS.md](FINAL-RESULTS.md).
Follow-up registrations appear in `PHASE-C.md`, `CONDITIONAL-REFINEMENT.md`,
`NESTED-REFINEMENT.md`, `CHECK-SCHEDULE.md`, and `VARIANCE-SCREEN.md`.

## Phase A: registered before results

Reuse the frozen pass-05 benchmark executable (SHA256
`07d9ac1a4ecbf39d343cdb96eb3481d0d970b26da8279349e7016eb1466fe304`).
Its copy in `target/followup-frozen-bin` prevents an audit build from replacing it.
All source/executable/input/cache hashes are recorded. Source edits during a run
do not alter this binary; its pass-05 provenance remains authoritative.

- Original eight-player input: 64 samples, additional seeds 314159 and 90210;
  DCFR, limit 2000, full check every 50, cap 3600 seconds each.
- Existing fresh adaptive Ignition fixture: 64 samples, seeds 42 and 314159;
  DCFR, limit 1500, full check every 50, cap 1800 seconds each.
- Small six-player input: gamma15 plus 64 and 128 samples, seeds 42, 314159,
  90210; limit 1500, full check every 25, cap 600 seconds each.

Keep the 0.005bb summed learning-gap threshold and two consecutive full-1024
checks. Include initialization/checking costs; report save/reload-inclusive time
separately. Compare to matching pass-05 native controls only after verifying
input, cache, fit and executable hashes and normal exits. Do not assume measured
effects multiply. Repeat expanded own-policy/reference-policy local audits on
all candidates after the timed queue; inspect six required paths with legal
equal-blind SB checks. Forced nodes are not learning successes.

## Phase B: investigate rare-branch convergence

Inspect regret and average-strategy accumulation, conditional reach weighting,
and numerical scale. Reproduce on a bounded game before changing GPU learning.
Any targeted learning experiment must retain correct arriving ranges, action
menus, pot/stack accounting, fixed profiles and locks. Evaluate both local and
global quality after the extra work, including its time. A local change cannot
be called a converged full-tree answer without that recheck.

## Phase C: remaining overhead

Use measured phase-A results to select a candidate. Screen full-check cost and
schedule improvements against equally scheduled native controls, retaining full
accuracy and the two-pass stopping condition. Validate discount schedules by
actual time and local decisions, not iteration counts alone. Register subsequent
timing trials before examining their results.

## Phase D: variance reduction, if needed

If sampling variance limits quality or speed, prototype the control-variate
estimator described in pass 05. Begin with an offline variance/cost screen under
fixed current/reference ranges. Evaluate their nonlinear terminal functions
separately on matching particles, retain current counterfactual reach, and count
full reference refresh and memory costs. Reject biased clamping or stale cache
reuse. A neural range predictor is outside this pass.

One hardware workload at a time. The read-only live guard stops only owned
research if the user starts a solve/report. Preserve failures and partial runs;
never count them as successful speedups. Production release requires a separate
qualification decision after correctness and convergence evidence are reviewed.
