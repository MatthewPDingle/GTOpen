# Ignition NL10 regular: separate postflop betting contexts

This retrospective audit separates the situations previously combined under
the pool's 25.25% `donk` / “bet without initiative” statistic. It is population
evidence for a conservative contextual model, not a measured KQ9 strategy.

The independent collector reproduces **34,466 fully validated hands** from
38,342 raw records, using the unchanged Ignition converter, source selection,
deduplication and canonical replay exclusions. It checks every extracted
zero-price opponent action against the canonical replay's old postflop
counters before accepting a hand. **542 source sessions** contain eligible
heads-up postflop decisions. Hero observations are excluded; opponents' actions
against hero remain included. No raw cards, histories or player identifiers are
published in the evidence artifact.

## What counts

Only hands with exactly two players reaching the flop are included. Both must
still have chips at the decision; all-in runouts do not generate synthetic
checks. Facing-bet decisions are excluded from this betting-opportunity model.
A real all-in lead is a bet in the numerator, but its size is counted separately.

The last aggressor is carried through checked-through streets. Classification
occurs before the first bet on each street, using actual checks already made:

- **Donk:** OOP flop action without initiative, before the preflop aggressor acts.
- **Lead:** OOP turn/river action without initiative, before the previous
  street's aggressor acts.
- **Probe:** OOP turn/river action without carried initiative after the preceding
  street checked through.
- **Stab:** action without carried initiative after that initiative holder
  already checked this street.

Situations with no identifiable carried initiative are explicitly recorded as
`no_initiative_other`; they are not silently included in donks or probes.
Initiative-holder bets are also retained as audit rows, not exported as new
c-bet targets. A limped pot can acquire an aggressor postflop, enabling later
lead/probe/stab observations.

Pot type is defined by preflop raise count: zero = `limped`, one =
`single_raised`, two or more = `three_bet_plus`. Multiway flops that later become
heads-up remain excluded. Short raises and other invalid canonical histories
remain excluded rather than patched into this new dataset.

## Main findings

| Context | Single-raised bets / opportunities | 3-bet+ bets / opportunities |
|---|---:|---:|
| Flop donk | 735 / 5,048 = 14.56% | 131 / 911 = 14.38% |
| Flop stab | 602 / 1,409 = 42.73% | 193 / 420 = 45.95% |
| Turn lead | 182 / 1,930 = 9.43% | 30 / 368 = 8.15% |
| Turn probe | 525 / 1,302 = 40.32% | 88 / 180 = 48.89% |
| Turn stab | 432 / 941 = 45.91% | 144 / 280 = 51.43% |
| River lead | 170 / 844 = 20.14% | 26 / 160 = 16.25% |
| River probe | 518 / 1,191 = 43.49% | 77 / 164 = 46.95% |
| River stab | 249 / 648 = 38.43% | 56 / 152 = 36.84% |

This separation has substantially more support than using one 25.25% target
everywhere. It still does not establish a 14.38% lead on a particular flop.
Opportunity counts are correlated within hands and sessions and should not be
treated as independent effective sample sizes.

## Historical validation

The fixed chronological boundary is **2025-11-03**, already used and inspected
in earlier project research. This is **not a fresh holdout**. Train sessions
end before the boundary; evaluation sessions start on or after it. Four
boundary-straddling sessions are excluded to keep sessions disjoint:

- 456 eligible training sessions and 82 eligible evaluation sessions.
- 2,978 evaluated no-initiative opportunities across 81 scoring sessions.
- Broad pooled baseline log loss: **0.55586**.
- Street/kind/pot-context estimate log loss: **0.48357**.
- Paired session-bootstrap improvement: **0.06245 to 0.08147** nats per
  opportunity (95% descriptive interval; 1,000 resamples, seed 20260910).

The contextual estimate uses a fixed 20-opportunity prior toward the earlier
period's eligible pooled no-initiative rate. It was not optimized on these
evaluation outcomes. The comparison tests historical contextual aggregate
prediction, **not** the solver's final regularization, per-hand distribution,
board-specific calibration, or profitability. The artifact includes each
context's predicted and observed later rate. No runtime release gate or
automatic expansion to other datasets is inferred from this comparison.

