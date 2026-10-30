# E014: direct-three-action training-up entry point

Candidate only; no build, solver execution, exact-state qualification, or speed result was performed by the builder. Starts from accepted E004. E012/E013 host encoders and E005 direct2 work are not included.

D021's isolated resource probe measured direct3 at 40 registers and zero local bytes per thread versus dispatcher 66/64; theoretical 128-thread residency was 12 blocks per SM versus 7. Resource counts justify testing this bounded hypothesis, not a performance claim. E005's failed direct2 screen remains relevant prior evidence.

For each action level with at least 4096 nodes, stable-partition NA3 nodes before all other action counts. Preserve each bin's original order, all membership, node IDs, child order, data/reach/CFV offsets and aggregate level spans. Small levels remain unchanged. Store only one host-side u32 prefix count per level in GpuPlan/GpuSolver; starts derive from the existing aggregate spans. This metadata remains with its solver and is not part of paged mutable workspace swaps.

Only training-up dispatch changes: launch the nonempty NA3 prefix through up_action_3, then the nonempty remainder through the original dispatcher, on the same stream with 128 threads. Both launches contribute to existing profile bucket 6. Down and evaluation still use the complete aggregate span. Homogeneous eligible levels still use one launch. The constructor loads the added entry point before any iteration or graph capture, including resumed solves.

Production kernels.cu is byte-identical to D021/candidate.cu, SHA256 `cfcbaff4ed6815fd6d27ffd2b2d3bb95fba64c0e56bee96308e64df5605a8704`. This retains the complete accepted kernel source as an exact prefix and appends the inspected direct3 wrapper calling unchanged up_action_impl<3>. No discount or numerical arithmetic changed.

Retained-host capacity includes the new full-plan prefix-count vector. Device allocations, uploaded metadata, and VRAM accounting do not grow. Complete-cycle qualification must include partition allocation/work and new function compilation/loading/capture overhead.

Builder-added plan tests cover empty and small spans, 4095/4096/4097 thresholds, reverse-order stable membership, untouched outside guards, arbitrary action counts, and all3/no3 cases. Existing real-plan checks now verify prefix membership/order while retaining same-level CFV disjointness, adjacent-level dependency and cached-terminal invariants for isomorphic/nonisomorphic plans. Root owns execution; separate supplemental lock/resume controls are prepared by another agent.

Owned files: gpu/plan.rs, gpu/mod.rs, gpu/kernels.cu, gpu/continuation_capacity.rs. No Cargo build, kernel launch, solve, deployment, or commit by the builder. Syntax-only parsing, whitespace checks, source identity checks and read-only diff review precede handoff. Acceptance remains pending root's exact-state and complete-cycle comparisons.
