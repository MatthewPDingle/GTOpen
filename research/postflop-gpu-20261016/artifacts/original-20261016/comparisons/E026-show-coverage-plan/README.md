# E026 showdown coverage audit / prospective D051

The minimum missing control is a complete original-kernel differential before quantization. The existing tests are valuable integration checks but do not independently execute old128 and new256 showdown kernels on the same frozen buffers. D051 therefore compares exactly those two complete kernels, with no additional scan helper, physical shapes, speed metric or altered solver workload. Root approved148 comparison pairs/296 launches before execution.

| Existing evidence | Coverage and limit |
|---|---|
| gpu/mod.rs:1193,1204,1274 | Raw device regrets/strategy/reach across eager/capture/replay, profiled/eval interleaving, locks, warm resume, both algorithms/storage and compact/full. Both arms share compiled up_show; CFV scratch is deliberately excluded. |
| gpu/mod.rs:1403,1435,1484 | Shared/independent evaluation, royal-board ties, rake, budget boundaries, full/compact warm F32. Same compiled showdown kernel. |
| tests/gpu.rs:39,89,135,168,207,280 | Six GPU convergence/CPU-equivalence, tiny one-hand, locks, compressed, rake/isomorphism and closed-form controls; tolerance-based, not exact original/new CFV. |
| tests/postflop_state_perf.rs:11,postflop_action_menus.rs:12,postflop_resume_state.rs:36 | Frozen original state/menu/resume exact records (24+24+112). CPU raw arena/save bytes after readback; these do not expose every prequantized CFV. |
| tests/postflop_autoresearch.rs | Full compressed/F32 state fingerprints and exact convergence anchors on fixed three fixtures, not prescribed chunk boundaries or all raw device CFVs. |
| gpu/plan.rs:326,507 | Actual strength/card/boundary metadata and integer bound tests. No GPU scheduling comparison. |
| D036 full-kernel probe | Reuse explicit CUDA error conversions, immutable corpus, actual-kernel launch, input/guard bit checks and root-owned bounded runner. Its fold kernels/raw-total supplement do not validate showdown. |

D051 uses two real boards and valid root-flop hands with turn/river exclusions. A legal five-card board leaves47 cards, hence at most1081 distinct surviving hole hands.1326 is a whole-deck/resource upper bound, not a legal showdown m_o case. Empty sorted own/opponent lists remain covered while root ranges contain hands invalidated on this final board. Active full root CFV spans must be zeroed by the existing kernel; padding and count0 outputs retain guards.

The two payout nodes are actual pot10 showdown coefficients with rake0 and rake0.5: [5,-5,0] and[4.5,-5,-0.25]. Both player orientations use the same kernel ABI; training/evaluation caller and compressed/F32 lifecycle remain integration obligations. The direct kernel uses floats independently of host store encoding, so duplicating identical native inputs by storage label would add no coverage.

All generated actual inputs and precise counts must be sealed before execution. D051 can establish exactness for its finite corpus only; the fixed128 scan/barrier source and compiled PTX reviews are complementary. It provides no latency, throughput, full-cycle or acceptance claim. No new implementation or execution is included in this coverage archive.
