# Shared normalized reach in CDF construction

The current preferred CDF kernel assigns four warps to four independent
particles over the same normalized 169-hand reach. Each warp gathers those
169 input values from global memory through its particle-specific rank order.
Stage the source vector into 676 bytes of shared memory once per CTA, then
perform the identical gathers and prefix scans over shared memory.

For a full CTA this reduces normalized global gather loads from 676 floats to
169 coalesced floats. It does not reduce CDF output bytes or particle-order
loads. Hardware L1 may already reuse much of the source data: this is a claim
about source-level global loads, not a guaranteed 4x reduction in DRAM traffic.
The tradeoff is one block barrier, shared gathers with possible bank conflicts,
and a small shared/register footprint. Benchmark it; do not infer a speedup.

The existing eight-seat phase diagnostic attributed roughly 2.5 seconds per
iteration to CDF construction before the latest terminal specialization. That
justifies a bounded CDF experiment, but is not a current candidate measurement.

## Exact scope

`cdf-shared-normalized.patch` changes only `pf_multiway_cdf`. It does not alter
launch dimensions, batch width, physical CDF layout, VRAM planning, normalized
division, particle count, order tables, prefix-scan sequence or terminal math.
`pf_multiway_cdf_direct` remains byte-for-byte unchanged. No terminal cache or
cross-seat reuse is introduced. The proposal is independent of queued terminal
restrict and launch-geometry experiments.

`git apply --check` passed against the recorded isolated source; no active source
edits, builds or hardware jobs were performed to prepare this proposal.

## Source-level synchronization audit

- `slot = work[start + blockIdx.x]` is block-uniform. Therefore the existing
  `gate && !active[slot]` return is taken by the whole CTA. Activity flags are
  established by the preceding ordered prepare kernel, not modified by CDF.
- `block = blocks[slot]`, `sample_count` and `mass[block]` are also uniform.
  Empty-particle or nonpositive-mass exits happen before any shared staging.
- All remaining threads stage `h = threadIdx.x; h < 169; h += blockDim.x`.
  With the unchanged 128-thread launch, indices 0–168 each have exactly one
  writer. No vector entry is left unwritten and none has multiple writers.
- Every remaining thread reaches the same `__syncthreads`. Only AFTER the
  barrier is `local = blockIdx.y*4 + threadIdx.x/32` checked against sample_count.
  Thus one- and seven-particle tails cannot strand a block at the barrier.
- Partial-particle exits are warp-uniform. Every surviving warp retains all
  32 lanes for the unchanged full-mask shuffle scan. For the last hand tile,
  out-of-range lanes still contribute zero and participate, exactly as before.
- Inactive/zero-mass blocks exit before touching potentially stale normalized
  input. The compact/global source index is unchanged. Shared stores/loads copy
  existing f32 bits; they introduce no reciprocal, division, rescaling or sum.
- Shared reach is immutable after the one barrier; no second barrier or reuse
  phase is required within a CTA.

## Acceptance gates

Run existing direct/normalized and compact/union CDF tests for batches 32, 7 and
1, including positive→zero→positive reach, inactive poisoned scratch and partial
final particle batches. Require exact CDF values and exact fixed-state arena
fingerprints at the same batch. Run 3/6/7/8 controls and modeled/adaptive/frozen
controls as available; all sample/precision/convergence settings remain fixed.

Compare unchanged terminal geometry between baseline/candidate. Use alternating
paired process timings and the phase diagnostic to check whether CDF time falls
without shifting cost elsewhere. Keep only a repeatable end-to-end gain above
the existing threshold and no material control regression. Check register/shared
resource use if results are marginal. Revert on deadlock, exactness failure or
no useful gain; do not relax numerical gates for a copy-only change.
