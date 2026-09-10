# Opt-in eager CUDA phase profile

Proposal only; no compilation or GPU execution performed by the proposal agent.
Base commit/source hash is in `base.txt`. Apply `combined.patch`, or
`instrumentation.patch` followed by `tests.patch`. The source checkout and
frozen benchmark harness are unchanged by this proposal.

Every instrumentation field, helper and call site is `#[cfg(test)]`. Release
application and example binaries have no event allocation, recording, branch,
or profiling field. Normal unit tests leave the optional trace empty.

## What it measures

The actual `iterate` and `gaps_and_evs` call paths are measured with preallocated
CUDA events on the engine stream. No solver logic or kernel launches are copied
into the profiler. One trace contains either one full alternating iteration or
one average-strategy / best-response check. Phase totals include:

- `down`: root initialization, all downward levels, reach masses and HU cache.
- `ordinary_terminals`: ordinary terminal kernel.
- `prepare`: active-mask clearing (learning only) and counterfactual probability.
- `normalize`: one normalization launch per needed traverser, if enabled.
- `cdf` and `coupled_terminals`: separately accumulated across every sample batch.
- `up_learn`, `up_br`, `up_average`: all upward levels for that operation.
- `discount` (iteration) or `root_copy` (average check).

Each row has seat, milliseconds and interval count. `gpu_ms` is the first to
last device event; `wall_ms` includes queueing plus final synchronization and,
for average checks, root download and host reductions. Event creation, result
aggregation and final arena download/hash are outside `wall_ms`.

This is **eager diagnostic timing**, explicitly labeled `eager_cuda_events`.
Graphs bypass host hook calls, so beginning a trace synchronizes, drops existing
graph handles and resets only graph warm flags. Kernel/data buffers and solver
state are retained. Warm-up still uses the normal production call paths.
Each trace then launches exactly the normal eager operation sequence.

Event insertion adds overhead and intervals can include stream idle time caused
by host launch latency. Do not claim these timings are production graph runtime
or add these event timings to the frozen performance leaderboard. Use dominant
phase shares to choose hypotheses, then judge them with the untouched canonical
graph benchmark. Do not infer graph-bound speedups by summing eager reductions.

## Focused regression first

Run on an otherwise idle GPU:

```powershell
cargo test --release -p solver --features gpu --lib coupled_phase_event_hooks_preserve_solver_bits -- --test-threads=1 --nocapture
```

The 4-seat coupled fixture compares two complete iterations and checks with
and without events. The uninstrumented second check uses a graph. It compares
all regret/strategy/gap/EV bits and verifies phase/count coverage: one downward
pass for an average check, every traverser for learning, every particle batch,
BR and average upward passes, copies, and discount. Event intervals must be
finite/nonnegative and sum to total within timestamp precision.

## Supplementary eight-seat profile

From the isolated research checkout:

```powershell
$env:PREFLOP_PHASE_INPUT = 'T:/Dev/GTOpen/saves/preflop/Before preflop autoresearch 20260910 2104.gtop'
$env:PREFLOP_PHASE_EQ = 'T:/Dev/GTOpen/target/autoresearch/preflop-20260910/cache/preflop_eq169.bin'
$env:PREFLOP_PHASE_BUDGET_MB = '23000'
$env:PREFLOP_PHASE_WARMUP = '2'
$env:PREFLOP_PHASE_REPEATS = '3'
cargo test --release -p solver --features gpu --lib profile_coupled_gpu_phases_from_frozen_input -- --ignored --test-threads=1 --nocapture
```

The ignored test accepts the same config JSON / `.gtop` input forms as the
frozen harness, reads an existing equity-cache sample header, and asserts the
loaded model is coupled. It never changes/saves the input or contacts the app.
`PREFLOP_PHASE` JSON records describe metadata, each operation, gaps/EVs and the
final arena hash. Compare output fingerprints to a canonical run only at the
same input state and total iteration count (`warmup + repeats`). Intermediate
checks are read-only. Prefer medians of each phase across repeated samples.

Two warm-up iterations plus three measured iterations means five total
iterations. To match the frozen six-iteration eight-player fingerprint, set
`PREFLOP_PHASE_WARMUP=3` and leave `PREFLOP_PHASE_REPEATS=3`.

## Next decisions after measurement

If CDF dominates, inspect particle-CDF memory traffic before changing the
terminal arithmetic. If coupled terminals dominate, inspect its class/sample
loop and occupancy. If average-check CDF dominates much more than learning,
measure evaluation reuse separately: average reaches are shared across seats,
but learning reaches change between alternating sweeps and cannot be reused
without invalidation. No model, sample count, precision or action abstraction
change is implied by profiling.
