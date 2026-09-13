# R03 qualification sequence

The first normal-GPU integration test passed on source version 1. Version 2
adds only qualification instrumentation: full-work public-selection timing and
R02 exercising the shared production selection helper directly. Preserve both
source versions and the first test result. Source remains frozen during tests.

Run bounded-address/PTX, expanded cohort, exact-reuse and selection/failure
suites. Freeze that research-capable test executable before other feature builds.
Use all four saved-game modes (explicit C14, public adaptive, ordinary, forced
fallback), both fixture sizes, six sweeps/checks, save/reload and a seventh sweep.
Compare metadata, full arenas and every checkpoint against existing C14/R01.

For integration overhead, compare public adaptive selection against explicit
C14 in three alternating pairs at both sizes, using the full six-step timing
including initialization. Require no more than 3% median complete-work regression
on either fixture; no new speedup is claimed. Compare exact outputs and plans.
Keep rejected or failing runs; do not add repetitions to seek a pass.

Run native GPU tests, the normal-feature production selection test, default
solver regressions and server tests/build. Add server source files as explicit
inputs for server qualification. The real isolated-server run remains required.
