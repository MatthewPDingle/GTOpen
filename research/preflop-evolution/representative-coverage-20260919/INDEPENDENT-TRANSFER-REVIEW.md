# Original transfer study: all four comparisons complete

20 September 2026, reviewed after the queue completed at 05:41 Adelaide.
All 210 one-board workers finished their registered 2,000 postflop iterations.
The exact frozen preflop policies were preserved. Every aggregate passed the
independent card-mass, probability, frequency and cash-conservation checks.
All four postflop residuals passed the unchanged 0.01 bb numerical gate.

## Results

Values are bb conditional on entering this two-player branch, not bb per
hand dealt at the original eight-player table.

| Evaluation panel | Training source | Postflop residual | Full deviation gain, summed over players |
|---|---|---:|---:|
| Reserved 10 stress boards | 10 flops | 0.000983558 | 4.473859571 |
| Reserved 10 stress boards | 47 flops | 0.000140574 | 3.694894065 |
| Independent 95 eligible boards | 10 flops | 0.000967534 | 2.733421356 |
| Independent 95 eligible boards | 47 flops | 0.000145706 | 0.669223704 |

The 47-flop source has a substantially smaller deviation gain on independent95.
However, both players' preflop policies and rebuilt postflop responses differ
between sources. This is not a head-to-head win-rate improvement, a comparison
against one common opponent, or a measured full-deck exploitability reduction.

The reserved10 and independent95 panels describe different board populations.
The former is a deliberately narrow low-board stress panel. The latter samples
the eligible population after excluding the previously used board orbits.
Do not compare their numbers as though they were interchangeable random samples
of the full deck, or treat the 95 points as independent statistical replicates.

## Remaining sensitivity

For source47 on independent95, OOP and IP deviations are 0.482543417 and
0.186680287 bb. Changing only OOP's entering action, keeping later own play
fixed, gains 0.447695477 bb. Thus the remaining issue is substantially visible
at the preflop decision; it is not merely the small measured postflop residual.
QQ, 66, AKo, AQs and QTs are the largest weighted root contributors in this
diagnostic. Those are conditional values against this source's rebuilt
opponent, not instructions to override production ranges.

Every source47 independent95 board's aggregate postflop residual is below
0.01 bb; the largest is 0.000284410. This rules out a large board-level
aggregate convergence failure on this completed panel, but not individual
rare-hand errors or sensitivity to different continuation strategies.

The original connected 47-flop solve had total gap 0.007423827 bb on its
training panel. The transfer experiment preserves its preflop policy but
rebuilds both postflop strategies. Consequently, the difference cannot yet
be attributed entirely to board-sample overfitting. The newly registered
matched-training-panel aggregation will evaluate independently rebuilt
continuations on the exact original boards and weights. See
RESOLVING-INTERPRETATION.md and POPULATION-SUPPLEMENT-RUNTIME.md.

## Decision

Proceed with the preregistered full-population supplement and matched-panel
diagnostic. Reuse only exact, verified worker artifacts; solve the 59 missing
excluded orbits for each source. Keep the original results, panels, policies,
gates and 09:00 deadline unchanged. No source has earned production promotion.

This remains a restricted two-player continuation with fixed incoming ranges,
one postflop size menu, omitted earlier folded cards and configured rake.
It is progress toward robust preflop valuation, not a replacement for the full
multiway preflop game or evidence that we now match GTO Wizard.

Evidence: independent-transfer-summary.json, the four held-*-result-review.json
files, validation95-report47-{board,decision}-diagnostics.{json,md}, and
independent-transfer-comparison.{png,json}. Per-worker manifests, source and
executable hashes, logs, guards and compressed outputs are retained.
