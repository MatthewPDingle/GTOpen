# Launch-width review after exact opponent specialization

Proposal only. No active edits, compilation or hardware jobs. Source hashes are
in `baseline.json`; each patch is independent against the current192-thread
specialized terminal. CDF normalization also currently has a192-thread launch:
the generator matches only `Self::cfg(self.mw_nterms)`, leaving that CDF work alone.

## Small deterministic sweep

Primary sequence: **192 control,128,160,256,192 control**. Repeat a winning width
against192, then include modeled fresh-coupled and legacy controls. Width96 is
an optional second-stage candidate if smaller blocks show benefit. Width384/512
patches are supplied only as low-priority negative controls, not recommended
routine trials: they cannot expose additional hands in this169-class kernel.

| Threads | Warps at32 lanes | Max hero-loop passes | Threads unused on first pass |
| --- | --- | --- | --- |
| 96 | 3 | 2 | 0 |
| 128 | 4 | 2 | 0 |
| 160 | 5 | 2 | 0 |
| 192 | 6 | 1 | 23 |
| 256 | 8 | 1 | 87 |
| 384 | 12 | 1 | 215 |
| 512 | 16 | 1 | 343 |

O specialization may have changed register pressure and therefore resident
blocks. Smaller blocks may fit more terminals but some threads calculate a
second hero hand. Width160 limits that second pass to9 threads; width128 gives
41 threads a second hand. Width192 processes each hand once with six warps.
Larger widths retain the same useful hands while reserving more threads and
potentially registers. Actual occupancy depends on compiled allocation, shared
memory and the device; no register count or occupancy is assumed from the GPU
name alone. Higher reported occupancy is not automatically faster.

Every hero hand is independent; changing which thread owns h preserves its
particle/q/quadrature operations and batch order. Thread0 prepares the same
shared bases/probability before the unchanged block barrier. Width changes do
not move or remove that barrier, and preserve positive/zero counterfactual
paths. There is no warp-level reduction in this terminal kernel. Exact GPU
parity is still required because compiler/runtime effects must be measured.

Each `terminal-N.patch` changes one launch width in gpu.rs; do not stack patches.
The specialized kernel source is byte-identical during geometry trials. Keep
the CDF geometry, compact/normalized mode, budget, batch, HU cache, profiles,
checkpoint and iteration counts fixed. Rebuild captured graphs in a fresh
benchmark process. Use the existing guarded benchmark workflow and `sweep.json`
as the ordering manifest; no new background scheduler is proposed.

## Register and occupancy evidence

`resource-test.patch` adds one ignored manual test, compiling only the preflop
CUDA source for the detected device and querying `pf_multiway_terminal`. It
reports registers/thread, local memory, shared bytes, supported block width,
PTX source size and compiler/module load times. CUDA's occupancy API is queried
for all proposed widths with zero dynamic shared memory. The helper methods
were verified in the installed cudarc0.19.7 source; the test is uncompiled.

The test performs no kernel launch, but it creates a context and compiles/loads
CUDA, so schedule it with the parent's hardware work rather than alongside
timed benchmarks. These are maximum residency estimates, not measured achieved
occupancy. The ignored test can be run once per changed kernel source; launch-
width-only candidates do not change its register count/PTX.

```powershell
cargo test --release -p solver --features gpu --test coupled_terminal_resources -- --ignored --nocapture --test-threads=1
```

## Separate output restrict candidate

`restrict-terminal-output.patch` adds only `__restrict__` to the terminal's
`float* val` argument. Its nonaliasing precondition follows from GPU construction:

- val is `d_val`, a standalone CUDA allocation for value slots.
- cdf, lower/upper, invested, pots, terminal probabilities and slot maps are
  separately allocated device buffers, never views into d_val.
- Value-slot reuse is internal to the val allocation. Accesses through val
  itself may refer to the same allocation; that does not violate this promise.
- Each launched terminal has a distinct terminal value slot. Action slots reuse
  storage in later ordered kernels, not through another pointer during this call.

All input kernel pointers already have restrict qualifiers; this extra qualifier
may be redundant after inlining/alias analysis. Test it independently rather
than attributing an assumed gain. It can affect caching and increase register
pressure, so record resources again and retain only if exact-bit parity and
repeated wall timing support it. No restrict annotations are added to the
read-only helper arguments: they contain no stores, already inherit restricted
global pointers, and the shared-base versus global-memory distinction provides
additional compiler information without more assumptions.

Do not add launch_bounds, max-register compiler limits, fast math, alternative
precision, shuffled q order or a parallel reduction to this sweep. Those would
confound geometry with generated code or arithmetic changes.

## Acceptance

Run the all-opponent test (3–9 live seats, batches 32/7/1) with exact terminal-bit comparison against
the same specialized192-thread control, plus existing zero/stale/compact and
captured arena/gap/EV checks. All launch variants keep1024 particles. Prioritize
eight/seven-seat wall time, confirm three/six-seat and modeled controls, and
record any memory/layout difference as a confound. Repeat winners bracketed by
the control; do not choose a width from a single noisy timing or occupancy alone.
