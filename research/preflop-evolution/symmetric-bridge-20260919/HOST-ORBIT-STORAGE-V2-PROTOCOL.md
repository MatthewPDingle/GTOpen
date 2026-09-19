# Storage-only prototype: raw fallback for non-isomorphic plans

Registered after the first host-storage diagnostic stopped at its first rainbow case. Preserve that failed build/run and all eight completed two-tone/monotone rows. They restored exactly and resumed exactly. The failure was a prototype layout assumption: without active suit isomorphism, the existing planner retains full array offsets, including unreachable gaps, so visited blocks do not sum to the complete allocation.

Version 2 keeps the original 24 cases, every bitwise restoration/resumption requirement, and original timing/resource limits. The only algorithmic adjustment is explicit raw-array storage and raw restoration when `plan.iso_active` is false. That branch saves no array space and preserves unused bits too. Active isomorphic plans keep the original canonical-block gather and sibling materialization with the same complete packed-length assertion. No threshold change and no compact chance traversal.

Separate source: `crates/solver/tests/continuation_host_orbit_storage_v2.rs`. Separate build/runtime/results use `host-orbit-v2-*`; do not overwrite version 1. A passing tiny-fixture result still requires repeated switching, fuller trees, forest metadata accounting and performance measurements before integration or larger training.
