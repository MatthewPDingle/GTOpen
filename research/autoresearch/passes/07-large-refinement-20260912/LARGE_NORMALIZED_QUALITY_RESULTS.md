# Large full-particle normalization: rejected

The registered fresh 8-seat, 1,567,754-node run did not meet the combined
quality gate. No deployment or qualified speed improvement follows from it.
The successful small-game result did not transfer to this large fixture.

| Final iteration | Full-reference global gap | Conditional paths passing | Wall time |
| --- | --- | --- | --- |
| 1,500 | 0.557943 bb | 11 / 27 | 4,062.41 s (67.71 min) |

The requirement remains a global gap at most 0.005 bb and all 27 conditional
paths passing at two consecutive checks. None of the 30 checkpoints met
that combined gate. These are canonical coupled-deck model checks, not
physical-deal equity validation or full conditional subgame best responses.

`check_large_normalized_quality.py` independently recomputed every global
gap and all per-hand conditional acceptance decisions. A separate executable
loaded the terminal save and reproduced the final per-hand audit exactly.
The saved game also passed the exact arena round-trip check. Compressed raw
results have byte-count and SHA-256 envelopes; the guard recorded source,
executable and immutable input hashes. The process completed normally at its
registered iteration limit, without a restart or time-cap extension.

The original GPU process continued through the desktop capacity/stalled-goal
message. It was resumed for observation, not restarted. Port 56708 was only
queried by the existing read-only busy guard and was not deployed or changed.

Next, inspect current-policy prefix masses alongside averaged-policy masses
at all 27 final paths. Separately, run the registered fixed-state sampling
diagnostic on the three small saved games. Full-particle learning already
failed on this large fixture, so sampling noise alone cannot explain this
large-run failure. These diagnostics must distinguish causes before choosing
another convergence candidate.

Evidence: `raw/large-normalized-quality-verified.json`,
`raw/large-normalized-quality-v1-result.json.gz`, its envelope, the saved-game
audit, both guarded process records, and `LARGE_NORMALIZED_QUALITY_PLAN.md`.
