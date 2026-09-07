# GTOpen: three-hour optimization research

2026-09-07, 00:38–03:38 UTC. Six research paths were measured independently,
with one implementation hypothesis per trial, frozen workloads, repeat runs,
explicit keep/discard decisions, and accuracy checks before promotion.
The run explored 20 numbered hypotheses through 87 recorded runs, retaining
17 implementation families and keeping graphs for all 64 measured metrics.

The [tracking page](index.html) contains every metric graph and the experiment
ledger. [Raw results](results.tsv), [audit events](events.jsonl), [protocol](program.md),
and [working notes](notes.md) retain the evidence, including unsuccessful trials.

## What the comparisons mean

The baseline is `bc192bfa0a9b1bd025003fdee3d70ab0d5f8f326`, which already includes
the earlier optimization passes documented in
[preflop performance](../../docs/preflop_performance.md) and
[postflop performance](../../docs/postflop_performance.md). Gains in this report
are additional to that baseline; percentages from the separate passes must not
be added together.

The first combined retained snapshot was `f28e16f45f570cfd86f201b698dd1a1eb2816c86`.
Fresh original-code controls B013–B017 ran in the isolated worktree, then the
retained implementation was restored at `cd84600`. The user's main checkout
kept the retained implementation throughout those controls.
E019 subsequently added profile aggregate-buffer reuse, and E020 added runtime
CPU vector dispatch. The current retained
snapshot is recorded as `final_kept_commit` in [run.json](run.json).
The [incremental production patch](patches/final-retained.patch) is relative
to the research baseline. Main-checkout changes are left uncommitted for review.

Hardware: Windows 11, Ryzen 5950X, 16 solver/Rayon threads, RTX 3090 24 GB.
Hardware benchmarks ran serially. Timings exclude compilation and chart
generation. These are measurements on fixed workloads, not universal speedup
guarantees. All MB values are decimal unless explicitly labeled MiB.

## Final comparisons

These comparisons use the combined retained implementations. Individual trial
effects and repeat variability are documented below and in the ledger.

| Workload / metric | Original | Combined retained | Change | Evidence |
|---|---:|---:|---:|---|
| Six-seat CUDA solve to total gap ≤0.03 | 5.392 s | 3.200–3.217 s | 40–41% less time | B013 / F001, F009 |
| Eight-seat CUDA solve to total gap ≤0.03 | 17.699 s | 7.931–7.986 s | 55% less time | B013 / F001, F009 |
| CPU six-seat iteration | 197.02 ms | 72.92 ms | 63% less time | B014 / median E020 repeats |
| CPU six-seat accuracy check | 1424.24 ms | 296.15 ms | 79% less time | B014 / median E020 repeats |
| Rainbow flop CUDA solve to 0.3% pot | 11.305 s | 10.994 s | 2.8% less time | B015 / F003 |
| Two-tone flop CUDA solve to 0.3% pot | 6.739 s | 6.557 s | 2.7% less time | B015 / F003 |
| Full report line summaries | 199.18 ms | 77.63 ms | 61% less time | B014 / F002 |
| Postflop profile generation | 638.09 ms | 435.54–445.79 ms | 30–32% less time | B014 / E019R, E019R2 |
| Warm f32 save-file loading | 47.49 ms | 37.20 ms | 22% less time | B017 / F005 |
| Load-process peak working set | 201.59 MB | 170.63 MB | 15% lower | B017 / F005 |
| Six-seat CUDA allocated memory | 1140.85 MB | 671.09 MB | 41% lower | B004 / F006 |
| Eight-seat CUDA allocated memory | 3590.32 MB | 1711.28 MB | 52% lower | B004 / F006 |
| Rainbow flop CUDA allocated memory | 7683.96 MB | 6241.12 MB | 19% lower | B006 / F007 |
| Two-tone flop CUDA allocated memory | 7683.96 MB | 4932.50 MB | 36% lower | B006 / F007 |
| Six-seat GPU-to-CPU checkpoint | 59.99 ms | 25.96 ms | 57% less time | B001 / F006 |
| Eight-seat GPU-to-CPU checkpoint | 150.46 ms | 68.30 ms | 55% less time | B001 / F006 |

The memory and transfer rows use the run's initial controls; repeated trials
support the reductions. Final warm CUDA iteration/check medians were
17.892/12.265 ms for six seats and 62.182/38.806 ms for eight seats. The final
memory figures include the optional equity cache. Earlier minimum VRAM points
on the charts predate that cache and do not describe the final default engine.

