# Paged-reference transfer audit and deferred candidate

Read-only audit, 19 September 2026. The current reference, frozen source
files and executable remain unchanged. The attached patch is **unapplied
and untested on the GPU**; its application preflight passes.

At iteration 500 the existing byte counter records 52,884,279,168,000 bytes
of arena traffic: **105.769 GB per iteration**. This exactly equals three
times the independently planned 35.256 GB of F32 regret and average arrays
across all 94 continuations. Each player pass uploads both players' arrays,
then downloads only the updated player's arrays. Across both passes, that
is two complete uploads plus one complete download. This counter excludes
other traffic, including root weights, returned values and initialization.
It is not a timing profile, so it does not prove how much wall time transfers
consume.

## Candidate: omit the opposing player's average-sum upload

The training sweep's downward action kernel reads **both regret arrays**
to construct current policies. Its upward action kernel reads and updates
only the traverser's regret and average-sum arrays; at opponent nodes it
sums child values. The research wrapper calls this training sweep directly.
The average-policy evaluation path is separate, and this paged reference's
checkpoint evaluation uses synchronized host state.

On this inspected path, uploading the non-traversing player's average sums
therefore appears unnecessary. Both players' regrets, the traverser's
average sums, and both traverser downloads must remain. The deferred patch
changes only that upload and its byte accounting.

If qualified, counted traffic would fall from 3 times all arena bytes to
2.5 times: **88.140 GB per iteration**, saving **17.628 GB (16.67%)**. This is
a deterministic byte-count prediction, not a measured runtime improvement.
It provides no host-memory capacity reduction and does not make the richer
47-board menu safe to allocate. It also does not establish any change in
production Preflop Lab performance; this is an isolated reference harness.

## Qualification before use

After the current accuracy queue releases the GPU, use an isolated candidate
build and a fresh resource/production-idle check. Preserve the baseline.

1. Keep all existing input rejection and 160 alternating board/player
   switching controls. Require bitwise-identical returned values and all
   four host arrays after every sweep, including zero own-range passes.
2. Assert the new exact traffic formula for the known sequence, and verify
   the untouched opponent host arrays remain bitwise unchanged. Repeated
   board switching deliberately leaves unrelated data in device buffers;
   parity must hold despite that stale unused average buffer.
3. Run the same two-board connected case for 2,000 iterations. Require
   every checkpoint evaluation and final policies identical to the frozen
   baseline; repeat its independent physical-card/chip/rake audit.
4. Measure end-to-end elapsed time and resource peaks with no competing
   research GPU worker. Report time separately from byte savings. A failed
   parity check disqualifies the candidate regardless of speed.

Do not apply or rebuild this candidate into tonight's frozen queue. Do not
change update ordering, sampling, precision, supported hands or thresholds.
Larger caches or asynchronous prefetching are separate proposals with their
own lifetime, synchronization, resource and equivalence requirements.

Evidence: `paging-transfer-audit.json`; reproducible reader and patch
generator: `tools/research/paging_transfer_audit.py`; unapplied candidate:
`paging-own-average-candidate.patch`. The first application-only preflight
caught Windows patch line endings; writing the patch as LF bytes corrected
that packaging issue. No candidate solve was attempted.
