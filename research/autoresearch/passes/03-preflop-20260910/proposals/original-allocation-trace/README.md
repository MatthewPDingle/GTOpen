# Original constructor requested-byte trace (diagnostic only)

The zero-launch module probe reported only2MiB loaded-module overhead, which returned to baseline after module drop. It does not explain the original constructor's approximately1.12GB residual. A second source audit found no additional large buffer beyond the already-known forced-policy accounting omission in **literal**1b8fc3f.

Keep these variants distinct:

- `literal-1b8fc3f.patch` / `literal-1b8fc3f-gpu.rs`: generated directly from git1b8fc3f. Original planner remains untouched, including its uncharged forced-policy buffer. This omission is414,292,684bytes for the modeled fixture. The trace reports actual forced bytes explicitly.
- `original-forced-budget-corrected.patch` / corresponding full `.rs`: generated from the prior frozen original wrapper with only forced-budget correction and existing layout diagnostic. This matches the controls exhibiting the unexplained~1.12GB after subtracting baseline and plan. The trace itself does not modify that planner.

Neither variant changes CUDA source, action order, policies, precision, allocated lengths, copies, model or solve kernels. All existing frozen files/harnesses and the active worktree were left untouched. Proposal not built or run.

## What is traced

Opt in with `PREFLOP_GPU_ALLOCATION_TRACE=totals` or `each`.

Both modes record device-global CUDA free/total/used after context creation, stream setup, module load, constructor function loads, and all buffers. They record actual lengths and `CudaSlice.num_bytes()` for **every** device-array field, plus total requested bytes and difference from planned need. A generated second ledger reads the completed object's fields and must match the per-allocation records and total exactly. No buffer-capacity guess or reconstructed tree size is used in that final check.

`totals` performs no synchronization between array allocations. Start with this mode to preserve the original allocation/copy sequence as closely as possible. It adds synchronization only before arrays exist and at the final snapshot, similar to the existing constructor memory probe.

`each` additionally synchronizes and snapshots after each successful array allocation/copy/memset. This localizes which allocation interval exposes a discrepancy. **It can change asynchronous allocator scheduling and pool reservation behavior**, so compare it to the totals-mode result rather than assuming identical memory behavior. A discrepancy disappearing in each mode is itself a scheduling-sensitive observation, not evidence that the original snapshot was wrong.

Each record includes cumulative requested bytes, driver delta since context, and delta minus requested. Those differences can include allocation rounding/reservation and other device users. They do not identify paging, residency or a specific runtime mechanism. The zero-launch module-probe result argues against assigning the original residual to module loading alone.

## Standalone constructor control

`preflop_allocation_control.rs` is an optional new example (same gpu-required example registration convention):

```
preflop_allocation_control INPUT.gtop BUDGET_MB
```

It loads the frozen native fixture and existing equity cache, creates the traced GPU solver, snapshots and drops it. No iterate, gaps/EV, native save, browser/API calls, or solver-kernel launches. CUDA array allocation, initialization memsets and host/device copies do occur. Use the parent's pinned absolute REALIZATION_FIT path, CWD, equity-cache/input SHA256 and standard environment. This harness does not alter the existing frozen budget/convergence/module harnesses.

Build copies only after the frozen queue, with the corresponding original kernels. Freeze separate executable hashes. Use one existing modeled fixture, one predeclared budget, and run `totals` first. If its residual reproduces, repeat under `each`; retain both logs. The corrected19000MB control is a reasonable first target because it reproduced the residual with more free memory than23000. A literal1b8 run is a separate case because missing forced accounting changes its batch/cache selection.

Do not compare uncorrected literal planned need directly with corrected plan without accounting for its forced allocation. For the corrected current modeled tree, the prior ledger predicts requested buffers approximately26.97MB below plan, owing to the64MB allowance. The exact trace will verify that arithmetic independently from allocator/device usage.

## Alignment and placeholders

Installed cudarc0.19.7 calls the CUDA allocator once per clone_htod/alloc_zeros with exactly len*sizeof(T); it does not round the request in Rust. Any allocator-side granularity/reservation is outside these CudaSlice payload lengths and should appear in the driver-minus-requested column. Disabled cache placeholders and the forced empty-buffer minimum are counted by their actual returned slice sizes, including4byte objects. Stream objects, functions, graphs and host-pinned memory are not CudaSlices; constructor stage snapshots separate streams/functions, and no graphs or host snapshot have been created yet.
