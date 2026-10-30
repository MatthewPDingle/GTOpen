# Target the remaining chance variation

Research review, 27 September 2026. No algorithm or running experiment changed.
This is preparation for interpreting the stratified study, not a decision to
launch another long training run before its results are available.

## What is already implemented or tested

`action_integrated_root_targets_v1.py` evaluates the same physical deal under
each forced BB root action and integrates later action choices. The initial
jam also integrates compatible private hands and future boards separately.
Call and ordinary raise still use sampled private cards and boards.

`showdown_root_targets_v1.py` is a different technique: a root-only centered
showdown feature with frozen class coefficients. Its completed comparison did
not demonstrate better play. Earlier eight-feature flop-rank controls did not
give useful consistent variance reduction either. These failures do not test
every variance-reduction method, but repeating those features without new
evidence is a poor use of another training budget.

See [completed showdown study](SHOWDOWN-MATCHED-FINAL-FINDINGS.md),
[flop controls](FLOP-CONTROL-VARIATE-FINDINGS.md), and
[current within-class diagnostic](WEIGHTED-WITHIN-CLASS-NOISE.md).

## What the primary research says

Schmid et al. use action-dependent baselines with recursive, sampling-probability
corrections. Their construction preserves expected values; its usefulness
depends on baseline quality. The reported speedups are for their algorithms and
benchmarks, not a prediction for this learner. [VR-MCCFR, equations 7–18 and
experiments](https://arxiv.org/html/1809.03057).

Davis et al. distinguish trajectory noise from variation caused by sampling a
private history. Their public-outcome method enumerates private states while
sampling public outcomes. Their predictive-baseline zero-variance theorem has
specific coverage and sampling conditions. It does not automatically apply to
our neural continuation approximation. [Low-Variance and Zero-Variance
Baselines, sections 6–7](https://proceedings.mlr.press/v119/davis20a/davis20a.pdf).

## Applicability to this code: our analysis

A quick root-only per-class baseline is not enough. For a baseline `b` that is
constant over one class/update, averaging `b + (Q - b)` gives exactly the same
sample mean as averaging `Q`. Fixed within-class source weights do not change
that identity. Merely training another network to predict that constant does
not reduce the observed within-class variation. A useful control needs a
varying predictor with a correctly computed expectation, or a different
conditional integration/sampling scheme. This does not rule out recursive
baselines for other sampled parts of the learner.

Two distinct possibilities remain worth a bounded feasibility comparison if
the completed study still shows large instability:

1. Hold a complete strategy fixed and evaluate additional private holdings and
   boards per starting class. Measure paired target dispersion against elapsed
   time, including inference, native traversal, storage and verification. This
   is the simple reference against which a clever estimator should compete.
2. Investigate a board-first evaluator that sums compatible private holdings
   in batches. Reusing each board across many hands could suit the GPU better
   and remove sampled-opponent-card noise. This is a proposed engineering
   direction, not an implemented public-outcome CFR algorithm or a speed claim.

For the second option, preserve the original chance law. If `p(h)` is the
normalized entering distribution over compatible private-hand pairs and a
board is drawn from proposal `q(B)`, a joint-value estimator has terms
`p(h) * P(B | h) * value(h, B) / q(B)`. Conditional class values additionally
divide by the original class entry mass. Drawing boards uniformly and then
normalizing the surviving hands independently on each board generally changes
the target unless the board marginal correction is retained. Street order,
blockers and original range weights must remain explicit.

Even when the evaluator knows a sampled complete board, a player's policy may
only see its own cards and the board prefix revealed at that decision. Neither
opponent cards nor future streets may enter the policy input. Native leaf
evaluation and an internal training control have different information access
from a player's strategy.

The full action tree times all private pairs can still be expensive. Tile pair
work, reuse rank/compatibility data, and measure peak memory rather than assuming
24GB VRAM is sufficient. First enumerate a small finite chance fixture to check
means and conditional class weights, then compare against the existing native
evaluator under fixed strategies. The earlier large explicit-continuation
experiments and their storage limits must inform this design; do not restart
that approach at full scale under a new name.

## Decision order

Finish both registered training audits and the fresh payoff comparison. Combine
their findings with trajectory stability and the within-class diagnostic. If
more work is justified, qualify one small fixed-policy precision/cost experiment
before another long training study. Compare complete runs, not GPU utilization
or visual smoothness alone. Changes to positions, stacks and multiway modeling
remain separate accuracy requirements; success on this one spot cannot satisfy
the broader preflop goal.
