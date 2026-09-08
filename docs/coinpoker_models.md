# CoinPoker player models by stake

Measured 8 September 2026 from HHDealer CoinPoker hand histories recorded in 2025. No raw histories or individual player identifiers are included in this public study.

## Using the library

In Preflop Lab, open **Manage models** and search **CoinPoker**, or choose a **CoinPoker · NL… · measured** group in a seat menu. **Pool** is the opponent average; the other entries describe fitted behavior groups. Hover a library entry for its source and sample size, or Edit it to inspect/copy its stats. This version requires the updated server with dataset-context support. Once installed, refresh to load the library. The dataset checkbox in the model editor preserves measured entry contexts; uncheck it to use editable reference-generated entry rates. Existing profiles and seat assignments are unchanged.

These models describe **seven-max ante tables with five to seven players dealt in**. They are not measurements of live casino games or no-ante tables. Date windows differ across stakes, so differences between stakes are not necessarily caused by the stake itself.

## Coverage

| Stake | Validated hands | Player names | Pool VPIP / PFR / 3-bet | Fitted types | Dates |
|---|---:|---:|---|---:|---|
| NL10 | 773,370 | 6,371 | 25.5 / 16.8 / 8.8 | 6 | 2025-06-17 to 2025-08-24 |
| NL25 | 802,608 | 4,936 | 24.7 / 17.1 / 8.9 | 6 | 2025-07-04 to 2025-08-24 |
| NL50 | 873,554 | 5,026 | 24.4 / 17.5 / 9.3 | 5 | 2025-05-26 to 2025-08-22 |
| NL100 | 734,030 | 5,030 | 24.7 / 17.5 / 9.3 | 5 | 2025-03-31 to 2025-08-22 |

Hand counts are distinct games; model sample sizes in the library are **player-hands**, not additional independent games. Names can overlap between stakes. Short-history players contribute to Pool even when they cannot be classified reliably.

## Validation and type selection

Each stake uses its last 14 calendar days as a temporal holdout. A stable hash additionally withholds 20% of player identities from both grouping and group-frequency estimation. Those players are assigned using only their earlier observations and scored on their later decisions. Types use 11 smoothed preflop/postflop features. We compare standardized k-means and a fitted decision hierarchy with 2–8 groups, plus the historical seven behavior bands remeasured on CoinPoker. Rare historical bands merge into the nearest supported group. All groups must contain at least 30 fitting players. Fixed seeds make fitting reproducible.

The decision hierarchy fits smoothed action distributions, emphasizing common situations and capping each player’s fitting weight at 3,000 hands. Its squared-error training criterion is only a proxy: every candidate is selected using the same later-action log-loss score. K-means fits players equally.

The score is opportunity-weighted multinomial log loss across entry/defense situations and street-specific betting/folding. Lower is better. A player-level bootstrap checks whether the gain over Pool is positive; it does not treat every action as independent. We select the smallest supported grouping within 0.1% of Pool log loss of the best candidate. This is model-selection validation, not an untouched final test set and not proof of natural, discrete player species.

| Stake | Method | Groups | Withheld players | Later opportunities | Gain over Pool | Old seven bins, refitted gain |
|---|---|---:|---:|---:|---:|---:|
| NL10 | behavior_bands | 6 | 141 | 135,227 | 2.68% | 2.68% |
| NL25 | tree | 6 | 130 | 293,477 | 2.07% | 1.93% |
| NL50 | behavior_bands | 5 | 92 | 316,913 | 3.85% | 3.86% |
| NL100 | behavior_bands | 5 | 73 | 134,917 | 1.07% | 1.06% |

![Held-out action prediction by number of player groups](coinpoker/validation.png)

The old-bin comparison remeasures the historical seven VPIP/PFR categories on the same CoinPoker training players; it does not use 2009 parameter values. Its unmerged benchmark can include poorly supported bins, so it is a comparison rather than an automatically publishable library. Published names are descriptive labels assigned **after** fitting. Sticky/High-fold means at least seven percentage points below/above that stake pool’s fold-to-flop-bet rate, not a claim about profitability or skill. When two groups share a label, their VPIP/PFR appears as a disambiguator.

## Position and player-count validation

A multinomial model learns fold/call/raise entry tendencies from joint position and dealt-player-count observations. Position is distance from the button, with separate blind indicators. Player-type effects are regularized action intercepts fitted with these position effects held fixed, separating type tendencies from table geometry. Open and over-limper situations are modeled separately.