CPU final values are medians of E020, E020R, E020R2 and E020R3. Against fresh
portable controls B020, B021 and B021R, runtime AVX2 dispatch itself reduces
iteration/check medians by 5%/8%. Runtime feature detection preserves the
portable implementation on other processors. Both paths preserve each hero
hand's accumulation order and match the independent scalar calculation exactly.
No FMA or fast-math optimization was enabled.

Preflop target timings include all iterations, CUDA graph capture and scheduled
accuracy checks after initialization; final CPU readback is measured separately.
Both implementations finished at exactly 175 iterations for six seats and 125
for eight seats. Every arena bit, EV and per-seat gap matched. Final total gaps
were 0.0248476629043 and 0.0205216594862, respectively.

Postflop target timings exclude tree/device initialization and final CPU
readback. Both large boards finished at 200 iterations, using checks every 20.
Original/final exploitability was 0.279914604/0.275829435% pot on rainbow and
0.255958513/0.251358787% on two-tone. The original atomic fold reductions varied
between independent runs. The retained implementation uses fixed-order f32
sums, which make repeated learning and evaluation deterministic.

The isolated loader benchmark takes the median of 20 loads after two warmups.
Its peak working set is sampled from a prebuilt test executable; it excludes
the compiler. The 104.20 MB fixture, iteration count and exploitability stay
fixed. Saving still flushes and synchronizes durably; no durability or format
change was made. Save timings fluctuated substantially and are not claimed as
an improvement. Compressed loading is unchanged.

CPU postflop output-buffer reuse gave a modest 2–4% gain in its immediate
paired controls (26.05 ms to 25.11–25.49 ms). Broader lifecycle runs show timing
drift, so this small gain should not be inferred from the earliest and fastest
points on the chart. Full report/profile/save fingerprints remain identical.
Compressed report adaptation was nearly unchanged in the final comparison:
5.008 to 4.925 seconds. The earlier 3.7× CPU-to-GPU adaptation gain predates this
research run and is not counted again.

## Research paths and retained implementations

| Path | Retained trials | Implementation and outcome |
|---|---|---|
| Preflop CUDA | E001, E010, E015 | Capture per-seat learning launches; calculate shared reach masses once; cache exact equity vectors by shared opponent reach. Large solves and checks are faster; tiny heads-up iterations benefit from lower launch overhead. |
| CPU solving | E008, E017, E020 | Compute independent hero equities in parallel SIMD lanes while preserving each accumulation order; select wider lanes on supported CPUs with a portable fallback; reuse showdown output for intermediate mass instead of acquiring scratch storage. |
| Memory and transfers | E003, E007, E014, E016R | Reuse transactional pinned snapshots; share unchanged preflop reach vectors; upload borrowed arenas directly; use actual compact postflop plans for GPU budget admission. |
| Postflop CUDA | E009, E011D, E013 | Pack reach buffers by their existing owner; replace fold atomics with deterministic sums; allocate CFVs only for visited nodes. Capacity is the main gain, with a smaller solve-time gain. |
| Reports and profiles | E005, E012, E019 | Classify each board lazily once per report; specialize common action counts in profile raking; reuse aggregate storage across fitting iterations without changing arithmetic. |
| Build, save and load | E006 | Read f32 save data directly into the new solver's private arenas, removing an allocation and copy. File compatibility and durable writes stay intact. No separate repeatable tree-build or save-speed gain is claimed. |

## Memory tradeoffs

- Preflop pinned readback retains host RAM equal to the two CPU arenas while
  the GPU engine is alive: about 224.55 MB for six seats or 587.24 MB for eight.
  It stages both downloads before publishing either CPU arena. If page locking
  fails, the ordinary-memory transactional download remains available.
- The optional preflop equity cache adds approximately 67 MB / 168 MB of actual
  VRAM for six/eight seats. The constructor omits it when the budget only fits
  the base engine, using the exact direct calculation instead. Overall GPU
  memory still falls substantially after reach sharing.
- Postflop CFV compaction costs about 1–2% iteration time versus the best
  pre-compaction repeat, while saving a further 705 MB on the two-tone flop.
  That trial was retained for capacity. This is a concrete example of a blue
  timing dot sitting above the green best-observed line.
- CPU batched equity adds an approximately 114 KB transposed table. Report
  board classifications live only for the duration of one report.

## Rejected and deferred paths

E002's CPU scratch pooling became a near-tie on repeat and slowed checks.
E004's larger CUDA blocks slowed flop iterations by roughly 20%; smaller blocks
did not give a repeatable overall gain. E011's initial ordered f64 fold variants
were too slow on this GPU; the eventual retained E011D uses the existing f32
precision. E018's CPU showdown-boundary cache reproduced the answers but did
not improve timing enough to justify its memory and setup cost.

