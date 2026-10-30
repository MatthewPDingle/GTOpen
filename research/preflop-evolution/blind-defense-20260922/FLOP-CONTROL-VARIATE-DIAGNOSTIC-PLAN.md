# Exact-mean flop-feature variance diagnostic

Status: proposed exploratory follow-up, separate from the fixed-root precision pass and the completed confirmatory study. No training or production change is authorized by a positive diagnostic alone.

## Why this is worth checking

The training code still samples private cards and boards after integrating actions. It updates BB's 169 class regret tables from only 512 population deals per generation. Increasing class coverage can help, but it does not eliminate the randomness of good and bad boards within a class. An older continuation-label investigation used rank-event control variates; those different policies and approximate labels do not establish effectiveness for the present learner.

The present archived population consists of compatible physical private pairs followed by a uniform five-card runout. Conditional on the four private cards, the first three board cards form a uniform subset of the 48 remaining cards. Simple flop-event probabilities are therefore available exactly from rank counts, without equity estimation or solver inference.

## Fixed proposal

Use eight binary flop events relative to BB's ranks: at least one high rank, at least two high ranks, at least one low rank, at least two low ranks, at least one overcard, at least two overcards, any paired board rank, and three identical board ranks. Low-rank indicators are identically zero for a pocket pair. Overcards are ranks higher than BB's highest card. Center each indicator by its exact conditional expectation given both private hands.

For each bank, BB hand class and action contrast (call-fold, raise-fold, raise-call), fit a linear control coefficient using the opposite global-index parity half only. Use centered least squares with an intercept for coefficient fitting and a fixed ridge penalty of 1 on the sum-of-squares normal matrix. Apply only the feature correction, not the fitted intercept, to the held-out action contrast. If fewer than 20 fitting observations exist, use zero coefficients and disclose that coverage. No penalty search, feature selection or best-bank selection.

For an independently fitted coefficient, the feature correction has conditional expectation zero. It can reduce variation without changing the target's expectation. The coefficient may condition on the actor's class; using the simulated opponent cards to calculate the conditional expectation is target construction, not a new policy input or access to private cards during play.

Reusing these inspected archives makes the entire comparison exploratory. Report raw and corrected class means, variances, descriptive variance ratios, coefficient norms and exact coverage for all four banks. Cross-fitting introduces dependencies between the two corrected halves: do not turn a naive pooled standard error into a confidence guarantee. Do not interpret finite-sample mean shifts as improved player value. Jam remains outside this diagnostic.

## Gates before any full diagnostic or learner change

1. Validate the eight event expectations by exhaustive enumeration of all 17,296 flops for several explicitly fixed private-card fixtures, including pocket pairs and rank overlap. Verify card uniqueness and class-independent formulas.
2. Verify that zero coefficients preserve targets, constant shifts in training payoffs do not affect the coefficient, and changing held-out payoffs cannot affect the coefficient used for those payoffs.
3. Complete and independently audit the current frozen-root pass first. Decide whether its remaining noise warrants this diagnostic; no partial-result selection.
4. Authenticate source cards and fixed action values, register exact source hashes, bound storage/runtime and preserve the original population law. No new deals or inference are needed for an archived comparison.
5. If diagnostic variance improves consistently, test integration with fresh training seeds and a separate fixed-budget evaluation. Recheck gradient/regret target identities, actor conditioning and resource use. Do not promote a range based on lower variance alone.

Root class stratification is a separate candidate. Its existing actor-specific sampler must not be fed unweighted into both players' reservoirs: conditioning BB's cards changes BTN's opponent distribution. A root-only stratified supplement or correct importance weighting would need a separate protocol and cost comparison.
