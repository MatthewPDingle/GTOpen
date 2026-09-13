# C05 protocol: aligned first-prefix stores

D03 shows CDF construction still consumes about43% of both large learning and
check time. C04 decoding was much slower. Try changing only CDF storage addresses
while keeping ordinary direct reads.

The pass03 padding assessment rejected plain192 padding because the +1 prefix
write remained misaligned. Its explicitly deferred alternative is the target:
stride192 floats, with a constant31-float leading bias. Logical CDF0 is at
bias+row*192; logical CDF1 starts at32+row*192 and is128-byte aligned. Keep all170
logical values and the exact scan/carry operations. Allocate rows*192+32 floats
so the last row's highest written index is safely inside the trailing capacity.

At instruction address-coverage level, five full warp stores plus the9-value
tail cover22 rather than27 32-byte sectors (excluding the separate zero store).
This is not a DRAM transaction count or a speed estimate. Cache merging,
increased footprint and scattered terminal reads may eliminate any gain.

Large compact capacity388082,batch32: CDF storage grows from8,444,664,320 bytes
to9,537,503,360 bytes, an extra1,092,839,040 bytes. Preserve batch32,1024 samples,
cache choices, normalization, C01 aliases and all arithmetic. No model change.

Implementation must use an explicit memory-headroom check for both steady and
transient allocation peaks. Enable only on a fresh unwarmed research engine;
allocation failure must leave the original valid buffer/layout intact. Do not
reduce batch size or displace caches. Budget-limited production behavior remains
unchanged; this is an opt-in prototype, not a universal planner modification.

Before timing: compare every logical prefix against the canonical writer with
poisoned leading/padding/trailing regions, aliases, dense/sparse/zero/varied
inputs, sample offsets, gates and partial batches. Full original/C01/C05 arena,
terminal and checkpoint comparisons must include2..8 opponents, forced/frozen
policies, zero/recovery and graphs. Then first large pair must save1% to extend;
retention needs3% large median complete improvement across3 alternating pairs,
small regression no more than3%, and the required full regression suites.

Registered before implementation. On the large frozen benchmark, the original
allocation is about13,075MB under a23,000MB engine budget. Permit9,800,000,000
bytes of extra transient headroom: the new9,537,503,360-byte allocation fits
while the old buffer stays valid. Steady growth is only1,092,839,040 bytes.
Small synthetic fixtures use200,000,000-byte headroom under their2,000MB budget.
Reject before allocation when the required transient or steady growth exceeds
the explicitly supplied headroom. Prepare all new functions/buffer first; swap
only after every fallible step succeeds. No allocation failure can publish the
new layout with an old buffer. Record old/new CDF size and transient bytes. Build/test cap240s; benchmark cap180s; run07 guard,
immutable inputs and serial workload rule apply. Production56708 untouched.
