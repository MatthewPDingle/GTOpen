# Native finish after behavioral pretraining: registered next experiment

Design/admission protocol only; transition code and numerical tests remain to
be implemented. `BEHAVIORAL_FIXED_RESULTS.md` admits both saved candidates.

## Explicit heuristic, not an exact history transformation

Use the fixed-stage policies as starting points for unrestricted native CFR.
Keep every regret entry and the global iteration unchanged. For the reset
variant, clear only strategy sums at learning nodes; preserve forced/frozen
averages. Destroy the old GPU engine and construct a fresh native engine with
no behavioral mode. Do not modify the original saved files.

The retained regrets are a warm-start initializer. They are not claimed to be
the regret history of a single unperturbed game: action-dependent DCFR discounts
make a simple scalar coordinate conversion unjustified. Clearing averages
removes the forced behavior from the reported mixture; it is not evidence that
new native behavior is accurate. All acceptance follows new native learning.

## Required numerical admission

On a bounded fixture with a frozen seat and point lock, prove the transition
preserves all regrets, all nonlearning averages, game configuration, model and
iteration exactly; only selected learning averages become zero. Reject invalid
or stopped inputs before mutation. Compare the first several native iterations
and full checks to an independently constructed native state with the same
specified initializer. Verify roundtrip, cancellation, capture and absence of
behavioral state. Keep the API research-only and capped to 50,000 nodes for
this stage. Run the applicable native/default regression suites.

## Four fixed finishing cases

Inputs are the immutable iteration-1000 files from the fixed diagnostic:

1. Epsilon 0 control, keep averages.
2. Epsilon 0 control, reset learning averages.
3. Epsilon 0.01 candidate, reset learning averages.
4. Epsilon 0.05 candidate, reset learning averages.

Use all 1024 particles, gamma15/horizon1000, seed42. Continue the global age;
do not restart it or introduce local ages. At most 1000 additional iterations
(ending at age2000), full checks and all six per-hand audits every25 finishing
iterations, 180-second process cap per case. Stop at two consecutive combined
passes (unrestricted gap <= 0.005 bb AND all six fixed conditional checks).
Do not evaluate a cleared uniform average as a passing initial strategy.

Record the retained pretraining duration, complete finishing duration, input
and executable hashes, every checkpoint, fixed-state preservation and a fresh
saved-file audit. Compare total cost, not finishing time alone. The matched
reset control separates a benefit of behavioral pretraining from a benefit of
discarding old averages.

## Decision boundary

If neither pretrained candidate passes the combined native gates, stop this
transition without increasing its budget or tuning history scales. If a
candidate passes but is slower than a qualifying matched reset control, it is
not admitted as a faster method. If the matched reset control fails, report a
quality result at the fixed budget, not a measured speedup ratio.

A surviving candidate permits a separately registered second seed and a
sampled-learning comparison. No large run, live change or 10x speed claim is
authorized by this first-seed finish. Port56708 stays read-only; owned processes
stop if user work becomes busy. Run hardware workloads serially.
