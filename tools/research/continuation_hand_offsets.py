"""Cheap-to-evaluate hand-specific residuals, selected only on training families."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys
import numpy as np
import continuation_policy_refinement as study
import continuation_curvature as curvature

OUT=curvature.OUT


def features(c,kind):
    encoded=study.fit.features(c,dict(kind='shape'))
    kinds={'hand_bias':['bias'], 'hand_equity':['bias','equity'], 'hand_equity_ip':['bias','equity','ip']}
    columns=[];names=list(encoded['names'])
    eye=np.broadcast_to(np.eye(169),(2,169,169))
    for field in kinds[kind]:
        value={'bias':np.ones((2,169)), 'equity':c['raw'], 'ip':np.broadcast_to(np.arange(2)[:,None],(2,169))}[field]
        columns.append(eye*value[...,None])
        names += [f'hand_{field}_{h}' for h in range(169)]
    return dict(c,x=np.concatenate([encoded['x'],*columns],axis=-1),names=names)


def fit(cases,kind,alpha):
    encoded=[features(c,kind) for c in cases]
    model=study.pilot.fit_ridge(encoded,alpha)
    model.update(encoder=dict(kind=kind),feature_names=encoded[0]['names'])
    return model


def predict(c,model):
    encoded=features(c,model['encoder']['kind'])
    assert encoded['names']==model['feature_names']
    return study.pilot.predict(encoded,model)


def predict_compact(c,model):
    """Equivalent inference with at most three table lookups per hand."""
    encoded=study.fit.features(c,dict(kind='shape'))
    n=encoded['x'].shape[-1]
    mean=np.array(model['mean']);scale=np.array(model['scale']);coef=np.array(model['coef'])
    correction=((encoded['x']-mean[:n])/scale[:n])@coef[:n]
    tables=(coef[n:]/scale[n:]).reshape(-1,169)
    correction-=float((coef[n:]/scale[n:])@mean[n:])
    correction+=tables[0]
    if len(tables)>=2:correction+=tables[1]*c['raw']
    if len(tables)>=3:correction+=tables[2]*np.arange(2)[:,None]
    correction-=(correction*c['mass']).sum()/2
    return c['raw']+correction


def select(mode):
    assert mode in ['pilot','final']
    cases=study.fit.load_cases('train')
    if mode=='final':cases+=study.contexts('development')
    families=sorted({c['case']['family'] for c in cases})
    assert len(families)==4 and all(c['case']['partition']=='train' for c in cases)
    control=study.read(OUT/f'curvature-{mode}-selection.json')
    control=next(s for s in control['scores'] if s['kind']=='shape' and s['alpha']==.1)
    scores=[]
    for kind in ['hand_bias','hand_equity','hand_equity_ip']:
        for alpha in [.03,.1,.3,1.]:
            rows=[]
            for family in families:
                model=fit([c for c in cases if c['case']['family']!=family],kind,alpha)
                for c in cases:
                    if c['case']['family']==family:
                        rows.append(dict(case=c['case']['id'],family=family,**study.pilot.metrics(c,predict(c,model))))
            means={f:float(np.mean([r['candidate'] for r in rows if r['family']==f])) for f in families}
            mean=float(np.mean(list(means.values())))
            improvement=1-mean/control['mean']
            worst=max(means[f]/control['family_means'][f] for f in families)
            scores.append(dict(kind=kind,alpha=alpha,feature_count=len(model['coef']),family_means=means,mean=mean,
                improvement=improvement,worst_family_ratio=worst,eligible=improvement>=.05 and worst<=1.05,cases=rows))
            print(mode,kind,alpha,mean,'improvement',improvement,'worst ratio',worst,flush=True)
    eligible=[s for s in scores if s['eligible']]
    winner=min(eligible,key=lambda s:s['mean']) if eligible else None
    result=dict(mode=mode,cases=len(cases),scores=scores,selected=winner,provisional=mode=='pilot',production_enabled=False,
        selection='Fixed twelve hand-offset candidates; same training-family CV eligibility rules as curvature; select once on 26 cases before new evaluation.')
    study.freeze(OUT/f'hand-offset-{mode}-selection.json',result)
    if mode=='final' and winner is not None:
        model=fit(cases,winner['kind'],winner['alpha'])
        model.update(schema=4,production_enabled=False,training_case_ids=[c['case']['id'] for c in cases],training_families=families,
            selection_sha256=study.pilot.sha(OUT/f'hand-offset-{mode}-selection.json'))
        study.freeze(OUT/'hand-offset-candidate.json',model)
    print('Eligible:',[(s['kind'],s['alpha']) for s in eligible],flush=True)


if __name__=='__main__':select(sys.argv[1])
