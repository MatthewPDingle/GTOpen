# D044 constructor diagnostic source

Source-only temporary instrumentation against accepted E020 game.rs (immutable E023-design/base/game.rs). This is not an optimization, ranking deduplication implementation, numerical harness or acceptance experiment. Root alone may activate, compile or execute a separately frozen protocol. No checkout source was changed during preparation.

## Minimal insertion scope

Five insertion blocks leave every original byte, statement, allocation, ranking call and evaluation order intact. Removing those blocks exactly recovers the base. Four Instant::now starts and four elapsed reads measure:

- tree_build: the existing TreeBuilder::build_with_options call, including its validation and allocations.
- river_table: the existing build_river_table call, including Rayon scheduling, evaluate7 calls, sorting, table allocations and internal cleanup. This does not isolate duplicate ranking from other table work.
- suit_symmetry: the existing symmetry construction through identity permutation reordering, including its maps and tables.
- constructor_us_before_logging: new_impl entry through completion of symmetry, excluding diagnostic output, the final Spot return and subsequent cleanup.

All are finite nonnegative host-wall microseconds. Duration conversion cannot overflow f64 at Rust Duration's finite range. There are no new loops, census/ranking calls, heap-allocation expressions, CUDA calls, waits or environment reads. Formatting uses stack arguments and one locked stderr writeln with ignored I/O error; no format!/JSON allocation or eprintln panic path is added. Standard I/O initialization/locking may have runtime cost; zero instrumentation cost is not claimed.

## Record and identity

One `SPOT_CONSTRUCTOR_PROFILE ` JSON record is attempted after successful symmetry construction, immediately before Ok(Spot). The instrumentation field explicitly says D044_unconditional_source_only: the compiled diagnostic is always on and has no environment gate. Failed constructors return as before and emit no record. An output failure leaves solver behavior intact but makes diagnostic marker validation fail. Other Spot users may emit other counts; only the fixed primary test expects exactly three records.

schema.json specifies fields and the three expected board masks, hand lengths and node counts from immutable E020 B071. The candidate reads existing lengths/mask only; it does not encode fixture names or build a census. The assessor should associate each marker between fixture_start and build_complete, validate the fixed board plus existing build_complete hands/nodes, require three markers and all finite nonnegative spans, and reject incomplete/malformed instrumentation. The frozen evaluator and CUDA remain unchanged.

## Residuals and interpretation

Constructor minus the three stage spans is a diagnostic residual for earlier validation, parsing, hand/mass/cross-index/weight setup and timer/gap overhead. Outer build_ms*1000 minus constructor_us_before_logging additionally includes final return and destruction of constructor temporaries, Arc and Solver::with_storage setup/allocation, other evaluator setup and marker/timer overhead. Neither residual is an exact allocation timer. Do not add either residual to an already inclusive parent span as an independent cost. Logging is outside the reported constructor but remains inside the original complete-cycle build boundary.

The river_table span is an upper bound on its directly removable work, not evidence that all of it can be removed. Only credible repeated measured ranking headroom would justify a later separate overlapping-combo census. No such census or deduplication is included. The full build gap may instead belong to tree construction, allocation or other residual work; this diagnostic is intended to distinguish those cases.

The separate prospective six-run procedure is expected to use D044B1/P1, P2/B2, B3/P3, retain all three fixture records per diagnostic run and all 18 complete non-timing result states plus 138 convergence records. An absolute 10% outer-suite perturbation screen is only a prospective diagnostic-usefulness check, not a bound on component bias or native kernel shares. Diagnostic cycles are never performance acceptance. No additional extension, retuning or exclusion is authorized by this source artifact.

## Apply/remove and preservation

After verifying all accepted source identities, root may check/apply candidate.patch from the research checkout, then verify the candidate game.rs hash. Root must first freeze and review its execution scripts and hold the existing serialization lock during build/native work. The candidate owns only crates/solver/src/game.rs; no frozen evaluator, tests, GPU source, input or dependency changes are needed. Removal is the reverse patch or exact archived accepted game.rs after verifying no intervening source changes. Keep this archive and every failed outcome unchanged; any repair is a new additive revision.

Preparation performed byte-identity checks, explicit UTF-8/LF preservation, fixed card encoding verification and read-only git apply --check --whitespace=error-all against restored E020. No Rust build, native test or GPU execution occurred. Compilation and runtime validation remain pending.
