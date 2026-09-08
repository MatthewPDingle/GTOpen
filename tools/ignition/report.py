"""Publish aggregate evidence, without sessions, table IDs or player histories."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
d=json.loads((root/'docs/ignition/NL10.json').read_text(encoding='utf-8'));v=d['validation'];s=d['splits'];src=d['source']
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
if 'response_validation' in d:
    rv=d['response_validation']
    text=text.replace('# Ignition NL10 regular: measured opening ranges','# Ignition NL10 regular: measured preflop ranges')
    text=text.replace('The engine consumes these probabilities directly for the unopened-pot bucket. Over-limper, defense and postflop rates come from the same validated opponent sample, but their **hand composition remains inferred**. Over-limper rates in this first Ignition release are pooled, not a learned per-hand isolation model.',
        'The engine consumes these probabilities directly for Unopened, Vs Raise, Squeeze, and Vs 3-bet+. Cold re-raise responses and four opening-size bands have their own known-card policies. Vs Limps and defense after limping/calling retain inferred composition because their learned candidates did not reliably beat the comparator. Postflop hand composition remains inferred.')
    text=text.replace("The editor's dataset checkbox keeps measured entry policies active. Uncheck it to edit first-in/over-limper rates and return to reference-generated entry ranges.",
        "The editor's dataset checkbox keeps published measured policies active. Disabled HUD fields display source rates; each tab labels its provenance. Uncheck to edit those rates and return to reference-generated ranges.")
    text=text.replace('python tools/ignition/report.py','python tools/ignition/responses.py --input output/ignition/analysis.json --out docs/ignition\npython tools/ignition/report.py')
    labels={'limps':'Vs limps','raise':'Vs raise','squeeze':'Squeeze','reraise':'Vs 3-bet+ after entering','cold_reraise':'Cold vs 3-bet+','limp_defense':'After limping/calling','raise_2.5':'Open to ≤2.5bb','raise_3.5':'Open to >2.5–3.5bb','raise_5':'Open to >3.5–5bb','raise_999':'Open to >5bb'}
    lines='\n'.join(f"| {labels[k]} | {v['opportunities']:,} | {v['test_opportunities']:,} | {v['reference_log_loss']:.4f} | {v['learned_log_loss']:.4f} | {'Learned' if v['published'] else 'Inferred fallback'} |" for k,v in rv.items())
    extra=f'''## Response-range extension

Known cards are now counted separately for each preflop decision situation, including folds. Cold responses (no voluntary investment yet) are separated from responses after entering. BB checks behind limpers count as passive decisions; forced blind posts do not. All hero observations are excluded before fitting.

Each situation uses its own smoothing parameters, selected on the original chronological tuning sessions. The later-session holdout is used to evaluate and screen publication. Learned policies are published only when a 1,000-resample session bootstrap gives a positive lower 95% bound on improvement over the reference-order comparator. These are per-comparison intervals, not a simultaneous guarantee across all situations. No parameter search was repeated after seeing the response test results. The opening evaluation above is unchanged.

| Situation | Source decisions | Test decisions | Reference log loss | Learned log loss | Published policy |
|---|---:|---:|---:|---:|---|
{lines}

The comparator uses the same continue/raise ordering rules as the zero-naivety generator: reference CALL+THREEBET for cold defense, half reference/strength ordering for raises, strength ordering for re-raises. It receives training-only context action totals and reaching-hand weights, with a separately tuned probability mixture. It is a smoothed benchmark, not an exact replay of every saved model or an equilibrium solve.

![Response-range validation](ignition/responses-validation.png)

**Limits that remain:** these are pooled anonymous opponents, not individually tracked players. Position/player count is conditioned within each situation, but aggressor position, stack depth, preceding action sequence and re-raise depth are pooled. The Vs 3-bet+ grid is conditional on prior entry; a separate cold policy is applied when no voluntary chips were invested. Vs Raise shows the pooled grid; actual play uses the matching size-band policy. The >5bb band has only {rv['raise_999']['test_opportunities']} test decisions, so its estimate is particularly uncertain. Very large responses still follow the model's explicit adaptive-stack threshold. Raise/jam sizing is chosen from the configured menu rather than learned as a separate action-size distribution. Transfers to 8-handed equal-blind live games remain unvalidated and are labeled in the editor.

Existing copies and saved games retain their compiled ranges. Select the updated built-in Ignition pool to generate the new response policies. Raw histories and session-level counts stay local.

'''
    text=text.replace('## Sample depth',extra+'## Sample depth')
if 'limp_validation' in d:
    groups=d['limp_validation']['groups']
    text=text.replace('Vs Limps and defense after limping/calling retain inferred composition because their learned candidates did not reliably beat the comparator.',
        'Vs Limps now uses separate legal-action and limper-count policies described below. Defense after limping/calling remains inferred.')
    text=text.replace('python tools/ignition/report.py','python tools/ignition/limps.py --input output/ignition/analysis.json --out docs/ignition\npython tools/ignition/report.py')
    lines='\n'.join(f"| {label} | {groups[k]['opportunities']:,} | {groups[k]['test_opportunities']:,} | {groups[k]['reference_log_loss']:.4f} | {groups[k]['learned_log_loss']:.4f} | {(1-groups[k]['learned_log_loss']/groups[k]['reference_log_loss'])*100:.1f}% |" for k,label in [('free','BB free checks'),('complete','SB completions'),('field','Other positions')])
    extra=f'''## Vs Limps refinement

The original pooled Vs Limps candidate above was rejected. Its replacement separates **free checks**, **SB completions**, and **other paid entries**, then conditions on position/player count and **one, two, or three-plus limpers**. The editor exposes these three counts; the engine selects them from the actual history. Forced posts, antes and free checks never add a limper. An equal-blind SB checks free and borrows BB observations: this transfer remains unvalidated.

| Decision | Source | Later evaluation | Reference log loss | Refined log loss | Improvement |
|---|---:|---:|---:|---:|---:|
{lines}

These results are **retrospective chronological validation**, not a fresh untouched test: the late period was already inspected during the initial response work. This refinement's candidate family was fixed before scoring that period, with smoothing and blend weights selected on earlier tuning sessions. All three session-bootstrap improvement intervals have positive lower bounds, but a new period is needed for independent confirmation. Prediction improvement does not establish profitable exploitation.

BB and SB policies blend learned hand probabilities and a smoothed reference model **50/50**, as selected on tuning data. Other positions use the learned probabilities. Sparse cells borrow pooled hand, position and player-count estimates. There are 11,234 decisions facing one limper, 2,024 facing two, and only **379 facing three or more** across all roles. Unsupported contexts use the nearest available context, not invented observations. Limper identity/position, exact preceding sequence, stack depth and isolation sizing remain pooled; after-limp defense is still inferred.

Existing saved games/copies keep their ranges. Select the updated built-in Ignition pool, or regenerate a model using its updated dataset, to use these policies. Painting one count changes only that count's entry policy.

See [additional data sources and the sample checklist](poker_datasets.md) before acquiring more histories.

'''
    text=text.replace('## Sample depth',extra+'## Sample depth')
if 'position_validation' in d:
    pv=d['position_validation']
    lines='\n'.join(f"| ≤{e['source_max_players']} players → {e['target_players']}-handed earliest position | {e['extra_positions']} | {e['opportunities']:,} | {e['nearest_loss']:.4f} | {e['adjusted_loss']:.4f} | {(1-e['adjusted_loss']/e['nearest_loss'])*100:.1f}% |" for e in pv['evaluations'])
    text=text.replace('python tools/ignition/report.py','python tools/ignition/positions.py --input output/ignition/analysis.json --out docs/ignition --publish\npython tools/ignition/report.py')
    text=text.replace('Unsupported positions/table counts borrow the nearest observed context;',
        'Unsupported early opening positions use the positional adjustment below; other unsupported positions/table counts borrow the nearest observed context;')
    extra=f'''## Opening positions beyond six-handed coverage

The earlier nearest-position fallback copied the six-handed earliest opening policy to eight-handed UTG, UTG1 and MP. UTG and UTG1 now receive a **position-adjusted estimate**. MP and all originally supplied non-extrapolated opening matrices remain unchanged, as do every response policy and the original validation scores.

The adjustment uses fold/call/raise counts including known folded hands. A regularized multinomial model estimates a shared positional trend, with shrunk deviations for pairs, suited hands and offsuit hands, individual hand intercepts and nuisance terms for observed table sizes. Its positional log-odds change tilts the nearest measured hand policy; it does not replace that policy with ranked ranges. Extra occupancy effects are not extrapolated. Both entry-versus-fold slopes are constrained to be nonpositive and capped at 0.75 log-odds per added position. This structural restraint is a modeling assumption, not a measured law for every hand.

Smoothing of the anchor uses the previously fixed opening parameters. Trend regularization and adjustment strength are selected on earlier tuning sessions, using only smaller tables for each prediction exercise. Entire larger-table contexts are removed from training; later sessions provide the comparison below.

| Hidden-context exercise | Extra early positions | Evaluation decisions | Nearest log loss | Adjusted log loss | Improvement |
|---|---:|---:|---:|---:|---:|
{lines}

All three 2,000-resample session-bootstrap improvement intervals have positive lower bounds. The two six-handed exercises reuse the same decisions, so their counts are not additive independent observations. Intervals are per comparison. This is **retrospective validation** on a period already inspected in prior work, not a fresh untouched test or proof of eight-handed/live-game accuracy.

![Hidden-position prediction checks](ignition/positions-validation.png)

For eight players, the final model raises/limps approximately **11.6%/9.2% UTG**, **15.0%/9.5% UTG1**, and **19.0%/9.8% MP**. Adjustment stops after two extra positions, the greatest distance checked here; the earliest nine-handed position therefore retains that capped estimate and explicitly says so. Source 3–6-player positions keep their measured probabilities. Other table sizes with the same players left to act retain the existing borrowed-context probabilities and are labeled accordingly. Blind-ratio, stakes and site transfers remain unvalidated.

The range editor labels each opening grid as measured, borrowed across table sizes, or position-adjusted. Existing saved copies retain their old dataset; select the updated built-in Ignition pool to generate the new estimates.

'''
    text=text.replace('## Sample depth',extra+'## Sample depth')
if 'smoothing_validation' in d:
    sv=d['smoothing_validation'];sb=sv['buckets']
    text=text.replace('BB and SB policies blend learned hand probabilities and a smoothed reference model **50/50**, as selected on tuning data.',
        'The earlier BB and SB policies blended learned hand probabilities and a smoothed reference model **50/50**. This blend was subsequently replaced by the hand-aware smoothing below because it injected substantial premium-hand folds.')
    text=text.replace('python tools/ignition/report.py','python tools/ignition/smoothing.py --input output/ignition/analysis.json --out docs/ignition --publish\npython tools/ignition/report.py')
    names={'limps_free':'Vs limps: free checks','limps_complete':'Vs limps: SB completions','limps_field':'Vs limps: other positions','raise':'Vs raise','squeeze':'Squeeze','reraise':'Vs 3-bet+ after entering','cold_reraise':'Cold vs 3-bet+','raise_2.5':'Open ≤2.5bb','raise_3.5':'Open >2.5–3.5bb','raise_5':'Open >3.5–5bb','raise_999':'Open >5bb'}
    lines='\n'.join(f"| {names[k]} | {e['decisions']:,} | {e['old_loss']:.4f} | {e['new_loss']:.4f} | {'Updated' if e['published'] else 'Prior policy retained'} |" for k,e in sb.items())
    example='\n'.join(f"| {e['hand']} | {e['old_fold']*100:.2f}% | {e['new_fold']*100:.3f}% |" for e in sv['sb_three_plus_example'])
    extra=f'''## Hand-aware response smoothing

The SB 3+ limper grid exposed an artifact: a hand-independent reference mixture contributed a minimum 11.6% fold probability to every hand, including premiums. This was a modeling assumption, not observed premium-hand folding. The new response smoother has **no population-wide action-percentage mixture**. Openings, including the positional adjustments above, are unchanged.

Sparse hands first borrow observations from nearby ranks within the same pair/suited/offsuit family, then from the same hand across contexts. Own-hand counts and the selected smoothing strengths determine the resulting probabilities. Limper count and free-check/completion/other-entry distinctions remain intact. A tiny 0.001 pseudo-count avoids numerical zeroes in paid situations; it is not a constant probability floor. Free checks have exactly zero folding. No premium hand is hard-coded to always continue.

Squeeze additionally borrows the same hands from ordinary cold raise-response data, with fitted hand-family action offsets to match squeeze tendencies. This is transfer between related situations, not a claim that they have identical strategies. Raise-size and prior-entry distinctions remain in use.

| Situation | Later decisions | Previous log loss | Candidate log loss | Production |
|---|---:|---:|---:|---|
{lines}

Parameters minimize 75% overall tuning log loss plus 25% equally weighted premium/other-pair/other-suited/other-offsuit tuning loss. Publication requires lower retrospective mean loss and no clearly negative 95% session-bootstrap improvement interval for a subgroup with at least 30 decisions. This screen does **not** prove noninferiority: several overall and subgroup intervals overlap zero, some subgroup means worsen, and some premium samples are very small. The ≤2.5bb response band retains its prior learned policy because the candidate did not improve overall loss.

The candidate family was expanded after initial results: broader smoothing strengths, then related-context transfer for squeeze. All comparisons reuse previously inspected historical evaluation sessions; they are development diagnostics, **not an untouched test**. Independent future-period validation remains necessary. The aggregate JSON contains all candidates, subgroup loss, observed/predicted fold rates and bootstrap intervals; do not add overlapping size-band and pooled sample counts.

For the reported eight-handed SB-versus-3+ limpers preview (borrowing the six-handed SB context):

| Hand | Previous fold | Updated fold estimate |
|---|---:|---:|
{example}

These small values reflect the prior and limited observations, not precisely established population rates. See [full diagnostics](ignition/NL10.json).

![Response smoothing comparison](ignition/smoothing-validation.png)

The running app reads the library on request, so the library and provenance can update without rebuilding or restarting the solver. Refresh the browser and select the built-in Ignition pool; existing saved copies/solves retain their compiled policies. CoinPoker models and postflop composition are unchanged.

'''
    text=text.replace('## Sample depth',extra+'## Sample depth')
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
if 'response_validation' in d:
    items=list(d['response_validation'].items());y=list(range(len(items)))
    fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
    ax.barh([i-.17 for i in y],[v['reference_log_loss'] for k,v in items],height=.32,color='#587aac',label='Reference order + smoothing')
    ax.barh([i+.17 for i in y],[v['learned_log_loss'] for k,v in items],height=.32,color=['#6da96c' if v['published'] else '#9d9693' for k,v in items],label='Known-card candidate')
    ax.set_yticks(y,[labels[k]+(' · fallback retained' if not v['published'] else '') for k,v in items]);ax.invert_yaxis()
    ax.set_xlabel('Later-session log loss · lower is better');ax.set_title('Ignition NL10 regular · response policies')
    ax.legend(loc='lower right');ax.spines[['top','right']].set_visible(False)
    fig.savefig(root/'docs/ignition/responses-validation.png',dpi=160);plt.close(fig)
if 'position_validation' in d:
    items=d['position_validation']['evaluations'];y=list(range(len(items)))
    fig,ax=plt.subplots(figsize=(8,3.3),layout='constrained')
    ax.barh([i-.17 for i in y],[e['nearest_loss'] for e in items],height=.32,color='#587aac',label='Copy nearest position')
    ax.barh([i+.17 for i in y],[e['adjusted_loss'] for e in items],height=.32,color='#6da96c',label='Position-adjusted estimate')
    ax.set_yticks(y,[f"≤{e['source_max_players']} players → {e['target_players']}-handed earliest" for e in items]);ax.invert_yaxis()
    ax.set_ylim(len(items)+.25,-.6)
    ax.set_xlabel('Later-session log loss · lower is better');ax.set_title('Hidden-position checks · retrospective validation')
    ax.legend(loc='lower right');ax.spines[['top','right']].set_visible(False)
    fig.savefig(root/'docs/ignition/positions-validation.png',dpi=160);plt.close(fig)
if 'smoothing_validation' in d:
    items=list(d['smoothing_validation']['buckets'].items());y=list(range(len(items)))
    fig,ax=plt.subplots(figsize=(9,6.5),layout='constrained')
    ax.barh([i-.17 for i in y],[e['old_loss'] for k,e in items],height=.32,color='#587aac',label='Previous model')
    ax.barh([i+.17 for i in y],[e['new_loss'] for k,e in items],height=.32,color=['#6da96c' if e['published'] else '#999999' for k,e in items],label='Hand-aware candidate')
    ax.set_yticks(y,[names[k]+(' · retained previous' if not e['published'] else '') for k,e in items]);ax.set_ylim(len(items)+.5,-.6)
    ax.set_xlabel('Later-session log loss · lower is better');ax.set_title('Response smoothing · retrospective development checks')
    ax.legend(loc='lower right');ax.spines[['top','right']].set_visible(False)
    fig.savefig(root/'docs/ignition/smoothing-validation.png',dpi=160);plt.close(fig)
