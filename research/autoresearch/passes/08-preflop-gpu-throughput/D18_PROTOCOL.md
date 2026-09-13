# D18: bounded two-kernel rank-product pipeline screen

Registered before resource/work calculation. GPU preflop only, C14/R03 control,
port56708 read-only. C18's shared-scratch rank reuse was 43.67% slower; D14's
warp-local version removed no modeled warp paths. C21's empty scan shortcut
also failed complete timing. This is a different scheduling mechanism.

For each existing32-sample batch and contiguous terminal tile, one producer
kernel computes ordered opponent products once per exact sampled rank group.
Each block owns one terminal, its threads own rank groups, and each thread
walks the original sample order independently: no block barriers per sample.
Store each separate quadrature product as f32, then a consumer kernel performs
each of169 hands' original quadrature/sample additions, starting from the
original running accumulator. Never collapse quadrature products into one
subtotal or reassociate additions. The stream orders producer before consumer;
only then may the scratch tile be reused. CDF production and aliases stay as is.

Use fixed slots [terminal-in-tile][local sample][max group][max quadrature]
for a first prototype, writing only actual groups/quadratures. Maximum groups
comes from the exact D13 table. Max quadrature is floor((players+1)/2).
Reserve the three169x1024 u32 rank maps plus1024 group counts, as in C18.
Choose the largest power-of-two terminal tile from8192..65536 whose float
scratch plus those maps fits1GiB; clip allocation to the actual terminal count.
Preserve batch32, caches, precision, sample count and all existing buffers.
No active-terminal queue, sorting or device compaction is added.

Count producer and consumer launches for every tile/batch/traverser, including
inactive terminal slots. Count actual positive-task arithmetic and logical
traffic from D10/D11 histograms. Source arithmetic shares only O+3QO work;
every hand retains2Q accumulation operations. Logical terminal traffic includes
grouped CDF gathers, Q scratch writes per group, and Q scratch reads per hand.
Do not infer native instructions, cache/DRAM traffic or timing from these counts.
Count original CDF writes separately; they are unchanged.

Admission gates, both large learning and checks: source arithmetic reduction
>=30%, net logical terminal traffic reduction>=10%, additional producer/
consumer launches<=32768 per complete learning sweep or accuracy check.
Scratch+maps<=1GiB and total declared device bytes<=23000MiB at both fixtures.
No tile fits => rejection. Report small work reductions descriptively. A pass
admits a separately registered exact GPU prototype, not a speedup claim.

Verify all1024 rank permutations and group boundaries. Independently rebuild
opponent histograms from the D10 binary witnesses, derive resource capacity
and work sums a second way, and reconcile original counts with D11. Preserve
all hashes and the immutable protocol. One run07-guarded host census, cap180s;
no GPU solver work or source mutation. Next device qualification must cover
partial tiles/batches,2..8 opponents, sparse/dense/zero recovery, aliases,
all prefixes/arenas, graph/stop and real launch/memory overhead before timing.

This pipeline may still lose to extra scratch traffic, grid scheduling or graph
size. Passing these coarse gates cannot establish a10x solve improvement or
resolve the outstanding convergence requirement.
