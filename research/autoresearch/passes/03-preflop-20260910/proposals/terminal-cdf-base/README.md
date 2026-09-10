# Optional terminal CDF base hoisting

Kernel-only proposal based on the **proposed live-terminal-work kernel**, whose
hash is in `base.txt`. `cdf-base.patch` changes no Rust launch ABI, launch width,
particle count, precision, worklist membership or probability indexing. Apply
only as a separate experiment after measuring/retaining or rejecting that list.
No compilation or GPU execution was performed here.

## Change

The block's thread0 already resolves each live opponent's global/compact slot.
Store its 64-bit CDF origin in shared metadata at that point:

`origin = size_t(slot) * batch_capacity * 170`

The existing sample/opponent loop then addresses:

`origin[q] + size_t(local_sample) * 170 + rank_boundary`

instead of:

`(size_t(slot[q]) * batch_capacity + local_sample) * 170 + rank_boundary`.

The cast precedes multiplication in both paths. Origins and addresses remain
`size_t` throughout; shared metadata is rebuilt for every block/particle-batch
launch and uses the current batch capacity. The final partial batch retains
capacity stride, as before. No floating expression or loop order is modified.
The slot-space membership still comes from the retained global/compact mapping.

The sum helper no longer needs batch_capacity because the origin includes it.
The kernel ABI remains unchanged; only the inlined device helper signature
changes. All four existing quadrature specializations receive the same bases.

## Hypothesis and tradeoff

At source level, slot*capacity*170 was expressed inside the sample/opponent
loop for every hero thread. The proposal computes that invariant once per
opponent per terminal block. The compiler may already hoist or strength-reduce
some/all of this address work; source inspection cannot determine the savings.
There is no guaranteed speedup.

Shared opponent metadata grows from nine u32 values (36 bytes) to nine size_t
values (72 bytes on the CUDA target), plus any changed padding. Total shared
allocation and occupancy are compiler/device dependent. Each metadata read is
wider, and register scheduling can change. This could offset the saved integer
address arithmetic. No register/shared-memory or assembly claim has been
verified by compilation in this proposal.

The fixed extra shared bytes do not change global VRAM planning. The live work,
CDF and normalized buffers remain exactly the same size. Zero-counterfactual
blocks retain the existing path that initializes nopponents=0 and never reads
opponent metadata; first-batch zero writes stay unchanged.

## Verification and acceptance

The generator ran pure integer edge checks across slot0/1, current compact and
union high slots, 2^31 and u32::MAX; batch1/7/32/1024; first/last local sample;
and rank boundaries0/1/169. Both expressions matched without 64-bit overflow.
These arithmetic checks do not replace CUDA validation.

Reuse existing terminal CPU comparisons, compact/union parity, live-worklist
identity parity, zero/poison transitions and actual direct/normalized boundary
tests. These exercise batch1/7/32 and the irregular final batch. The frozen
eight-player exact arena fingerprint/gaps/EVs must still match.

Measure this patch alone against the retained predecessor, including the small
3/6/7-seat controls. Prefer repeated/interleaved production graph benchmarks.
Supplementary eager phase events should show a terminal-only effect while CDF
timing stays stable, but event estimates are not acceptance measurements.
Reject if no repeatable meaningful win. Do not respond to a null result by
mixing opponent templates, altered launch width or arithmetic in the same
candidate; inspect generated address instructions if more investigation is
justified.
