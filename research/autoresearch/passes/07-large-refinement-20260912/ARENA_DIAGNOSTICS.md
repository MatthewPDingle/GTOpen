# Original large-game arena inspection

The native and sampled original 1,050-iteration saves were inspected read-only
at all 27 registered paths, with 169 hand classes per path. Both runs had zero
current-policy uniform fallbacks, zero average-policy uniform fallbacks, and
zero positive sums at or below the 1e-12 normalization threshold.

| Original save | Minimum positive regret sum | Minimum positive average sum |
|---|---:|---:|
| Native | 7.1958702e-8 | 1.05529594 |
| Sampled | 1.5703056e-7 | 0.19664711 |

This rules out that cutoff as an explanation of the inspected saved policies.
It does not inspect every historical iteration or every node in the tree.
Do not lower thresholds on the basis of small incoming reach alone.

Evidence: `raw/original-arena-summary-v1.json`, the ten
`raw/original-{native,sampled}-arena-v1-{0..4}.json` files, and corresponding
exit manifests. The existing diagnostic takes six paths, so the last batch
overlaps earlier paths; the summary deduplicates and requires 27 unique paths.
All inputs were hashed before and after each run and remained unchanged.

Full default solver tests passed (`default-solver-tests-v1`). GPU equivalence
passed all 6 postflop and 13 preflop tests (`gpu-equivalence-tests-v1`). These
are correctness checks, not a CPU performance campaign. Port 56708 was not
modified or restarted.

Next candidate: alternate upstream and compact downstream updates with fresh
incoming ranges, auditing the complete resulting policy after each cycle.
Previous experiments updating either side in isolation failed; a joint
iteration still requires direct qualification. Preserve original global and
conditional gates, fixed arenas, and explicit mixed-history resume limits.
