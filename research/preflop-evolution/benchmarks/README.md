# Contextual model regression and performance

Run from the repository root:

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:RAYON_NUM_THREADS='4'
python tools/research/model_benchmark.py
```

`--no-build` reuses the release example; `--target-dir PATH` selects a separate
Cargo output directory. The native process never contacts the running app. It
reads the cached equity table and constructs its own compact games. It does not
solve or alter saved sessions, train a model, or open raw hand histories.

Open [the charts](index.html). [latest.json](latest.json) contains full measured
results and [history.json](history.json) retains each benchmark run. History
records are measurements of specific working revisions and conditions, not
evidence that each successive run is an improvement. The graphs compare the
latest baseline and candidate; no earlier measurements are invented.

## Pass 2: compile invariant model arithmetic once

The frozen artifact and model probabilities are unchanged. Initialization now
computes baseline logarithms once and precomputes each hand's weight sums for
the entry type, price and raise-depth modifiers. Each prediction evaluates only
the changing context and combines those cached terms. Nearest-observed context
selection also avoids temporary allocations.

The paired dense-versus-compiled benchmark measures both implementations in the
same process, rotating their order each batch. It currently shows a median
**3.20× inference speedup** across the 26 supported contexts. Six-player full
ranges take approximately **17–18 μs → 5–6 μs** on this run. These are prediction
costs, not overall CFR solve times. Host load can change absolute timings.

Compiled numeric model storage increases from **114,848 to 139,184 bytes**:
**24,336 extra bytes (23.77 KiB)** of hand terms, shared by every prediction.
This excludes headers/allocator overhead; the baseline probability arrays are
replaced by logarithms, not duplicated in the application. Median first
prediction time over five fresh processes was **678 μs → 753 μs**, including
artifact parsing and the one-time compilation. Every measured sample is saved.

The original dense arithmetic remains an independent test/benchmark oracle;
the app never selects it or loads its separate reference copy. A deterministic
test compares **2,048 contexts × 169 hands** across table size, position, entry,
depth, investment, price and remaining stack. Its maximum observed `f32`
difference is **zero**, with a fixed **1e-7** acceptance ceiling. The 26 paired
benchmark ranges also match exactly; their Python comparison remains below
7.24e-8. No prediction-accuracy threshold or support restriction was relaxed.

## Correctness gates

- Compare all 169 hand classes with the original Python inference code in 26
  contexts, including 3–6 players, cold/called/ever-raised history, 3-bets and
  later raises, blind credit, a low call price and a short remaining stack.
  The maximum observed absolute probability difference is **7.24e-8 or less**,
  below the 2e-6 acceptance tolerance.
- Check four unsupported contexts (8-player $2/2 and $2/5, equal blinds, ante)
  return the fixed-policy fallback.
- Construct six independent compact games: existing and contextual profiles
  for each of a source-supported 6-player game and 8-player $2/2 and $2/5 games.
  Query 24 legal re-raise nodes, check finite/nonnegative/normalized action
  probabilities, and fingerprint their exact `f32` strategy bytes. Unsupported
  games must match the existing policy exactly; the supported game must change.
- Repeat the game cases three times and require deterministic strategies.

The compact games use one opening size, one re-raise size, no limps, and a
three-raise cap. They exercise real engine action construction but are **not
the user's saved scenarios** or a test of solved EV/convergence. Table profiles
in this harness are deliberately synthetic aggregate policies so inference cost
can be compared while holding all other policy inputs fixed. Adaptive responses
are not enabled here; their correctness belongs to the solver's integration
tests.

## What each metric means

| Graph | Measurement |
| --- | --- |
| Compiled inference | Dense original versus compiled implementation of the same frozen model, paired within each run. The fixed-policy baseline is shown separately in the original inference chart. |
| Compiled model memory | Numeric arrays resident in the application: baseline probabilities/logits and weights, plus cached hand terms. Does not count the optional benchmark-only reference copy. |
| Model cold start | First prediction in a fresh native process, five samples per implementation with alternating process order. Includes parse/validation/compile; excludes process startup and fixture JSON parsing. |
| Prediction loss | Frozen retrospective chronological experiment, imported from `research/ignition-reraise/experiment.json`. All source periods were previously inspected. The runtime artifact was subsequently refitted on all data; it is not re-evaluated against its own training data here. |
| Inference latency | Materialize one 169-hand range after loading the frozen artifact once. Existing fixed-policy clone versus full contextual feature/inference calculation, 9 alternating batches, median shown. Excludes initial model parsing; this measures added computation, not a solving speedup. |
| Build | Independent compact tree construction; policy mode is applied only afterward. Differences between baseline/candidate here are timing noise, not an effect of the model. |
| Install profiles | Apply a complete table of profiles, including normal engine bookkeeping. Inference is cached on demand. |
| First/repeat queries | Query the same 24 legal re-raise nodes including their history; repeat queries reuse cached contexts. |
| Materialize all/repeat all | Obtain strategies for every action node in the compact tree. The first pass follows the 24-node warmup; the repeated pass reuses the cache. This is policy compilation/materialization, not CFR iterations. |
| Arena memory | The engine's explicit regret and strategy-sum allocation, unchanged between model versions. Excludes nodes, profile objects and cache allocations. |
| Context cache memory | `entries × 169 × 3 × sizeof(f32)` after visiting the entire compact tree. Excludes map/allocation/strings overhead; not process RSS or GPU memory. |
| Parity | Maximum absolute Python/Rust probability difference for each whole-range fixture. |

The 6-player compact game has 10,331 nodes and 13.97 MB of solver arenas. Its
complete policy pass creates **1,016 contextual cache entries**, a **2,060,448
byte vector payload** (1.97 MiB). The two unsupported 8-player games allocate no
context cache and keep their original strategies. The runtime cache is bounded;
these measurements do not imply a complete large tree will fit inside it.

Prediction quality improves from 0.5353 to 0.4858 mean negative log probability
on the frozen later-period sample (2,351 decisions). That is a **9.3% reduction
in prediction loss**, not a measured EV or win-rate improvement. Individual
hand/context probabilities, especially weak hands at cheap prices, can remain
uncertain despite improved average predictive performance.

Run timings on an otherwise idle host before comparing regressions. Full test
suites or other solves running concurrently can materially affect the numbers.
The native measurement records all batch samples so variability stays visible.
