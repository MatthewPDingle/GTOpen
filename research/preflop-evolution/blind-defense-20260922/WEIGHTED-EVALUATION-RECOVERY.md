# Recoverable fixed-deal comparison

Use `weighted_complete_evaluation_study_v2.py` for the prospective study. It
requires both completed training arms, both full training audits, the full-bank
GPU/CPU control and its independent review. These gates have not all completed.
The actual evaluation registration and 65,536-deal stream have not been created.

The driver retains the fixed seed 9278101 and the original one-look comparison.
After every 32 batches (1,024 deals), it drains the bounded archive workers and
publishes a checksummed recovery point containing the sampler state, running
statistics and exact archive routes. Each invocation has a separate attempt
directory. A restart with `--resume` restores the longest committed prefix,
checks its archives and replays chance to confirm the registered sampler state.
Partial attempts are preserved but excluded. Previously committed batches are
not evaluated again. Work completed after the last checkpoint may need replay;
that uses the same deals and does not enlarge the statistical sample.

## Verification completed

The checkpoint control used 64 previously evaluated deals with the old seed
9267201. It restored identical sampler and accumulator states at 32 and 64 deals
and reproduced the uninterrupted final statistics exactly. It rejected missing
batches, inconsistent statistic counts, wrong registration/seed/budget, a
corrupted checkpoint and a corrupted durable archive. Incomplete attempt data
and a partially published checkpoint were preserved and excluded.

The first controller integration test found that progress reporting incorrectly
used the immutable evidence writer. It failed after safely committing 32 deals.
That source, failed registration and checkpoint remain preserved. The separately
versioned v2 driver atomically replaces only mutable status files.

The v2 integration test completed two invocations of 32 deals each, using two
distinct archive attempts. It restored the first batch, evaluated only the second
and reproduced all final statistics exactly. Actual archive subprocesses,
checkpoint publication, restoration and controller boundaries executed. GPU
inference and scientific admission were replaced with replay of old outcomes:
this is a workflow test, not evidence that the new models play better or that
full-bank GPU inference has passed. The live training lock was unchanged.

The real v2 admission path separately rejected incomplete training before
creating any prospective study artifacts or acquiring its GPU lock. Runtime
guards account for nested attempt scratch being retired by archive workers;
disappearing durable archives and checkpoints remain errors.

Next steps remain the full-bank control/review and a separate final reader for
the routed study archives, followed by the fixed comparison and its analysis.
