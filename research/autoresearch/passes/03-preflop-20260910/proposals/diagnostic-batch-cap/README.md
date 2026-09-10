# Optional matched-batch diagnostic

Generated from optimized `739c68d:crates/solver/src/preflop/gpu.rs`, not the active file (which may currently be the original benchmark wrapper). `gpu.rs` is the entire proposed optimized snapshot; `batch-cap-30.patch` contains only the constructor diagnostic. No active source edits, builds, or hardware runs by the proposing agent.

Opt in with `PREFLOP_MW_DIAGNOSTIC_BATCH_CAP=30`. Leave it absent for unchanged constructor behavior. No other values are accepted. In a legacy/non-multiway game this branch is not entered, so the variable has no effect.

The original planner runs first, including its minimum one-particle fit and normalization decision. The cap then replaces batch B with min(B,30), and replaces CDF cache length with `slots * 170 * min(B,30)` f32 values. The existing `need += fixed + normalized_bytes + cache_len*4` sees the revised length exactly once. No stale 32-particle allocation or budget charge remains. Later HU-cache admission sees the actual reduced need, so record that mode as well.

It cannot force a 30-particle batch when fewer fit: check the diagnostic's `actual_batch`, not just the requested cap. If the original comparison ran batch30, the optimized paired run must actually report30. All1024 particles remain; 35 passes are evaluated, final count4. The sample/product arithmetic within a batch, order, and kernel source are untouched. Compared with the default32 boundary, changing the batch intentionally changes where existing floating-point scaling/addition occurs; it is a numerical control, not an optimization to ship.

Set `PREFLOP_GPU_LAYOUT_STATS=1` to record full final memory plan, forced bytes, HU cache, compact/normalized flags and batch. The cap prints planned vs actual batch and actual CDF/normalization bytes even when the full layout flag is absent.

## Bounded validation suggested for the parent

1. Build from the frozen optimized snapshot plus this patch. Unset flag: constructor plan and arena fingerprint must match the optimized control.
2. Set flag30: use the same frozen modeled INPUT and original23GB comparison arguments, verify actual30, then compare full arenas and diagnostics against the original30 result. Equal boundaries remove one known cause of rounding differences; they do not guarantee exactness if another optimization changed arithmetic. Report any mismatch rather than relax the comparator.
3. A smaller natural batch (e.g.27) must stay27, and the one-particle minimum-fit case must stay1 with its prior normalization decision. The cap should not turn an existing minimum-fit rejection into an accepted run.
4. Invalid flag values must fail before GPU allocation for a multiway game. Run sequentially: environment changes are process-global.

For memory accounting, planned32→30 releases exactly `2 * slots * 170 * 4` CDF bytes. Normalization allocation is unchanged; a newly affordable HU cache could consume some of the freed budget. This comparison addresses numerical batch parity. Memory-pressure effects remain a separate reason original23GB can run slower, so do not describe the full timing ratio as a pure kernel speedup.
