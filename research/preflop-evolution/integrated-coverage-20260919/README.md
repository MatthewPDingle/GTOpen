# Board coverage and folded-card research

Research only; the application on port 56708 is unchanged. This follows the
[connected preflop/postflop prototype](../integrated-continuation-20260919/README.md).

## What is established

The solver can reuse a board under all 24 suit relabelings without allocating
24 postflop solvers. A separate vector-algebra check agreed within 8.9e-16;
an explicit 24-copy river solve agreed within 4.4e-7 bb through 100 iterations.
This averages counterfactual values inside the connected solver, not final
strategies from separately solved games. Public-board strategies retain
individual hole-card combos and full turn/river enumeration.

The original two boards, closed under suit relabeling and using a 50% bet
menu, converged to 0.002057 bb combined deviation gain in 129.9 seconds.
Its root strategy is 58.87% fold, 24.52% call, 16.60% 4-bet and negligible
jam. AA almost always 4-bets. The earlier literal two-board, 50%/75% menu
mixed AA between calling and 4-betting. **That difference is not yet attributed
to a single cause**: two controls are registered to separate suit coverage
from betting-menu effects. Neither result is a recommended poker range.

The preselected ten-board smoke run completed and passed probability and
pot/rake accounting. Five-board panel A passed through 500 iterations
(0.04284 bb combined gain). The longer run was deliberately stopped when a
new production preflop solve began. Its valid 500-iteration output is retained
as `panel-a-interrupted-500.json`. No production process was interrupted.

## Folded cards: completed independent audit

We sampled 34 million physical deals: two million conditional entry deals,
plus four million for each of eight preselected hands. Each deal was used
twice, with and without the likelihood implied by the six earlier folds.
Cards were mutually disjoint, and boards came from the remaining deck.

| UTG hand | Equity vs entering LJ range | Including six folds | Change, percentage points (95% interval) |
|---|---:|---:|---:|
| AA | 83.255% | 83.285% | +0.029 [0.018, 0.041] |
| AKs | 49.827% | 50.107% | +0.280 [0.269, 0.292] |
| AKo | 47.243% | 47.523% | +0.280 [0.268, 0.292] |
| QQ | 58.584% | 58.109% | -0.474 [-0.486, -0.463] |
| JJ | 51.072% | 50.653% | -0.418 [-0.438, -0.399] |
| TT | 45.171% | 44.878% | -0.294 [-0.313, -0.275] |
| 99 | 38.503% | 38.363% | -0.140 [-0.155, -0.125] |
| AQs | 40.338% | 40.444% | +0.106 [0.092, 0.120] |

These are raw equities against the **entering** LJ range, not equities against
its later calling range and not action EVs. Intervals are pointwise paired
batch estimates. Earlier opening/3-betting/folding policies stay fixed.
This measures one scenario, not a universal fold adjustment.

![Paired equity changes from the earlier folds](fold-equity.png)

Effective sample sizes were 3.62–3.74 million per four-million-hand probe.
The proposal's class frequencies passed an independent exact enumeration
of 1,326×1,326 private-card pairs (largest supported-cell discrepancy 1.75
standard errors). Unit fold weights produced identical paired controls.

The six folds slightly favor remaining high cards. In this entry population,
ace-high flops increase by about 0.205 percentage points and king-high flops
by 0.176 points. The live players' class priors also shift. This is why a
single generic equity penalty or marginal-range correction is inadequate:
the posterior links both live hands and future boards. Giving a postflop
solver the actual hidden folded cards would leak information; any future
integration must share strategies across those unobserved possibilities.

## What remains

1. Finish panels A, B and their ten-board union using the same bet menu.
   Compare converged strategies, not merely the solver's numerical gaps.
2. Run the two controls that isolate suit coverage from bet-menu changes.
3. If small panels disagree materially, expand chance coverage with a method
   that fits memory before drawing range conclusions. Keep the reserved
   ten-board panel untouched until a new validation protocol is registered.
4. Incorporate folded-card uncertainty into the connected game without
   revealing hidden cards or replacing the joint posterior by marginals.

The expanded panel reduces the private-pair prior's total variation from
16.63% for the earlier literal two boards to 3.96% for the weighted ten-board
sample. This is a distribution-distance diagnostic, **not** a bound on poker
strategy error or proof that ten boards are enough.

## Resume and verify

The queue is a manual foreground runner. It checks production state before
launching and during every run, and stops only its own research process if
production starts solving. It also leaves the app's resident GPU allocation
in place and skips panels that cannot fit a conservative memory budget.
Interrupted checkpoints are preserved; they contain reported preflop policies,
not full postflop arenas, so resuming restarts that experiment from iteration 1.

From the repository root, with Python 3.12, numpy, scipy and matplotlib:

```powershell
python tools/research/integrated_coverage_queue.py
python tools/research/integrated_coverage.py audit
python tools/research/integrated_coverage_review.py folds
python tools/research/integrated_coverage_review.py report
# Only after both additional controls finish:
python tools/research/integrated_coverage_review.py controls
```

`freeze.json`, `fold-freeze.json` and `control-freeze.json` record the original
protocol, inputs and executable digests. A rebuild with a different digest
requires an explicitly documented new run registration; do not replace the
old freeze silently. No reserved Wizard case is opened by these commands.

See [coverage-audit.json](coverage-audit.json), [fold-review.json](fold-review.json),
[PROTOCOL.md](PROTOCOL.md), [FOLD-PROTOCOL.md](FOLD-PROTOCOL.md) and
[CONTROL-PROTOCOL.md](CONTROL-PROTOCOL.md) for the detailed evidence and scope.