## Reproduce without interacting with running reports

From the repository root:

```powershell
python tools/ignition/postflop_contexts.py --source "T:/Dev/Poker Data/Ignition" --out research/ignition-postflop-contexts/evidence.json
python -m unittest discover -s tools/ignition -p test_postflop_contexts.py
```

The collector uses Python's standard library, one process, no GPU, and a
20 ms pause between source files. It reads source histories and writes only the
chosen aggregate artifact. It never calls a running server, changes the
canonical model library, restarts a process, or loads a live solve.

`evidence.json` records dependency hashes and an ordered source-content digest.
Its `contextual_bets` rows have the runtime-compatible fields:

```json
{"street":0,"kind":"donk","pot_type":"three_bet_plus","opportunities":911,"bets":131}
```

For the optional runtime profile, these rows can be wrapped as
`{"version":1,"source":"Ignition NL10 regular; HU postflop; contextual evidence v1","cells":[...]}`.
The separate `all_contexts` rows contain ordinary bet-size band counts and
all-in bet counts for auditing. Sizes are not fitted or projected into tree
actions here. This file does not update any live or saved model automatically.

Fourteen focused tests cover donk/check denominators, stabs, leads, probes,
initiative transfers, limped/3-bet pots, hero removal, multiway exclusion,
all-in runouts, actual shove counts, incomplete histories and chronological
session separation.

## Staged library migration (not activated)

`tools/ignition/migrate_postflop_contexts.py` defaults to a read-only dry run.
It verifies the exact corpus fingerprint and matches library entries by source
provenance (site, stake, anonymous-pool type, dates, hand/session counts and
dataset site), never merely their displayed names. Renamed copies with matching
provenance are eligible. It accepts f32 serialization roundoff but skips
changed or missing postflop statistics, other stakes, other player populations,
and existing different contextual evidence. Preflop data, model IDs and all
other fields are preserved exactly. Already upgraded entries are idempotent.

```powershell
python tools/ignition/migrate_postflop_contexts.py
python tools/ignition/migrate_postflop_contexts.py --out "T:/Dev/GTOpen-contextual-postflop/cache/archetypes.json"
python -m unittest discover -s tools/ignition -p test_migrate_postflop_contexts.py
```

An output path is required to write. In-place writes, overwriting evidence, and
writing the primary `T:/Dev/GTOpen/cache/archetypes.json` are forbidden. Eleven
focused migration tests cover preservation, provenance, custom edits,
idempotence, evidence validation, float roundoff, write boundaries, and source
LF/CRLF and trailing-newline preservation. Output uses two-space JSON formatting
and writes encoded bytes explicitly, avoiding Windows newline translation.

The staged full library updated **one of 46 entries**, the unchanged Ignition
NL10 regular pool. Other entries were preserved. The input hash remains
`6e7e006b1f89e0d8aec23a8cd3ba7eaf491f13cdfadcf312e9d1fd84ac8f349c`;
the isolated candidate hash is
`776862208cd18b53c8142a8e66ab3fbf9f6cf32bc6e6da37f897be3c60cbfd4c`.
The complete audit is `staged-library-migration.json`.

This candidate is **not activated in the primary application**. Running
reports, saved report snapshots, current seat profiles and browser-local model
copies are not changed by staging this file. Deployment and any source-verified
saved-copy migration remain separate operations after preserving active work.

The current browser's **Save Player** path saves a generated `SeatProfile`
with its HUD stats and postflop tendencies. Selecting an archetype does not
copy its full library `source` provenance into that profile. Such saved profiles
are not eligible for this library migration solely because their names or
dataset-site strings look similar. Existing saved profiles and current seat
snapshots therefore retain their old postflop settings. After activation,
reselect the updated measured pool for the desired seat to obtain its new
context evidence; separately preserve any hand-painted custom ranges before
replacing a profile. This staged migration never silently replaces custom or
saved ranges.
