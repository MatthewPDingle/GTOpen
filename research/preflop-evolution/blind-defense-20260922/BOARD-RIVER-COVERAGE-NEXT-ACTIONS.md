# Next research after fixed-policy river and preparation controls

Updated 2026-09-28. Coverage, shared preparation, synthetic estimator controls,
native exporter controls, fixed-current-policy pilot, CPU profile and vector
preparation controls are terminal. The broader goal remains active.

## Completed evidence

- Broader exact training passed the two predeclared fresh local gates: prediction
  error -16.28%, Fold/Call cost -36.28%. Mixed subgroups and a generalization gap
  remain. See BOARD-RIVER-DEAL-COVERAGE-REVIEW.md. No full-preflop gain proven.
- Full-bank shared preparation was byte-identical and 1.761x faster in its
  separate workload. Do not multiply it by later speedups without integration.
- Synthetic conditional estimator: 40 positive configurations, 168,000
  trajectories and six deliberately wrong controls checked. Gated exact
  requests with poor baselines increased variance despite correct expectation.
- Native full-action exporter: nine configurations, all 990 opponent pairs,
  both actors and all legal river actions. Independent payoff and path-value
  checks passed. Full-source replay reproduced exports byte-for-byte.
- Fixed-current-policy pilot: generation 77 from both played arms, 12 cases,
  23/24 supported; 18 supported zero-own-reach cases. CPU/GPU probabilities
  agree within 1.94e-13, values within 1.17e-12 bb. The unsupported A/p1-jam-raise
  case is retained. The private opponent hand dominates target variance in
  these reused training fixtures. No training or fresh policy evaluation yet.
- Vectorized visible-card summaries: 40,528 direct examples and 57,025 query
  rows byte-identical. Complete preparation 1.837x faster in paired timings;
  direct summary calculation 10.69x faster. CPU-only, no production change.

Read RIVER-CURRENT-POLICY-PILOT-FINDINGS.md for timings and limitations.
All executed/registered implementations are immutable; version additional work.

## Next bounded implementation

A NEW visit-preserving native walker remains required. It must traverse the
same updater branches, sample the same opponent actions, retain all records
and consume the identical random stream before replacing the complete river
action vector. Center regrets and return values under the same fixed policy.
Compare against the unchanged policy_walk_allin_v1.rs. Apply source-deal
importance weights exactly once outside the target calculation.

Use the existing exact exporter and qualified fixed-policy math; vectorized
preparation can be used only in new work. First qualify transport, visit/RNG
preservation, full regret vectors and ancestor returns, both actors, zero own
reach, unequal proposal weights and rake. Retain unsupported states explicitly.
Pilot cost was dominated by CPU preparation, so batch/reuse actual visited
queries and measure the complete integration before launching large training.

Then register bounded matched training and use new full-policy evaluation.
Spent final deals cannot become tuning inputs. Cross-stack/rake/sizing coverage
remains separate under STACK-CONTEXT-PLAN.md. Local zero conditional variance
or prediction MSE improvements alone are not proof of better preflop ranges.

No production deployment, historical deletion, additional GitHub push, Jev or
application popups. Keep the 800 GB allocated research cap (last admission
717.79 GB); new control evidence is small and on T:. Light desktop/video GPU
sharing is authorized. The qualified guard permits utilization below 65% with
4 GB own budget, 2 GB external headroom and 24 GB free RAM. Production solves
and heavier GPU jobs take priority. The last live probe found heavy GPU load,
so continue CPU-only work until a fresh guard allows GPU research.
