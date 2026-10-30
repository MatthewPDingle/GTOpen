# GPU research pass 2

Active: 2026-09-07 03:57–06:57 UTC. Baseline: end of pass 1 (`a557aede`).
The first pass is preserved in `passes/01-first-pass/` and `report.md`.

## Retained so far

E021 removes the preflop sigma arena. Recompute each own-node probability
from the same unmodified regret/strategy inputs immediately before use.
No precision, algorithm, input or convergence-target changes.

| Metric | Fresh B022 | E021 repeat | Change |
|---|---:|---:|---:|
| Six-seat VRAM | 671.09 MB | 536.87 MB | 20.0% less |
| Eight-seat VRAM | 1711.28 MB | 1409.29 MB | 17.6% less |
| Six-seat iteration | 19.437 ms | 18.120 ms | 6.8% less |
| Eight-seat iteration | 67.243 ms | 63.133 ms | 6.1% less |

Complete 2/6/8-player arena, gap and EV fingerprints match the controls.
28 unit and 5 preflop GPU tests pass. Normal-versus-tight-budget paths match
every arena/gap/EV bit after 65 iterations at six and eight seats. The manual
fallback test budgets were tightened from 700/1600 to 550/1350 MB because
the old values no longer trigger the fallback after this memory saving.
The workload and numerical assertions were unchanged; the harness change
is recorded in the append-only audit.

## Active next

Postflop action specialization; compact postflop GPU action storage with
explicit preservation of inactive initial state; preflop kernel launch and
resource tuning. All measurements and rejected trials remain in the ledger.


E022 retains common 2/3/4-action postflop update specialization. Local memory
per thread falls from 64 bytes to zero (registers 40 to 66). Fresh B023
iteration times 57.573/34.151 ms become 54.490/32.618 and 54.530/32.663 ms
on rainbow/two-tone flops. All 24 existing saved-state and EV fingerprints
remain exact, and 28 unit + 6 GPU tests pass. The retained source is in main.
E023 tests the corresponding down-sweep specialization. Controls now cover
1/2/3/4/5/11 actions, DCFR/CFR+, and locks, using original pre-specialization
CUDA source for the new reference run B025. Full readback/resume controls
were recorded before any action-arena compaction (E022R).


E023 retained: both action specializations reduce large-flop iteration time
from fresh B025 58.213/34.090 ms to 51.820/31.797 ms (about 11%/7%). Earlier
repeat was52.084/31.235ms. All 24 action-count/DCFR/CFR+/lock states match.

E024F retained after six measured refinements and one initial build failure.
GPU action arrays contain visited blocks; unchanged inactive initial values
have exact host snapshots, with bitwise zero-block compression. Packed upload
and readback share one pinned buffer; disjoint CPU scatter/encoding is parallel.
The default app uses compressed CPU storage. F32 uses direct full arenas when
the budget permits, avoiding warm-host-memory and readback regressions; tight
F32 budgets use the same validated compact representation. Packing requires
at least5% action-element savings, so small savings do not add scatter costs.

| Default compressed two-tone case | B026 full arenas | E024F | Change |
|---|---:|---:|---:|
| GPU allocation |4932.50MB|3825.21MB|22.4% less|
| Cold live host working set |5320.19MB|2310.36MB|56.6% less|
| Warm live host working set |5320.28MB|3765.89MB|29.2% less|
| Cold GPU initialization |1543.57ms|670.95ms|56.5% less|
| Warm GPU initialization |1585.71ms|987.25ms|37.7% less|
| Cold full download |925.25ms|251.91ms|72.8% less|
| Warm full download |1289.08ms|286.38ms|77.8% less|

E024E gives similar compressed results before the adaptive F32 policy. Host
working set is measured with Windows process counters after sync, in the same
fixed lifecycle; driver/allocator memory is included. It is not GPU VRAM.
Plain F32 keeps the original allocation and transfer behavior with ample VRAM.
Tight-budget F32 may trade host snapshots and scatter costs for fitting the GPU.
All112 raw-store/save snapshots plus queries and EV bits in16 cold/warm,
F32/compressed, iso-on/off resume cases match the pre-compaction reference.
Large lifecycle EV bits also match;29 unit +6 GPU tests pass, including a
warm/queried/signed-zero tight-F32-versus-full exact comparison.

