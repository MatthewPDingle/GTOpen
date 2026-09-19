# Entry-support cutoff audit

Chance-only audit, 19 September 2026. No solve, reserved strategy, or
production setting was changed. The registered relative cutoff remains
1e-5 of each seat's largest physical-combination weight.

The source contains positive weights for all 1,326 combinations in both
seats, many extremely small. The cutoff retains 322 opener and 106 reraiser
combinations. Despite this large reduction in stored hand count, it removes
only **0.00030844%** of the compatible joint entering probability under
full-deck chance. The 47-board panel removes **0.00030925%**; the independent
95-board sample removes **0.00030919%**. Suit averaging and board removal
are included. No action-value outcomes were used.

| Relative cutoff | Opener combinations | Reraiser combinations | Full-deck joint probability removed |
|---|---:|---:|---:|
| 0 | 1,326 | 1,326 | 0% |
| 1e-7 | 486 | 182 | 0.00000736% |
| 1e-6 | 398 | 130 | 0.00006968% |
| **1e-5, registered** | **322** | **106** | **0.00030844%** |
| 1e-4 | 250 | 90 | 0.00235553% |
| 1e-3 | 220 | 82 | 0.01304892% |

This is sensitivity reporting, not a recommendation to change the cutoff.
The full/trimmed compatible-pair distributions were explicitly normalized;
their total variation equals the removed mass, as required for conditioning
on a retained subset. Mass decreases monotonically across the tested
cutoffs. The class-based inputs are exactly invariant under all 24 suit
permutations, so each orbit's scalar normalizer can be computed from one
representative. Full-deck chance permits the same number of flops for each
compatible four-card private deal.

The audit makes a large population shift from this cutoff unlikely in this
specific input. It does **not** prove that the supplied entering ranges are
correct, bound changes in equilibrium strategies, certify rare-hand play,
or validate the postflop model. Nor is it evidence for other scenarios with
different ranges. Those questions remain separate from pruning tiny mass.

Reproduce with `tools/research/entry_support_audit.py`. Exact values and
input/source hashes are retained in `entry-support-audit.json`.