Failed benchmark builds and an incorrect new budget-test assumption are also
recorded. They were corrected without changing the frozen workloads or relaxing
solver accuracy requirements. Failed runs without metrics have no chart dots.

Further GPU regret/strategy arena compaction remains a promising separate
path. It needs explicit preservation of inactive arena values during CPU
readback, suit-isomorphic queries, saves and resume; blindly scattering only
active values changes complete saved state. No such shortcut was retained.

## Accuracy and verification

Frozen harness hashes are in [run.json](run.json). Preflop learning, CPU
learning, reports, profiles and saves were compared with complete fingerprints.
Cached and direct GPU computations were also compared on the same states,
including raw/static/calibrated realization, locks, profiles, frozen seats,
hero mode, stop requests and nonzero starting iterations.

Postflop buffer compaction matched all 24 complete saved states and evaluation
bit patterns in the dedicated board/rake/isomorphism/lock matrix. The fold
arithmetic retains f32 precision; its fixed reduction order changes the original
atomic order, so original independent trajectories are assessed with the same
accuracy target rather than an inappropriate bitwise identity requirement.

Final combined main-checkout checks, including E019 and E020:

| Suite | Passed | Failed | Ignored | Log |
|---|---:|---:|---:|---|
| CPU solver | 124 | 0 | 4 manual benchmarks | [CPU](raw/final-main-cpu-v2.log) |
| CUDA-enabled unit and integration checks | 40 | 0 | 0 | [CUDA](raw/final-main-gpu-v2.log) |
| Server continuation, locks, storage and stopping | 1 | 0 | 1 manual benchmark | [Server](raw/final-main-server-v2.log) |

The CUDA count includes unit tests also covered by the CPU suite; these are
suite totals, not a sum of unique tests. Its large-game budget check compares
every arena, gap and EV bit after 65 iterations at normal and tight budgets:
700 MB for six seats and 1,600 MB for eight seats.

[Final verification](validation.json) records source/harness checks and exact
result comparisons. Run `python research/autoresearch/verify_final.py` to
recheck that evidence against the retained main and research worktrees.

## Reproduction

Run hardware measurements one at a time, with other solves stopped. Use the
same cache files and frozen workloads for any comparison. From the repository
root in PowerShell:

```powershell
$env:PATH = "$PWD\.cuda-nvrtc\nvidia\cuda_nvrtc\bin;" + $env:PATH
$env:RAYON_NUM_THREADS = '16'
$env:SOLVER_THREADS = '16'
cargo test --release -p solver
cargo test --release -p solver --features gpu --lib --test gpu --test preflop_gpu --test preflop_budget -- --include-ignored --test-threads=1
cargo test --release -p server --features gpu -- --test-threads=1
cargo test --release -p solver --features gpu --test preflop_target_perf -- --ignored --nocapture --test-threads=1
cargo test --release -p solver --test research_perf -- --ignored --nocapture --test-threads=1
cargo test --release -p solver --features gpu --test preflop_perf --test capacity_perf --test postflop_capacity_perf -- --ignored --nocapture --test-threads=1
$env:POSTFLOP_PERF_CONVERGENCE = '1'
cargo test --release -p solver --features gpu --test postflop_perf -- --ignored --nocapture --test-threads=1
Remove-Item Env:POSTFLOP_PERF_CONVERGENCE
```

The research runner records each measured command, its source commit, harness
hashes, checks and raw output. It runs commands in the isolated research
worktree. To continue research, follow [program.md](program.md) and assign new
run IDs; never overwrite prior evidence. For load-process memory comparisons,
compile the load-only harness first and measure its executable directly,
excluding Cargo/compiler memory.

The running desktop server was not replaced or restarted. A normal next launch
through `GTOpen.cmd` rebuilds the executable and picks up the retained changes.

## Reading the charts

The x-axis is the global run sequence, including controls and repeats across
all paths. Each chart shows only runs that measured its metric. Expand the
measurement list below a chart to identify its points and their roles.

Gray dots are baselines, repeated controls, or measurements outside a trial's
target. Blue dots identify retained code for a targeted metric, including
repeats. Amber marks candidates or inconclusive runs. Crosses indicate rejected
or failed runs, including gray crosses for measurements outside their target.
Green is the lowest eligible baseline/retained observation so far. It is not
the average, current typical performance, or an estimate with error bars.

The loop adapts the hypothesis/measure/keep-or-discard structure of
[Karpathy's autoresearch](https://github.com/karpathy/autoresearch) to a solver
with multiple accuracy-preserving performance objectives.
