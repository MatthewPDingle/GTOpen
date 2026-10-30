"""CPU readback of saved curve artifacts; publication uses development rows only."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import math
from pathlib import Path
import numpy as np
from board_river_target_common_v1 import ROOT,OUT,STORE,PREFIX,read,sha,verify
from board_prefix_publication_v1 import atomic_json
from sampled_visible_features_bulk_v1 import features

NAME='board-river-generalization-curve-v1'


def main():
    import torch
    torch.set_num_threads(1)
    path=OUT/(NAME+'-result.json');reg_path=OUT/(NAME+'-registration.json');result=read(path);reg=read(reg_path)
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(reg_path);verify(reg['inputs'])
    assert not result['original_final_evaluation_reused'] and result['exploratory_development_only']
    selection=read(OUT/(PREFIX+'-selection.json'));assert selection['unique_train_board_groups']==64
    hashes={str(p):sha(p) for p in (Path(__file__),path,reg_path,ROOT/'tools/research/sampled_visible_features_bulk_v1.py')}
    dataset=STORE/'verified-dataset.npz';assert sha(dataset)==reg['inputs'][str(dataset)]
    with np.load(dataset,allow_pickle=False) as z:
        mask=~z['evaluation'];ids=z['case_ids'][mask].tolist();active=z['active'][mask];actors=z['actor'][mask]
        deals=z['deal'][mask];exact=z['delta'][mask]
    assert np.all(deals<64);index={name:i for i,name in enumerate(ids)};assert len(index)==1152
    expected={(b,a,r,n) for b in (0,1) for a in (0,1) for r in range(3) for n in (8,16,32,48)}
    rows=result['rows'];assert len(rows)==48 and {(r['bank'],r['actor'],r['repetition'],r['training_deals']) for r in rows}==expected
    maximum=0.;metric_error=0.
    for row in rows:
        artifact=STORE/'generalization-curve-v1'/(row['name']+'.npz');assert sha(artifact)==row['artifact_sha256']
        with np.load(artifact,allow_pickle=False) as z:
            selected=np.array([index[k] for k in z['case_ids'].tolist()]);d=deals[selected];n=row['training_deals']
            tm=np.isin(d,reg['fit_deals'][:n]);vm=np.isin(d,reg['validation_deals'])
            assert np.all(tm|vm) and not np.any(tm&vm) and np.all(actors[selected]==row['actor'])
            assert tm.sum()==9*n and vm.sum()==144 and np.array_equal(tm,z['is_training']) and np.array_equal(d,z['deals'])
            truth=exact[selected,row['bank']];assert np.array_equal(truth,z['exact_bb'])
            x=features([dict(active_features=a.tolist()) for a in active[selected]])
            y=torch.tensor(x,dtype=torch.float64)
            for layer in ('0','2','4'):
                y=torch.nn.functional.linear(y,torch.tensor(z[layer+'.weight'],dtype=torch.float64),torch.tensor(z[layer+'.bias'],dtype=torch.float64))
                if layer!='4':y=torch.relu(y)
            pred=(y[:,1]-y[:,0]).numpy()*400.5
            error=float(np.max(abs(pred-z['predicted_bb'])));maximum=max(maximum,error);assert error<1e-7
            for label,m in (('training',tm),('validation',vm)):
                p=pred[m];t=truth[m];count=len(t)
                values=dict(mse_bb2=math.fsum((float(a)-float(b))**2 for a,b in zip(p,t))/count,
                    decision_cost_bb=math.fsum(abs(float(b))*(.5 if a==0 else float(a*b<0)) for a,b in zip(p,t))/count)
                assert row[label]['rows']==count
                for key,value in values.items():
                    error=abs(value-row[label][key]);metric_error=max(metric_error,error);assert error<1e-9*max(1.,abs(value))
    assert not torch.cuda.is_initialized();verify(hashes)
    proof=dict(passed=True,complete=True,inputs=hashes,models=48,disjoint_deals_and_boards=True,
        original_final_evaluation_reused=False,maximum_saved_prediction_error_bb=maximum,maximum_metric_error=metric_error)
    dest=OUT/(NAME+'-readback.json');assert not dest.exists();atomic_json(dest,proof)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    counts=(8,16,32,48);aggregate=result['aggregate']
    fig,axes=plt.subplots(1,2,figsize=(11.5,4.8),layout='constrained')
    for split,color,label in (('training','#427d5b','Training error'),('validation','#b56b39','Development error')):
        axes[0].plot(counts,[aggregate[str(n)][split]['mse_bb2'] for n in counts],'-o',color=color,label=label)
    axes[0].set_yscale('log');axes[0].set_ylabel('Mean squared error (bb squared, log scale)');axes[0].legend()
    for rep in range(3):
        values=[np.mean([r['validation']['decision_cost_bb'] for r in rows if r['training_deals']==n and r['repetition']==rep]) for n in counts]
        axes[1].plot(counts,values,'--',alpha=.45,color='#4380a0',linewidth=1)
    axes[1].plot(counts,[aggregate[str(n)]['validation']['decision_cost_bb'] for n in counts],'-o',color='#245b78',label='Mean over all runs')
    axes[1].set_ylabel('Development call/fold decision cost (bb)');axes[1].legend()
    for ax in axes:
        ax.set_xlabel('Distinct training deals');ax.set_xticks(counts);ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Coverage diagnostic inside the original training pool\nSame learner and 512 steps; 16 development deals kept separate',fontsize=12)
    fig.text(.5,-.025,'Exploratory: the original final evaluation is not reused. Local errors, not bb/hand or preflop accuracy.',ha='center',fontsize=9)
    plot=OUT/(NAME+'.png');assert not plot.exists();fig.savefig(plot,dpi=170,bbox_inches='tight');plt.close(fig)
    lines=[]
    for n in counts:
        a=aggregate[str(n)];lines.append(f"| {n} | {a['training']['mse_bb2']:.3f} | {a['validation']['mse_bb2']:.3f} | {a['validation']['decision_cost_bb']:.3f} | {a['validation']['direction_agreement']*100:.1f}% |")
    table='\n'.join(lines);bank=[]
    for b in (0,1):
        for a in (0,1):
            values=[np.mean([r['validation']['decision_cost_bb'] for r in rows if r['bank']==b and r['actor']==a and r['training_deals']==n]) for n in counts]
            bank.append(f"| {'AB'[b]} / {('BB','BTN')[a]} | "+' | '.join(f'{v:.3f}' for v in values)+' |')
    bank_table='\n'.join(bank)
    text=f'''# Exact-target training coverage diagnostic

This exploratory diagnostic reuses only the original 64 training deals. It
keeps 16 of those deals separate for development validation and fits nested
sets of 8, 16, 32 and 48 deals. It does not re-score or tune on the original
32-deal final evaluation. Both banks, actors and all three new seeds are kept.

The architecture, visible inputs, exact targets, normalization, optimizer and
512-step budget remain fixed. All 48 models start fresh. Equal means over
banks, actors and repetitions are reported; no favorable run is selected.

| Training deals | Training MSE | Development MSE | Development decision cost (bb) | Direction agreement |
|---|---:|---:|---:|---:|
{table}

MSE is in bb squared. Decision costs concern the local Fold/Call pair, not
all legal actions or losses per dealt hand. Validation deals and all their
selected histories stay together. Multiple histories on one deal are not
independent samples. Dashed lines in the decision-cost plot are repetition
means, not confidence intervals.

![Training-only coverage curve]({NAME}.png)

| Bank / actor | Cost: 8 deals | 16 deals | 32 deals | 48 deals |
|---|---:|---:|---:|---:|
{bank_table}

The original exact-versus-sampled probe still failed its registered integration
gate. This development curve does not reverse that result or qualify a model
for production. A downward trend can motivate broader coverage, but these
small subsets do not establish a scaling law. Any later candidate needs fixed
settings and new final evaluation deals.

Saved weights reproduced their stored predictions within {maximum:.3g} bb;
scalar readback reproduced MSE and decision costs within {metric_error:.3g}.
Checks covered all 48 fits, disjoint deal/board groups, exact split membership,
and original-final-deal exclusion. Computation took {result['seconds']:.2f}
seconds and retained {result['storage']['logical_bytes']/1e6:.2f} MB. No new
native label collection, full self-play training or production changes ran.

Evidence: `{NAME}-result.json`, `{NAME}-readback.json`, and the frozen plan and
registration. All predictions and model weights are retained in the study's
`generalization-curve-v1` directory.
'''
    report=OUT/'BOARD-RIVER-GENERALIZATION-CURVE-FINDINGS.md';assert not report.exists()
    with report.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    print(dict(report=str(report),maximum_saved_prediction_error_bb=maximum,maximum_metric_error=metric_error))


if __name__=='__main__':main()
