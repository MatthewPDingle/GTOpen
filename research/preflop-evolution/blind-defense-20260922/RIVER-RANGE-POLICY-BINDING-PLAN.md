# Bind the weighted river reference to played policies

This is an arithmetic and input-binding check, not a new training experiment.
The reference must reproduce the existing exact per-hand calculation when the
opponent range comes from actual prior actions. It must not replace that range
with a uniform distribution or count the hero's own action likelihood twice.

Use the two retained generation-77 current policies from the qualified
river-posterior64 native control. These are individually played policies, not
the historical average policy bank. Use all eight retained TRAIN fixture cases.
For each case and each actor, select the first Fold/Call decision in native
document/node order whose children are terminal Fold and Showdown. Selection
uses structure only, before new inference or payoff calculations. This gives
16 fixed public situations covering both actors, both policies, and four boards.

For each situation use its original private holding and the first two
lexicographic board-legal holdings disjoint from all earlier chosen cards.
Three disjoint holdings cover every board-legal opponent holding: a two-card
opponent can overlap at most two of the three. Reconstruct a single vector of
1,081 opponent masses from these three native exports, then validate it on a
fourth disjoint holding chosen in reverse lexicographic order. Preserve every
native observation, actual action, legal arity, and model identity.

Canonical suit labels may differ between hero holdings. Retain the exact suit
permutation for each request and invert it before combining opponent holdings.
Check that overlapping holdings have identical canonical opponent observation
and action sequences, and identical pre-normalization mass. Confirm that the
source entry range is invariant to all 24 suit permutations. Do not generalize
this control to suit-asymmetric entry ranges or correlated model mixtures.

For all four hero holdings compare the assembled range to the existing
qualified per-hero posterior calculation, including zero support. Obtain exact
native ranks for the public board. Compare card removal, win/tie/loss outcomes,
conditional equity, and call-minus-fold value with the native terminal payouts.
Test conservation of posterior mass and independence from the hero's own reach.
Run explicit negative controls against incomplete coverage, inconsistent
overlap, and mismatched opponent action history.

Use the corrected river_range_reference_v2.py. Gates: absolute mass error
1e-10, posterior/equity error 1e-12, cashflow error 1e-9 bb; exact identity,
coverage, and discrete outcome checks. Do not relax gates following a failure.
Retain raw exports, inferred probabilities, range vectors, scalar comparisons,
source hashes, terminal process evidence, and failures. Independently read back
the retained arrays and payouts after the run.

CPU only, four workers with one BLAS thread each, 15-minute total bound,
192 MB new storage plus 64 MB reserve, global allocated cap 800 GB, 40 GB S:
free, 28/24 GB RAM admission/running, CPU below 50/75 percent. Acquire the
existing research lock; native children are hidden and owned. Leave production
56708 and the waiting GPU learning comparison unchanged. This control provides
no new model-quality, convergence, full-preflop, or end-to-end speed claim.
