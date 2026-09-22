# Second-context study: BB defense

Status: export and accounting qualification passed. Full-panel memory planning
also finished and rejects the existing storage design for this wide context.
See `CAPACITY-FINDINGS.md`. No new blind-defense policy has been trained or deployed.

The completed independent 190-flop comparison supports weighted training in
one three-bet response situation. The next question is whether that benefit
transfers to a BB facing an open, including the calling hands the application
has historically undervalued. Success means lower independently evaluated
deviation gains in the new situation, not making a chart look looser or adding
mixed strategies by hand.

## Qualified candidate

The read-only export comes from `7max 200bb corrected multiway 20260910.gtop`:
UTG through CO fold, BTN raises to 2 bb, SB folds, and BB acts with 1 bb posted.
There is no straddle. BB calls one additional bb; no third player remains live.

- Seven-player source, 200 bb stack, 0.5/1 blinds, no ante, 5% rake capped at 2 bb.
- OOP is BB, IP is BTN, regardless of their original numerical seat indices.
- Root pot 3.5 bb; folded SB contributes 0.5 bb of dead money.
- BB retains all 169 classes. BTN has 96 classes above the existing negligible
  entry-weight cutoff. Do not narrow BB's support to make memory admission easier.
- Three distinct postflop continuations: pot/remaining stack 4.5/198,
  12.5/194, and 36.5/182 bb. All-in showdown pot is 400.5 bb.
- The postflop-to-preflop utility adjustment is 0.25 bb per player here, not
  the original study's 1.75 bb. BB folding at entry loses its posted 1 bb;
  BTN receives a net 1.5 bb. These values sum to the 0.5 bb dead contribution.

The incoming BTN range inherits a **calibrated approximate preflop solve** at
iteration 578. It is a reproducible conditional input, not measured player
behavior, a GTO Wizard range, or a newly validated opening range. Using it can
test continuation methods given that range; it cannot validate the upstream
opening strategy or the whole seven-player game. Folded players' private cards
remain omitted. This candidate is currently qualified for geometry only.

## Evidence completed

`conditional_hu_context_export` derives player order, terminal types, pots,
remaining stacks, and utility offsets from saved-game nodes. It leaves the
original hard-coded exporter and research executables intact. Source save and
equity-cache hashes are identical before and after export; in-memory strategy
arenas are also checked for mutation.

`export-audit.json` records independent Python checks of all action transitions,
live-player masks, topology, investments, strategy normalization, fold outcomes,
and terminal chip/rake conservation. Seven intentionally corrupted inputs were
rejected, including the old pot offset, wrong seat order, and a third live player.

As a regression check, the new exporter reproduced the original 12-node study's
incoming ranges and all saved strategies exactly. Its two postflop leaves still
derive to 39.5/182 and 93.5/155, with the original 1.75 bb offsets. Terminal actor
and winner fields that do not apply are now null rather than arbitrary seat
labels; decision actors and fold winners match exactly.

## Work before the next experiment

1. Plan memory for the wide BB/BTN support and all three continuation branches.
   The three texture probes are resource checks only, not a training/test panel.
2. Introduce a separate context-driven training/evaluation executable. Replace
   fixed leaf indices, two-branch allocation, player order, rake, chip bounds,
   and four-action root-report assumptions. Keep completed evidence reproducible
   with its original binaries and snapshots.
3. Validate the generalized executable against the original context and against
   independent BB fold/call/raise/jam cashflow controls. Verify exact imported
   policy preservation for evaluation.
4. Freeze the chosen incoming range, action menu, training panel, disjoint test
   panel, weights, budgets and stopping rules before inspecting new outcomes.
   Compare weighted and equal training under otherwise identical conditions.
5. Train only after actual RAM/VRAM admission with reserves and a live idle guard.
   Do not use reduced entry support or an easier action tree as a substitute for
   the stated blind-defense question.

Production port 56708 is untouched. All work in this directory is research;
no production solver logic or player model is changed.
