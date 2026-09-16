"""Training-family-only predictor selection for the ten-hour night shift."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys
import numpy as np
import continuation_policy_refinement as study

OUT=study.ROOT/'research/preflop-evolution/continuation/night-shift-20260916'
CURVES=['equity*equity*pair','equity*equity*equity*pair',
        'equity*equity*suited','equity*equity*equity*suited',
        'equity*equity*ace','equity*equity*equity*ace',
        'low*low*pair','low*low*low*pair']


def features(c,kind):
    if kind=='base':
        return dict(c,x=c['base_x'],names=list(c['base_names']))
    encoded=study.fit.features(c,dict(kind='shape'))
    if kind=='shape':return encoded
    assert kind=='curvature'
    values={name:c['base_x'][...,i] for i,name in enumerate(c['base_names'])}
    extra=[];names=list(encoded['names'])
    for curve in CURVES:
        for suffix in ['', '*ip', '*log_spr']:
            name=curve+suffix
            extra.append(np.prod([values[part] for part in name.split('*')],axis=0))
            names.append(name)
    return dict(c,x=np.concatenate([encoded['x'],np.stack(extra,axis=-1)],axis=-1),names=names)


def fit(cases,kind,alpha):
    encoded=[features(c,kind) for c in cases]
    model=study.pilot.fit_ridge(encoded,alpha)
    model.update(encoder=dict(kind=kind),feature_names=encoded[0]['names'])
    return model


def predict(c,model):
    encoded=features(c,model['encoder']['kind'])
    assert encoded['names']==model['feature_names']
    return study.pilot.predict(encoded,model)


def select(mode):
    assert mode in ['pilot','final']
    cases=study.fit.load_cases('train')
    if mode=='final':cases+=study.contexts('development')
    families=sorted({c['case']['family'] for c in cases})
    assert len(families)==4
    assert all(c['case']['partition']=='train' for c in cases)
    scores=[]
    for kind in ['base','shape','curvature']:
        for alpha in [.03,.1,.3]:
            rows=[]
            for family in families:
                model=fit([c for c in cases if c['case']['family']!=family],kind,alpha)
                for c in cases:
                    if c['case']['family']==family:
                        rows.append(dict(case=c['case']['id'],family=family,**study.pilot.metrics(c,predict(c,model))))
            means={family:float(np.mean([r['candidate'] for r in rows if r['family']==family])) for family in families}
            scores.append(dict(kind=kind,alpha=alpha,feature_count=len(model['coef']),
                family_means=means,mean=float(np.mean(list(means.values()))),cases=rows))
            print(mode,kind,alpha,scores[-1]['mean'],flush=True)
    control=next(s for s in scores if s['kind']=='shape' and s['alpha']==.1)
    for s in scores:
        s['improvement']=1-s['mean']/control['mean']
        s['worst_family_ratio']=max(s['family_means'][f]/control['family_means'][f] for f in families)
        s['eligible']=s['improvement']>=.05 and s['worst_family_ratio']<=1.05
    eligible=[s for s in scores if s['eligible']]
    winner=min(eligible,key=lambda s:s['mean']) if eligible else None
    result=dict(mode=mode,cases=len(cases),scores=scores,selected=winner,
        selection='Fixed nine candidates, training-family-only CV; 5% mean improvement and no family worse by more than 5%.',
        provisional=mode=='pilot',production_enabled=False)
    study.freeze(OUT/f'curvature-{mode}-selection.json',result)
    if mode=='final' and winner is not None:
        model=fit(cases,winner['kind'],winner['alpha'])
        model.update(schema=3,production_enabled=False,training_case_ids=[c['case']['id'] for c in cases],
            training_families=families,selection_sha256=study.pilot.sha(OUT/f'curvature-{mode}-selection.json'))
        study.freeze(OUT/'curvature-candidate.json',model)
    print('Eligible:',[(s['kind'],s['alpha']) for s in eligible],flush=True)


if __name__=='__main__':select(sys.argv[1])
