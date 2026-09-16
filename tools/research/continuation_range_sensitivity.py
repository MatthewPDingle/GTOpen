"""Label-free local range sensitivity on training contexts only; no fitting."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import copy
from pathlib import Path
import numpy as np
import continuation_nonlinear_residual as network
import continuation_compact_residual as timing

study=network.study
OUT=network.OUT.parent/'range-sensitivity-20260916'
MODEL=network.OUT.parent/'shrunk-residual-20260916/candidate.json'


def perturb(weights,side,mask,epsilon):
    assert side in [0,1] and 0<epsilon<1 and np.any(mask)
    d=np.asarray(weights,dtype=float)*study.pilot.COMBOS
    d/=d.sum(axis=1,keepdims=True)
    target=mask*study.pilot.COMBOS;target=target/target.sum()
    shifted=d.copy();shifted[side]=(1-epsilon)*d[side]+epsilon*target
    tv=float(np.abs(shifted[side]-d[side]).sum()/2)
    assert 0<=tv<=epsilon+1e-12
    return shifted/study.pilot.COMBOS,tv


def context(case,counts,eq):
    c=study.pilot.context(case,counts,eq)
    c.update(case=case,base_x=c['x'].copy(),base_names=list(c['names']))
    return c


def predictions(c,model):
    return dict(candidate=network.predict(c,model),linear_base=study.fit.predict(c,model['base']),
        balanced=c['balanced'],raw=c['raw'])


def run():
    timing.require_no_timing()
    # No reference labels or holdout outcomes are loaded.
    fixtures=study.read(study.night.OUT/'fixtures.json')
    cases=[c for c in fixtures['cases'] if c['partition']=='train']
    assert len(cases)==24
    model=study.read(MODEL)
    assert study.pilot.sha(MODEL)==study.read(MODEL.parent/'candidate-freeze.json')['sha256']
    counts,eq=study.pilot.matrices()
    masks=dict(premium_pairs=np.array([a==b and a>=8 for a,b,s in study.pilot.PARTS]),
        offsuit_broadways=np.array([a!=b and not s and min(a,b)>=8 for a,b,s in study.pilot.PARTS]),
        suited_connectors=np.array([s and 0<a-b<=2 for a,b,s in study.pilot.PARTS]))
    rows=[]
    for case in cases:
        baseline=context(case,counts,eq);before=predictions(baseline,model)
        for side in [0,1]:
            for direction,mask in masks.items():
                for epsilon in [.001,.01]:
                    weights,tv=perturb(case['weights'],side,mask,epsilon)
                    altered=dict(copy.deepcopy(case),weights=weights.tolist())
                    c=context(altered,counts,eq);after=predictions(c,model)
                    assert tv>0
                    changes={name:float((baseline['mass']*np.abs(after[name]-before[name])).sum()*50) for name in before}
                    rows.append(dict(case=case['id'],side=['OOP','IP'][side],direction=direction,epsilon=epsilon,
                        range_tv=tv,weighted_value_change_pct_pot=changes,
                        change_per_one_percentage_point_range_tv={k:v/(tv*100) for k,v in changes.items()}))
    assert len(rows)==288
    summaries=[]
    for epsilon in [.001,.01]:
        for name in ['candidate','linear_base','balanced','raw']:
            values=[r['change_per_one_percentage_point_range_tv'][name] for r in rows if r['epsilon']==epsilon]
            summaries.append(dict(epsilon=epsilon,model=name,median=float(np.median(values)),p95=float(np.quantile(values,.95)),maximum=max(values)))
    OUT.mkdir(parents=True,exist_ok=True)
    caveat='Descriptive local response to prescribed small range mixtures on24 training contexts, without labels. Higher sensitivity can be legitimate and does not prove a convergence cause or prediction error. No model or acceptance gate changes.'
    study.night.dump(OUT/'diagnostic.json',dict(checked_at=study.night.now(),candidate_sha256=study.pilot.sha(MODEL),
        fixture_sha256=study.pilot.sha(study.night.OUT/'fixtures.json'),source_sha256=study.pilot.sha(__file__),
        cases=24,perturbations=288,rows=rows,summaries=summaries,caveat=caveat,production_enabled=False))
    lines=['# Local range sensitivity','',caveat,'',
        'Change in values (% pot) per one percentage point of actual range total variation. '
        'Values are weighted by original compatible hand mass; directions add premium pairs, offsuit broadways or suited connectors. '
        'The unchanged other player retains its original normalized range.', '',
        '| Mixture amount | Predictor | Median response | 95th percentile | Maximum |','|---|---|---:|---:|---:|']
    for r in summaries:lines.append(f"| {100*r['epsilon']:.1f}% | {r['model']} | {r['median']:.4f} | {r['p95']:.4f} | {r['maximum']:.4f} |")
    (OUT/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    print('\n'.join(lines),flush=True)


if __name__=='__main__':run()
