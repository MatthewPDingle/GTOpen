# Independent evaluation for sampled poker models

The interval implementation and its finite-game controls passed. This prepares
evaluation of a future physical-poker policy; it does not qualify a new range,
establish physical-poker convergence, or change the experimental viewer.

## What must be frozen before evaluation

Freeze the candidate policy bank, opponent policy, each unilateral responder,
context, chance distribution, sample budget, reported series and inspection
counts before drawing evaluation deals. Train responders on separate data.
Selecting or improving a responder using the evaluation draws invalidates this
contract. Reserve a fresh board panel: the original 190-board evaluation and
earlier inspected panels are diagnostic evidence, not fresh confirmation.

Draw complete deals independently from the qualified joint distribution of
board and compatible private hands. Pair the baseline and alternative on the
same deal, optionally with shared independent action randomness. One complete
paired deal value is one observation. Actions, traversals or model members
within that deal are correlated and must not be counted as additional samples.
Batch merging requires disjoint independent deal batches; the accumulator cannot
detect duplicated draws or a caller that reuses the same batch twice.

Policies may see only the player's observable history. They may not select a
preflop action separately for each hidden flop, opponent hand or future runout.
Exact conditional action integration is allowed as variance reduction, provided
the policy remains fixed and information-correct throughout that integration.

The interval concerns the mean under its registered distribution. IID draws
from a finite board panel give uncertainty conditional on that panel; they do
not quantify generalization to all flops or uncertainty in upstream ranges.
The previous common private-hand prior standardizes frequency comparisons;
it does not replace each panel's board-conditioned EV prior. Different panel
populations must not be silently pooled into one equally weighted estimate.

## What the result means

A positive lower bound for a unilateral alternative demonstrates a profitable
tested deviation. Its gain is a lower bound on the best response's gain. A small
gain, even with a narrow interval, does not establish a small best-response gap:
the responder may have missed better play. Do not label this result convergence
or exploitability certification. Finite-game tests retain their exact independent
best-response evaluator and their existing stopping rules.

## Bounded uncertainty

The two-sided interval scales Theorem 4 of
[Maurer and Pontil (2009)](https://www.cs.mcgill.ca/~colt2009/papers/012.pdf).
For paired values bounded in `[L,U]`, unbiased sample variance `s2`, `n` deals,
`K` registered series, `J` registered inspection counts and family error `alpha`:

```
log_term = log(4*K*J/alpha)
radius = sqrt(2*s2*log_term/n) + 7*(U-L)*log_term/(3*(n-1))
```

Clip the interval to the known bounds. The factor four accounts for the theorem's
constant and two-sided union bound; another union bound covers series and looks.
This permits stopping at registered looks without silently adding repeated 95%
tests. It does not permit unlimited peeking or post-hoc extra series. Even zero
observed variance retains a positive uncertainty term for unseen rare outcomes.

Enumerating all 602 public terminal templates and all winner assignments in
the registered BB game gives utilities in `[-200,198.5]` for each player.
Thus paired differences are conservatively in `[-398.5,398.5]`. This also lies
inside the independent cash-flow envelope `[-200,200.5]` from two 200-bb stacks
and the folded 0.5-bb SB. These bounds are context-specific, include the frozen
rake and offsets, and must be regenerated for changed stacks or accounting.

The resulting bounds can be conservative for deep-stack poker. A small sample
must not earn an accuracy claim by substituting its observed extrema for known
possible payoffs. Conditional action integration and a well-defined control
variate are possible later variance reductions; neither is implemented here.

## Executed controls

`sampled-evaluation-v1-registration.json` froze 11 input hashes, two payoff
settings, two players, two inspection counts and independent policy/test seeds.
The policies are synthetic fixed observable policies, not learned poker ranges.

- Four series each use 32,768 IID finite-game deals; inspect at 8,192 and 32,768.
- Forward terminal enumeration agrees with the independent reverse evaluator's
  exact profile differences within 1.95e-16. Only one player's policy changes.
- Streaming variance, direct variance and the interval formula agree within
  2.42e-15; merging disjoint batches agrees within 2.17e-15.
- The pairwise sample-variance identity is independently checked.
- Eleven invalid inputs are rejected, including nonfinite/out-of-bound values,
  unregistered series/looks, exhausted budgets and self-merging.
- Constant observations still have nonzero uncertainty. The eight observed
  interval outcomes are reported, not treated as proof of nominal coverage.

The CPU control completed in 0.33 seconds. No GPU training, live server or
production strategy was changed. Frozen evidence prefix: `sampled-evaluation-v1`.
