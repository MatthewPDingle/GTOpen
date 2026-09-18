# A small external benchmark for preflop accuracy

Captured from the user's open GTO Wizard subscription on 18 September 2026.
**Six situations, eight hands each, with all suit combinations verified.**
This is the first reference set for judging the next GTOpen experiment. No
model was trained, no solve started, and port 56708 was not changed.

## What is in it

Eight players, 200 original-bb stacks, SB 0.5, BB 1, straddle 2, opening size
6bb. The open Wizard solution is **NL25: 4% rake capped at 6bb**. It is separate
from our [earlier rake-free comparison](../wizard-action-ev-20260915/README.md).

| Decision | Raise size | Raise | Call | Fold |
|---|---:|---:|---:|---:|
| UTG unopened | 6bb | 13.4% | — | 86.6% |
| LJ facing UTG's open | 18bb | 5.3% | 1.5% | 93.2% |
| SB facing UTG; intervening players folded | 24bb | 5.1% | 0.3% | 94.6% |
| BB facing UTG; intervening players folded | 27bb | 4.6% | 2.8% | 92.6% |
| STR facing UTG; everyone else folded | 30bb | 4.1% | 13.3% | 82.6% |
| UTG facing LJ's 18bb 3-bet; others folded | 45bb | 12.6% | 18.7% | 60.1% |

The final row also jams 8.6%; the other rows display jams as 0.0%, with tiny
nonzero per-hand remnants possible. These are rounded whole-range frequencies.
The 3-bet response is conditional on UTG having opened, not all dealt hands.

The fixed hand probes are AA, A5s, KQo, QJs, 99, 88, 55 and 76s. They intentionally
cover premiums, borderline pairs, suited hands and offsuit broadways; they are
not a representative sample of the whole range.

## What this already tells us

- Almost no SB calling can be correct in this particular configuration. The
  closing straddler is a much stronger test of whether GTOpen undervalues calls.
- A different mix is sometimes inexpensive. UTG opens 99 about 72.79% and 88
  about 34.37%, but raising and folding both display 0.00bb. Matching those exact
  percentages is a poor optimization target at the displayed precision.
- Other decisions have a clear cost. STR's QJs call displays +0.21bb, 99 call
  +0.98bb and 55 call +0.33bb relative to folding. Routinely folding those hands
  would be a meaningful discrepancy against this reference continuation.
- After UTG opens and faces LJ's 3-bet, 55 calls for +0.53bb and 76s for +0.55bb,
  while KQo calling displays -2.54bb. A blanket wider or tighter response cannot
  fix both kinds of mistake.

These are Wizard values against its continuation policies, not new measurements
of GTOpen's error. The live GTOpen game has SB 0.4, rake 5% capped at 4.1bb and
different raise menus, so it is **not eligible for a matched comparison**.
The old rake-free results also must not be scored against these NL25 labels.

## Files and use

- `ui-captures.json`: source URLs, settings, action frequencies/EVs and individual
  combo identities. EVs come from visible action legends; percentages from the
  rendered combo-bar widths. No hidden endpoint or application state was read.
- `PROTOCOL.md`: fixed development/reserved split and interpretation rules.
- `score.py`: validates observations and reports local action regret per hand,
  alongside frequency differences and a rounding-only uncertainty interval.
- `test_score.py`: seven checks covering costly and harmless disagreements,
  wrong settings/actions, stale hand identities, suit differences and NaNs.

From this directory, run `python score.py` to validate the capture. Run
`python -m unittest -v test_score.py` for the checks. To score a candidate,
run `python score.py candidate.json`. A candidate has this shape:

```json
{
  "context": "replace with an independently audited context object matching ui-captures.json",
  "cases": [{
    "id": "nl25-utg-open",
    "hands": {"99": {"Allin 200": 0, "Raise 6": 0.5, "Fold": 0.5}}
  }]
}
```

Probabilities are fractions, not percentages. Case IDs specify the exact actor
and history recorded in the corresponding source URL. Only provide a context
match after checking the candidate's actual settings; copying the object is
not evidence of a match. Partial coverage is explicitly reported. The scorer
does not run GTOpen or silently map different bet sizes to reference actions.

## Next experiment

First run a separate GTOpen baseline matching these inspected settings and
audit its later raise rules. Then compare the same 48 probes, solve time and
convergence target. Use action-value loss to prioritize work; use frequencies
as supporting evidence. Full downstream/postflop tree equivalence and Wizard's
no-flop-no-drop convention remain unverified, so this remains a diagnostic
benchmark rather than an exact solver-equivalence test.

Keep the proposed 100bb cases unopened until a candidate is frozen. They are
reserved future tests, not collected holdout evidence. No next model search or
deployment was started as part of collecting this set.
