# Zero-own-reach continuation control (N32)

Frozen before GPU output. N31 found 446 large-case terminal/traverser pairs with
zero current own range but positive opponent reach. The learned kernel switches
to Balanced at these counterfactual branches. This does not occur in the two N27
heads-up fixtures and cannot explain their residual gaps.

Change exactly one boolean guard in the N20 full-double kernel: retain learned
values at SPR 1 through 20 even when the traverser's own range is empty. The
existing normalized combo prior then supplies the missing own range. Opponent
zero-mass branches still return zero. No coefficient, clipping, centering,
precision, legal-pair accounting or positive-range prediction changes.

This is a diagnostic hypothesis. The uniform own-range prior is a modeling
assumption, not observed behavior or a proven correct off-path value.

After N21 releases the GPU:

1. Verify exact selected action-value parity on the existing N19 1500-iteration
   average policy (both ranges positive).
2. Run existing sparse 2/3/8-player fixtures; require finite values and chip
   conservation. These are safety checks, not an independent value oracle.
3. Resume the exact same N19 candidate save for 500 steps under the original
   kernel, then separately for 500 steps under this guard change. Zero warmup.
4. Record all per-seat gaps, existing 17-node strategy changes and learning time.
   A 25% gap reduction is interesting diagnostic evidence; the practical target
   remains 0.005 bb. No deployment follows from this experiment alone.

One ordered pair is not a repeated timing benchmark. New ranges need fresh
accuracy validation if this becomes a candidate. Existing N15/N20/N21 labels
cannot be represented as prospective qualification of newly generated ranges.
Keep experimental saves local and never load them in the ordinary app.

Fixed night deadline: 2026-09-16 20:49:02 UTC. Reserve at least 40 minutes before
starting the pair; otherwise defer. No competing GPU owner or production writes.
