# First independent transfer panel: substantial sensitivity remains

Both sources completed all ten originally reserved flops, with 2,000 postflop
iterations per board. The preflop probabilities were preserved exactly.
Independent normalization, frequency, terminal-probability and chip/rake checks
passed. Both complete panels passed the registered 0.01 bb postflop residual
gate. These are new-board evaluations, not additional joint preflop training.

| Frozen preflop source | Postflop residual | Full combined deviation gain | OOP gain from changing only the first decision |
|---|---:|---:|---:|
| 10 training flops | 0.000984 bb | 4.473860 bb | 3.385748 bb |
| 47 training flops | 0.000141 bb | 3.694894 bb | 2.521398 bb |

The larger-panel strategy has a smaller deviation gain on this particular
stress panel, but neither profile is close to a joint equilibrium of this
new finite game. Much of the measured OOP gain is available from changing
the first preflop decision alone. Therefore, simply reporting the small
postflop residual would conceal an important strategic mismatch.

These gains are against each source's own evaluated opponent and postflop
continuations. They are not a head-to-head win rate, measured real-world
loss rate, or full-deck exploitability certificate. Off-path responses can
be poorly determined, especially for the 47-flop source's almost-unused
calling branch. Neither a small aggregate residual nor this comparison
certifies every rare conditional hand value.

## What contributes to the mismatch?

For the 10-flop source, JJ, 76s, 99, 55 and 77 contribute most to the
entering-decision gain. For the 47-flop source, the largest contributors
are 55, 76s, 66, 77 and AKo. This panel deliberately stresses board coverage:
it gives substantial weight to low coordinated flops and contains no ace-
or nine-ranked flop. It should not be treated as a representative full-deck
answer. The broader, independently selected 95-flop comparison is still
pending and remains the next registered test.

All local board residuals were below 0.01 bb: the largest was 0.001790 bb
for the 10-flop source and 0.000283 bb for the 47-flop source. These checks
make the numerical result more interpretable; they do not remove the
rare-hand caveat or establish strategic accuracy.

The evaluator averaged hidden-board hand values before choosing a preflop
best response. It did not let the player choose preflop actions after
seeing the future flop. Entering private-card weights, including blockers,
were used for aggregation.

Evidence: `held-reserved10-ab-result-review.json`,
`held-reserved10-report47-result-review.json`, the corresponding complete
aggregate results and twenty lossless worker archives, and the
`reserved10-*-board-diagnostics` / `reserved10-*-decision-diagnostics`
JSON and Markdown pairs. No changes were deployed to production.
