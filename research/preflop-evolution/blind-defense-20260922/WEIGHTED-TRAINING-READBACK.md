# Independent weighted-training readback

The first two stratified generations passed a separate scalar reconstruction of
1,024 BB root decisions, 23,962 postflop targets and all 26,064 inserted learning
visits. The checker rebuilds physical samples, source-deal weights, action seeds,
weighted root sums, exact initial BTN regrets, reservoir contents and RNG state.
It also checks the played model chain and saved recovery checkpoints.

Targets are recalculated from native cashflows and conditional action values.
The checker does not call the training update, target ingester, matrix evaluator
or regret-accumulator update. It does share the sampler, reservoir implementation,
model feature definitions and native poker outputs; it is not an independent
poker engine, a refit of the parameters, or evidence of playing strength.

Independent CPU workers now verify separate frozen-policy batches, with results
inserted into the reconstructed state in original order. Only one generation's
eight tasks may be outstanding. Root contributions are returned per deal rather
than reordered by a parallel reduction. Workers finish before the next generation.

The four-worker registered control passed with maximum policy error 5.06e-13,
target error 5.68e-14 and accumulated root-state error 2.27e-13. Actual counts,
weight arrays, sampling/action RNG state and reservoir selection agree with the
saved trainer. Full-arm verification is still required; passing two generations
does not certify the remaining 76.

## Queued full verification

weighted_study_audit_queue_20260927.py is tied to the live trainer's PID,
creation time and command. It waits for the fixed 78-generation endpoint and
then checks production activity, CPU use and free RAM before starting four
hidden CPU workers. It can audit the first completed arm while training the
second. It does not restart a missing trainer or change the sample budget.

The final policy-bank loader requires both completed training and the matching
78-generation audit. It verifies the checkpoint and full played history, includes
generations 0 through 77, and excludes unplayed generation 78. Its early admission
checks reject incomplete training, changed registration, unknown arms and a
changed storage location. Full-bank numerical qualification and the registered
crossed-policy evaluation remain separate gates.

The immutable registrations and results are named
weighted-training-readback-parallel-v1-w4-9266201-stratified-0002 and
weighted-study-audit-queue-v1. Mutable process logs are observations, not proof
that a process is live or that a full audit has passed.

The same registered checker took 120.906 seconds with one worker and 44.359
seconds with four workers (2.73x faster), with identical counts, checkpoint
identity and reported numerical errors. Both ran while training continued, so
this is an observed throughput comparison, not an isolated hardware benchmark.
See weighted-readback-worker-comparison-v1.json for the bound result identities.
