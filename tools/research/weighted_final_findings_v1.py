"""Render all fixed study outcomes only after complete independent verification."""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='weighted-complete-evaluation-study-v1'


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def render(analysis,roots,trajectory,audit):
    contrasts=analysis['contrasts']
    assert len(contrasts)==8 and len({x['name'] for x in contrasts})==8
    assert all(x['count']==65536 and all(math.isfinite(x[k]) for k in ('mean','lower','upper','standard_error'))
               and x['lower']<=x['mean']<=x['upper'] for x in contrasts)
    positive=sum(x['lower']>0 for x in contrasts)
    negative=sum(x['upper']<0 for x in contrasts)
    inconclusive=8-positive-negative
    c=roots['comparisons'];old=c['baseline_cross_seed'];new=c['candidate_cross_seed']
    rows='\n'.join(f"| {x['name']} | {x['mean']:+.4f} | {x['standard_error']:.4f} | [{x['lower']:+.4f}, {x['upper']:+.4f}] |" for x in contrasts)
    freq='\n'.join('| '+p+' | '+' | '.join(f'{100*v:.2f}%' for v in f)+' |' for p,f in zip(roots['policy_order'],roots['aggregate_action_frequencies']))
    movement='\n'.join(f"| {x['arm']} | {x['mean_zero_sample_classes_per_update']:.2f} | {100*x['middle_last_window_tv']:.2f}% | {100*x['mean_step_tv_last_26']:.2f}% |" for x in trajectory['findings'])
    return f'''# Stratified training: completed comparison

All eight registered payoff comparisons are reported below. Their simultaneous
intervals support a positive gain in {positive}, a negative gain in {negative},
and leave {inconclusive} inconclusive. These counts are per tested player and
fixed opponent, not a general ranking or an equilibrium certificate.

## What was compared

Two stratified training runs were compared with the two previously completed
baselines in the restricted 200bb BB-versus-BTN game (2bb open, 0.5bb dead money,
5% rake capped at 2bb). The runs share seed identities and settings, but different
sampling algorithms do not produce identical training deals. Baselines were
already known before this candidate study.

Each candidate uses 78 updates of 512 deals, guarantees at least three observations
per starting-hand class per update, and carries source-deal importance weights
through learning. This does not eliminate variation among runouts within a class.
Evaluated strategies average all played generations 0-77 with weights 1-78 and
own-action reach. Unplayed generation 78 was not selected for evaluation.

## Range consistency

Entry-weighted cross-seed total variation is **{100*old['entry_weighted_total_variation']:.2f}% for the baseline**
and **{100*new['entry_weighted_total_variation']:.2f}% for stratified training**.
The candidate-minus-baseline difference is
**{100*(new['entry_weighted_total_variation']-old['entry_weighted_total_variation']):+.2f} percentage points**;
negative means less disagreement between these two runs. This is descriptive.
It is not the percentage of hands played incorrectly and does not measure EV loss.
The most frequent action differs across seeds in
{old['classes_with_different_most_frequent_action']} baseline classes and
{new['classes_with_different_most_frequent_action']} stratified classes, out of 169.

| Complete bank | Fold | Call | Raise | Jam |
| --- | ---: | ---: | ---: | ---: |
{freq}

Aggregate frequencies can hide per-hand disagreement. The
[complete class table](weighted-final-all-hand-classes.json) contains all 169
native class labels, entry masses, all four policies and per-class distances.

## Coverage and policy movement

| Arm | Classes absent per update | Middle-to-last window TV | Mean step TV, last 26 updates |
| --- | ---: | ---: | ---: |
{movement}

Windows contain played generations 0-25, 26-51 and 52-77 with their original
generation-plus-one weights normalized within each window. Every consecutive
update and every class appears in the [full trajectory](weighted-root-trajectory-v1-result.json).
Its last-current-versus-average diagnostic includes unplayed generation 78 only
as a diagnostic. Reduced movement alone does not establish better poker play.

## Payoff comparisons

Positive means the replacement player gained against the named fixed opponent.
Units are bb per entry into this research spot, not bb/100 dealt hands.
The fixed test used 65,536 fresh common physical deals, seed 9278101, eight crossed
profiles, and one final statistical look. Intervals use the registered bounded
empirical-Bernstein method with Bonferroni adjustment across eight contrasts.

| Replacement and fixed opponent | Mean gain | Paired standard error | Simultaneous 95% interval |
| --- | ---: | ---: | ---: |
{rows}

![All eight gains and intervals](weighted-final-gains.png)

An interval containing zero is inconclusive, not proof of equivalence. Large-pot
outcomes and the fixed payoff bounds limit precision. No favorable seed or
checkpoint was selected, no sample extension followed the outcomes, and no
narrower post-hoc interval replaces the registered result.

## Verification and remaining scope

Both candidate training histories passed full independent readback. The final
evaluation review checked {audit['batches']:,} batches and {audit['observations']:,}
policy observations, the registered chance stream, crossed profiles, cashflows,
root summaries and all eight statistical reductions. Maximum statistical
discrepancy was {audit['maximum_statistical_error']:.3g}.
This review does not independently reimplement the poker engine and is not a
best-response or exploitability certificate.

These findings require scientific interpretation before a next experiment is
chosen. No automatic promotion or deployment follows this report. Other positions,
stacks, sizing menus, multiway pots and agreement with GTO Wizard remain unproven.
Production was not changed by this research report.
'''


