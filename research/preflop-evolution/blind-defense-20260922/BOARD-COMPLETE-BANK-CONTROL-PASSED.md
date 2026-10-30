# Complete model-bank control passed; fixed evaluation launched

The actual four complete model banks passed the CPU/GPU agreement control and
its CPU readback on 2026-09-28. Each bank averages all 78 played models, in
generation order 0 through 77, with weights 1 through 78 and each player's
own-action reach.
The final unplayed generation 78 is excluded. Both historical stratified banks
and both board-root candidates were included.

The control reused 64 old deals in two batches. It did not draw any of the fresh
test sample. All four banks were checked on both batches: 29,062 query
observations, eight bank/batch checks, plus four 265-observation root-catalog
checks. The root-catalog CPU/GPU differences were zero. Across the complete
batch checks, the largest policy difference was 2.544e-12 and the largest
own-reach difference was 1.501e-11, both below the fixed 1e-10 threshold.

The independent archive readback checked the model identities, old chance
sample, actor routing, native cashflows and scalar statistics. Its maximum
statistical discrepancy was 8.527e-14. It shares the poker engine and policy
implementations; this establishes numerical and transport consistency, not
playing strength or independent poker-engine correctness.

The control took 506.390 seconds; its resource wrapper took 508.766 seconds.
These are overlapping durations, not additive. The separate readback took
5.797 seconds. The two archives and their manifests occupy 1,565,078 logical bytes.

## Evidence

- Control registration: `board-complete-evaluation-control-v1-registration.json`
  SHA-256: `2b51e94f0f57144e37a88a457f51cdc87b01858184c3ea78a0e906e90c11e2f3`
- Control result: `board-complete-evaluation-control-v1-result.json`
  SHA-256: `60c94eee3914b805aca2d1239e592c9c0ead9f021fc9fae957d10ca3e5091ac6`
- Readback registration: `board-complete-evaluation-control-v1-readback-registration.json`
  SHA-256: `1aac8bb7253f3cb5c5d490be714a7d4ede11fef3aa3f23f68da3efb741849c73`
- Readback result: `board-complete-evaluation-control-v1-independent-review.json`
  SHA-256: `505e35ebb9fedf087f769d8bf01a217500e11b37e664a5cb2cec17ffe214d8e8`
- Resource wrapper registration/result:
  `board-control-resource-wrapper-v1-initial-registration.json` and
  `board-control-resource-wrapper-v1-initial-result.json`.

A separate metadata check verified the hash links, all eight bank/batch pairs,
four complete model histories, excluded generation and reported error bounds.
The control registration binds 1,218 inputs; its readback binds 1,222.

## Fixed evaluation now running

The existing queue started the evaluation wrapper as PID 69396, creation time
1790544462.3017652, at 06:57:42 Adelaide. This is a launch snapshot, not a current
liveness claim; inspect the queue and process identity before recovery.

The immutable `weighted-complete-board-root-study-v1-registration.json` has
SHA-256 `127088852b6bd3bd4c900b076872b449385c5c693803eb3e276f239b513a4497`.
It retains exactly 65,536 fresh deals with seed 9281101, 32 deals per batch,
checkpoints every 32 batches, four archive workers and one fixed final look.
Both matched seeds and all eight payoff contrasts remain included. No partial
payoff or range-comparison result was inspected for this note.

The fresh storage admission measured 714,235,393,101 allocated bytes across all
three research roots and reserved another 5,131,299,840 bytes, remaining below
the 800 GB ceiling. The evaluation output bound is 2,131,299,840 bytes; the
invocation limit is 43,200 seconds. An interruption requires explicit recovery
from the committed chance prefix, not a new test sample.

The evaluation still requires all-batch readback, the all-outcomes report,
visual review and scientific interpretation. No model promotion, production
deployment or general preflop accuracy claim follows from this control.
