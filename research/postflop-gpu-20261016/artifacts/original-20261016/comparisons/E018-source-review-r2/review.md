# E018 revision 2 independent source review

**PASS for source; no actionable finding.** This supplement covers the explicitly authorized `game.rs` VRAM-estimate change and verifies the four previously reviewed E018 files remain byte-identical. It does not replace or modify the preserved four-file review. No build, test execution, GPU work, live-server action or production edit was performed by this reviewer.

## Additive scope

`Spot::vram_estimate_bytes` adds exactly `4 * tree.children.len()` bytes for the new immutable training child-slot array. Its multiplication and final estimate additions are checked. The existing reach count, conservative CFV staging estimate, learning-arena estimate and reserve are unchanged. The explicit addition counts all child coordinates, including unused and chance sentinel entries, matching the full-length device allocation. It does not rely on the conservative CFV estimate accidentally absorbing the extra payload.

The public estimate and the constructor's exact plan admission are separate calculation paths. Adding the same payload to each is necessary and does not charge it twice within either result. `GpuPlan::training_metadata_bytes` continues to account for the payload once through `staging_bytes`; continuation planned/observed metadata continue to count the new allocation once. No constructor, kernel, serialization, saved-state field, evaluator or control workload changes are introduced by revision 2.

The CPU-only estimate intentionally includes the payload even without the `gpu` feature, so the server can display a prospective GPU estimate. The method remains documented as rough/conservative; this review does not claim all existing estimate arithmetic or allocator overhead is exact.

## Focused validation obligation

The new `game::tests::vram_estimate_counts_unused_child_mapping_entries` builds a small river spot, records its estimate, appends three unreachable sentinel child positions, and requires an exact twelve-byte increase. Reachable nodes, hands and arena sizes stay fixed. This directly checks the full-vector accounting boundary and distinguishes it from counting only visited action edges. Run this test with the registered unit suite; it has not been executed by this reviewer.

All runtime obligations in `../E018-source-review/review.md` remain applicable. In particular, the in-process lifecycle reference uses the same changed training kernel and is not an independent original-up numerical oracle. Immutable E015-versus-E018 full-state, exploitability-bit and stopping-iteration comparisons are required. If performance qualifies, retain the frozen saved-state/action-menu/resume and bounded continuation controls. Include all mapping construction, upload, allocation and runtime compilation costs in the unchanged complete-cycle gate.

## Identity checks

The reviewer independently verified both design archives against their checksum files, all five current source hashes against the r2 manifest, and all five base snapshots against Git HEAD `54cd923bf1f0e77b12b6df0c4e872d8cbc73e04b`. The four original candidate hashes are unchanged. The CUDA candidate remains the exact D031 artifact and was independently reconstructed from the original kernel by only four child-slot expression substitutions, two parameter renames and four forwarding renames within the training-up region. The protected arena/store/frozen evaluator hashes also match the original manifest.

The r2 five-file patch SHA-256 is `c094026376165de0d51071d8ea0c94457023565e8d77801d8a594e4e335b8213`; `game.rs` SHA-256 is `fc72c39cf5bf21b5ffdad51c0b58e68daefb5895878132c4aa154247f0dbaf8c`. The adjacent manifest records all checked inputs. The original four-file review and design evidence are preserved unchanged.

Proceed through the parent's serialized build and registered qualification process with these five files frozen. This source PASS makes no runtime-equivalence, performance, statistical-significance or deployment claim.
