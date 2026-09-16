"""Descriptive hand-group accuracy; never changes fitting or acceptance gates."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys
import numpy as np
import continuation_shrunk_evaluation as fresh
import continuation_policy_transfer_optimized as transfer
import continuation_nonlinear_residual as network

study=transfer.study
GROUPS=['TT-AA','22-99','Suited broadways','Offsuit broadways','Other suited aces','Other suited hands','Other offsuit hands']


def group(label):
    ranks='23456789TJQKA';a,b=map(ranks.index,label[:2])
    if a==b:return 'TT-AA' if a>=8 else '22-99'
    suited=label.endswith('s')
    if min(a,b)>=8:return 'Suited broadways' if suited else 'Offsuit broadways'
    if suited and max(a,b)==12:return 'Other suited aces'
    return 'Other suited hands' if suited else 'Other offsuit hands'


def summarize(contexts,model,side=None):
    prior=study.read(study.night.OUT/'candidate.json')
    totals={g:dict(mass=0.,candidate=0.,balanced=0.,previous=0.,candidate_bias=0.) for g in GROUPS}
    masks={g:np.array([group(h)==g for h in study.pilot.LABELS]) for g in GROUPS}
    cases=[]
    for c in contexts:
        target=c['raw']+c['residual'];w=c['mass']*(c['observed']>0)
        if side is not None:w[1-side]=0
        assert w.sum()>0
        w=w/w.sum()
        predictions=dict(candidate=network.predict(c,model),balanced=c['balanced'],previous=study.fit.predict(c,prior))
        errors={k:float((w*np.abs(v-target)).sum()*100) for k,v in predictions.items()}
        cases.append(dict(case=c['case']['id'],mae_pct_pot=errors))
        for g,mask in masks.items():
            weights=w[:,mask]/len(contexts);totals[g]['mass']+=float(weights.sum())
            for name,pred in predictions.items():totals[g][name]+=float((weights*np.abs(pred[:,mask]-target[:,mask])).sum()*100)
            totals[g]['candidate_bias']+=float((weights*(predictions['candidate'][:,mask]-target[:,mask])).sum()*100)
    rows=[]
    for name,t in totals.items():
        mass=t.pop('mass')
        rows.append(dict(group=name,mass_fraction=mass,**{k:v/mass if mass>0 else None for k,v in t.items()}))
    assert abs(sum(r['mass_fraction'] for r in rows)-1)<1e-10
    return dict(cases=cases,groups=rows)


def run(name):
    assert name in ['N15','N20']
    if name=='N15':
        directory=fresh.OUT;contexts=fresh.adapter().contexts('prospective')
    else:
        directory=transfer.OUT/name
        assert (directory/'evaluation.json').exists(),'Do not inspect an incomplete changed-policy evaluation'
        contexts=transfer.adapter().adapter(directory).contexts('prospective')
    evaluation=study.read(directory/'evaluation.json');model=study.read(directory/'candidate.json')
    assert study.pilot.sha(directory/'candidate.json')==evaluation['candidate_sha256']
    result=summarize(contexts,model)
    expected={r['case']:r['mae_pct_pot'] for r in evaluation['cases']}
    for case in result['cases']:
        for metric,value in case['mae_pct_pot'].items():assert abs(value-expected[case['case']][metric])<1e-9
    result['by_position']={label:summarize(contexts,model,side)['groups'] for side,label in enumerate(['OOP','IP'])}
    result.update(checked_at=study.night.now(),model=name,source_sha256=study.pilot.sha(__file__),
        candidate_sha256=evaluation['candidate_sha256'],evaluation_sha256=study.pilot.sha(directory/'evaluation.json'),
        production_enabled=False,interpretation='Descriptive only; groups were not used for fitting or acceptance. Equal context weight and within-context compatible mass. Errors/bias are percent of pot; positive bias means overvaluation. Small group mass and finite reference samples limit inference.')
    study.night.dump(directory/'hand-group-diagnostics.json',result)
    lines=['# Hand-group diagnostic: '+name,'',result['interpretation'],'']
    for title,rows in [('Both positions',result['groups']),*result['by_position'].items()]:
        lines += ['## '+title,'',
            '| Group | Range mass | Balanced error | Previous error | Candidate error | Candidate signed bias |',
            '|---|---:|---:|---:|---:|---:|']
        for row in rows:
            fmt=lambda k:f"{row[k]:.3f}" if row[k] is not None else 'unavailable'
            lines.append(f"| {row['group']} | {100*row['mass_fraction']:.2f}% | {fmt('balanced')} | {fmt('previous')} | {fmt('candidate')} | {fmt('candidate_bias')} |")
        lines += ['']
    (directory/'HAND-GROUPS.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8',newline='\n')
    print('\n'.join(lines),flush=True)


if __name__=='__main__':run(sys.argv[1])
