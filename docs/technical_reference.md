# Technical reference

Engine details, runtime settings, historical benchmarks, and scripting interfaces.
For installation and the app workflow, start with the [README](../README.md).

## Runtime settings

Optional environment:

| var | default | meaning |
|---|---|---|
| `PORT` | 3737 | HTTP port |
| `SOLVER_THREADS` | physical cores | rayon worker threads (SMT hurts this workload; 12–16 is the sweet spot on a 5950X) |
| `SOLVER_COMPRESS` | 1 | `0` = full-precision f32 arenas instead of 16-bit compressed |
| `SOLVER_GPU` | 1 (if built with `gpu`) | `0` forces the CPU engine even when CUDA is available |
| `SOLVER_GPU_MEM_MB` | live free VRAM − 512 MB | manual VRAM cap for the GPU engine; spots over budget fall back to CPU |
| `SOLVER_MEM_MB` | 80% of free RAM (≤48 GB) | solver-arena + tree RAM budget; bigger builds are refused |
| `PREFLOP_EQ_SAMPLES` | 20000 | Monte-Carlo samples per hand-class pair for the Preflop Lab equity table |
| `PREFLOP_MAX_NODES` | RAM-derived | Preflop Lab tree-size limit; the lab shows a live estimate + this machine's caps before BUILD |
| `PREFLOP_MAX_ARENA_MB` | ~40% of free RAM | Preflop Lab regret/strategy memory limit (MB) |

## Engine

- **Algorithm**: Discounted CFR (α=1.5, β=0, γ=2) with alternating updates,
  vectorized over hands. CFR+ and Predictive CFR+ (PCFR+) are selectable per
  solve (`POST /api/solve {"algorithm": "pcfr+"}` or `SOLVER_ALGO` in the CLI).
- **Compressed arenas (16-bit)**: regrets stored as i16 and strategy
  sums as u16, quantized per node against the node's max magnitude — half the
  memory of f32, and faster on big trees because CFR is memory-bandwidth
  bound. Verified equivalent to f32 within 0.1% pot exploitability by test;
  save files stay full-precision f32 and load into either mode.
- **Zero-allocation traversal**: all per-node-visit scratch vectors come from
  a thread-local buffer pool instead of malloc.
- **CUDA GPU solver**: level-synchronous CFR with f32 working arenas in VRAM
  (`--features gpu`). On the current RTX 3090 benchmarks, the 1.35M-node
  rainbow/two-tone flop cases take **51.8 / 31.4 ms per iteration**.
  Exploitability also runs on the GPU, with reusable evaluation graphs and
  batched root downloads. Node locks, DCFR/CFR+, and both CPU storage modes
  are supported; PCFR+ uses the CPU. Compressed CPU arenas decode on upload
  and re-encode on sync. Visited action blocks are packed where worthwhile,
  value scratch is reused between tree levels, and inactive state is preserved
  for exact save/resume and CPU browsing. The server uses CUDA when available;
  `SOLVER_GPU=0` opts out. The default VRAM budget is **live free VRAM minus
  512 MB headroom**, with `SOLVER_GPU_MEM_MB` as a manual override. The final
  GPU plan is checked at solve time; allocation or CUDA failures fall back to
  CPU. The UI's conservative full-tree estimate can exceed that final plan.
  See [current performance and validation](../research/autoresearch/gpu-pass.md).
- **Terminal evaluation**: O(n) sorted showdown sweep with exact card-removal
  (blocker) accounting via per-card prefix sums; precomputed 7-card strengths
  for every river runout.
- **Exploitability**: true best-response traversal both ways, reported as % of
  pot — a best-response measure for the configured game; locks change the game being evaluated.
