# Separate preflop holdout and source routing

The future prediction comparison needs a test it cannot accidentally train on.
Preflop has no visible flop, so a future board cannot define its test split. This
helper provides an explicit optional test based on the acting player's own
169 hand classes. No actual scientific split, seed or budget is chosen here.

For a held hand class, every suit combination stays on the same side. That class
is excluded from predictor fitting on all streets, for both actors and at every
stack depth. Otherwise, the same predictor could see its supposedly unseen
preflop hand in postflop training. This is a demanding test of generalizing to
unseen hand classes, not the only useful way to measure preflop accuracy.
The original common teacher can know those hands; the exclusion applies to the
new supervised predictors.

Postflop rows also retain the already-qualified public initial-flop split. Turn
and river descendants keep that flop's side. Held stack depths, held own hands
and held public flops are recorded as separate test axes. Only visible own cards
and the currently visible public prefix enter this routing. Opponent cards and
hidden future boards have no argument slot. Partition flags are bookkeeping,
never model input. Preflop conditional action values must still integrate all
legal future boards, rather than conditioning on a future fit/test flop.

## Parent sources and weighting

Row-level splits alone do not prevent reuse of a physical parent hand: its two
actors or later decisions might land on different sides. This helper therefore
requires prospectively distinct fit and evaluation source identities. A fit
source discards test-classified rows before generating labels. An evaluation
source supplies test rows only; its other fit-like rows cannot enter training.
All decisions descended from the same source draw share one cluster identity,
regardless of actor or street. Independent sampling and source/seed provenance
must be established by the eventual registration; distinct hashes do not prove
independence.

The exhaustive catalogue records 1,326 physical own-card combinations and their
169 classes: 13 pairs have six combinations, 78 suited classes have four, and
78 offsuit classes have twelve. Those are combinatorial counts, not entry-range,
opponent-blocker or action-reach weights. Actual sampling, importance weights,
supported-state rules and descendant weights must still be specified. Teacher
queries over hidden-card hypotheses are inference plumbing, not extra predictor
training examples.

## Completed implementation checks

`stack_context_private_hand_holdout_v1.py` is not imported by the live four-arm
study. Its CPU check passed in 1.906 seconds with synthetic explicit contracts:

- All 1,326 physical pairs match the existing native class/count convention;
  63,648 suit and card-order transformations preserve the assignment.
- 112 routing controls cover both actors, both source sides, held/fit depth,
  held/fit own hands and held/fit visible flops. They include 96 postflop
  descendants and 2,304 complete visible suit transformations.
- 918 already-retained native observations at 20bb/60bb yield 1,836 routed
  source-side controls. Preflop padding stays hidden; held depths cannot enter
  fitting; neither actor's evaluation-source rows become training rows.
- 31 malformed-contract, source-reuse, hidden/future-card and invalid-state
  cases are rejected.

The independent reader authenticated eight consumed source/fixture identities
and recomputed card classes, physical counts, source clusters and all visible
routes without importing the new splitter. Its synthetic private split has
946 fit and 380 test physical combinations; these numbers are qualification
parameters, not a registered data allocation. The catalogue's semantic digest
uses integer multiplicity keys; the reader explicitly restores their declared
type after JSON decoding when authenticating that digest.

Evidence begins `stack-context-private-hand-holdout-check-v1` and
`stack-context-private-hand-holdout-readback-v1`. No new scientific samples,
native invocation, predictor fitting, CUDA work or accuracy result was produced
by these controls. Production and registered main-study inputs remain unchanged.

## Still outstanding

The complete main comparison must finish all 64 cycles per arm, pass the actual
complete-bank resource gate, complete fresh evaluation and independent readback,
and receive a plain-English analysis. The separate prediction diagnostic still
needs the prospectively fixed complete A-baseline teacher, actual sampling and
holdout choices, unsupported-state handling, declared data/label-noise/fit
budgets, seeds, selection, scoring and uncertainty registration. This helper
qualifies an available holdout option; it does not admit or complete that trial
or demonstrate better flexible preflop ranges.
