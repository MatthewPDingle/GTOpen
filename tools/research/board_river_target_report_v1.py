"""Publish the registered held-out comparison after independent prediction readback."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import math
from pathlib import Path
import numpy as np
from board_river_target_common_v1 import OUT,STORE,PREFIX,PLAN,read,sha,verify
from board_prefix_publication_v1 import atomic_json

ARMS=('exact','sample16','sample1')
LABELS={'exact':'Exact conditional target','sample16':'16 sampled opponents','sample1':'1 sampled opponent'}


def scalar_metrics(prediction,target):
    n=len(target);assert n
    mse=math.fsum((float(p)-float(t))**2 for p,t in zip(prediction,target))/n
    cost=math.fsum((abs(float(t))/2 if p==0 else abs(float(t)) if p*t<0 else 0.) for p,t in zip(prediction,target))/n
    return mse,cost


def mean_group(rows,arm,group='all',**filters):
    selected=[r['groups'][group] for r in rows if r['arm']==arm and all(r[k]==v for k,v in filters.items()) and r['groups'][group]['rows']]
    if not selected:return None
    return {key:math.fsum(s[key] for s in selected)/len(selected) for key in ('mse_bb2','fold_call_decision_cost_bb')}


def main():
    names=('selection','collection','readback','frozen-models','evaluation','evaluation-registration')
    sources=[OUT/(PREFIX+'-'+name+'.json') for name in names]
    selection,collection,readback,frozen,evaluation,registration=map(read,sources)
    assert all(v['passed'] and v['complete'] for v in (selection,collection,readback,frozen,evaluation))
    assert evaluation['registration_sha256']==sha(sources[-1]);verify(registration['inputs'])
    hashes={str(p):sha(p) for p in sources+[Path(__file__),PLAN]};rows=evaluation['rows']
    assert len(rows)==36
    maximum=0.;comparisons=[]
    # Reconstruct the two key metrics from retained predictions, rather than
    # using evaluator functions. Models, labels and selection remain frozen.
    for row in rows:
        path=STORE/'evaluation'/(row['name']+'.npz');assert sha(path)==row['predictions_sha256']
        hashes[str(path)]=sha(path)
        with np.load(path,allow_pickle=False) as z:
            predicted=z['predicted_bb'];target=z['exact_bb'];pot=z['pot'];share=z['initial_share'];onpath=z['hero_on_path']
            assert np.all(z['deal']>=64) and np.isfinite(predicted).all() and np.isfinite(target).all()
            masks={'all':np.ones(len(target),dtype=bool),'initialization_only':abs(share-1)<1e-12,
                'later_generations_contribute':abs(share-1)>=1e-12,'no_hero_mixture_support':~np.isfinite(share),
                'hero_on_path':onpath,'hero_off_path':~onpath}
            for band,lo,hi in (('under10',0,10),('10to50',10,50),('50to100',50,100),('100to200',100,200),('200plus',200,np.inf)):
                masks[band]=(pot>=lo)&(pot<hi)
            for group,mask in masks.items():
                expected=row['groups'][group];assert int(mask.sum())==expected['rows']
                if not mask.any():continue
                actual=scalar_metrics(predicted[mask],target[mask])
                for value,key in zip(actual,('mse_bb2','fold_call_decision_cost_bb')):
                    error=abs(value-expected[key]);maximum=max(maximum,error);assert error<1e-9*max(1.,abs(value))
    for other in ('sample16','sample1'):
        exact=evaluation['aggregate']['exact'];sampled=evaluation['aggregate'][other]
        comparisons.append(dict(other=other,**{key:100*(sampled[key]-exact[key])/sampled[key] if sampled[key] else None
            for key in ('mse_bb2','fold_call_decision_cost_bb')}))
    checks={}
    for other in ('sample1','sample16'):
        for metric in ('mse_bb2','fold_call_decision_cost_bb'):
            checks[f'aggregate_exact_better_than_{other}_{metric}']=mean_group(rows,'exact')[metric]<mean_group(rows,other)[metric]
        for bank in (0,1):
            checks[f'bank_{bank}_exact_cost_not_worse_than_{other}']=mean_group(rows,'exact',bank=bank)['fold_call_decision_cost_bb']<=mean_group(rows,other,bank=bank)['fold_call_decision_cost_bb']
    assert checks==evaluation['advancement_checks'];passed=all(checks.values())
    assert passed==evaluation['qualifies_for_separate_estimator_integration']
    review=dict(passed=True,complete=True,inputs=hashes,prediction_readback_models=36,maximum_metric_error=maximum,
        comparisons_percent_improvement_exact=comparisons,advancement_checks=checks,
        qualifies_for_separate_estimator_integration=passed,production_qualified=False)
    destination=OUT/(PREFIX+'-report-readback.json');assert not destination.exists();atomic_json(destination,review)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11.5,4.8),layout='constrained')
    for ax,metric,title,unit in zip(axes,('mse_bb2','fold_call_decision_cost_bb'),
            ('Value prediction error','Cost of the call/fold choice'),('Mean squared error (bb squared)','Mean local decision cost (bb)')):
        values=[mean_group(rows,arm)[metric] for arm in ARMS]
        ax.bar(range(3),values,color=['#287d62','#497cac','#ba8650'],width=.65,alpha=.85)
        for i,arm in enumerate(ARMS):
            repeats=[mean_group(rows,arm,repetition=r)[metric] for r in range(3)]
            ax.scatter([i-.12,i,i+.12],repeats,color='#17232c',s=22,zorder=3)
            ax.annotate(f'{values[i]:.3f}',(i,values[i]),xytext=(0,6),textcoords='offset points',ha='center',fontsize=10)
        ax.set_xticks(range(3),['Exact','16 samples','1 sample']);ax.set_ylabel(unit);ax.set_title(title)
        ax.set_ylim(0,max(values+[mean_group(rows,a,repetition=r)[metric] for a in ARMS for r in range(3)])*1.18)
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    fig.suptitle('Fresh-deal river target learning: held-out results\nLower is better; dots show the three paired repetitions',fontsize=13)
    fig.text(.5,-.025,'576 selected states from 32 unseen deals; two frozen opponents. Local diagnostics, not bb/hand or preflop accuracy.',ha='center',fontsize=9)
    plot=OUT/(PREFIX+'.png');assert not plot.exists();fig.savefig(plot,dpi=170,bbox_inches='tight');plt.close(fig)
    totals=[]
    for arm in ARMS:
        m=evaluation['aggregate'][arm]
        train=[r['training_exact_mse_bb2'] for r in frozen['models'] if r['arm']==arm]
        totals.append(f"| {LABELS[arm]} | {np.mean(train):.3f} | {m['mse_bb2']:.3f} | {m['fold_call_decision_cost_bb']:.3f} | {m['directional_agreement']*100:.1f}% |")
    breakdown=[]
    for bank in (0,1):
        for actor in (0,1):
            parts=[mean_group(rows,arm,bank=bank,actor=actor) for arm in ARMS]
            breakdown.append(f"| {'AB'[bank]} / {('BB','BTN')[actor]} | "+' | '.join(f"{p['mse_bb2']:.3f} / {p['fold_call_decision_cost_bb']:.3f}" for p in parts)+' |')
    groups=[]
    for group in ('initialization_only','later_generations_contribute','hero_off_path','under10','10to50','50to100','100to200','200plus'):
        parts=[mean_group(rows,arm,group) for arm in ARMS]
        n=sum(r['groups'][group]['rows'] for r in rows if r['arm']=='exact' and r['repetition']==0)
        groups.append(f'| {group} | {n} | '+' | '.join('n/a' if p is None else f"{p['mse_bb2']:.3f} / {p['fold_call_decision_cost_bb']:.3f}" for p in parts)+' |')
    decision=('The exact-target arm passed the registered descriptive gate. It warrants a separate estimator-integration experiment.' if passed else
        'The exact-target arm did not pass the registered descriptive gate. This result does not justify integrating it into self-play or launching a larger training run yet.')
    table='\n'.join(totals);bank_table='\n'.join(breakdown);group_table='\n'.join(groups)
    failed='; '.join(k for k,v in checks.items() if not v) or 'none'
    report=f'''# Fresh-deal conditional river target learning

{decision} No production change is qualified by this supervised test.

## What this tested

The experimental later-play model still makes avoidable river decisions. This probe asks whether removing opponent-sampling noise from its training answers helps it learn the value of calling rather than folding. It uses the same visible inputs, network, initialization, 512-step fitting budget, and training examples for three targets: an exact conditional answer, the mean of 16 sampled opponents, or one sampled opponent.

The 96 new physical deals were split before observation selection: 64 deals / 1,152 training states and 32 deals / 576 final evaluation states. Board groups and complete observation keys are disjoint. Both original 78-model opponents are frozen. For each state, all 990 legal opponent hands are weighted by the original entry range and the probability of the actual action history. Hidden opponent cards and equity labels never become model inputs.

There are 36 fits: two opponents, two actors, three paired initializations and three target types. All fits were frozen before any final evaluation. These are contrast regressors, not CFR regrets or complete poker strategies.

## Aggregate results

| Training target | Training exact MSE (bb squared) | Held-out MSE (bb squared) | Held-out decision cost (bb) | Direction agreement |
|---|---:|---:|---:|---:|
{table}

Decision cost is the loss from choosing the wrong member of the Fold/Call pair. A zero prediction mixes the two equally. A zero true contrast incurs no decision cost. Raising may also be legal, so this is not a complete best-response test. Query-balanced costs are not bb per dealt hand, exploitability or expected deployment gains.

![Held-out target-learning comparison]({PREFIX}.png)

The bars average equally across banks, actors and repetitions, as registered. Dots are repetition means, not confidence intervals. Cases on one physical deal and comparisons against two banks are correlated. This is a small descriptive feasibility study, not a significance claim.

## Both banks and actors

Cells show held-out MSE / local decision cost.

| Frozen bank / actor | Exact | 16 samples | 1 sample |
|---|---:|---:|---:|
{bank_table}

## Rare histories and pot size

Initialization-only means that later trained generations contribute no measurable own-history weight at this decision. Such rare histories remain in the study. The remaining rows have later trained contributions. Initializer classification uses the registered numerical tolerance, not a result-selected cutoff.

| Group | Bank/states, one repetition | Exact MSE / cost | 16 samples MSE / cost | 1 sample MSE / cost |
|---|---:|---:|---:|---:|
{group_table}

Group means retain equal bank/actor/repetition weighting among nonempty groups. They are diagnostic summaries, not a reweighted primary gate. Unsupported opponent-history counts by bank: {readback['unsupported_by_bank']}; zero hero-history counts: {readback['zero_hero_reach_by_bank']}.

## Advancement decision and limits

{decision}

Failed registered checks: {failed}.

The gate requires lower aggregate held-out MSE and decision cost than both sampled targets, plus non-increasing decision cost against each bank separately. All settings and repetitions are retained. No final evaluation result selects hyperparameters, additional iterations or a favorable initialization.

The scope is still a restricted 200bb BB-versus-BTN continuation with inherited incoming ranges. More accurate local river predictions do not prove equilibrium, better full-policy play or better preflop ranges. Successful integration would require the correct self-play reach and importance weights, independent estimator controls, retraining and a fresh complete-policy evaluation. Failure calls for inspecting fitting versus generalization limitations before further compute.

## Verification and resources

Independent scalar label reconstruction passed across {readback['cases']:,} cases and {readback['observations']:,} exported observations, with maximum arithmetic discrepancy {readback['maximum_scalar_error']:.3g}. Native poker outcomes are reused, so this is not a second poker engine. CPU/GPU training controls passed before fits. Every final prediction was independently reconstructed with NumPy and Torch CPU; the maximum difference was {evaluation['maximum_numpy_torch_prediction_difference_bb']:.3g} bb. Report readback reproduced the retained prediction metrics within {maximum:.3g}.

Retained study files total {evaluation['storage']['logical_bytes']/1e9:.3f} GB against the 2 GB study limit. Training took {frozen['seconds']:.2f} seconds; final scoring took {evaluation['seconds']:.2f} seconds using {evaluation['workers']} CPU workers. Research shared light desktop use while yielding to production solves and heavier workloads. No production settings or historical archives were changed.

Evidence: `{PREFIX}-evaluation.json`, `{PREFIX}-report-readback.json`, the frozen model manifest, and their source/data registrations. The broader preflop research goal remains active.
'''
    path=OUT/'BOARD-RIVER-TARGET-LEARNING-FINDINGS.md';assert not path.exists()
    with path.open('x',encoding='utf-8',newline='\n') as f:f.write(report)
    verify(hashes);print(dict(report=str(path),plot=str(plot),gate_passed=passed,maximum_metric_error=maximum))


if __name__=='__main__':main()
