# Final analysis of the matched stack-depth comparison

Prepared 1 October 2026 while the registered evaluation is running. This is a
root review checklist, not a new protocol, result, admission or permission to
modify the study. No interim payoff estimates or range probabilities were read
to prepare it. Existing scientific gates and the single final look remain fixed.

## What this comparison measures

The candidate adds 25 river hand-versus-board inputs to a 362-input baseline.
Both train the full existing heads-up preflop/flop/turn/river action tree; the
extra inputs are zero before the river, so upstream changes must arise through
learned continuation. This is distinct from the older terminal river Fold/Call
diagnostic. Its result cannot be substituted for that separate prediction test.

The entry spot is BB facing a BTN min-raise after SB folds, with 0.5bb dead money,
5% rake capped at 2bb. The inherited 200bb BTN entry range is held constant at
every depth to isolate continuation effects. It is not an optimized opening
range at each stack. This is neither a complete multiway game nor an external
accuracy comparison against GTO Wizard or observed player histories.

## Evidence required before interpreting outcomes

1. Verify the actual evaluator and final reader exited successfully, including
   immutable started/finished process identities, exit codes and log identities.
   Observe the sole existing helper; do not independently launch its consumers.
   A timeout is not failure. A partial/failed started attempt requires review;
   do not automatically retry it or change the registered budget.
2. Authenticate final registration, consumed input identities, actual four
   training banks and source provenance. Preserve recognized old failures and
   authenticated completed-boundary recovery evidence.
3. Confirm every arm has 64 completed cycles, played generations 0..63 and
   actor weights 1..64 (sum 2080). Authenticate and exclude unplayed generation
   64. Test results must not select a model, checkpoint, teacher or weight.
4. Inspect the reader's actual coverage rather than infer it from a pass flag:
   256 reconstructed training chance cycles, 896 evaluation archives,
   28 complete preflop catalog CPU-reference replays and 14 prespecified
   first/last 32-deal postflop batch replays. Not every postflop policy row is
   replayed, and the reader shares the original native payoff oracle.
5. Verify fit depths 20/40/100/200/400 and held-out fitting depths 60/150 from
   actual registry fit state and retained training evidence. Known geometry for
   an evaluation depth is not itself training-data leakage or evidence of fit.
   Evaluation uses independent full-deck physical draws, not strictly disjoint
   training/test boards; training collisions were not filtered.
6. Check exactly 4096 fresh physical deals per depth, seeds 9309000 + depth,
   eight within-replication crossed profiles and all 56 paired comparisons.
   Verify cashflow, legal actions, physical-card compatibility, all-in values
   and source-to-native-value bindings within the reader's stated scope.

## Interpret every planned comparison

For each replication A and B, compare replacing BB against baseline BTN and
candidate BTN, and replacing BTN against baseline BB and candidate BB. These
four gains per replication keep the opponent fixed for each replacement;
comparing just candidate-versus-candidate to baseline-versus-baseline obscures
which actor changed. Common physical deals couple the comparisons, and the
registered uncertainty method permits this dependence.

Report all seven depths, both actors, both replications and all 56 comparisons,
including adverse results. Use bb per entry, not an unconditional cash-game
win rate. For pooled values divide each depth's gain by its starting stack and
weight depths equally. Do not pool raw bb values so that deep games dominate.

Recompute/check the primary decision exactly: all eight equal-depth normalized
bounded-interval lower limits must be strictly positive AND none of the 56
per-depth mean gains may be negative. Keep the registered simultaneous
empirical-Bernstein intervals (family alpha .05) and one final look. An
exploratory normal interval cannot replace this gate. If the gate fails,
state whether results are adverse, mixed or inconclusive; failure to establish
improvement does not establish equivalence. Report uncertainty in payoff units,
not as percentage-point uncertainty in hand-range frequencies.

Include the declared negative-deal fraction, signed paired-loss 95th/99th
percentiles, worst observed paired loss, mean positive paired loss and
individual-deal value extrema. A negative signed loss is a gain. Separate the
held-out depths explicitly rather than letting a pooled score conceal them.

Positive value against these frozen opponents is not a best-response bound,
exploitability estimate or equilibrium certificate. It is conditional evidence
about the four fixed banks in this entry family.

## Read ranges as descriptive behavior

Only after final evaluation and successful independent verification, inspect
all 28 depth/arm exports. Confirm policy identity, legal action geometry,
physical compatible-card weights, chronological action history, true arriving
ranges and own-history weighted support. Frequency totals must use the actual
arriving range and blocker-adjusted mass; equal weighting of 169 classes is not
valid. Every preflop branch must conserve the registered entry population.

Compare weighted action totals and hand-class changes across both replications,
especially at 60/150bb. Highlight supported calls/folds/raises and unstable
boundary hands, while making clear that plausible-looking matrices are not
external accuracy measurements. Do not interpret decisions in negligible or
zero arriving support as robust recommendations for that hand.

## Deliverable and outstanding goal

Save a concise plain-English analysis, complete numerical comparison table and,
if useful, a static scientific figure showing primary intervals and held-out
stack results. Bind them to terminal evidence and disclose replay, chance,
statistical and fixed-entry limitations. Describe next steps justified by
these results, preserving adverse evidence.

The separate correctly targeted continuation-prediction diagnostic remains
unregistered/unadmitted. No new scientific trial, production56708 change,
GitHub push or deployment is authorized by this checklist or a statistical
pass. Robust flexible preflop ranges across positions, entry histories, stacks,
rake, sizes and multiway situations remain the broader goal. Do not mark that
goal complete from this comparison.
