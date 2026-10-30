# D052 independent source review

Source-feasible and distinct within the scoped history; no measured gain or native validation.

The completed read-only audit found no continuation/save-layout blocker for a separate physical reach pitch. Paging and stored continuation use actual slice lengths, swap whole scratch buffers and drain before release. Saved/parked state contains only regret and strategy arrays.

Physical pitch must be used consistently in plan bytes, the two reach allocations, the public estimate and `continuation_capacity.rs:67`. The existing stored capacity check does not compare predicted workspace bytes with actual lengths. Extra payload is `4 * sum(reach_blocks[p] * (pitch[p] - nh[p]))`; constructor zero-fill, retained workspace and budget/layout decisions can therefore change.

Keep all logical hand counts, arithmetic/indexing outside reach row addresses and root slot zero unchanged. E015's second sweep passes `down_nh1=0`; derived zero pitch is harmless only because the original logical loops perform no player-1 reach accesses. Existing same-layout raw-reach lifecycle tests do not prove cross-layout raw-buffer equality.

No direct duplicate appeared in the scoped ledger/design-note search. Rejected E025 was CFV-only alignment; D038/D039 kept the original reach stride. D049 and E026 are distinct rejected pointer/launch changes, not support for a gain here. Exact finding locations and limitations are in `report.json`.

This directory only preserves the completed source review. No production changes, build, native/GPU run, new experiment or measured speed claim occurred.