We compare position alone with position plus player count on later decisions of withheld players, preferring position alone within 0.0001 log loss of the best candidate. The following validates the pool geometry versus the previous fixed positional prior; it does not independently validate each published type intercept or extrapolation. Type selection retains its separate validation above.

| Stake | Opening log-loss reduction | Over-limper reduction | Additional count effect selected |
|---|---:|---:|---|
| NL10 | 1.14% | 2.53% | Open: False; limpers: False |
| NL25 | 0.78% | 4.00% | Open: False; limpers: False |
| NL50 | 1.56% | 2.13% | Open: True; limpers: False |
| NL100 | 1.88% | 3.53% | Open: True; limpers: False |

Player-bootstrap gain intervals are positive at all four stakes. These scores are model-selection evidence, not exploit EV gains. Final parameters refit the full sample.

Contexts outside five to seven players extrapolate learned log odds and are explicitly labeled in the editor. If player count was not selected, only positional effects apply. Ante and blind-ratio changes are also labeled as unvalidated transfers. Opening hand composition is inferred; the separate [Ignition model](ignition_models.md) uses known-card observations.

The parser now normalizes repeated `PokerStars PokerStars Hand #` prefixes before splitting, recovering 24,807 validated hands previously rejected as joined blocks. The source files remain unchanged.

## Models

| Stake / type | Players | Player-hands | VPIP | PFR | 3-bet | Fold vs flop bet |
|---|---:|---:|---:|---:|---:|---:|
| NL10 · Pool | 6,371 | 4,946,813 | 25.5 | 16.8 | 8.8 | 44.1 |
| NL10 · Moderate-mixed | 99 | 173,862 | 20.1 | 10.7 | 4.2 | 44.8 |
| NL10 · TAG · 20/16 | 672 | 2,588,922 | 20.5 | 16.0 | 8.5 | 47.6 |
| NL10 · Loose-mixed | 821 | 489,023 | 34.3 | 14.4 | 6.3 | 43.3 |
| NL10 · TAG · 28/20 | 841 | 1,475,673 | 27.9 | 19.7 | 10.3 | 42.0 |
| NL10 · Very loose-passive | 240 | 82,708 | 64.1 | 14.2 | 8.5 | 39.0 |
| NL10 · Very loose-mixed · Sticky | 60 | 18,926 | 59.3 | 35.5 | 20.2 | 35.2 |
| NL25 · Pool | 4,936 | 5,152,391 | 24.7 | 17.1 | 8.9 | 43.7 |
| NL25 · Loose-mixed | 400 | 228,073 | 40.7 | 24.0 | 11.5 | 38.4 |
| NL25 · Very loose-passive | 392 | 150,630 | 51.4 | 11.8 | 7.6 | 40.2 |
| NL25 · Moderate-mixed | 260 | 203,863 | 27.2 | 13.1 | 5.6 | 43.0 |
| NL25 · TAG · 27/20 | 541 | 1,333,030 | 27.0 | 19.7 | 10.1 | 43.0 |
| NL25 · TAG · 18/13 | 234 | 712,547 | 18.4 | 12.8 | 7.1 | 46.3 |
| NL25 · TAG · 21/17 | 435 | 2,433,409 | 21.3 | 17.0 | 8.8 | 46.1 |
| NL50 · Pool | 5,026 | 5,654,278 | 24.4 | 17.5 | 9.3 | 43.7 |
| NL50 · Moderate-mixed | 60 | 94,297 | 19.9 | 9.3 | 3.4 | 43.6 |
| NL50 · TAG · 21/17 | 680 | 3,663,376 | 21.2 | 16.8 | 9.2 | 45.5 |
| NL50 · Loose-mixed | 611 | 351,059 | 34.9 | 14.8 | 6.5 | 41.5 |
| NL50 · TAG · 28/21 | 724 | 1,394,552 | 27.9 | 20.6 | 10.9 | 42.6 |
| NL50 · Very loose-passive | 171 | 57,222 | 63.5 | 12.9 | 8.1 | 38.8 |
| NL100 · Pool | 5,030 | 4,744,009 | 24.7 | 17.5 | 9.3 | 43.6 |
| NL100 · Moderate-mixed | 75 | 81,972 | 21.3 | 9.1 | 3.5 | 46.6 |
| NL100 · TAG · 21/17 | 652 | 2,783,157 | 21.3 | 16.8 | 9.1 | 45.5 |
| NL100 · Loose-mixed | 603 | 314,663 | 34.7 | 14.6 | 5.9 | 42.0 |
| NL100 · TAG · 27/20 | 826 | 1,422,737 | 27.3 | 20.0 | 10.9 | 42.3 |
| NL100 · Very loose-passive | 132 | 49,206 | 59.9 | 15.1 | 7.7 | 38.6 |

