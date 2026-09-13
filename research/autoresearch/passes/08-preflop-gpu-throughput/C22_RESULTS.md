# C22: separate kernels pass standalone qualification

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

Remaining: integrate real terminal metadata, cohort aliases, scratch allocation
and tiled dispatch; qualify complete arrays, saved games, graph/eager execution,
zero recovery and stop behavior; then measure complete learning/check workloads.
The planned 834 MiB extra large-case allocation and 18,688 additional launches
could still erase the arithmetic benefit. No full solver timing, convergence
claim or production deployment is justified by this stage. Normal constructors
remain unchanged; the new module is compiled only for manual research tests.
