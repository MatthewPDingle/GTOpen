# C22: separate kernels rejected after complete solver timing

The complete large workload took **53.23675 seconds with C14 versus
108.8617684 seconds with C22**, a 104.49% regression. Warm learning was 91.20%
slower and checks 131.55% slower. Every saved checkpoint and final arena
fingerprint matched. The first timing gate failed; no repeat pairs or retention
regressions were run. All runtime integration has been removed, leaving the
standalone diagnostic and archived experiment evidence.

The extra intermediate memory transfers and dispatch schedule did not pay off.
This comparison cannot separate the contribution of memory traffic, cache
behavior and launch/scheduling costs; no hardware-counter attribution is claimed.
D18's source-arithmetic savings remain valid counts, not runtime predictions.

## Integration and complete-work evidence

All nine solver tests passed, covering 3..9 seats, batch5/32, fixed/learning
policies, terminal outputs, zero-range recovery, strategy/regret arrays,
eager/graph equivalence, already-requested stop behavior, partial allocation
recovery and tile3 dispatch. The integrated producer uses 40 registers and
44 bytes of shared metadata with one initial barrier; the consumer uses
38 registers and no shared memory. Neither spills. All 20 original exact-reuse
module entries remain unchanged. The earlier standalone module has 18 entries.

Both saved allocation inventories exactly match D18: extra 285,546,496 bytes
small and 874,496,000 bytes large, preserving batch32 and original caches.
Full qualification took 205.782 seconds including compilation; its tests took
71.24 seconds. Layout runs took 2.125 and 9.125 seconds. Each timed process
includes construction, six learning sweeps and accuracy checks, and final
CPU synchronization. The 529,900,514-entry arena fingerprint remains
`27b4d2870b404cae`, and all six gap/EV/iteration checkpoints match C14.

The preparation script initially used the platform-default text encoding when
reading gpu.rs. It stopped before any GPU run; the one partial file edit was
verified and restored before rerunning with UTF-8. No runtime test failed.

Independent audits: `check_c22_integration.py`, `check_c22.py`;
`raw/c22-integration-verified.json`, `raw/c22-timing-screen-verified.json`.
Hash-gated restoration: `restore_c22.py`, `raw/c22-restoration.json`.
Integrated source: `artifacts/c22-v2/`. Frozen complete-work executable:
`target/c22-benchmark-frozen.exe`, SHA256
`debb14c81ff28e235ebea25a6b277bf00f8393bb3328c649f304e9f69ad64c2e`.

Actual mid-sweep interruption and save/reload continuation were not newly
qualified for this rejected candidate. There is no convergence improvement,
retained speed gain or deployment. Qualified R03 remains unchanged.

## Earlier standalone qualification

The producer/consumer prototype matches the retained evaluator bit for bit
in all 5,040 registered cases: 3,407,040 hand values and 398,566,240 scratch
slots checked. It uses no per-sample block barriers or shared memory. Producer
register use is 28-40; consumer use is 22-32. Neither reports local spill
allocation. This admits full solver integration, not a measured speed gain.

The test rotates partial terminal tiles, nonzero output offsets, inactive
terminal holes and aliased/distinct opponent rows. Every unused sample,
quadrature, rank-group and terminal slot retains its poison value. The real
fixed deck's maximum group count is 104; synthetic all-distinct maps exercise
169 groups. All 18 original cohort-module kernel entries match the retained
R03 PTX exactly.

The guarded build/test completed in 138.594 seconds, with 6.84 seconds in the
test itself. `check_c22_screen.py` independently checks source/input/executable
hashes, reconstructs the case set and slot totals, compares the original ordered
product arithmetic, and inspects original entries and candidate resources.
Its initial audit expected 20 original entries (the exact-reuse module count);
the actual cohort module has 18. The assertion was corrected after comparing
the complete entry sets and contents against retained R03. No kernel, test,
resource gate or numerical comparison was changed.

Frozen standalone executable: `target/c22-pipeline-frozen.exe`.
SHA256: `a8ca390f6952a2d8f266e09e7779125abbbcdfa75523183151b76edbf7e53611`.
Evidence: `raw/c22-screen-verified.json`, `raw/c22-pipeline-v1/`, source archive
`artifacts/c22-v1/`, and the immutable `C22_PROTOCOL.md`.

The standalone stage admitted integration only. Its evidence remains archived
even though the later complete-work timing rejected the approach. Normal
constructors remain unchanged; the retained diagnostic module is compiled only
for manual research tests.