- **Parallelism**: rayon across chance branches; arenas use disjoint unsafe
  slices (each tree node's data is touched by exactly one branch).
- **Suit isomorphism**: chance branches that are suit-symmetric (given the
  board and ranges) are solved once and mirrored exactly — ~1.4x on two-tone
  flops, ~2.2x on monotone, no effect on rainbow. Exact (verified against the
  non-isomorphic solver). Zero-reach subtrees are also pruned exactly.
- **Trees**: per-street/per-player bet, raise and (OOP) donk sizes, all-in
  threshold conversion, raise caps, NL min-raise rules, rake (% + cap),
  flop/turn/river root. EVs use the pot-share convention (EV OOP + EV IP =
  pot).
- **Accuracy tests** (`cargo test -p solver --release`): hand evaluator vs an
  independent reference on 20k random deals; range parser round-trips; the
  clairvoyance game converges to its known closed-form solution (bet-ratio
  1/3 bluffs, MDF 50% calls, EVs exact); equity matches brute-force
  enumeration; full flop trees reach <1% pot exploitability; node-lock
  semantics; save/load roundtrip (both storage modes); compressed-vs-f32
  exploitability equivalence; PCFR+ convergence; exploit-view best response
  vs a locked station (bets the nuts, never bluffs, BR EV dominates);
  per-hand locks land on the right combos across suit-isomorphic runouts;
  preflop CFR vs an independent fictitious-play Nash oracle on HU jam/fold,
  plus multiway limp-tree chip conservation and rake-drain direction.

## Performance

Latest validated results: **7 September 2026**, Windows, RTX 3090 24 GB,
Ryzen 5950X, 64 GB RAM, 16 solver threads. These are fixed workloads, not a
promise for every tree or machine. The comparison below is the latest GPU
research pass versus fresh controls of the code at the start of that pass.

| Workload | Before | Current | Improvement |
|---|---:|---:|---:|
| Six-seat preflop, same accuracy target | 3.549 s | 2.317 s | 34.7% less time |
| Eight-seat preflop, same accuracy target | 8.926 s | 5.323 s | 40.4% less time |
| Rainbow flop, 0.3%-pot target | 12.067 s | 11.107 s | 8.0% less time |
| Two-tone flop, 0.3%-pot target | 7.219 s | 6.667 s | 7.6% less time |
| Six-seat preflop GPU allocation | 671 MB | 503 MB | 25.0% less |
| Eight-seat preflop GPU allocation | 1,711 MB | 1,309 MB | 23.5% less |
| Two-tone compressed postflop GPU allocation | 4,933 MB | 3,624 MB | 26.5% less |
| Rainbow compressed postflop GPU allocation | 6,241 MB | 5,906 MB | 5.4% less |
| Warm compressed two-tone full readback | 1,531 ms | 297 ms | 80.6% less time |

Target timings exclude tree construction and initial GPU upload. Preflop
still stops at 175/125 iterations, and the two flop cases at 200/200, with
identical checked states and final values. No precision, model, bet menu,
or accuracy target changed. MB are decimal; device allocations are measured,
while the UI shows estimates and a live memory budget.

The [current GPU report](../research/autoresearch/gpu-pass.md) contains all
comparisons, limitations, and 696 source/numerical audit checks. The
[progress image](../research/autoresearch/gpu-pass-progress.png) renders on GitHub;
the [interactive tracker](../research/autoresearch/index.html) can be opened
locally and includes 130 metric graphs, controls, and rejected trials.

The [first research pass](../research/autoresearch/report.md) additionally covers
CPU solving, profiles, reports, and loading: the measured six-seat CPU
iteration fell from 197.02 to 72.92 ms, report-line summaries from 199.18 to
77.63 ms, and warm f32 save loading from 47.49 to 37.20 ms. These earlier
comparisons have their own baselines; percentages across passes must not be added.
[Preflop](preflop_performance.md) and [postflop](postflop_performance.md)
notes summarize the latest results and preserve the earlier measurements.

RAM budgets cover solver arenas plus tree storage; actual process memory also
includes caches, staging, driver allocations, and other overhead. Compressed
CPU arenas use half the per-entry storage of f32, but do not halve total RAM
or GPU VRAM. The server refuses over-budget CPU trees. GPU packing and scratch
reuse reduce device allocation by different amounts on different trees.

## CLI

```bash
./target/release/solve-cli spot.json [max_iterations] [target_exploit_pct]
./target/release/solve-cli batch spot.json boards.txt [max_iterations] [target]
```

`spot.json` matches the `SpotConfig` JSON schema (see `bench_spot.json`).
Env: `SOLVER_STORAGE=f32|i16` (default i16), `SOLVER_ALGO=dcfr|cfr+|pcfr+`
(default dcfr), `SOLVER_ISO=0`, `SOLVER_THREADS=N`, `SOLVER_GPU=1`
(gpu-feature builds) — all of them apply to every mode (single spot, batch,
realization). Batch rows report range-average root EVs weighted by
reach × valid (the app's convention, so `ev_oop + ev_ip = pot`).

**Batch mode** solves the same ranges/tree across many boards (file with one
board per line, or an inline `b1,b2,..` list), prints one row per board
(iterations, exploitability, reach-weighted root EVs) and writes
`batch_results.json` — the raw material for multi-flop aggregate analysis.
Batch duration depends on each board, ranges, bet menu, target, and any
CPU fallback; the current single-board measurements above are not a full-set ETA. `SOLVER_BATCH_SAVE=1` also
writes `saves/batch_<board>.gto` per board.

## API

Everything the UI does is plain JSON over HTTP — scriptable:

`POST /api/spot`, `POST /api/solve`, `POST /api/stop`, `GET /api/status`,
`POST /api/node {path}`, `POST /api/exploit {path, exploiter}` (per-hand best
response + EV gain vs the current strategy), `POST /api/lock {path, mode}`,
`POST /api/unlock`, `GET /api/locks`, `POST /api/runouts {path}`,
`POST /api/range/parse`, `POST /api/save|load {name}`, `GET /api/saves`,
`GET /api/presets`.

Preflop lab: `POST /api/preflop/spot {config}`, `POST /api/preflop/solve`,
`POST /api/preflop/stop`, `GET /api/preflop/status`,
`POST /api/preflop/node {path}` (path = action indices),
`POST /api/preflop/export {path}` (heads-up flop node → postflop spot inputs),
`POST /api/preflop/save|load {name}` + `GET /api/preflop/saves` (whole-session
snapshots: config, seat models, point locks, full solver state — loading
resumes mid-convergence).

Path steps: `{"type":"action","index":0}` / `{"type":"card","card":"Ah"}`.
Browse deep links: `/#line=a1,a1,cQh` opens BROWSE at that node (`a<i>` =
action index, `c<card>` = dealt card).
