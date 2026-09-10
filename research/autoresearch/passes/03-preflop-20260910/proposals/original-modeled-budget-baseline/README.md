# Fair original GPU baseline for modeled-player comparisons

Frozen GPU source is `1b8fc3f04fe2bc3c000346368f8da346738d1c45`, plus only the
same forced-policy device-allocation accounting used by the optimized candidate.
No active checkout edits, builds or hardware jobs were performed to prepare it.

Files:

- `gpu.rs`: original GPU implementation + forced-memory fix + optional layout log.
- `gpu-budget-only.rs`: identical corrected baseline without the optional log.
- `kernels.cu`: **byte-for-byte original** kernel source from the frozen revision.
- `forced-budget-only.patch`: accounting correction against original gpu.rs.
- `layout-diagnostic.patch`: optional diagnostic applied after accounting fix.
- `combined.patch`: both changes against original gpu.rs; do not apply twice.
- `manifest.json`: source/revision hashes and checked invariants.

Use the original kernel file together with this original GPU wrapper. Current
optimized kernels have different signatures/layout assumptions and are not a
valid partner for the baseline wrapper. The optional log does not alter kernels.

## Precisely what changes

The three helpers `forced_storage_bytes`, `forced_policy_elements` and
`reserve_forced_vram_mb` are copied verbatim from the current corrected GPU
source. The estimator counts each node's actual `forced_sigma` length, streaming
one node policy at a time. The constructor reserves the actual concatenated
forced allocation **before** choosing the multiway particle batch or optional
HU cache. The empty-policy one-float allocation is included, as in the candidate.

The original forced_sigma calls, selected policies, hero/frozen/lock precedence,
policy concatenation, uploads, discounted strategy/regret math and kernel source
are unchanged. The original union CDF layout, direct normalization, original
terminal loop and all original launch dimensions remain. There are no active-
slot, compact-CDF, normalized-reach, geometry, base-hoist or O-specialization
optimizations transplanted into this baseline.

This correction can legitimately lower the original particle batch, disable an
optional HU cache or reject an over-budget modeled tree. Its previous planning
silently omitted forced allocation, so preserving that old choice would not be
a fair equal-budget comparison. Do not increase the baseline budget just to hide
the effect; compare same hardware budget and report the resulting layouts.

## Optional layout evidence

`PREFLOP_GPU_LAYOUT_STATS=1` prints one `preflop gpu layout: ` JSON record per
constructor with model, budget/planned need, forced nodes/elements/bytes, particle
batch, union CDF slots/allocated bytes, and HU cache slots/allocated bytes.
The baseline explicitly reports compact=false and normalized=false. An absent
flag or any value other than1 prints nothing. This is host metadata only.

Use frozen, identical input sessions or deterministic fresh fixtures for both
arms, including profiles/hero/point-lock settings. Record model identity:
`coupled_deck_v1` and `legacy_product` must be separate comparisons. A frozen
seat playing its stored sums is not automatically a forced-buffer allocation;
the exact helpers preserve the existing distinction.

For same-batch candidates, exact terminal/arena/gap/EV checks remain the preferred
test (subject to the separately documented candidate normalization behavior).
**Different particle batches change f32 accumulation order:** retain all1,024
particles and report numerical errors under the established tolerance rather
than requiring an impossible same-bit claim. Keep batch changes visible in the
benchmark result. Also report any HU cache or direct/normalized path differences.

The generator verifies that policy construction is unchanged, all source after
the original GPU initialization expression is unchanged, and original kernels
are byte-identical. These are textual checks; compilation and runtime parity
remain for the parent to perform in its scheduled isolated comparison.
