# Testing whether a policy misses profitable first decisions

The root-deviation evaluator now has a passing implementation control. It can
compare a frozen policy with a response learned on separate training deals,
while leaving every later action unchanged. This is preparation for evaluating
the physical-poker pilot; it does not show that the pilot plays well.

## What is compared

For each complete deal, the native evaluator integrates all later legal actions
under the frozen policies. It returns the value of the original root strategy
and of each of the four root actions. A responder selects one action per own
hand class using training deals only. Classes below the declared training-count
threshold retain the original strategy. Opponent cards and future board cards
cannot select the responder's action.

Evaluation then measures the paired difference between that frozen responder
and the baseline on separate deal IDs. It does not choose the best action after
seeing evaluation outcomes. Negative differences are retained. A successful
deviation would expose a weakness, but failure to find one would not certify
equilibrium: later decisions are frozen and the responder is restricted.

## Completed checks

`sampled-root-deviation-v1-result.json` records:

- All 16 registered input hashes verified.
- Eight complete deals, with the original policy plus four pure root actions.
  The baseline payoff equals its root-probability-weighted action values with
  maximum numerical error **0**. Folding returns exactly **-1 bb**.
- The reused fixture's first four deals train the response; the final four
  evaluate it. Those held-out classes are absent from training, so all four
  differences are **0 through unchanged-baseline fallback**. This is not evidence
  of poker strength or independent generalization.
- A synthetic case chooses action 1 from training, then correctly keeps a
  **-6** evaluation difference when that action performs poorly. A sparse class
  preserves the baseline and gives a difference of **0**.
- Seven invalid inputs rejected: overlapping sample IDs, duplicate IDs, invalid
  class, non-finite payoff, invalid support threshold, changed action count,
  and a responder that overrides the required sparse-class fallback.

The control took 0.313 seconds, used no GPU, and changed no production session.
The small native outputs, registration and responder are retained here. The
generated profile transport remains a local disposable artifact; its hash is in
the result. This control depends on the separately verified fixed-profile
evaluator and its chip-accounting checks.

## Requirements before a real strength evaluation

Sample IDs alone cannot establish independent sampling. A future experiment
must bind the saved policy bank, context, incoming ranges, chance distribution,
action menu, training/evaluation seeds, support threshold, sample budgets and
planned comparisons before inspecting fresh outcomes. Train the responder first,
freeze it, and then evaluate paired payoffs on fresh independent deals. Report
uncertainty across complete deals, including unsupported-class fallback coverage.

The eight-deal fixture above has already been inspected and must not become
that fresh test. This evaluator is a restricted deviation test, not an upper
bound on best-response gain, a new joint equilibrium, or a Wizard comparison.