def main():
    rp=OUT/f'{PREFIX}-registration.json';pp=OUT/f'{PREFIX}-result.json'
    ap=OUT/f'{PREFIX}-independent-review.json';ar=OUT/f'{PREFIX}-readback-registration.json'
    tp=OUT/'weighted-root-trajectory-v1-result.json';tr=OUT/'weighted-root-trajectory-v1-registration.json'
    result,audit,trajectory=map(read,(pp,ap,tp))
    assert result['passed'] and result['complete'] and result['deals']==65536 and result['test_seed']==9278101
    assert audit['passed'] and audit['deals']==65536 and audit['batches']==2048
    assert audit['source_result_sha256']==sha(pp)
    assert result['registration_sha256']==audit['source_registration_sha256']==sha(rp)
    assert audit['readback_registration_sha256']==sha(ar)
    assert trajectory['passed'] and trajectory['registration_sha256']==sha(tr)
    for registration in (rp,ar,tr):
        for p,h in read(registration)['inputs'].items():assert sha(p)==h,p
    store=Path(result['store'])
    for name,key in [('analysis.json','analysis_sha256'),('root-stability.json','root_stability_sha256')]:
        assert sha(store/name)==result[key]
    analysis,roots=read(store/'analysis.json'),read(store/'root-stability.json')
    text=render(analysis,roots,trajectory,audit)
    from storage_strategic_common_prior_20260920 import PAIRS,CLASSES
    labels={};ranks='23456789TJQKA'
    for pair,c in zip(PAIRS,CLASSES):
        hi,lo=sorted((int(pair[0])//4,int(pair[1])//4),reverse=True)
        name=ranks[hi]+ranks[lo]+('' if hi==lo else 's' if int(pair[0])%4==int(pair[1])%4 else 'o')
        c=int(c);assert c not in labels or labels[c]==name;labels[c]=name
    assert set(labels)==set(range(169))
    classes=[dict(native_class_index=i,hand=labels[i],entry_mass=roots['entry_masses'][i],
        policies={p:dict(zip(roots['action_order'],bank[i])) for p,bank in zip(roots['policy_order'],roots['root_probabilities'])},
        total_variation={k:v['class_total_variation'][i] for k,v in roots['comparisons'].items()}) for i in range(169)]
    paths=[OUT/n for n in ('WEIGHTED-FINAL-FINDINGS.md','weighted-final-all-hand-classes.json','weighted-final-gains.png','weighted-final-report-evidence.json')]
    assert not any(p.exists() for p in paths)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,5.6),layout='constrained')
    for i,x in enumerate(analysis['contrasts']):
        ax.errorbar(x['mean'],i,xerr=[[x['mean']-x['lower']],[x['upper']-x['mean']]],fmt='o',capsize=4,color='#286e9e' if i<4 else '#b36326')
    ax.axvline(0,color='#555',linewidth=1);ax.invert_yaxis();ax.grid(axis='x',alpha=.2)
    ax.set_yticks(range(8),[x['name'].replace('first:','Run 1: ').replace('replication:','Run 2: ').replace('-v-oldBB','').replace('-v-oldBTN','').replace('-against-',' vs ') for x in analysis['contrasts']])
    ax.set_xlabel('Gain from replacing one player (bb per entry; positive favors stratified training)')
    ax.set_title('Stratified training: all eight payoff comparisons\n65,536 common deals; registered simultaneous 95% intervals')
    fig.savefig(paths[2],dpi=150);plt.close(fig)
    paths[0].write_text(text,encoding='utf-8');paths[1].write_text(json.dumps(classes,indent=2)+'\n',encoding='utf-8')
    paths[3].write_text(json.dumps(dict(inputs={str(p):sha(p) for p in [rp,pp,ap,ar,tp,tr,store/'analysis.json',store/'root-stability.json',Path(__file__)]},
        outputs={str(p):sha(p) for p in paths[:3]},interpretation_pending=True,accuracy_qualified=False,production_modified=False),indent=2),encoding='utf-8')
    print('Rendered complete verified outcomes; scientific interpretation and visual review remain required.')


if __name__=='__main__':main()
