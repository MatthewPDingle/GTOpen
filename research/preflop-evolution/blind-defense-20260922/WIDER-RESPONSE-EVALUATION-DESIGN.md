# Next wider evaluation: preparation, not a registered run

23 September 2026. Do not launch automatically from this design. The active
fresh averaging study must complete its audits and exact screen first. No
active-candidate probabilities have been read for this preparation.

## Question and limits

Can a capable class-only counter-strategy improve the candidate at BB's first
decision when calls and ordinary raises, including their postflop continuations,
are evaluated too? Downstream play stays frozen. This is a lower-bound deviation
test in the fixed 200 bb BB-versus-BTN game, not a full best response or proof of
accuracy at other positions, stacks or incoming ranges.

## Candidate and independent samples

If the averaging screen passes, use its complete 78-generation linear-weighted
bank with the already verified own-action-reach averaging. Recompute all exact
fold/shove values against that same frozen opponent. Do not reuse an old
candidate's opponent-dependent values or select a late checkpoint.

The planning counts are 256 training deals for each of all 169 BB classes
(43,264 total), followed by 131,072 independent population test deals. These
are not yet a resource-admitted or frozen budget. The two seeds, counts, time
cap, source/binary identities and storage limits must be registered before
execution. Distinct sample IDs track provenance; they are not by themselves
proof of independent random streams. A class-balanced training stream is not
an IID population test stream.

The tested class-stratified sampler preserves each class's compatible opponent
distribution and physical shared-board law. Its round-robin ordering permits
two equal 128-per-class training halves for stability diagnosis. Preserve the
original minimum 16-example support threshold; with complete execution every
class exceeds it. Report both-half disagreement without selecting between the
halves or altering the final responder from test outcomes.

## Response and value estimator

The checked `exact_aware_root_response_v1.py` fits call/raise conditional means
from training observations and replaces fold/shove means with exact values.
It retains a class's full baseline policy below the fixed support threshold
and chooses the first legal maximizing action otherwise. Only own hand class
selects an action. Freeze its complete output and hash before instantiating
the population test sampler.

Use the existing explicit conditional-all-in native evaluator with the complete
private-pair cache. Policy inference receives only unlabelled visible queries;
future cards/equity labels belong only to terminal evaluation. Sample ordinary
postflop boards and integrate legal downstream action probabilities as before.

Evaluate the trained deviation and all four fixed-action alternatives. For each,
combine its exact fold/shove contribution with sampled call/raise residuals.
Class centring remains off: the old diagnostic found little additional benefit.
Derive each residual's physical bounds prospectively from the frozen policies,
stack and dead money. Use the existing bounded empirical-Bernstein calculation
with one fixed final look and family error .025 across all five alternatives.
Shift each interval by its exact offset. No adaptive stopping on apparent gain.

Negative fitted gain is not reassurance about the true best response, which can
retain the baseline. Broad intervals are inconclusive. Publish all alternatives,
all class support/stability rows, achieved widths, and the already exact BTN
response test. Do not combine unilateral gains into an achievable joint winrate.

## Implementation admission still required

The exact-aware fitting control passed independent scalar fixtures for every
class, unequal coverage, fallback, exact-value replacement, tie behavior and
invalid/overlapping sample identities. It reproduced all 169 choices from the
old-data diagnosis; maximum scalar mean discrepancy was 4.44e-16. It did not
perform native inference, train a candidate or certify poker strength.

Before a real run, finish the wider controller/readback, exercise a complete
small end-to-end CPU control, compare frozen weighted CPU/CUDA probabilities
and payoffs, and independently reconstruct final residual sums/intervals.
Check that test creation occurs only after responder publication and that
stratified observations never enter population confidence calculations.

Resource admission must account for training, test, numeric controls, compressed
disk usage and verification. Previous 24,576-deal visible-model evaluation took
about 3,300 seconds, but the new conditional evaluator and storage compression
change the cost; do not promise a completion time from simple scaling. Current
free space is about 90 GB after lossless compression of completed evidence.
Measure the new end-to-end control before choosing the final bounded budget.

If the active averaging screen fails, preserve its full result and assess the
cause. Do not silently switch this design to another candidate or bypass that
decision. A tractable independent reference remains the fallback if wider
testing cannot establish useful progress within a reasonable budget.
