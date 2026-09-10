# Interpreting the modeled GPU memory result

The parent measured original corrected planning at22.894GB, batch30, versus
optimized15.358GB, batch32. Original iteration/check times were28.086s/28.175s;
optimized3.519s/4.414s. EV/gap differences were about3e-8. These show an
approximately8x end-to-end iteration gain on this modeled workload; they do not
isolate an8x kernel-throughput gain.

Original device-wide usage was23,716/24,576MiB in one nvidia snapshot, leaving
860MiB at that instant. The planner uses decimal MB (`bytes/1e6`), while nvidia
reports MiB: do not subtract the numeric values without conversion. Allocation
planning excludes some driver/other-process effects. A high-usage snapshot is
consistent with memory pressure but is not proof of WDDM eviction or paging.
GPU100% and high clocks do not prove the kernel is free from memory stalls.

Batch30 requires35 passes over1024 particles; batch32 requires32 passes. That is
9.375% more batches before other effects, and cannot by itself explain an8x
difference. Active-slot masking, smaller scratch/cache working sets, normalized
CDFs and specialized terminal work also change actual work/traffic. Memory
avoidance is a real product benefit, even if not a pure arithmetic speedup.

## Small matched-budget controls

Use the same frozen modeled input and same number of iterations for both arms.
Keep original corrected accounting, optimized accounting, model version, forced
profiles/locks/frozen flags and GPU external workload fixed. Compare:

1. Both arms at21,000 decimal MB (first pressure-relief control).
2. Both arms at19,000 MB if the first control changes original timing materially.
3. Both arms at23,000 MB again to bracket drift against the already measured run.

Suggested bound:6 iterations per invocation, same warm-up/statistical rule as the
existing pass. Do not start a whole matrix concurrently. Use fresh processes,
unique guarded run IDs, and the existing live-work/deadline guard. If the
optimized15.358GB plan is unchanged across these budgets, it provides a useful
control for clocks/external drift. Record actual layout; do not assume unchanged.

Lower original budgets may reduce its particle batch and increase launch count.
That is intentional: if fewer allocated bytes make the original much faster
despite more batches, it supports a memory-footprint/pressure explanation. It
still does not uniquely identify OS paging: cache working-set or scheduling
effects can also matter. If the original remains much slower with clear memory
headroom, the new work reduction and kernel/traffic improvements explain more
of the gain. No result of this unrun control is predicted as fact.

Do not artificially pad the optimized allocation to match original VRAM usage,
reserve dummy memory, disable WDDM features, change other applications, or alter
driver settings. Those introduce risk and unrelated behavior. Do not force
original batch32 beyond its corrected budget merely to chase equal bits.

## CUDA memory visibility

Installed cudarc0.19.7 exposes `CudaContext::mem_get_info()`, which binds the
context then calls the CUDA driver's free/total byte query. It can record before
and after allocation snapshots. It does **not** return an OS per-process residency
budget, resident allocation history, eviction count or transfer-stall diagnosis.
Do not present `total-free` as this solver's resident bytes: other contexts and
driver accounting affect the interpretation.

Windows residency/eviction attribution would require separate OS-level telemetry
(for example a WDDM-aware budget/residency trace), beyond this simple control.
There is no reason to implement that broader instrumentation unless matched
budget controls leave the cause ambiguous and the distinction matters.

## Separate frozen-derived harness

`preflop_budget_control.rs` is a **new** example, derived from the original frozen
`preflop_research_bench.rs` SHA256
`357dfa690981df26dc7e8a872c58addfeb598b45adda7c97957a087822359de4`.
The original remains untouched. `derivation.diff` exposes every difference;
`add-budget-harness.patch` adds the example and its GPU feature declaration.

Usage: `preflop_budget_control INPUT ITERATIONS BUDGET_MB [--legacy]`.
Budgets are limited to19000/21000/23000; iteration count1..8. It retains the same
load/build, iteration, evaluation, arena hash and save-roundtrip operations.
Roundtrip files use a separate budget-specific research filename. Input files
are read only. The init/result JSON includes budget and a distinct harness ID,
so its records cannot silently masquerade as the original frozen benchmark.

Set `PREFLOP_GPU_LAYOUT_STATS=1` for the already prepared matching original/
optimized layout logs. Optional `PREFLOP_GPU_MEMORY_PROBE=1` creates a retained
primary-device context and queries driver free/total bytes before construction,
after construction, after iterations, after evaluation and after GPU drop.
Queries sit **outside** timed regions and do not run between individual timed
iterations. The probe context creation time is separate. It changes context
lifetime and constructor warm-up, so use the same setting in both arms and do
not compare its init timing directly with the unprobed frozen harness. Driver
queries can also have costs; final performance claims should use matched probe
settings, with an unprobed repeat if a result is close.

No dynamic `min(configured_budget, free_bytes)` adjustment is made: budget must
remain an explicit experimental variable. Memory snapshots inform analysis, not
policy or solver behavior. Query failures are recorded rather than changing
the budget. An over-budget constructor failure remains a failure, with no
fallback or automatic rerun at a larger budget.

The parent can use its existing `run_guarded.py` with the separately built example
executable and normal deadline check. Record the fixture SHA256, example/exe
hash, budget, memory-probe setting and layout output for each arm. Keep these
control records separate from original frozen-harness events in summaries.

## Report fields and wording

For each arm/budget report planned MB; actual forced bytes; CDF slots/batch/
bytes; HU cache; compact/normalized flags; driver free bytes at each stage;
iteration samples/check time; exact arena hash or numerical EV/gap error;
fixture/executable/source identities. Different batches require numerical
comparison, preserving all1024 samples and existing tolerances.

Appropriate current claim: **the optimized implementation is about8x faster on
this modeled fixture at the tested23GB budget, while reducing planned GPU memory
by about7.54GB; memory pressure may contribute to the old implementation's time.**
Reserve any claim about how much came from paging or pure kernel throughput
until controlled evidence supports it.

Proposal only: no active source edits, builds, API calls or hardware jobs were
performed by the author. The harness and probes remain uncompiled/unrun.
