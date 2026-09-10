# Minimum-memory normalization fallback proposal

Proposal only, generated from the current isolated normalized-reach source. No worktree/main source changes, compilation, GPU jobs, or server interaction. `combined.patch` includes implementation plus pure planner tests; separate `fallback.patch` and `tests.patch`, full proposed sources, and source hashes are also provided. Read-only patch applicability passed.

## Selection policy

The new pure `multiway_batch_plan(available_bytes, slots)` sees the bytes remaining after existing coupled metadata and common solver storage. It first verifies that the original one-particle CDF cache fits. If not, it returns no plan and the existing same-model CPU fallback remains applicable.

When `normalized_bytes + one_particle_bytes` fits, retain normalization and choose the largest batch up to32 that fits after reserving it. Otherwise retain GPU execution with the original direct-division CDF kernel. This is deliberately not a general throughput selector: even if the direct path could fit two particles and the normalized path only one, the preferred normalized path remains selected.

The preferred kernel's source/body is unchanged. A separate `pf_multiway_cdf_direct` entry point contains the old plain f32 division and otherwise identical scan/gating code. Select the function and input-buffer pointer at construction/capture time, so the fast kernel pays no per-thread flag branch or extra register cost. Skip the normalization launch on the direct path. Existing active gating, counterfactual preparation, samples, precision, and all terminal arithmetic remain unchanged.

Both paths have fixed allocations/launch dimensions for the lifetime of the engine and retain graph replay compatibility. Normalized storage is not allocated at full size on the fallback path; it keeps only the customary single-float disabled-buffer placeholder, covered by the existing common allocation safety reserve. The planner's minimum coupled cache requirement is exactly the pre-normalization one-particle requirement.

The constructor prints a concise direct-CDF fallback diagnostic. Public preferred VRAM estimation remains the normalized32-particle recommendation rather than being confused with the lower actual-fit boundary.

## Added planner tests

Two pure tests need no CUDA context. They cover:

- One byte below/at the old one-particle minimum.
- One byte below/at the normalized minimum.
- Continued preference for normalization when direct division could fit a larger batch.
- One byte below/at the32-particle cap and excess budget above it.
- Allocated cache/normalization bytes staying inside the supplied allowance.
- Zero-slot rejection and multiplication overflow rejection.

They have not been compiled or executed. Existing GPU equivalence tests must exercise the direct entry point before retention; planner correctness alone cannot validate the new kernel binding/input pointer.

## Practical boundary benchmark

Use a small-to-medium coupled fixture whose normalization allocation exceeds roughly2MB (at least about3,000 slots), so the server/constructor's integer-MB budget can land safely inside the direct-only interval. Avoid the user's large eight-seat tree: a one-particle batch on that tree would require1,024 particle-loop repetitions per seat and make this boundary check unnecessarily expensive.

Determine counts from the built frozen fixture without starting a server. Let `B` be common solver bytes plus fixed coupled metadata (excluding CDF scratch and normalization), `P = slots*170*4`, and `N = slots*169*4`.

1. Pick an integer-MB budget strictly inside `[B+P, B+P+N)` with a margin for float-to-byte rounding. The patched constructor must choose `normalized=false`, batch1. The pre-normalization control must also fit at this same budget.
2. Pick a budget just above `B+P+N`, but below `B+2P+N`. It must choose `normalized=true`, batch1. Comparing at the same batch size isolates cached versus repeated division from batch effects.
3. On separately created solvers from exactly the same state, compare all-hand terminal values and complete strategy/gap/EV fingerprints after a short fixed iteration count. Include both learning and ungated evaluation. Record actual allocation and printed path/batch choice.
4. Optionally time a few warm iterations and one checkpoint at each budget. This is a fit/correctness regression check, not an argument to prefer the direct path globally.
5. Keep byte-exact minimum checks in the pure planner tests. Physical free VRAM, safety reserve, and integer-MB API resolution make hardware tests at a one-byte boundary inappropriate.

For algebraic budget calculations near the threshold, use the same `minimum_vram_mb` and fixed-byte expression as the constructor rather than estimating from process VRAM. If no integer-MB value lies in the direct-only interval, slightly enlarge the fixture instead of adding live-GPU load.
