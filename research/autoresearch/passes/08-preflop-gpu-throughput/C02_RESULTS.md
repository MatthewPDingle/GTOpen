# C02: active terminal queue rejected

The first large paired benchmark took **16.6% more complete time** than retained
C01. It failed the preregistered requirement of at least 1% improvement before
extending to further pairs. The run stopped as designed; no small-fixture timing
or full regression suite was run for this rejected prototype.

Numerical checks passed: all six paired checkpoint gaps and EVs match exactly,
as does the final full-arena fingerprint. Three adversarial tests compared the
original solver, C01 and C02, including graph replay, partial batches, fixed
policies/locks, zero-reach recovery and two-to-eight opponents.

The experiment tested a 4096-block persistent queue with GPU atomic compaction,
keeping the first full terminal batch. This combination lost performance. The
benchmark does not isolate whether compaction, locality, occupancy or loop
barriers caused the regression. Do not claim all active-work scheduling is bad.

The candidate was removed from the solver. Its exact tested source is retained
under `artifacts/c02-rejected/`, with raw timing/source/executable records in
`raw/c02-*`. A local executable archive lives at
`target/c02-benchmark-frozen.exe`; its SHA is in `raw/c02-verified.json`.
The independent post-run audit checked every input and solver-source hash,
all paired outputs and the rejection threshold before restoring retained C01.

Production port 56708 remains unchanged. C01 remains the retained GPU throughput
improvement. The progress graph includes C02 as a rejected point above baseline.
