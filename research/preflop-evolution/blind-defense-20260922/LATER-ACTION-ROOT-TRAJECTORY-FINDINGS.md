# Root coverage and learning trajectory after the matched study

This exploratory diagnostic reads existing checkpoints only. It samples no cards, fits no models and changes no production behavior. The completed fresh study and its inconclusive result remain unchanged.

## Findings

Each 39,936-deal training run spreads its evidence across 169 hand classes and 78 changing policies. A typical class receives **171 deals in total**, about **2.19 per update**. The least-sampled class receives 93 or 95 deals; the most-sampled receives 409 or 421. Every class eventually has observations, but roughly **19 classes receive no new deal in a typical update** (about 6.2–6.4% of incoming hand mass).

Matched old/new runs have exactly the same per-class count at every update, as expected from their matched physical-deal seeds. The differing results are not explained by one treatment receiving more hands or different class coverage.

| Bank | Class deals: min / median / max | Mean classes absent per update | Middle-to-last window policy TV | Mean one-update policy TV, last 26 |
| --- | ---: | ---: | ---: | ---: |
| first-old | 95 / 171 / 421 | 18.58 | 16.43% | 2.14% |
| first-new | 95 / 171 / 421 | 18.58 | 14.80% | 2.14% |
| replication-old | 93 / 171 / 409 | 19.27 | 11.34% | 1.78% |
| replication-new | 93 / 171 / 409 | 19.27 | 15.41% | 2.08% |

The three diagnostic windows contain played generations 0–25, 26–51 and 52–77; each uses the original generation-plus-one weights normalized within that window. The current root policy still moves around 1.8–2.1% of probability mass per update late in training. Middle-to-last-window disagreement is 11.3–16.4%. The new target treatment reduces one seed's window disagreement and increases the other. There is no uniform stabilization result.

These are policy-distance diagnostics, not EV losses. Nearby actions can have similar values, so switching is not by itself proof that a range is wrong. Conversely, small changes in an averaged chart do not prove convergence. The final unplayed generation 78 is included only to describe its distance from the played average, never substituted into the evaluated policy.

## What this establishes, and what it does not

The available evidence per hand is limited, and the continuation changes while those observations accumulate. It is therefore unjustified to treat 171 observations as 171 independent measurements against one fixed opponent. This diagnostic does not separate card/runout variance from opponent drift, network fitting error, or strategic indifference. It does establish that the action-integration treatment did not solve either sparse class coverage or persistent root-policy movement at the fixed budget.

The four complete played root averages reconstructed from checkpoint regret states and the actual fallback policy match the previously audited evaluation policies to at most 3.89e-16. Content-addressed checkpoints and all 316 model documents were authenticated. This took 19.44 seconds without GPU use or a new solve.

An initial diagnostic draft incorrectly assumed an unobserved class retained a uniform policy. Its comparison with the authenticated played average failed by 0.00110, so no result was published from that draft. The completed diagnostic uses the existing CPU policy reader for unobserved classes, retaining learned neural/table fallback behavior. No trained model was modified to pass the comparison.

A separate presentation issue was corrected in the preceding study's CSV: native class order starts at 22 and places suited classes below the diagonal. Every exported label now matches decoded cards in the original catalog. Raw probabilities and all aggregate study results were unchanged.

## Next controlled diagnostic

The completed evaluation archive stores each complete profile's payoff, not individual root-action payoffs. It cannot directly answer how noisy call-versus-fold or call-versus-raise estimates are under a frozen continuation. Reusing its authenticated deals and policy transport allows those action values to be recomputed without neural inference or more training.

The next diagnostic should use all four frozen self-play policy pairs, force each BB root action separately, and keep every later policy fixed. Compare per-class call-minus-fold and raise-minus-call dispersion and predetermined half-sample disagreement. Report this as estimator precision for those fixed continuations, not a best-response certificate: changing the root action may expose continuations with little original reach. Exact initial-jam integration requires separate treatment; do not conflate sampled compatible-private-pair jam values with the training estimator's all-private-card expectation.

Before the full archived-data pass, validate the forced-action transport and linear root-mixture identity on a small fixed batch, measure storage/time, and enforce a bounded resource admission. Do not select a nicer checkpoint or extend the completed confirmatory evaluation.

Evidence: `later-action-root-trajectory-v1-result.json` contains authenticated source identities, every update and all per-class diagnostics. `later-action-root-trajectory-v1-classes.csv` is the compact table, using explicit native class indices. The result's broad source-hash snapshot describes files at execution time; the publication-only CSV label correction followed afterward and does not change any consumed checkpoint or policy reader.