Current next trials: preflop terminal seat-count specialization, followed by
postflop nonterminal CFV scratch reuse across alternate tree levels.


E025B/E025BR retained: common 2/6/8-seat preflop terminal kernels have separate
entry points selected once at initialization. Their local memory is zero;
the generic fallback retains its46-register/40-byte resource usage. Eight-seat
iteration59.263/60.351ms vsB02763.517ms; six-seat17.535/16.183 vs18.213ms.
All48 seat/menu/plain/frozen/hero+locked states and original complete large
fingerprints match; GPU equivalence and tight-budget tests pass.

E026A/E026R retained: terminal CFVs keep persistent slots for exact evaluation
reuse, while action/chance values share scratch between alternate tree levels.
No new kernels or arithmetic changes. Actual VRAM drops335.54MB on rainbow,
201.33MB on two-tone,335.54MB with isomorphism disabled. Combined default
compressed two-tone allocation3623.88MB vs4932.50MB at pass start (26.5% less).
All112 resume snapshots and24 original saved states remain exact. The fixed
postflop target still takes200/200/60 iterations with identical final values.

The initial E026 measurement was invalid because a copied source proposal
preserved an old timestamp and Cargo reused an older library for integration
benchmarks. Its raw evidence remains, but those numbers are excluded from
plots. The runner now compares compiler-input content hashes and refreshes
changed input timestamps before Cargo. E026A is the rebuilt valid measurement.


E027/E027R/E027S retained: full compressed arenas upload through existing pinned staging and encode independent nodes in parallel on download. Rainbow full sync falls from1.20-1.27s to0.33-0.34s; init1.31-1.34s to0.80-0.84s, live host RAM about0.72GB lower. All112 resume snapshots and large lifecycle EV bits exact. Server report benchmark4.914s to3.734s, identical80-iteration result and both server tests pass.


E028/E028R retained: common2/3/4-action preflop specialization lowers large iteration timings by3-5% vsfreshB030. All48 variants and full arenas/gap/EV remain exact. Generic kernels retain64-byte local reservation.

E029/E029R retained: GPU evaluation graphs with batched root downloads. Steady2-seat check0.099-0.108ms vs0.424ms,6-seat11.89-11.95ms vs13.20ms,8-seat37.22-37.24ms vs39.51ms. Startup/capture measured separately. Repeated EV bits, all48 variants, full target states at175/125iterations, private exact comparisons, GPU and tight-budget tests pass.


E030A/E030AR retained: postflop evaluation graph reuse with original eager first-check transfers. Repeated river checks0.310/0.327ms vsfresh control0.828ms; prior eager repeats0.582-0.825ms. Large flop timings near control; global timing drift rules out a broad speed claim. First-call timings remain noisy0.876/1.253ms vsfresh0.857ms, so this is retained for repeated-check benefit. All original states/EVs and stopping checks exact. E030/E030R superseded.


E032/E032R retained: preflop terminal values persist while action values share alternating-level scratch. Actual VRAM503.316MB at6seats and1308.623MB at8seats, another33.55/100.66MB below B032. Full arenas/gap/EV,48variants, target states and tight-budget fallback exact. Combined reduction versus pass start25.0%/23.5%.


E033/E033R retained: broadcast terminal masses only in the generic seat kernel. New frozen large9-seat benchmark1.825Mnodes:251.8/252.7ms per iteration vs290.7ms; checks161.8/162.0ms vs197.1ms. Seven-seat iteration12.33ms vs13.09ms. All7 full2/3/5/6/7/8/9 fingerprints and48variants exact. Direct all-seat specializationE033B was slower, so rejected. E034 postflop card-run loops preserved all states but regressed runtime and were rejected.
