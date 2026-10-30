# Optional wider CPU pool for the next training run

Prepared 2026-09-28. The running four-worker pilot is unchanged.

The first completed candidate qualification update took 366.141 seconds:
307.281 in the physical-target pipeline, 36.328 fitting, and 11.406 publishing.
Its worker river-target category totals 1,035.264 seconds across overlapping
workers; that sum is not wall time. The matched baseline updates took 60.625
and 61.907 seconds, with physical-target pipelines around 19-20 seconds. The
candidate measurement is qualification work, not a production speed benchmark.

Eight physical workers could execute the eight subbatches in one wave instead
of two. Fitting, initial inference and publication remain serial/GPU stages.
Even perfect scaling of the physical-target stage would improve the observed
candidate round by only about 1.7x. Measure actual performance before claiming
a speedup. More detailed profiling may be needed afterward.

## Prepared implementation

- eight_worker_training_pools_v1.py changes only process dispatch, allowing 1-8
  workers while retaining the original worker initialization and work functions.
- board_training_pipeline_eight_v1.py and river_training_pipeline_eight_v1.py
  replace only the imported pool factory. Their non-import ASTs match the
  original pipelines exactly. Ordered insertion, stochastic streams, fitting,
  joint checkpoint publication and target definitions are unchanged.
- Board workers remain capped at four. Use the wider physical pool only when
  spare CPU and RAM exist; it is not authorization to crowd out other work.

## Qualification still needed

eight_worker_training_control_v2.py --run compares 32 spawned tasks against
previously qualified fixtures: two source models, baseline/candidate methods,
four one-deal fixtures each, repeated twice. It compares every target/native/
integration artifact byte-for-byte, checks original counts, and reports actual
worker identities. It generates no new poker data and uses no GPU.

This check may run during the main pilot's excluded qualification phase or
after its verified successful process termination. It refuses to overlap the
pilot's measured training or evaluation. It requires CPU below 40% and at least
40 GB free RAM on admission, retains all evidence, and has a 90-second budget.
Run without --run for read-only phase readiness.

The initial v1 launch was rejected before registration/work by its resource
admission assertion. A follow-up read-only probe confirmed production idle,
58.8% CPU utilization and 86.2 GB free RAM. No experiment or test data was
created by that attempt. V1 remains intact; v2 adds a clean path to run after
the pilot finishes. Neither version has yet passed an eight-worker runtime
check. Do not use the wider pipelines for a scientific training run until it
passes. The source-level equivalence check alone is insufficient.

After parity passes, register a bounded full-update timing comparison or use
the wider dispatch symmetrically in the longer matched continuation with clear
timing limitations. Keep the existing four-worker pilot results separate.
