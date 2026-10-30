# Combining direct preflop tables with exact all-in targets

The combined trial completed, and its training replay, blind-defense evaluation
and opponent-response evaluation all passed their integrity audits. It restores
more calling than the exact-all-in network-only trial, while producing fewer
shoves than the earlier direct-table trial. **This is a change in behavior, not
evidence that the resulting ranges are accurate enough to deploy.**

## What changed in the ranges

These frequencies use all 1,326 physical starting combos, weighted by compatible
opponent cards and the frozen incoming ranges. They aggregate the recorded class
policies, removing differences caused by the random hand mix in each test set.
The exact-prior check independently enumerated 776,650 positive-weight compatible
private-card pairs and reproduced the sampler's marginal to 7.6e-19.

| Research policy | Fold | Call | Raise | Jam |
|---|---:|---:|---:|---:|
| Original network | 53.77% | 26.15% | 12.84% | 7.24% |
| Direct preflop tables | 45.89% | 28.79% | 13.45% | 11.87% |
| Exact all-in targets, network preflop | 55.88% | 26.23% | 16.12% | 1.78% |
| Both changes together | **48.54%** | **31.42%** | **15.86%** | **4.17%** |

Relative to exact-all-in targets alone, the combined version calls 5.20 percentage
points more and folds 7.34 points less, but jams 2.39 points more. Its action mix
differs substantially across hands: the incoming-range-weighted total variation
between these two policies is 29.32%. That is a policy-distance description,
not an accuracy score. The original sampled-test mixes are also retained in the
comparison artifact; none of the registered value tests have been reweighted.

## What the value tests establish

Both families used the frozen complete played bank, a separate 8,192-deal set for
choosing a restricted response, and 16,384 fresh test deals. The BB-root and
BTN-versus-jam families each used alpha 0.025, for a joint within-trial error
allocation of 0.05. Gains below are per original BB spot entry, not per jam.

| Restricted alternative | Mean gain over the candidate | Registered interval |
|---|---:|---:|
| Learned BB root response | -0.354 bb | [-1.802, +1.093] bb |
| BB always folds | -0.639 bb | [-2.033, +0.755] bb |
| BB always calls | -1.239 bb | [-2.538, +0.060] bb |
| BB always raises | -5.277 bb | [-6.748, -3.805] bb |
| BB always jams | -15.663 bb | [-18.610, -12.717] bb |
| Learned BTN response to jam | -0.180 bb | [-1.171, +0.811] bb |
| BTN always folds to jam | +0.004 bb | [-1.005, +1.013] bb |
| BTN always calls the jam | -1.634 bb | [-2.903, -0.366] bb |

No tested alternative has a positive lower bound. This means these restricted
tests did not demonstrate a profitable deviation. It does **not** establish a
small best-response gap or a good equilibrium: the alternatives are limited,
and the intervals are wide. A negative learned-response mean also does not mean
the true best response loses; it shows that this fitted response failed to
outperform on the fresh sample. The BTN policy calls 25.88% conditional on a BB
jam in this test population; 29 sparse-class test deals used the declared
baseline fallback.

Cross-trial value comparisons remain descriptive. The four trials have different
opponent and continuation policies and different test seeds. The original dense
evaluation used float32 inference; the later three used checked float64
inference. Older BB studies also used a different error allocation. Their means
must not be treated as a paired improvement test.

## Why this still needs work

More total calling hides very uneven hand allocation. For example, the combined
policy calls 88 about 78.5%, but calls 77 only 0.7% while raising it about 95.0%.
TT jams about 92.0%; AQs folds about 25.0% and jams about 72.0%. These frozen
strategy frequencies are real outputs, not sampling uncertainty in the displayed
mixes. They warrant investigation in this 200 bb BB-versus-2 bb BTN-open game.
Visual implausibility alone is not a formal exploitability proof.

The per-hand value estimates do not settle those decisions. Many named suited
hands have only 35–50 test deals, and the different candidates face different
opponents and postflop policies. All 169 classes, including counterexamples, are
preserved. Do not patch selected hands from these inspected results or infer
that a higher calling total is automatically closer to Wizard.

## Next decision

Do not deploy or replace the existing range preview. Continue the visible
hand/board representation integration checks, motivated by the earlier finding
that most retained-target fitting error is postflop. If those pass, freeze a
matched full-budget experiment before training. This tests whether useful
postflop features improve learned continuation values; it does not assume that
representation is the only limitation. Sparse, noisy targets and incomplete
learning remain plausible contributors.

Sharper evaluation also remains necessary. The reviewed conditional all-in
evaluator can reduce board noise in a separately registered future evaluation;
it must not silently replace the just-completed sampled-payoff test. Larger
fresh samples may still be needed, since the current conservative interval has
a substantial sample-count term even with low variance.

This study remains a conditional two-player subtree with fixed incoming ranges,
limited action menus and omitted earlier folded cards. It is not an updated
UTG/LJ result, a general preflop model, or a Wizard-equivalence claim.

## Reproducibility

- 78 fixed updates, 39,936 training deals, 512 fitting steps per update/player;
  terminal training time 5,091.125 seconds. Played generations 0–77 are averaged;
  unused generation 78 is excluded.
- Final checkpoint SHA-256:
  `8ba97506fc04bae45c4bffc9995d171f6409b4f961dd37ce6f6e210b856523c1`.
- Training audit replayed 79,872 native reference/cashflow traversals and
  reconstructed every generated preflop table. It checked 94,619 BB and 51,258
  BTN supported, nonuniform preflop policy rows.
- Training/controller/audits/evaluations completed in about 124.3 minutes total.
  BB evaluation took 1,344.6 seconds, BB audit 362.6 seconds, BTN evaluation
  149.4 seconds and BTN audit 68.1 seconds.
- Complete evidence prefixes: `sampled-physical-hybrid-allin-pilot-v1`,
  `sampled-physical-hybrid-allin-evaluation-v1`,
  `sampled-physical-hybrid-allin-btn-evaluation-v1`,
  `sampled-physical-hybrid-allin-comparison-v1`, and
  `sampled-physical-hybrid-allin-exact-root-mix-v1`.

Production port 56708 and the experimental UTG/LJ preview were unchanged.
