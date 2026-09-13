# C23: static boundary tables pass standalone GPU qualification

The compact writer and reader preserve all tested results exactly. This admits
full-solver integration; it is not a speed result or a retained improvement.
R03 remains the best qualified build and port 56708 remains unchanged.

## What changed

The fixed sampled-rank table identifies which cumulative prefixes the evaluator
actually reads. The writer keeps every original scan addition and carry, but
stores only those prefixes. The reader uses static group and sample offsets.
There is no value-dependent compression, sample removal or precision change.

For the real table, the maximum 32-sample row is 2,160 floats rather than 5,440.
D19 separately establishes 60.29% less CDF allocation and 65.77% fewer logical
prefix stores. These are storage counts, not measured GPU traffic or speed.

## Evidence

- The guarded build and test completed in 154.078 seconds, including compilation.
  The GPU test itself took 19.53 seconds.
- Five rank tables, twelve input-pattern passes, compact/noncompact slots,
  gates, aliases, zero mass, inactive rows, four starting samples and seven
  batch/count combinations cover 6,720 prefix cases.
- 9,364,968 required prefixes match the original writer bit for bit. All
  63,813,144 unused compact slots remain poisoned as expected.
- The readers consume those GPU-produced tables. All 94,080 paired hand vectors
  match, comparing 15,899,520 hand values over 2-8 opponents and zero/nonzero
  initial accumulators. Output tail guards remain untouched.
- The independent checker rebuilds every synthetic and real rank map, checks
  case counts and storage accounting, reconstructs the appended kernel source,
  verifies source/input/executable hashes, and compares real maps with D19.
- The original 20 PTX entries are unchanged. The compact writer uses 25
  registers (original 26), and compact readers use 33-40. All have zero local
  spill storage and zero shared memory, passing the registered resource gate.

Frozen executable: `target/c23-static-frozen.exe`.
SHA256: `79556d44ad53ac6d3dfc388764d1764028e06b0d6306a6b734f24c64592640cc`.
Audit: `check_c23_screen.py`; immutable result: `raw/c23-screen-verified.json`.
Source archive: `artifacts/c23-v1-source-map.json`.

## Next gate

Integrate into a fresh private research engine, preserving the retained cohort
and duplicate-reuse choices. Large old/new CDF allocations cannot coexist within
the budget: release the private old table before replacing it, and never publish
a partially configured engine. Qualify full learning arenas, checks, graph/stop,
saved continuation and allocation recovery before timing. The first full large
pair must improve by at least 1% to extend to the registered retention pairs.

No complete-work timing, convergence improvement or deployment is claimed here.
