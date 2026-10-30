# Next diagnostic: enforce the exact river call/fold value bounds

## What the completed feature test says

The explicit river-strength input improved pooled under-50-bb Call-minus-Fold
validation prediction error by 9.58% versus original and 9.65% versus the
geometry-only control. It improved that metric in all four datasets. This
supports the small-pot representation diagnosis, but not an overall model
replacement: whole-river contrast error increased 0.75%, mean full-postflop
action error increased 0.10%, and Run B BB full-postflop error increased over
1%. The candidate failed the predeclared advancement gate. Preserve it as a
mixed result; do not integrate or promote it.

The next question is whether the original model sometimes violates an exact
physical constraint that the stored labels already passed. Unlike another
learned input or a uniform-opponent policy, this constraint needs no guess at
the opponent's range and no new fit.

## Derivation and precise transformation

At a river decision with legal Fold and terminal Call, let P be the current
pot, C the incremental call, and R rake on P+C. For every actual hidden hand,
the Call-minus-Fold advantage is one of -C, (P+C-R)/2-C, or P-R. Therefore its
conditional expectation, and every weighted average of these targets at this
same visible state, lies in [-C, P-R]. Branch offsets and the current-policy
mean cancel in this difference. The native and stored-label audit established
this identity for the current fixed context.

Let s0 and s1 be predicted Fold and Call advantages in bb, and d=s1-s0.
Set bounded_d=clip(d,-C,P-R), adjustment=(bounded_d-d)/2, then:

- projected_fold = s0 - adjustment
- projected_call = s1 + adjustment
- every other predicted action stays unchanged

This is the Euclidean projection of the action vector onto the closed slab
defined by the value bounds. It preserves the Fold-plus-Call sum. Because every
legal target vector lies inside the slab, projection cannot increase squared
distance to any of those targets. In this experiment each legal action in a
row has the same source weight, so the same non-increase holds for the original
weighted action loss, as well as the clipped one-contrast loss. Check the
statement directly, per row, rather than relying only on an aggregate.

This does not guarantee a better regret-matched policy or higher poker EV.
Projection can change positive-regret ratios or fallback argmax choices. It
does not repair a mistaken common offset, an opponent model, a noisy sampling
distribution, other streets, or a preflop continuation approximation.

## Fixed comparison

Use the four original saved 512-step baseline models, generation-77 reservoirs,
original partitions, source weights and train-only scales. Do not select among
the rejected geometry/strength models. No new training, data generation or
final-test scoring. Keep the production solver unchanged.

For inference use float64 with the stored float32 weights widened exactly and
the original float32 visible features widened exactly, matching the precision
convention of the existing research policy banks. Record the small scoring
difference from the earlier float32 validation readback explicitly; require
original normalized losses within 1e-6 of that reference. Check CPU/GPU float64
on a deterministic training-only prefix before any runtime proposal, especially
ties and all-negative-score fallback decisions.

Use exact native public amounts and recorded training scale to convert outputs
to bb, project the two actions, and restore normalized scores if needed. Apply
only at verified river Call/Fold menus; leave every other node byte-identical.
Reject invalid scales, wrong menus and unmatched public states.

## Required controls

- Hand-calculated lower violation, upper violation, interior and boundary cases.
- Idempotence, common-offset invariance and positive-unit-scale covariance.
- Other action values unchanged, Fold-plus-Call sum unchanged, legal bounds met.
- No increase in full action error or contrast error for every tested legal
  loss/tie/win target, including arbitrary common offsets and unequal source
  row weights. The within-row action weights must remain equal.
- Compare the same formula in normalized units and chip units.
- Positive-regret normalization, all-negative fallback and exact ties retain
  the existing policy rule. Report changed policies rather than describing the
  projection as policy-invariant.
- For actual training/validation rows, recheck the endpoint bound and verify
  non-increasing error per row with an explicitly recorded numerical tolerance.

Bind source, checkpoint, catalog and control hashes before the full diagnostic.
Save failed controls or mismatched rows as evidence; do not silently clamp
incorrect targets or exclude difficult cases.

## Reporting and next decision

For every dataset and the existing five pot buckets, report:

- Count and source-weight fraction below/above the bounds, before projection.
- Magnitude of violations in bb; retain maximum and weighted mean.
- Original and projected full-postflop action MSE, river contrast MSE and
  pooled under-50-bb river contrast MSE with their original denominators.
- Changed positive-regret policy fraction and weighted action-distribution
  distance, separately from prediction metrics. A better L2 score is not an
  independently validated better poker action.

If violations are absent or negligible, reject this as an explanation for the
range-quality problem. If common or materially consequential, qualify a
separate inference adapter with exact visibility, scaling and policy controls
before proposing a complete policy-training/fresh-deal experiment. Neither
outcome alone proves stronger preflop play or justifies a production change.

Keep the study bounded: four CPU workers where available, a small GPU control
only if needed, under 100 MB of new retained artifacts and under 30 minutes.
Retain shared locks, production checks, the 800 GB global allocated-storage cap,
and the approved light-desktop GPU sharing rule. Existing frozen experiment
sources and checkpoints remain unchanged.

The broader goal is still accurate, flexible preflop behavior across positions,
stack sizes, action menus and multiway situations. This is a physically grounded
check of one continuation component, not a substitute for that goal.
