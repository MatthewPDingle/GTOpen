"""Descriptive coverage and disjoint hand groups for the completed N21 check."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
import continuation_flop_menu as menu
import continuation_coverage_audit as coverage

study=menu.study

def group(hi,lo,suited):
    if hi==lo:return 'QQ+ pairs' if hi>=10 else 'Other pairs'
    if lo>=8:return 'Suited broadways' if suited else 'Offsuit broadways'
    if suited and hi==12 and lo<=3:return 'Suited wheel aces'
    if suited and hi-lo<=2:return 'Other suited connectors/gappers'
    return 'Other unpaired'

def run():
    assert study.read(menu.OUT/'status.json')['stage']=='complete'
    runner=menu.adapter();manifest=runner.checked('prospective');contexts=runner.contexts('prospective')
    model=study.read(menu.OUT/'candidate.json');groups=np.array([group(*p) for p in study.pilot.PARTS])
    names=sorted(set(groups));assert len(names)==7
    cases=[];coverage_rows=[];pooled=[]
    inputs={str(p.resolve().relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in [
        Path(__file__),Path(coverage.__file__),menu.OUT/'candidate.json',menu.OUT/'reference-audit.json',menu.OUT/'evaluation.json']}
    for c in contexts:
        coverage_rows.append(coverage.summarize(c['case'],c['rows']))
        target=c['raw']+c['residual'];predictions=dict(candidate=menu.bounds.shrunk.network.predict(c,model),balanced=c['balanced'])
        for side in [0,1]:
            for name in names:
                weight=c['mass'][side]*(groups==name)*(c['observed'][side]>0)
                total=float(weight.sum())
                if total==0:continue
                cases.append(dict(case=c['case']['id'],menu=c['case']['menu'],side=['OOP','IP'][side],group=name,mass=total,
                    error_numerator={k:float((weight*np.abs(v[side]-target[side])).sum()*100) for k,v in predictions.items()},
                    signed_numerator={k:float((weight*(v[side]-target[side])).sum()*100) for k,v in predictions.items()}))
    for which in ['control','expanded']:
        for side in ['OOP','IP']:
            for name in names:
                selected=[r for r in cases if r['menu']==which and r['side']==side and r['group']==name]
                mass=sum(r['mass'] for r in selected)
                if mass==0:continue
                pooled.append(dict(menu=which,side=side,group=name,mean_range_mass=mass/4,
                    mae_pct_pot={k:sum(r['error_numerator'][k] for r in selected)/mass for k in ['candidate','balanced']},
                    signed_error_pct_pot={k:sum(r['signed_numerator'][k] for r in selected)/mass for k in ['candidate','balanced']}))
    for p,h in inputs.items():assert study.pilot.sha(study.ROOT/p)==h,p
    result=dict(checked_at=study.night.now(),inputs=inputs,coverage=coverage_rows,pooled=pooled,cases=cases,
        all_positive_classes_observed=all(r['all_positive_classes_observed'] for r in coverage_rows),production_enabled=False,
        caveat='Post-evaluation descriptive breakdown, no changed acceptance gate. Seven disjoint groups, equal case weighting before group normalization. No subgroup confidence intervals or population inference. Effective weight counts are descriptive, not independent sample sizes.')
    study.freeze(menu.OUT/'hand-group-coverage.json',result)
    lines=['# N21 hand groups and coverage','',result['caveat'],'','| Menu | Side | Hand group | Mean range mass | Candidate MAE (% pot) | Balanced MAE (% pot) | Candidate signed error |','|---|---|---|---:|---:|---:|---:|']
    for r in pooled:
        lines.append(f"| {r['menu']} | {r['side']} | {r['group']} | {100*r['mean_range_mass']:.2f}% | {r['mae_pct_pot']['candidate']:.3f} | {r['mae_pct_pot']['balanced']:.3f} | {r['signed_error_pct_pot']['candidate']:.3f} |")
    lines += ['',f"All positive-weight classes observed: {result['all_positive_classes_observed']}. Every case has 20 planned boards. Passing coverage does not imply precise hand values.",'']
    (menu.OUT/'HAND-GROUPS.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print('Coverage:',result['all_positive_classes_observed'])
    for r in pooled:
        if r['mae_pct_pot']['candidate']>r['mae_pct_pot']['balanced']:print('Group regression:',r)

if __name__=='__main__':run()
