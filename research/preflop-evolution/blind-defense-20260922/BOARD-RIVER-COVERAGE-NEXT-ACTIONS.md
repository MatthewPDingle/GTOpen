# Next research after estimator correctness qualification

Updated 2026-09-28. All coverage, performance and synthetic estimator jobs are
terminal. There are no live study processes to resume. The broader goal remains
active; do not re-run completed one-shot sources.

## Completed evidence

- Equal-budget coverage: both predeclared gates passed. Broader exact training
  reduced fresh prediction error 16.28% and local Fold/Call cost 36.28%. Review
  BOARD-RIVER-DEAL-COVERAGE-REVIEW.md for limits and mixed subgroups. No preflop
  or full-policy improvement has been demonstrated.
- Full-bank shared preparation: byte-identical outputs and 1.761x faster
  preparation/inference excluding guards, saving 0.376 seconds/case. Reuse this
  exact helper only in newly registered work; do not rewrite completed sources.
- river-conditional-estimator-synthetic-v1: all 40 positive configurations
  passed, enumerating 168,000 trajectories in 2.8 seconds. All six deliberately
  wrong variants were detected. Updates, ancestor returns and visit weights
  were correct for both players, matched/skewed proposals and zero/capped rake.
  See BOARD-RIVER-ESTIMATOR-SYNTHETIC-FINDINGS.md and registered JSON evidence.

The synthetic conditional method reduced update variance, but gated exact
requests with poor baselines increased it despite preserving expectations.
Use full exact conditioning as the next native reference. The earlier learned
Call-minus-Fold contrast is not a complete action-value or regret vector.

## Next bounded implementation

Follow BOARD-RIVER-FULL-ACTION-BRIDGE-PLAN.md. The native bridge is NOT written
or tested yet. Adapt the existing research-only conditional query exporter in
a NEW example to include complete downstream legal action trees for all 990
opponent pairs. Preserve canonical keys, own-history ancestors, branch offsets,
terminal accounting and current-policy identity. Include raises, free checks
and zero-own-reach supported branches. Preflight size; never truncate actions.

Freeze old-training-only case identities and register sources, binary and bounds
before native controls. Reconstruct payoffs and values independently, reconcile
the existing Fold/Call references, and preserve negative controls/failures.
Only then run a bounded inference/variance-cost pilot against a current policy.

The following integration is still required: visit-preserving changes to a
separate research walker, correct complete action updates and ancestor returns,
then bounded self-play and a fresh complete-policy evaluation. No tuning on the
spent final deal sets or selecting favorable seeds/subgroups after scoring.

Current synthetic tests do not prove native sampling correctness or poker
accuracy. Cross-stack/rake/sizing generalization remains separate work under
STACK-CONTEXT-PLAN.md. No production deployment, archive deletion, additional
GitHub push, Jev or application popups. Respect hardware and storage budgets;
light desktop/video sharing is authorized and active solves take priority.
