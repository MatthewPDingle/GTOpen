# Full saved root-action replay: recovery and aggregation control

The replay control passed on two previously qualified batches (64 unique existing deals).
Both batches ran first, but only the first was committed. Recovery excluded and preserved
the complete but uncommitted second batch. A new attempt replayed that same second input,
reproduced its values exactly and completed the same ordered sample. No fresh deals or
model updates occurred.

The checks rejected changed completed output, a changed source route, a reordered
checkpoint prefix, scratch retirement outside the newly owned store, and duplicate
statistics batches. All 169 classes remain in the output, including explicit empty
classes. Conditional counts summed to 64 for each of the eight crossed profiles.

A separate 40-digit decimal calculation checked 9,072 means and standard errors.
Its largest discrepancy was 2.84e-14. A simple known-variance control also passed.
The control ran in 10.25 seconds and retained about 2.31 MB, including the preserved
uncommitted and deliberately corrupted fixture evidence. The corrupted fixture is
excluded from the registered sample and does not touch the original archives.

This qualifies the replay plumbing and descriptive statistics. It is not evidence
of improved poker strategy. The full 65,536-deal replay remains exploratory and must
pass its own independent readback before completion is published.

Source: board-root-action-replay-control-v1-registration.json and
board-root-action-replay-control-v1-result.json. Frozen helper/source hashes are
bound by the registration. Full driver default readiness mode passed; actual launch
requires fresh workload, ownership and global storage admission.
