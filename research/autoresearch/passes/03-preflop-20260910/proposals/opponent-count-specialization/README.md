# Exact opponent-count specialization

Separate candidate; do not combine with terminal-equity reuse instrumentation
for production timings. Proposal only: no build, GPU execution or active source
edits. `baseline.json` records the source hash. Requires the accepted terminal
CDF base-address hoist (`dea49d1`); the generator asserts those expressions remain.

`implementation.patch` changes only the `pf_multiway_sum` template and its
terminal dispatch. `template<int Q,int O>` uses the exact opponent bound O, and
an explicit unroll directive exposes each constant shared `opponent_bases[q]`
address. The block-uniform switch selects:

| Opponents O | Gauss points Q |
| --- | --- |
| 2 | 2 |
| 3 | 2 |
| 4 | 3 |
| 5 | 3 |
| 6 | 4 |
| 7 | 4 |
| 8 | 5 |

The default switch branch is O8 because production multiway terms have3..9
live seats and the traverser is live: positive-probability work therefore has
exactly2..8 opponents. Zero-probability work exits before dispatch. The existing
term construction and live guard remain unchanged. Do not reuse this function
for heads-up leaves without revisiting that precondition.

The candidate keeps all1,024 samples, particle and quadrature loops, ascending
opponent order, constants, multiplication expressions, batch accumulation,
probability/rake/investment arithmetic and hoisted size_t CDF offsets. It makes
no CDF geometry/layout, precision, fast-math or launch-width changes. The parent
should retain the existing192-thread terminal launch during this comparison.

## Possible benefit and risks

The exact bound can remove dynamic q-loop control, replace shared-address index
arithmetic with fixed offsets, and expose scheduling across opponent loads.
This is a hypothesis, not a measured speedup.

- Seven inlined variants replace four. Device code size and instruction-cache
  pressure may rise; NVRTC/JIT initialization may take longer.
- Full unrolling may increase live temporaries/register count. One large variant
  can raise the terminal kernel's register allocation for all blocks and reduce
  occupancy, even when most terminals have only two opponents.
- Unrolling may improve or worsen load scheduling; no hardware result can be
  inferred solely from a constant loop bound.
- Source operation order is unchanged, but compiler contraction/scheduling may
  still change generated float arithmetic. Require exact hashes and terminal
  bits before accepting; do not substitute a looser numerical tolerance.
- For resource comparison, record NUM_REGS, LOCAL_SIZE_BYTES/spills, shared
  bytes and active blocks/SM at192threads (if the existing resource tool exposes
  them). Also compare PTX/cubin size and compile/init time where available.
  No resource measurements were made by the proposal author.

## Parent validation plan

First apply-check and compile. Run existing internal terminal parity and stale/
zero/direct-boundary/compact tests. Existing3/6/9-seat checks cover O2/O5/O8;
for this candidate additionally exercise4/5/7/8 live seats to cover O3/O4/O6/O7.
Compare full terminal f32 bits to the unspecialized GPU path at batch32/7/1,
including non-unit reaches, ties and different masks. CPU comparisons remain
useful but do not replace exact GPU candidate/control comparison.

Run captured learning and evaluation parity, mixed ruled/live limper fixture,
and the standard preflop GPU suite. Benchmark frozen eight-seat and seven-seat
fixtures plus small3/6-seat controls with the same CDF geometry/layout and launch
width. Check arena hash/gaps/EVs, register/occupancy changes and repeated timing.
Reject if a flagship win comes with a material control regression. Keep this
candidate independently reversible from ongoing CDF geometry experiments.
