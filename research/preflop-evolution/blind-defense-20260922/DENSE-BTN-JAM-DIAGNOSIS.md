# BTN's shove response also needs work

This is a post-hoc diagnosis using the larger-data candidate's already inspected
evaluation streams. It is not another independent confirmation, does not change
the ongoing hybrid experiment, and supplies no hand edits for the live model.

## What was checked

Keep the complete dense average strategy fixed except BTN's fold/call decision
when BB jams to 200 bb over BTN's 2 bb open. The root BB jam probability supplies
the probability of reaching that decision for each compatible private-card pair.
Other branches remain unchanged.

Enumerating all 21 five-card subsets of each seven-card holding independently
reconstructed the showdown winner for all 24,576 saved deals. The resulting
conditional BTN payoff reproduced the native evaluator's forced-BB-jam profile
within 2.85e-14 bb. The called pot is 400.5 bb with 2 bb rake: BTN receives
198.5 bb when winning, -200 bb when losing, or -0.75 bb when tying, including
its investment. Folding loses the existing 2 bb investment.

A hand-class responder was chosen on the existing 8,192-deal response-training
stream, weighting outcomes by BB's jam probability. Under 16 raw observations
retains the candidate's original action mix. That response was saved before
reading the separate 16,384 test deals. The diagnosis is still post-hoc because
these test streams had already been used for another analysis.

## Result and limitations

| Measurement on the saved test deals | Result |
|---|---:|
| Probability of reaching BB's jam branch | 7.278% |
| BTN call frequency, weighted by reaching that branch | 41.327% |
| Gain from the separately selected class response, per original spot entry | +0.289 bb |
| Same gain, divided by the frequency of reaching the jam branch | +3.966 bb |
| Gain from always folding at this BTN decision, per spot entry | +0.167 bb |
| Gain from always calling there, per spot entry | -1.996 bb |

These are sample estimates, not a new equilibrium, a full best response or a
fresh confidence claim. In particular, 41.3% conditional calling alone does not
establish that BTN is too loose: the correct response depends on BB's actual
shoving range. The gain can involve changing different hands in opposite
directions. It must not be added to the earlier BB root result as a certified
full-game exploitability number.

The hand-level estimates are unstable. Among 82 test-observed classes with at
least 16 training observations, 19 change the sign of call-minus-fold between
training and testing. This includes JJ, KQs and AQs. The median effective test
sample after weighting by BB's jam probability is only about 30.2 deals per
eligible class. Raw sample counts overstate the precision of this conditional
decision. No single listed hand should be patched from these estimates.

## Consequence for the research

The smaller BB first-decision gain is insufficient on its own. A second player's
response has an improvement opportunity in this diagnostic. Tests need to cover
both players and later decisions before claiming broadly better ranges.

The running hybrid trial removes neural regression error at observed preflop
states, but preserves noisy sampled targets. A separate next question is whether
averaging more future boards for preflop all-in terminal values would reduce an
important source of that noise at reasonable cost. First validate that calculation
against exact conditional equities on a bounded fixture; do not change the
registered running experiment. Other uncertainty, including opponent private-card
sampling and changing training strategies, would remain.

The independent readback verified 6,144 source artifacts, reconstructed the
training response, all 16,384 paired differences, and all 87 test-observed BTN
classes. It did not rerun the hand evaluator. The original diagnostic performed
the independent hand enumeration and native-value cross-check on every deal.

Evidence: `sampled-physical-dense-btn-jam-diagnosis-v1-result.json`, its
`independent-review.json`, and the immutable row/response artifacts identified
there. The production model and range preview remain unchanged.
