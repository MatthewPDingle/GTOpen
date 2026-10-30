# Batched current-policy preparation candidate

The separate candidate combines the earlier preflop-overlay routing change with
batched computation of the existing 25 river hand/board features. It uses the
previously checked bulk feature implementation, preserves canonical input and
public-action validation, and replays the original 8,192-entry LRU order.
The registered training pipeline and production application remain unchanged.

CPU qualification v2 passed 78 exact equivalence cases and 32 malformed-input
checks. The cases cover both input representations, all seven stack depths,
initial and learned models, all streets, preflop classes and score-only queries.
Two additional synthetic visible-query cases contain 9,000 distinct card keys
plus 64 repeated rows: they exercise eviction, revisiting evicted keys in the
same batch, and a second pass with a warm cache. Features, histories, table
masks, cached values and order, and final probabilities match the original.
These are implementation fixtures, not new scientific training/evaluation deals.

Version 1 passed the numerical checks. Code inspection then found that cached
NumPy row views could retain their full batch arrays. Version 2 stores independent
100-byte feature vectors and explicitly checks their ownership and the cache
entry bound. Both versions and their evidence are retained; v2 is the candidate
for any later integration. Neither version is installed in this study.

On the same authenticated retained history/selected query pair:

| Implementation | Median scoring seconds |
| --- | ---: |
| Original current policy | 2.837641 |
| Routed overlays only | 1.812890 |
| Routed overlays plus batched features v2 | 1.535005 |

The v2 candidate used 45.9% less time than the
original, or 1.85 times the fixture scoring throughput.
It used 15.3% less time than routing alone in
this check. Each implementation was measured twice in ABCCBA order with fresh
policy caches, one CPU math thread and below-normal process priority. Such small
component samples do not establish a whole-cycle or parallel-study speedup.
They exclude native target generation, transport, archives and much of the rest
of collection. Other desktop load can affect timing.

No CUDA initialization, new fit, native solver execution, production change or
poker accuracy evaluation occurred. All 249 recorded input file identities
were reverified. The original admission helper remains the only launcher for
the four parallel scientific arms; any future adoption needs separate integration
qualification and explicit provenance, preserving the registered comparison.

Implementation: tools/research/stack_context_current_policy_batched_v2.py.
Evidence: stack-context-batched-policy-check-v2-result.json.
