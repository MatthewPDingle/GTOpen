# Finite-game qualification of conditional river update estimators

Prepared 2026-09-28 after both deal-coverage advancement gates passed. This is
a new, CPU-only synthetic correctness study. It changes no native solver,
completed experiment, saved policy, training dataset or production instance.

## Candidate and actual integration boundary

The current external-sampling walker explores every updating-player action,
samples opponents from the current policy, and records action value minus one
common policy-weighted value. Physical-deal importance weights enter the loss
once. The river learning probe supplies only a Call-minus-Fold contrast against
frozen averaged opponents, not the complete vector required by this walker.

For a fixed updating player i, visible river information set I and frozen
current policy sigma, define each legal action value as a conditional average
over compatible deals. Weight hidden deals by their target chance probability
times the opponent's policy likelihood along the public history. Do not include
the updater's own action likelihood: zero-probability own branches are explored.
Condition on the updater's private cards, visible board and complete history.
Let m(I,a) be the resulting full downstream value for action a, including all
future policy choices. Fold, Call and Raise all need values in the same units.

Candidate A preserves the original sampled visits and downstream records, but
at each visited river updater node replaces the action vector by m(I,*).
It records m minus sigma dot m and returns sigma dot m to ancestors. Ancestor
updates and weighted visit sums must match exhaustive counterfactual values;
conditional correctness at a single node is insufficient.

Candidate B uses an arbitrary baseline b(I,*) fixed before the traversal and
an independent Bernoulli B with known positive probability rho(I):

    corrected(I,*) = b(I,*) + B/rho(I) * (m(I,*) - b(I,*))

It then uses the same common centering and return as A. This reduces the rate
of exact conditional requests, not necessarily total runtime or variance.
Do not clip corrected values to payoff limits. An inaccurate baseline must not
be treated as a true payoff. All original sampled downstream visits remain;
skipping descendants would change their training distribution and is outside
this study. The native bridge and a useful full-action baseline do not exist yet.

If source deals are sampled from q rather than target chance p, retain p/q as
the original visit's loss weight, once. Compare weighted update numerators AND
weighted visit mass. Their population ratio is the weighted regression target;
this does not claim finite-sample ratio estimates are unbiased. At root and
ancestors compare weighted returned values, including conditional replacement.

## Frozen finite tests

Use an explicitly synthetic eight-card deck (four ranks, two suits), one private
card per player and one shared river card, with no overlaps. This is not NLHE
accuracy validation. Enumerate every compatible deal and every sampled opponent
action and Bernoulli outcome, retaining their probabilities. Include ties,
unequal private-card entry weights and visible-board information boundaries.

The public tree has an upstream player-0 decision, including a zero-probability
own action. Each continuing branch reveals the river; player 1 may check or
bet, player 0 may Fold/Call/Raise, and player 1 may Fold/Call the raise. Preserve
perfect recall. Test both updating players, asymmetric rank/board-dependent
policies and a rare opponent branch. Use zero rake and action-dependent capped
rake fixtures. Raked payoffs are not assumed zero-sum.

Enumerate target-matched and skewed full-support deal proposals. For each,
compare original external sampling, conditional replacement, and gated exact
correction with zero, deliberately inaccurate fixed, and oracle baselines.
Use visible-node-dependent rho in {1/4, 1/2}. The oracle baseline is only a
synthetic control. It is not a claimed trainable predictor or practical result.

Use an independent terminal-path oracle for complete continuation values and
counterfactual update sums. Compare expected root values, every reached
information set's legal action-update numerator and visit mass. Verify all
legal action vectors center under their local policy, including zero-probability
actions, and demonstrate a supported zero-own-reach update is not discarded.

Acceptance: absolute error <= 5e-10 times max(1, reference magnitude), all
enumerated probabilities sum to one, and matching original/candidate visit
mass. Also retain exact variances of root returns and per-information-set
updates. No requirement that every estimator reduce every variance: an inaccurate
baseline, importance weights or correlated branch returns may worsen it.

Negative controls must expose errors above 1e-6 in at least one substantive
root/update quantity for: omitting opponent-history likelihood, using proposal
rather than target chance in conditional values, weighting a record twice,
using the wrong opponent policy for conditioning, treating zero own reach as
unsupported, and substituting an uncorrected arbitrary baseline. Do not loosen
tolerances or remove failing controls after execution; preserve failed evidence
and version any correction.

## Execution and next gate

Register this plan, source and relevant inspected native/weighting identities
before analysis. Maximum 180 seconds CPU execution and 5 MB evidence. No GPU,
training, final evaluation queries or S-drive archives. Prefer exact arithmetic
where practical and independent formulations over a test that repeats code.

Passing qualifies the derivation on these finite games only. Next inspect how
to realize the same visit-preserving scheme in a separate native research
bridge using current-policy identities, full legal vectors and bounded cost.
Measure variance reduction per wall-clock time before any self-play experiment.
Failure remains failure; the broad preflop-range goal remains active.

The correction principle is consistent with baseline-plus-unbiased-residual
constructions in Schmid et al., VR-MCCFR (https://arxiv.org/html/1809.03057).
The particular conditional replacement and gated exact-request scheme above
are our proposed implementation derivation, to be checked here; the paper's
published speedups and equilibrium claims are not transferred to GTOpen.
