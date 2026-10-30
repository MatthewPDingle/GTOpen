# Possible next estimator improvement: exact initial all-in expectations

Design only, 23 September 2026. No training change or new trial is launched.
The current averaging study and broader call/raise evaluation retain priority.

## Opportunity supported by the implementation audit

The existing external-sampling walker enumerates the updating player's choices
but samples opponents' actions. Current all-in labels integrate the future board
for the particular dealt private cards. They still sample the opponent's cards
and, on BB's root shove branch, BTN's fold/call action.

The separately checked all-in matrix can calculate these initial all-in
expectations from the current iteration's complete 169 BB / 96 BTN class
policies. These must be the current frozen played policies, not final averages.
The matrix is cheap enough to consider recalculating once per iteration.

## BB first decision

For each actually sampled BB class, keep sampled call/ordinary-raise returns.
Replace only its sampled shove return with the exact conditional shove value
for that class against the current BTN policy. Fold is already deterministic.

If the shove return changes by d and BB currently shoves with probability p,
the root's expected value changes by p*d. Add d to the shove action return and
subtract p*d from **every legal action's regret target**. Changing only the
shove regret would be wrong: the baseline must change consistently. BB has no
earlier own decision above this node in the studied conditional game.

This preserves expected counterfactual targets at that root under the existing
compatible private-card distribution. It does not guarantee lower variance of
every regret coordinate, because sampled returns can be correlated.

## BTN response to the root shove

When the external-sampling traversal actually reaches this BTN node, obtain its
call payoff conditional on BTN's class **and BB choosing the shove**. Weight BB
classes by their compatible joint-card probability times current shove
probability, then normalize by that class's shove reach. Use this conditional
call value and the deterministic fold value to form both centred regret targets.

Do not divide by unconditional BTN entry mass, and do not multiply the resulting
conditional regret by shove reach again: the traversal's node visitation already
samples that reach. Zero-reach classes should never produce a visited training
record; any such occurrence must fail loudly instead of using a fabricated value.
This is BTN's first own decision on the studied branch. Its downstream fold/call
outcomes are terminal, so no later own regret record requires adjustment.

## Required checks before any candidate run

Use a distinct estimator/transport identity rather than relabeling old records.
Keep original controls and artifacts intact. Independently verify expected
regret targets by summing all compatible private pairs and opponent-action
outcomes under several fixed policies, including mixed play, zero shove reach,
and blocker-sensitive classes. Check that each modified target has zero own-
policy-weighted mean and that its expectation matches the original estimator.

Preserve unaffected records and action sampling, especially all ordinary
call/raise and postflop paths. The old per-private-deal cashflow replay cannot
be used as if the changed estimator returned the same value on each deal; the
new control must verify expectation equivalence at the stated information sets.
Then measure variance for **all** affected regret coordinates, not only shove.

Only after those checks, and analysis of the active study, would a separate
fresh training protocol be justified. This does not remove sparse own-class
coverage, neural postflop error, the restricted action tree, or the need to
validate different positions and stack sizes. It must not become a substitute
for fixing and measuring the broader calling-range problem.
