"""Independently read back saved coverage predictions and publish all four arms."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import math
from pathlib import Path
import numpy as np
from board_river_deal_coverage_common_v1 import ROOT,OUT,STORE,PREFIX,PLAN,read,sha,verify
from board_prefix_publication_v1 import atomic_json
from board_river_target_report_v1 import scalar_metrics,mean_group

ARMS=('dense-exact','broad-exact','dense-sample16','broad-sample16')
LABELS=('64 deals / exact','192 deals / exact','64 deals / 16 samples','192 deals / 16 samples')


def main():
    names=('selection','collection','readback','merged','frozen-models','evaluation','evaluation-registration')
    sources=[OUT/(PREFIX+'-'+name+'.json') for name in names]
    selection,collection,readback,merged,frozen,evaluation,registration=map(read,sources)
    assert all(v['passed'] and v['complete'] for v in (selection,collection,readback,merged,frozen,evaluation))
    assert evaluation['registration_sha256']==sha(sources[-1]);verify(registration['inputs'])
    sources += [Path(__file__),PLAN,ROOT/'tools/research/board_river_target_report_v1.py',ROOT/'tools/research/board_river_deal_coverage_common_v1.py']
    hashes={str(p):sha(p) for p in sources};rows=evaluation['rows'];assert len(rows)==48
    maximum=0.;expected_ids=set(selection['memberships']['evaluation'])
    for row in rows:
        path=STORE/'evaluation'/(row['name']+'.npz');assert sha(path)==row['predictions_sha256'];hashes[str(path)]=sha(path)
        with np.load(path,allow_pickle=False) as z:
            assert set(z['case_ids'])<=expected_ids and np.all(z['deal']>=192) and np.all(z['deal']<224)
            predicted=z['predicted_bb'];target=z['exact_bb'];pot=z['pot'];share=z['initial_share'];onpath=z['hero_on_path']
            assert np.isfinite(predicted).all() and np.isfinite(target).all()
            masks={'all':np.ones(len(target),dtype=bool),'initialization_only':abs(share-1)<1e-12,
                'later_generations_contribute':abs(share-1)>=1e-12,'no_hero_mixture_support':~np.isfinite(share),
                'hero_on_path':onpath,'hero_off_path':~onpath}
            for band,lo,hi in (('under10',0,10),('10to50',10,50),('50to100',50,100),('100to200',100,200),('200plus',200,np.inf)):
                masks[band]=(pot>=lo)&(pot<hi)
            for group,mask in masks.items():
                expected=row['groups'][group];assert int(mask.sum())==expected['rows']
                if not mask.any():continue
                for value,key in zip(scalar_metrics(predicted[mask],target[mask]),('mse_bb2','fold_call_decision_cost_bb')):
                    error=abs(value-expected[key]);maximum=max(maximum,error);assert error<1e-9*max(1.,abs(value))
    checks={'equal_effective_actor_pot_counts':merged['equal_effective_actor_pot_counts']};gates={};comparisons=[]
    for gate,other in (('coverage','dense-exact'),('target','broad-sample16')):
        local={};best=mean_group(rows,'broad-exact');ref=mean_group(rows,other)
        for metric in ('mse_bb2','fold_call_decision_cost_bb'):
            local[f'{gate}_aggregate_{metric}']=best[metric]<ref[metric]
        for bank in (0,1):
            local[f'{gate}_bank_{bank}_cost']=mean_group(rows,'broad-exact',bank=bank)['fold_call_decision_cost_bb']<=mean_group(rows,other,bank=bank)['fold_call_decision_cost_bb']
        checks.update(local);gates[gate]=all(local.values()) and merged['equal_effective_actor_pot_counts']
        comparisons.append(dict(comparison=gate,reference=other,percent_improvement={k:100*(ref[k]-best[k])/ref[k] if ref[k] else None for k in best}))
    assert checks==evaluation['advancement_checks'] and gates==evaluation['gates']
    passed=all(checks.values());assert passed==evaluation['qualifies_for_separate_estimator_integration']
    proof=dict(passed=True,complete=True,inputs=hashes,models=48,maximum_metric_error=maximum,
        comparisons=comparisons,advancement_checks=checks,gates=gates,
        qualifies_for_separate_estimator_integration=passed,production_qualified=False)
    dest=OUT/(PREFIX+'-report-readback.json');assert not dest.exists();atomic_json(dest,proof)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax,metric,title,unit in zip(axes,('mse_bb2','fold_call_decision_cost_bb'),
            ('Value prediction error','Cost of the call/fold choice'),('Mean squared error (bb squared)','Mean local decision cost (bb)')):
        values=[mean_group(rows,a)[metric] for a in ARMS]
        ax.bar(range(4),values,color=['#67948d','#287d62','#88a2c3','#497cac'],width=.65)
        repeats=[[mean_group(rows,a,repetition=r)[metric] for r in range(3)] for a in ARMS]
        for i in range(4):
            ax.scatter([i-.12,i,i+.12],repeats[i],color='#17232c',s=22,zorder=3)
            ax.annotate(f'{values[i]:.2f}',(i,values[i]),xytext=(0,6),textcoords='offset points',ha='center',fontsize=10)
        ax.set_xticks(range(4),['64 deals\nExact','192 deals\nExact','64 deals\n16 samples','192 deals\n16 samples'])
        ax.set_ylabel(unit);ax.set_title(title);ax.set_ylim(0,max(values+sum(repeats,[]))*1.18)
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    fig.suptitle('More varied deals, same 1,152 training examples\nFresh evaluation; lower is better; dots show paired repetitions',fontsize=13)
    fig.text(.5,-.025,'576 selected states from 32 unseen deals. Local river diagnostics, not bb/hand or preflop accuracy.',ha='center',fontsize=9)
    plot=OUT/(PREFIX+'.png');assert not plot.exists();fig.savefig(plot,dpi=170,bbox_inches='tight');plt.close(fig)
    lines=[]
    for arm,label in zip(ARMS,LABELS):
        m=evaluation['aggregate'][arm];training=np.mean([r['training_exact_mse_bb2'] for r in frozen['models'] if r['arm']==arm])
        lines.append(f"| {label} | {training:.3f} | {m['mse_bb2']:.3f} | {m['fold_call_decision_cost_bb']:.3f} | {m['directional_agreement']*100:.1f}% |")
    banklines=[]
    for bank in (0,1):
        for actor in (0,1):
            parts=[mean_group(rows,a,bank=bank,actor=actor) for a in ARMS]
            banklines.append(f"| {'AB'[bank]} / {('BB','BTN')[actor]} | "+' | '.join(f"{p['mse_bb2']:.3f} / {p['fold_call_decision_cost_bb']:.3f}" for p in parts)+' |')
    grouplines=[]
    for group in ('initialization_only','later_generations_contribute','hero_off_path','under10','10to50','50to100','100to200','200plus'):
        parts=[mean_group(rows,a,group) for a in ARMS]
        grouplines.append('| '+group+' | '+' | '.join('n/a' if p is None else f"{p['mse_bb2']:.3f} / {p['fold_call_decision_cost_bb']:.3f}" for p in parts)+' |')
    failed='; '.join(k for k,v in checks.items() if not v) or 'none'
    outcome=('Both descriptive gates passed; a separately controlled estimator-integration experiment is warranted.' if passed else
        'The joint advancement gate failed. These results do not qualify estimator integration or a production change.')
    report=f'''# Equal-budget deal coverage: fresh evaluation

{outcome}

Coverage gate: **{gates['coverage']}**. Exact-versus-16-sample target gate: **{gates['target']}**.
Failed checks: {failed}.

## What changed

Both training sets contain 1,152 selected situations with matching actor/pot quotas. Dense uses 64 distinct physical deals and 18 states per deal. Broad uses 192 deals and six states per deal, with 384 shared rows. All four arms use the same visible features, 64/64 network, three paired initializations and 512 Adam steps. Dense and broad each compare exact conditional answers against 16 sampled opponents. The 48 models were frozen before scoring 576 states from 32 new final deals.

Old training labels retain their original identities and samples. The earlier 32 final deals were excluded. New board groups and complete visible keys are separated from training and spent evaluation. The old training set had already supported exploratory work, so fresh final deals are essential. This comparison balances selected query types rather than sampling actual gameplay reach.

## Results

| Training data / answer | Training exact MSE | Fresh MSE (bb squared) | Local decision cost (bb) | Direction agreement |
|---|---:|---:|---:|---:|
{chr(10).join(lines)}

![Equal-budget deal coverage comparison]({PREFIX}.png)

Bars average all banks, actors and repetitions equally. Dots show repetition means, not confidence intervals. States on a deal and comparisons against the same opponents are correlated; this small diagnostic makes no statistical significance claim.

## Bank and actor

Cells show MSE / local decision cost. All repetitions are retained.

| Bank / actor | Dense exact | Broad exact | Dense 16 samples | Broad 16 samples |
|---|---:|---:|---:|---:|
{chr(10).join(banklines)}

## Pot and rare-history breakdown

| Group | Dense exact MSE / cost | Broad exact MSE / cost | Dense 16 MSE / cost | Broad 16 MSE / cost |
|---|---:|---:|---:|---:|
{chr(10).join(grouplines)}

Group summaries average nonempty bank/actor/repetition groups equally. They do not replace the primary gate. Unsupported counts across the combined data by bank: {merged['unsupported_by_bank']}. Equal effective actor/pot counts after support filtering: {merged['equal_effective_actor_pot_counts']}.

## Interpretation boundary

Decision cost measures the wrong choice within the local Fold/Call pair; raising may also be legal. These values are per selected decision, not bb per dealt hand, exploitability, full-policy EV or measured preflop improvement. Two frozen original 78-generation opponents, inherited incoming ranges, one restricted 200bb BB-versus-BTN context and river-only targets limit transfer claims.

The coverage gate requires broad-exact to beat dense-exact in aggregate MSE and cost without worse cost in either bank. The target gate makes the analogous comparison against broad-sample16. Dense-sample16 is secondary, not a substitute winner. Failed checks remain failed; no added data, seed picking or tuning on this evaluation is allowed. Passing both still requires the estimator reach/importance-weight controls documented in BOARD-RIVER-TARGET-INTEGRATION-NOTES.md, followed by actual self-play training and fresh complete-policy evaluation.

## Verification and resources

The {readback['cases']:,} new case labels passed independent scalar reconstruction across {readback['observations']:,} exported observations; maximum discrepancy {readback['maximum_scalar_error']:.3g}. The original training labels were reused only through their verified hashes. CPU/GPU fitting controls and independent NumPy/Torch CPU prediction checks passed. Saved prediction metrics agreed within {maximum:.3g}.

Collection took {collection['seconds_this_invocation']:.1f} seconds in its final invocation. Training took {frozen['seconds']:.1f} seconds; final scoring took {evaluation['seconds']:.1f} seconds. New store allocation at scoring: {evaluation['storage']['allocated_file_bytes']/1e9:.3f} GB against 2 GB. Production, old archives and application windows were unchanged.

Evidence: `{PREFIX}-evaluation.json`, `{PREFIX}-report-readback.json`, the membership and frozen-model manifests, and their immutable source registrations. The broader preflop research goal remains active.
'''
    path=OUT/'BOARD-RIVER-DEAL-COVERAGE-FINDINGS.md';assert not path.exists()
    with path.open('x',encoding='utf-8',newline='\n') as f:f.write(report)
    verify(hashes);print(dict(report=str(path),plot=str(plot),gates=gates,maximum_metric_error=maximum),flush=True)


if __name__=='__main__':main()
