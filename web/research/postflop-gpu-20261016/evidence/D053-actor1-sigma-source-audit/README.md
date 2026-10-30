# D053: actor1-only cross-pass sigma cache

**GO for one bounded experiment if root authorizes it; no predicted gain.** This source-only audit prepares no candidate/probe/harness and runs no compiler, solver or GPU. All162 accepted E020 sources remain unchanged. The earlier whole-cache deferral and actor1 scope clarification were unmeasured prioritization, not a closed failure to rescue.

The concrete candidate is one f32 cache at the finalized GPU actor1 action-arena offsets. Full p0 down produces each unlocked actor1 probability; p0 up changes only regrets0; E015's second down has nh1=0 and leaves the cache intact; up1 consumes it. Actor0 retains the original path. Standalone p1 always has a full producer, so root changes and continuation swaps do not require a cross-iteration validity scheme. Preserve ordered g0/g1 launch even when first use captures graphs. Evaluation disables cache writes because it normalizes strategy sums. Locks bypass cache reads, and subsequent full training refreshes after graph recreation. Symmetric projection/upload changes learning state, so scratch is regenerated, never projected or serialized.

The useful removal is actor1 up's ordered positive-regret sum/rc-fill loop and normalization divisions. Up still reads old regret for its sign-dependent discount and r*d update, reads child CFVs, accumulates values and writes both learning arrays. Common small-arity compiled code already shares sigma within up; two source expressions are not two guaranteed hardware divisions. Reuse the old rc register slots for cached sigma if practical, rather than adding another array; the generic case may reread sigma. Preserve all original floating expressions/order and compiler options. A cache store/load does not excuse compiled/native exactness checks.

Down's uniform child reach stays **pr/na**. Cache **1/na** separately; never recover sigma from child reach or skip production when own reach is zero. Positive-part sum, threshold, action order and original reach computation stay unchanged. Locked slots may stay unwritten only because the locked consumer never reads them.

| Fixed fixture/layout | Actor1 elements | Added scratch bytes |
|---|---:|---:|
| Rainbow full |185,172,163|740,688,652|
| Two-tone compact |110,745,280|442,981,120|
| River full |4,480|17,920|
| Two-tone full-layout bound |185,752,640|743,010,560|

The first three are preserved D012 constructor counts; its GpuPlan source hash exactly matches E020. Full bounds are corroborated by E020C1 arena fingerprints. Added payload is4*A1, about27.1% of current regret+strategy payload on these flops. One write plus one read of each unlocked cached element represents1,481,377,304 and885,962,240 logical bytes per paired flop iteration; this is not measured DRAM traffic. Extra allocation/zeroing, global traffic, cache pressure and compiler resource effects can erase savings.

## Smallest complete edit surface

Seven production files: `gpu/kernels.cu`, `gpu/mod.rs`, `gpu/plan.rs`, `game.rs`, `gpu/continuation_paging.rs`, `gpu/continuation_storage.rs`, `gpu/continuation_capacity.rs`. The report gives exact sites. Treat sigma1 as the eighth transient shared continuation workspace buffer, using actual finalized GPU offsets/lengths; parked compact StoragePlan offsets may differ from full traversal. Update take/swap/absorb/length/error-drain accounting and one extra parked dummy, but keep four stored learning arrays and all save formats unchanged.

Admission must include4*A1 once. A compact plan may be expanded for F32: computing full-fit from compact cache bytes undercounts; explicitly use full A1 in that decision, then allocate from the finalized layout. Public estimate adds4*tree.data_size[1]. Existing fixed11-component capacity examples need12 components (eight shared plus four compact), otherwise a zip can omit the new buffer. The two internal host/SSD paging test helpers also hard-code seven mutable buffers. These are required compatibility edits, not new evaluation workloads.

D045's selected up-action spans were about1.189/1.307ms, but are mixed actor launches and do not isolate normalization or full-solve share. Historical preflop E021/E021R moved in the opposite direction: removing its full sigma arena reduced six-player iteration19.437->18.194/18.120ms and eight-player67.243->63.324/63.133ms, with lower VRAM. The exact inspected ledger rows and git blob identity are archived here; this is counterevidence, not a current postflop prediction.

A bounded exact producer/consumer check must precede primary: threshold/uniform and zero reach, both algorithms, locks, generic arities, warm capture and standalone refresh. Then use the unchanged fixed primary gate before expensive broader work. Only a primary pass justifies full original raw-state/F32/menu/resume/continuation workspace and capacity checks, unchanged holdout and cumulative qualification. No extra resource non-regression gate, conditional rescue or new broad framework is proposed. Independent D053 source challenge found no lifecycle blocker; it is pinned in the report.
