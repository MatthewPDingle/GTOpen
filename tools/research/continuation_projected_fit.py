"""Train the pot-conserving linear function, using only fixed training families."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import continuation_policy_refinement as study

OUT=study.ROOT/'research/preflop-evolution/continuation/projected-fit-20260916'


def project(c):
    assert abs(c['mass'].sum()-2)<1e-10
    assert (c['mass']*(c['observed']==0)).sum()<1e-12
    mean=(c['x']*c['mass'][...,None]).sum(axis=(0,1))/2
    return dict(c,x=c['x']-mean)


def fit(cases,alpha):
    encoded=[study.fit.features(c,dict(kind='shape')) for c in cases]
    model=study.pilot.fit_ridge([project(c) for c in encoded],alpha)
    model.update(encoder=dict(kind='shape'),feature_names=encoded[0]['names'],
        fitting_projection='Case-wise compatible-mass centering of feature columns; ordinary inference unchanged.')
    return model


def screen():
    sources=['tools/research/continuation_projected_fit.py',
        'research/preflop-evolution/continuation/projected-fit-20260916/README.md',
        'tools/research/continuation_overnight_fit.py','tools/research/range_value_pilot.py',
        str((study.OUT/'development/manifest.json').relative_to(study.ROOT))]
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={p:study.pilot.sha(study.ROOT/p) for p in sources},
        production_enabled=False))
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    families=sorted({c['case']['family'] for c in cases});assert len(families)==4
    results=[]
    for kind,alpha in [('ordinary',.1),('projected',.03),('projected',.1),('projected',.3)]:
        rows=[]
        for family in families:
            training=[c for c in cases if c['case']['family']!=family]
            model=study.fit.fit(training,'shape',alpha) if kind=='ordinary' else fit(training,alpha)
            for case in cases:
                if case['case']['family']==family:
                    rows.append(dict(case=case['case']['id'],family=family,
                        **study.pilot.metrics(case,study.fit.predict(case,model))))
        means={f:float(np.mean([r['candidate'] for r in rows if r['family']==f])) for f in families}
        results.append(dict(kind=kind,alpha=alpha,cases=rows,family_means=means,mean=float(np.mean(list(means.values())))))
        print(kind,alpha,results[-1]['mean'],flush=True)
    control=results[0]
    for result in results:
        result['improvement']=1-result['mean']/control['mean']
        result['worst_family_ratio']=max(result['family_means'][f]/control['family_means'][f] for f in families)
        result['eligible']=result['improvement']>=.05 and result['worst_family_ratio']<=1.05
    eligible=[r for r in results[1:] if r['eligible']]
    winner=min(eligible,key=lambda r:r['mean']) if eligible else None
    study.freeze(OUT/'training-screen.json',dict(cases=26,scores=results,selected=winner,
        production_enabled=False,note='Training-family model selection only; no evaluation labels used.'))
    if winner:
        model=fit(cases,winner['alpha'])
        model.update(schema=2,production_enabled=False,training_case_ids=[c['case']['id'] for c in cases],
            training_families=families,selection_sha256=study.pilot.sha(OUT/'training-screen.json'))
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),frozen_at=study.night.now(),
            prospective_references_generated=0))
    print('Selected:',None if winner is None else winner['alpha'],flush=True)


if __name__=='__main__':screen()
