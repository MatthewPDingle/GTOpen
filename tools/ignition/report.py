"""Publish aggregate evidence, without sessions, table IDs or player histories."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
d=json.loads((root/'docs/ignition/NL10.json').read_text());v=d['validation'];s=d['splits'];src=d['source']
rows='\n'.join(f"| {c['players']} | {c['role']} | {c['opportunities']:,} | {c['hands_seen']} | {c['median_per_class']:.0f} |" for c in d['contexts'])
gain=100*(1-v['test_log_loss']/v['reference_test_log_loss'])
text=f'''# Ignition NL10 regular: measured opening ranges

Recorded {src['date_from']} to {src['date_to']}; model built 8 September 2026. The library entry is **Ignition · NL10 regular · Pool**, under Manage models. This is an anonymous opponent pool, excluding every `[ME]` observation. It is a separate source from CoinPoker and is never presented as measured CoinPoker behavior.

## What the model contains

- **{src['unique_hands']:,} validated hands** in **{src['sessions']} file/session groups**, with three to six players dealt in. No ante; small blind 0.5bb. Stack depths are pooled.
- First-in hand probabilities use all known-card opportunities: raises, folds, and calls/completions. A player folding before showdown still has a known hand. The 169-hand index and combination weights match the Rust engine (pairs 6, suited 4, offsuit 12).
- Hand/action counts first borrow a global action prior, then each position/player-count/hand cell borrows the pooled hand estimate. Smoothing strengths are selected on separate later sessions. This gives probabilities rather than cutting a deterministic range from reference rankings.
- The engine consumes these probabilities directly for the unopened-pot bucket. Over-limper, defense and postflop rates come from the same validated opponent sample, but their **hand composition remains inferred**. Over-limper rates in this first Ignition release are pooled, not a learned per-hand isolation model.
- The editor's dataset checkbox keeps measured entry policies active. Uncheck it to edit first-in/over-limper rates and return to reference-generated entry ranges. Hand painting remains available. Saved profiles preserve the dataset for later generation.
- Unsupported positions/table counts borrow the nearest observed context; outside three to six players is visibly labeled as extrapolation. Ante and blind-ratio changes are labeled as unvalidated transfers. None of this establishes a live-casino or cross-site population model.

## Validation

Sessions are split chronologically: training before {s['tune_from']}; tuning from that date until {s['test_from']}; untouched test from {s['test_from']}. Entire sessions crossing a boundary are excluded from evaluation ({s['cross_boundary_sessions_excluded']}); they return only for the final production refit. Split sizes: {s['train_sessions']} training, {s['tune_sessions']} tuning, {s['test_sessions']} test sessions. This prevents adjacent hands in the same session being scattered across training and test.

The selected smoothing uses {v['selected']['alpha']} prior opportunities per context/hand and {v['selected']['beta']} per pooled hand. The final test contains **{v['test_opportunities']:,} first-in decisions**.

| Predictor | Untouched-test multinomial log loss (lower is better) |
|---|---:|
| Hand-independent contextual action frequencies | {v['handblind_test_log_loss']:.5f} |
| Reference-ordered ranges with measured context totals and tuned smoothing | {v['reference_test_log_loss']:.5f} |
| Learned known-card ranges | {v['test_log_loss']:.5f} |

Learned ranges reduce log loss by **{gain:.1f}%** versus the reference comparator. A 1,000-resample session bootstrap gives a positive 95% interval for absolute log-loss improvement: **{v['reference_gain_ci'][0]:.4f} to {v['reference_gain_ci'][1]:.4f}**. The comparator uses GTOpen's OPEN_SCORE plus cached equity tie-breaking, fills to training context totals, and tunes a probability mixture on validation sessions. It is a smoothed reference-order benchmark, not a fresh equilibrium solve for the held-out games. The global-frequency comparator likewise receives no test labels.

These scores measure action prediction, not exploit profitability or solver accuracy. Final publication refits the chosen method on all validated sessions after the untouched test is scored. Future periods and different sites remain untested.

![Opening-range validation](ignition/validation.png)

## Sample depth

Roles: BTN=0, CO=1, HJ=2, LJ=3, continuing backwards; SB=-1. BB has no first-in opening decision after everyone folds. Many cells are sparse, which is why estimates borrow information rather than reporting every observed fraction as precise.

| Players | Role | First-in opportunities | Hand classes observed | Median opportunities per class |
|---|---:|---:|---:|---:|
{rows}

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
'''
(root/'docs/ignition_models.md').write_text(text,encoding='utf-8',newline='\n')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(8,3.8),layout='constrained')
values=[v['handblind_test_log_loss'],v['reference_test_log_loss'],v['test_log_loss']]
bars=ax.barh(['No hand composition','Reference order + smoothing','Learned opening hands'],values,color=['#8a929e','#587aac','#6da96c'])
ax.invert_yaxis();ax.bar_label(bars,fmt='%.3f',padding=5)
ax.set_xlim(0,max(values)*1.15);ax.set_xlabel('Untouched-test log loss · lower is better')
ax.set_title(f'Ignition NL10 regular · {v["test_opportunities"]:,} later first-in decisions')
ax.spines[['top','right']].set_visible(False)
fig.savefig(root/'docs/ignition/validation.png',dpi=160);plt.close(fig)