## What is measured and what is approximated

- Every rate pools its actual opportunities and outcomes, rather than averaging players’ percentages weighted by unrelated hand counts. Exported estimates use 100 prior opportunities from the stake pool. The aggregate JSON records denominators, sparse fields and any engine constraints.
- Players need 100 earlier hands to fit/validate types. At publication, players with 100 total eligible hands can be assigned with smoothed estimates; shorter histories remain in Pool. Final production groups refit on all eligible earlier players, then aggregate the complete sample.
- The 3-bet field follows GTOpen’s cold single-raise bucket with no caller ahead. Squeezes are measured separately; this is not necessarily a tracker’s combined 3-bet statistic. Fold-to-3-bet and 4-bet refer to the original raiser. Limp-then-face-raise is separate from cold defense.
- Postflop betting with initiative, betting without initiative and facing-bet decisions have separate denominators. The engine’s donk field pools no-initiative bets/stabs; raises facing bets are pooled across streets. All-in runouts do not generate fictitious checks or betting opportunities.
- Position, stack band, actual occupancy and size-band counters are retained in each public aggregate. Joint position/player-count entry opportunities now replace the fixed positional prior. Other response rates and stacks remain pooled. Hand composition remains reference-ordered; this is not learned from selectively revealed CoinPoker cards.
- `flatten=0` deliberately uses GTO reference hand ordering. Hole-card composition was not fitted; zero is a modeling assumption, not measured intelligence or skill. Shove responses still follow GTOpen’s adaptive large-bet model.
- The current engine can choose only the smallest/largest configured size. The exporter maps the majority opening-size band (up to 2.5bb versus larger) and bet-size band (up to 60% pot versus larger) to those choices. These are approximations, not an exact sizing distribution. Defense bands are floored at the overall 3-bet percentage where the engine requires it; such adjustments are recorded.
- Site population samples are not random censuses. Dealer coverage, observation dates, selection into long histories and unusual-hand exclusions can affect the results. Prediction gains do not establish an exploit EV gain or exact hand ranges.

## Data checks and exclusions

The parser validates action order, street progression, calls including short all-ins, stack limits, blind/button order, and exact cent-level contributions against the recorded total pot after uncalled returns. Forced blinds/antes are not VPIP. Sitting-out/out-of-hand seats are not dealt players. Implicit all-in raises are reconstructed only when their amount equals the actor’s remaining stack.

Deduplication is by hand ID within each site/stake input. Timestamp shifts, trailing padding and showdown-only differences do not create extra action observations. One inspected NL10 duplicate disagreed about the showdown winner; these models do not use winners, revealed cards or win rates. A conflicting **action** duplicate stops fitting for review.

Four-max tables, hands dealt to fewer than five players, extra/missing blinds, dead-button cases, irregular antes, under-minimum raises and multiple runouts are excluded from this release. Excluding those hands can particularly affect short-stack and all-in behavior; they are not quietly treated as standard situations.

| Stake | Raw records | Repeated IDs | Accepted | Excluded distinct hands |
|---|---:|---:|---:|---:|
| NL10 | 1,123,619 | 159,571 | 773,370 | 190,678 |
| NL25 | 1,196,362 | 246,791 | 802,608 | 146,963 |
| NL50 | 1,007,282 | 13 | 873,554 | 133,715 |
| NL100 | 901,515 | 37 | 734,030 | 167,448 |

Full exclusions, position/size counters, model-selection scores, opportunity counts and model parameters: [NL10](coinpoker/NL10.json), [NL25](coinpoker/NL25.json), [NL50](coinpoker/NL50.json), [NL100](coinpoker/NL100.json).

## Reproduce

Python 3.12; NumPy 1.26.4; scikit-learn 1.5.2; Matplotlib for the figure. No solver session is built or changed by the data pipeline.

```powershell
python -m unittest discover -s tools/coinpoker -v
python tools/coinpoker/analyze.py --source "T:/Dev/Poker Data/hhdealer/CoinPoker" --out output/coinpoker --workers 4
python tools/coinpoker/fit.py --input output/coinpoker --out docs/coinpoker --publish cache/archetypes.json
python tools/coinpoker/report.py
```

Per-player counters in `output/coinpoker` remain local. The fitting command without `--publish` creates reviewable aggregates without changing the library. Publishing replaces only the `Data · CoinPoker ·` collection and preserves other models. No raw data is uploaded.
