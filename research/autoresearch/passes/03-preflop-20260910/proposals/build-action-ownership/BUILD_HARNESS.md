# Standalone frozen build/load harness

`preflop_build_research_bench.rs` is a new standalone solver example. It does not
change either existing frozen harness. `build-harness.json` pins its source hash.
Only rustfmt parsing was performed here; the parent builds both executable
versions and runs them in its measurement slot.

```text
preflop_build_research_bench INPUT MODE EQ_CACHE FIT_CACHE OUTPUT_ROOT ROUNDTRIP_OUTPUT
```

Use absolute paths and a new ROUNDTRIP_OUTPUT for each invocation. Its parent and
OUTPUT_ROOT must already exist; existing outputs, `.tmp` paths and inputs are
protected. A tiny private `.equity.bin` copy is created beside the round-trip
save, so the native cache loader cannot write to the pinned source cache. Both
source caches are checked unchanged after verification and their fingerprints
are reported. The supplied fit path is installed through REALIZATION_FIT;
calibrated games must report a successfully loaded fit.

`fresh-from-config` accepts config JSON, `{config: ...}` JSON, or a native save
whose config is extracted before timing. It times only `PreflopSolver::new`:
zero arenas, current default model, all solver seats. It does not transport
native-input profiles, iteration or payoff-model metadata. `load` requires a
native save and times the complete native loader, retaining that saved state.
These modes are separate baseline/candidate comparisons.

There is one timed operation per process. The first `BUILD_BENCH` record reports
that duration. Everything afterward is untimed verification: full topology
fingerprint, typed config/profile hashes, retained action Vec/String bytes, a
native round-trip save and streaming arena verification with a 1 MiB buffer.
The arena fingerprint includes every actual native f32 byte, array length and
optional hero-backup arena. It avoids `arena_snapshot`'s extra multi-gigabyte
copies. Point locks are sorted by node for a stable typed hash; frozen and hero
metadata are reported separately. Fresh arenas are checked to contain zero bytes.

Require process success AND the final `phase=verified` record. A timed record
alone is not a passing run. Compare topology/config/profile/arena/lock hashes,
iteration and model across executable versions before comparing timing. The
capacity metrics can differ intentionally and must be assessed separately.

The harness reports FNV-1a64 fingerprints, matching the existing research style;
the parent also records external SHA256 hashes of source inputs, executable and
source commit. Native round-trip files remain in the caller's research directory
for review or controlled cleanup. The untimed write/hash can take several seconds
on large fixtures; never include it in claimed build/load speed. Alternate five
fresh-process pairs on the same pinned inputs/caches and report paired dispersion.
