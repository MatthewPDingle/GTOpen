# Next research after native river bridge controls

Updated 2026-09-28. All coverage, performance, synthetic and native control
jobs are terminal. There are no live study processes to resume. The broader
goal remains active; do not re-run completed one-shot sources.

## Completed evidence

- Equal-budget coverage: both predeclared gates passed. Broader exact training
  reduced fresh prediction error 16.28% and local Fold/Call cost 36.28%. See
  BOARD-RIVER-DEAL-COVERAGE-REVIEW.md for limits and mixed subgroups. No preflop
  or full-policy improvement has been demonstrated.
- Full-bank shared preparation: byte-identical outputs and 1.761x faster
  preparation/inference excluding guards, saving 0.376 seconds/case. Reuse the
  exact qualified helper only in newly registered work.
- river-conditional-estimator-synthetic-v1: all 40 positive configurations and
  six deliberately wrong controls passed. 168,000 synthetic trajectories
  checked updates, ancestor returns and visit weights. Gated exact requests
  with poor baselines increased variance despite preserving expectations.
- river-full-action-control-v1: all nine native configurations passed; full
  downstream legal river trees for all 990 opponent pairs. Both actors,
  Check/Fold/Call/Bet/Raise, ties, rake, branch offsets, identity checks and
  zero-own-reach support passed. Existing Fold/Call values matched within
  2.85e-14 bb. A complete-source replay resolved an initial source-inventory
  omission with byte-identical output; original evidence is unchanged.

Read RIVER-FULL-ACTION-BRIDGE-FINDINGS.md and both control/provenance plans.
The new Rust example and Python scripts are executed/registered and immutable;
version corrections or additional tests rather than editing them in place.
Primary checks took 14.47 seconds; replay 1.76 seconds; total evidence 39.67 MB.

## Next bounded implementation

Register a training-only fixed-current-policy inference/cost pilot. Use the
last played generation 77 from each audited board-root arm, not an average
policy or the unplayed generation 78. Their exact references are in
board-river-bounds-bank-v1-registration.json. Load those two model documents
with board_training_checkpoint_v1.model_document and validate against context,
catalog, matrix and root configuration. Existing board_training_policy_v1
probabilities supports independent CPU and CUDA paths for a single model.

Use the same identified model pair for history likelihoods and every future
river action. Reuse the frozen old-training cases, retain unsupported targets
explicitly, and add geometry-selected jam-as-bet/raise cases before declaring
that separate coverage. Preserve every failure and cap new evidence/runtime.
Profile CPU preparation, GPU inference and value propagation separately.
Compute exact conditional action/update variance against a correctly specified
sampled continuation; local zero target variance alone is not a wall-time win.

After that pilot, a NEW visit-preserving native research walker is still
required. Compare visits, full action updates and complete ancestor returns
against the unchanged sampler before registering bounded self-play. Then use
a fresh full-policy evaluation; spent final deals remain unavailable for tuning.

The old learned Call-minus-Fold regressor is not a complete action-value or
regret model. Do not insert it as an uncorrected payoff or pretend native
exporter controls qualify the full sampling algorithm. Cross-stack/rake/sizing
generalization remains separate under STACK-CONTEXT-PLAN.md.

No production deployment, historical deletion, additional GitHub push, Jev or
application popups. Keep the 800 GB allocated research cap; new control evidence
is small and on T:. Light desktop/video GPU sharing is authorized. Current
qualified guard permits utilization below 65% with 4 GB own budget and 2 GB
external headroom, while production solves and heavier GPU jobs take priority.
