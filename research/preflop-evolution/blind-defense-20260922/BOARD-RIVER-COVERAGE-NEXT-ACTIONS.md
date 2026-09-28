# Next research after fixed-policy river and preparation controls

Updated 2026-09-28. Coverage, shared preparation, synthetic estimator controls,
native exporter controls, fixed-current-policy pilot, CPU profile, vector
preparation and native single-target transport controls are terminal. No live
study process remains. The broader goal remains active.

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
- Native single-target substitution: 24 configurations passed, 576 preflop-root
  passes / 14,851 records unchanged in visit identity and RNG; 20 replacements
  reached from preflop, 288 additional direct-target passes. Ancestor values
  and regrets matched independent graph propagation within 3.56e-15 bb. All
  990 opponent-pair finite weight sums matched, including zero-own variants;
  seven malformed transports rejected. See RIVER-NATIVE-TRANSPORT-FINDINGS.md.

Read RIVER-CURRENT-POLICY-PILOT-FINDINGS.md for timings and limitations.
All executed/registered implementations are immutable; version additional work.

## Next bounded implementation

A separate native callback walker is now qualified for one target substitution
per fixture. It preserves every updater branch, sampled opponent decision and
RNG draw, with correct common centering and ancestor transport. The control
policy is a fully specified engineering fixture, not a learned model. Some
deep targets were not reached from preflop in the small seed set; direct-target
passes cover their callbacks. Do not overclaim this as full self-play validation.

Next register a bounded actual-current-policy batch cost/integration pilot.
Discover actual sampled river visits, group common visible states, reuse
queries across targets, and replay identical deals/seeds. Retain the trainer's
existing exact initial/board-root overrides. Qualify multiple nested targets
before enabling them together. Bind all vectors to one current policy/context;
omit unsupported vectors explicitly. Apply source-deal weights once at original
ingestion. Use the frozen exporter, exact math and vectorized preparation in
new modules only. Measure complete cost/variance before large training.

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
