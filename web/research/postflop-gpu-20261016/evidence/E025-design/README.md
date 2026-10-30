# E025: align only physical CFV rows to 128 bytes

Prospective candidate against accepted E020. Only `gpu/plan.rs` and `game.rs` change. `GpuPlan.nh_max` becomes `max(nh).div_ceil(32)*32`; the separate conservative public VRAM estimate uses the same rounding. All valid two-card hand ranges have at most1326 hands, so this arithmetic is bounded. Real `nh`, hand-loop limits, reach and learning-arena layouts, CUDA bytes, shared reservations, launches, graph and continuation ownership remain unchanged.

The existing river_bounds test retains its three actual boards and both isomorphism settings and now checks true counts, aligned physical rows, disjoint logical payloads, in-bounds CFV slots, evaluation-root spacing, staging-byte growth and conservative admission. No unit test was added: the GPU-only inventory remains84 passed/4 ignored, subject to root's actual execution.

Existing consumers already derive CFV allocation/offsets, four evaluation roots and continuation capacity from nh_max. Added device payload is4*cfv_blocks*delta +16*delta bytes. The existing budget gates receive the new staging size. A near-limit construction may now reject or select compact storage; this is an explicit tradeoff, not an unchanged-admission claim. Narrow ranges can have a much larger percentage padding cost. Root must retain budget-minus-one/exact-budget, warm F32, paging/stored-capacity checks in conditional broader qualification.

Registered physical strides: rainbow319→320, two-tone320→320, river280→288; wide-turn holdout1128→1152. Alignment may improve CFV memory access or cost more allocation/zeroing, and one primary fixture is structurally unchanged. No speed claim follows from source feasibility. CUDA arithmetic/order is unchanged but exact native state and convergence still require the frozen primary and later broader controls.

The independent all-use audit is pinned below. Preparation performed only byte/source checks and read-only git apply --check; no production edits, compiler/native tests, GPU runs or activation. Both candidate sources are frozen by manifest.json. Root alone activates and executes after independent source/script review.
