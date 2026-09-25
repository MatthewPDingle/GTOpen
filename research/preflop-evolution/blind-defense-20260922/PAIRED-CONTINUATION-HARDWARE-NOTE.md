# Hardware use during the paired diagnostic

25 September 2026. After bulk-feature averaging passed exact-equivalence
controls, a 25.11-second sample was taken during the live paired study.
Twelve observations, about two seconds apart, measured:

- Main worker CPU use: mean 0.926 logical-core equivalents.
- Whole-device GPU utilization: mean 6.08% in the periodic snapshots.
- Highest observed whole-device GPU allocation: 2,257 MiB.

These are process CPU deltas and whole-device GPU snapshots, not a continuous
whole-run trace. CPU work in short-lived native children is excluded from the
worker figure. The available 16 physical / 32 logical CPU cores and 24 GB GPU
still have substantial headroom. The first completed batch took 0.828 / 0.484
seconds for the two complete bank averages and 0.266 seconds for native payoff
evaluation. After initial loading, the first three logged blocks of 512 deals
took about 46–47 seconds each. Export, JSON transport, validation and durable
archiving remain additional serial work; this sample does not individually
attribute their costs.

The first archived batch also passed a separate transport check: all eight
profiles use the intended player's continuation at every non-root query, and
restoring the recorded unforced root probabilities reproduces both original
whole-policy hashes. This is an early implementation check, not an early look
at the scientific effect estimates. The complete scalar reader remains required.

## Next performance comparison, after the current run

The next useful performance test is bounded concurrent evaluation of independent
saved batches, under one owning research job. Compare identical jobs run
serially and with 2 and 4 workers, holding the bank, query batch shapes, precision,
model chunk size, arithmetic order and source data fixed. Verify complete
probability/support hashes against the serial reference; report total wall
time, startup separately, CPU use and peak host/GPU memory. Maintain production
activity guards, one admitted job, a combined memory/output cap, and terminate
only owned workers if a guard fails. Do not run independent uncoordinated GPU
jobs or change the live scientific sample to obtain a speedup.

Parallel scheduling is a candidate, not a proven speedup. Avoid predicting a
linear gain from spare cores or VRAM. A separate larger-model-chunk control
could test GPU batching, but exact output checks remain necessary. Use the
faster path only after equivalence and resource checks; the immediate priority
is finishing and interpreting the registered continuation comparison.

Evidence: `paired-continuation-v1-hardware-sample.json` preserves the individual
samples, worker identity and measurement limitations. Scientific progress and
completion are recorded separately by the study controller.
