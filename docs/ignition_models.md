# Ignition NL10 regular: measured opening ranges

Recorded 2025-08-20 to 2025-12-02; model built 8 September 2026. The library entry is **Ignition · NL10 regular · Pool**, under Manage models. This is an anonymous opponent pool, excluding every `[ME]` observation. It is a separate source from CoinPoker and is never presented as measured CoinPoker behavior.

## What the model contains

- **34,466 validated hands** in **555 file/session groups**, with three to six players dealt in. No ante; small blind 0.5bb. Stack depths are pooled.
- First-in hand probabilities use all known-card opportunities: raises, folds, and calls/completions. A player folding before showdown still has a known hand. The 169-hand index and combination weights match the Rust engine (pairs 6, suited 4, offsuit 12).
- Hand/action counts first borrow a global action prior, then each position/player-count/hand cell borrows the pooled hand estimate. Smoothing strengths are selected on separate later sessions. This gives probabilities rather than cutting a deterministic range from reference rankings.
- The engine consumes these probabilities directly for the unopened-pot bucket. Over-limper, defense and postflop rates come from the same validated opponent sample, but their **hand composition remains inferred**. Over-limper rates in this first Ignition release are pooled, not a learned per-hand isolation model.
- The editor's dataset checkbox keeps measured entry policies active. Uncheck it to edit first-in/over-limper rates and return to reference-generated entry ranges. Hand painting remains available. Saved profiles preserve the dataset for later generation.
- Unsupported positions/table counts borrow the nearest observed context; outside three to six players is visibly labeled as extrapolation. Ante and blind-ratio changes are labeled as unvalidated transfers. None of this establishes a live-casino or cross-site population model.

## Validation

Sessions are split chronologically: training before 2025-10-05; tuning from that date until 2025-11-03; untouched test from 2025-11-03. Entire sessions crossing a boundary are excluded from evaluation (4); they return only for the final production refit. Split sizes: 331 training, 137 tuning, 83 test sessions. This prevents adjacent hands in the same session being scattered across training and test.

The selected smoothing uses 10 prior opportunities per context/hand and 5 per pooled hand. The final test contains **12,828 first-in decisions**.

| Predictor | Untouched-test multinomial log loss (lower is better) |
|---|---:|
| Hand-independent contextual action frequencies | 0.80821 |
| Reference-ordered ranges with measured context totals and tuned smoothing | 0.61275 |
| Learned known-card ranges | 0.46486 |

Learned ranges reduce log loss by **24.1%** versus the reference comparator. A 1,000-resample session bootstrap gives a positive 95% interval for absolute log-loss improvement: **0.1383 to 0.1578**. The comparator uses GTOpen's OPEN_SCORE plus cached equity tie-breaking, fills to training context totals, and tunes a probability mixture on validation sessions. It is a smoothed reference-order benchmark, not a fresh equilibrium solve for the held-out games. The global-frequency comparator likewise receives no test labels.

These scores measure action prediction, not exploit profitability or solver accuracy. Final publication refits the chosen method on all validated sessions after the untouched test is scored. Future periods and different sites remain untested.

![Opening-range validation](ignition/validation.png)

## Sample depth

Roles: BTN=0, CO=1, HJ=2, LJ=3, continuing backwards; SB=-1. BB has no first-in opening decision after everyone folds. Many cells are sparse, which is why estimates borrow information rather than reporting every observed fraction as precise.

| Players | Role | First-in opportunities | Hand classes observed | Median opportunities per class |
|---|---:|---:|---:|---:|
| 3 | -1 | 697 | 157 | 3 |
| 3 | 0 | 1,204 | 168 | 7 |
| 4 | -1 | 1,417 | 168 | 8 |
| 4 | 0 | 2,478 | 168 | 13 |
| 4 | 1 | 3,413 | 169 | 15 |
| 5 | -1 | 2,615 | 169 | 12 |
| 5 | 0 | 4,562 | 169 | 20 |
| 5 | 1 | 6,598 | 169 | 29 |
| 5 | 2 | 9,033 | 169 | 41 |
| 6 | -1 | 2,706 | 168 | 13 |
| 6 | 0 | 4,881 | 169 | 24 |
| 6 | 1 | 7,345 | 169 | 37 |
| 6 | 2 | 10,340 | 169 | 45 |
| 6 | 3 | 14,060 | 169 | 68 |

## Parsing and exclusions

The adapter validates dealt-card uniqueness and board/hole-card consistency, converts Ignition's raise amount (chips added) to the solver replay's raise increment, and handles both `All-in` and `All-in(raise)` forms. The shared replay validates action order, complete street transitions, exact calls/returns, stacks and cent-level pot accounting. Forced blinds never count as VPIP. Hero observations are excluded before any population aggregation or fitting.

Nonstandard/dead blind arrangements, extra posted chips, heads-up hands, under-minimum raises and malformed/incomplete records are excluded and counted in [the aggregate audit](ignition/NL10.json). These exclusions can bias short-stack/nonstandard-game representation. Source labels are anonymous seat positions, so this release does not claim persistent-player archetypes. File/session grouping is a conservative split unit, not a persistent opponent identity.

## Reproduce

```powershell
python tools/ignition/test_models.py
python tools/ignition/analyze.py --source "T:/Dev/Poker Data/Ignition" --out output/ignition
python tools/ignition/fit.py --input output/ignition/analysis.json --out docs/ignition
python tools/ignition/report.py
```

Requires NumPy, SciPy, scikit-learn and Matplotlib, plus `cache/preflop_eq169.bin` for the reference comparator. Analysis and fitting do not mutate a solver session. Raw histories and session-level observations remain local; only aggregate counters, context coverage, validation and model parameters are published. See also [CoinPoker models](coinpoker_models.md).
