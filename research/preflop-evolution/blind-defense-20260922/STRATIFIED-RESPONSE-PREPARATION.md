# Give every hand enough response-training examples

The completed response-stability diagnosis found only 13–95 examples per hand
class (median 37) in the original 8,192-deal response-training set. Increasing
random samples spends much of the extra work on already common offsuit hands.

A separate response-training sampler can now request a fixed number of deals
for each supported hand class. It conditions the original entry distribution
on that class, preserving compatible opponent-card probabilities and drawing
the public board without replacement. It uses actual physical cards, the same
entry cutoff, and the original context identity. It does not copy a generic
opponent range over blocked cards or add outcome information to policy inputs.

This is for fitting the evaluator's counter-strategy, not for retraining the
self-play model. Each class chooses its action from its own examples, so more
even coverage does not require weighting those choices by overall class
frequency. A later aggregate strength test must still use the original separate
population sampler (or an explicitly validated weighted estimator). Taking an
unweighted mean over the new training stream would misstate population EV.

There is an additional two-player constraint: **do not reuse these BB-balanced
deals unweighted to learn BTN's response**. Conditioning on BTN's hand does not
undo the changed BB hand mix. BTN needs a separate population training stream,
its own correctly conditioned sampler, or explicit validated prior weights.
The current component only supplies BB-root response training. Preserving this
distinction is part of admission for the next two-player evaluation.

## Completed control

`stratified-response-control-v1-result.json` records a CPU-only check:

- Exactly 16 examples for each of all 169 classes: 2,704 deals.
- All private/public cards are distinct and all class labels agree with the
  independent existing hand-class conversion.
- Repeating the seed reproduces the complete stream; a different seed changes it.
- Independent enumeration of all compatible private-pair products agrees with
  the original marginal to 1.2e-18, and class-conditional probabilities to 8.4e-17.
- Eight malformed or unsupported requests fail, including a requested class
  with no incoming support.

The controller took about 1.6 seconds. This measures sampling/control overhead,
not the much more expensive policy inference or payoff evaluation.

## Conditional-payoff integration

The separate `stratified-conditional-integration-v1` control also passed. It
used the completed four-update visible control model, all four played policies,
and two physical deals per class (338 total). It constructed the needed exact
private-pair all-in labels, queried the model without those labels, evaluated
all four root choices, and exercised response selection/application with
distinct fixture IDs. These very small counts are transport fixtures only.

All 22 model calls used unlabelled observations. Root mixtures matched their
component action values to 7.2e-15 bb, and independent forward cashflows agreed
to 2.9e-13 bb. The CPU-only control completed in 65.4 seconds, without inspecting
or changing the active full trial. This does not establish CUDA equivalence for
the future final candidate or statistical quality of the fitted response.

## Admission still required

For illustration, 256 examples per class would require 43,264 response-training
deals and remove the uneven class-count problem. This is a planning choice,
not a frozen next-study budget or proof of sufficient precision. No fresh
strategic stream has been generated and no GPU evaluation has been launched.

Before use, fix the candidate, count, seeds and resource budget; check the actual
conditional-payoff integration; freeze the selected response before drawing the
held-out population stream; retain both-player tests and report all intervals.
Do not multiply sample counts after inspecting test results. More balanced
coverage cannot remove all value noise or turn a restricted response into a
full best response. The active visible-feature trial stays unchanged.
