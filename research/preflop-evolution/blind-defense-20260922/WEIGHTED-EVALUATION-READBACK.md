# Independent comparison readback

The CPU review implementation passed a control using two previously completed
batches: 64 deals and 29,062 observations. Serial and four-worker execution
returned exactly the same values, observation counts and summary identities.
Explicit scalar calculations of the eight paired confidence intervals differed
from the original results by at most 1.42e-14.

The control also rejected a changed batch identity, a duplicate batch and a
modified statistical mean. It consumed no new evaluation deals and used no GPU.
Only two tasks were available, so its 5.81-second serial and 5.00-second parallel
times are not evidence of full-study scaling.

Each worker checks the archived chance input, action legality, assigned player
policies, shared root probabilities, cashflow conservation, summary identities
and eight payoff differences. The coordinator receives batches in their original
order and recalculates means, variances and simultaneous intervals using scalar
sums. It shares the existing native outputs and sampler; this is not a second
independent poker engine.

The full weighted-bank control reviewer is prepared but has not run against
completed stratified banks. It requires the complete control result, both full
training audits and matching model histories before producing a review. Its
admission check correctly rejected currently missing control evidence without
creating a result. No claim about better play follows from this qualification.

Next: finish both training arms and their audits; run the full 78-policy GPU/CPU
control and this review; qualify recoverable batch checkpoints before launching
the fixed 65,536-deal comparison.
