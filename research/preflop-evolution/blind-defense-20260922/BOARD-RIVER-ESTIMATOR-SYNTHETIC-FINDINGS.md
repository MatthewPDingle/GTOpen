# Conditional update estimators: finite-game results

Completed 2026-09-28. The frozen study ran in 2.8 seconds on CPU. All 40
positive configurations passed, covering both updating players, zero/capped
rake, matched/skewed deal proposals and five estimator/baseline combinations.
Each configuration enumerated all compatible deals and sampled action/gate
outcomes: 168,000 positive-case trajectories in total, without Monte Carlo error.

This is an eight-card synthetic stake-choice game, not NLHE. Entering its two
continuation branches sets different matched stakes by definition; that root
choice is an artificial extensive-form fixture, not a claimed poker action.
River Fold/Call/Raise responses, private information, ties and capped rake
exercise the integration invariants. Native poker correctness remains untested.

## What passed

- Conditional full-action vectors reproduced expected external-sampling updates
  for every reached information set and weighted values returned to the root.
- Raw visit probabilities and weighted visit mass were preserved. Source-deal
  importance weights entered once, independently of conditional target values.
- Supported zero-probability own branches retained nonzero updates. Opponent
  history was included in conditional weights; own history was excluded.
- All vectors used one policy-weighted centering value. Visible information
  determined policies; the upstream policy did not see the future board.
- Ties, folds, a binding rake cap and no river rake on the initial exit had
  hand-calculated controls. Raked payoffs were not assumed zero-sum.
- Independent terminal-path enumeration agreed with recursive continuation
  values within 7.11e-15. Maximum scaled update/root error was 4.06e-15 and
  maximum visit-mass error 1.06e-15, below the frozen 5e-10 tolerance.

All six negative controls produced errors above 1e-6. Maximum root/update
discrepancies were 0.705 when history was omitted, 0.135 using proposal chance
in the posterior, 0.488 double-weighting, 1.193 using a different opponent
policy, 0.651 dropping zero-own-reach branches, and 2.195 substituting an
uncorrected arbitrary baseline. These are synthetic payoff units.

## Variance and the practical choice

Exact conditional replacement reduced root-return variance by 39.8%-49.6%
and the summed information-set update variances by 35.4%-52.2% across the eight
actor/rake/proposal fixtures. These are exactly enumerated variances in the
small games, not speed or convergence estimates for GTOpen.

The Bernoulli-gated correction stayed unbiased with every tested baseline,
including deliberately inaccurate ones. However, zero and inaccurate fixed
baselines increased variance substantially. An oracle baseline reproduced
exact conditional replacement, as it should. This supports mathematical
correctness, not adopting the cheap gated variant with an unqualified model.

Use full exact conditioning as the next native reference. A learned correction
needs a separately validated full-action baseline and variance-per-time evidence.
The successful Call-minus-Fold regressor has not learned its other action heads.
Do not insert it as an uncorrected payoff or complete regret vector.

## Limits and next gate

The tests preserve all sampled visits even when an exact conditional value
replaces a node's returned value. Skipping descendants is not qualified. The
conditional distributions use the policy actually generating visits, not a
different averaged opponent. The target is the population weighted objective;
no finite-sample unbiasedness is asserted for a ratio with a random denominator.

Next build a separate native research exporter for full legal river action
values, including raise continuations. Check its visible keys, histories,
terminal accounting, policy identity and integration with actual traversal.
Then measure real inference/enumeration cost and target variance before
registering self-play and a fresh complete-policy evaluation.

No native source or production process changed. No dataset, final evaluation
cases or GPU were used. Source, plan and evidence remain immutable under
river-conditional-estimator-synthetic-v1-registration.json and -result.json.

The general baseline-plus-correction principle is described in
[Schmid et al., VR-MCCFR](https://arxiv.org/html/1809.03057). This study's exact
conditional replacement and occasional exact-request scheme are separately
tested implementation proposals; published speedups/equilibrium guarantees
are not transferred to this raked research context.
