# Board-first chance arithmetic: finite control passed

This is an exact small-deck probability check for the proposed evaluator, not
a poker solver, GPU implementation, training experiment or accuracy result.
The running stratified study is unchanged.

The control enumerates an eight-card deck with two private cards per player
and a two-card board. It uses deliberately synthetic asymmetric utilities,
not hold'em rankings. Six fixtures combine uniform, weighted and restricted
private-hand ranges with uniform or nonuniform board proposals. Each fixture
enumerates all 2,520 disjoint private-pair/board outcomes.

Two different loop orders calculate expected values: private pairs followed
by legal boards, and boards followed by legal private pairs. Exact rational
arithmetic confirms equality globally and conditional on every positive-mass
hero holding, for all four utility columns. Restricted fixtures also contain
nine hero holdings with zero entry mass; they remain zero rather than acquiring
fabricated conditional values. The fourth utility column is a paired action
difference, checked alongside the individual values.

## A concrete trap the control exposes

Normalizing the surviving private hands separately on each board and averaging
those conditional values under the proposal changes the expected value. This
incorrect variant passed only the fully uniform symmetric fixture. It failed
all five other fixtures, with maximum absolute bias about 0.201 synthetic utility
units. Real range weights and blockers cannot be dropped during reordering.

The correctly importance-weighted proposal preserves means, but may introduce
variance into even a constant utility: the fold-like value is always -1 in the
original fixture, yet a mismatched board proposal gives a fluctuating mass
weight. Its variance reaches about 0.36 in one fixture. This is an engineering
warning: keep the learner's existing exact fold and initial-jam expectations
instead of replacing them with a generic noisy weighted-board estimate.

Conditioning on the **true** board marginal, in contrast, never increased
variance in these fixtures; that equality/inequality was checked with exact
fractions. Drawing from a convenient proposal and applying importance weights
is a different estimator. Neither the large variance reductions of these
synthetic utilities nor their runtime predict poker performance.

## Remaining gates before this can affect a range

The real evaluator still needs implementation and comparison with the native
physical-deal path. Its distribution must include the actual entry ranges,
physical blockers, board order and conditional class normalization. Policy
observations must exclude opponent cards and unrevealed future streets.
Check proposal support, impossible boards, all original action values and
regret centering, then benchmark time and memory against additional ordinary
samples under a fixed strategy. No new long training run follows from this
arithmetic check alone.

[Exact results](board-first-chance-identity-control-v1-result.json) bind the
source bytes of `tools/research/board_first_chance_identity_control_v1.py`.
All six fixtures took about 0.83 seconds on one CPU thread, using no GPU and
without touching training files. See the [research applicability review](CHANCE-VARIANCE-RESEARCH-REVIEW.md)
for the larger context and primary literature.
