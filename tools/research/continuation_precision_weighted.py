"""Fixed training-case precision weights; unchanged cheap shape inference."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import continuation_bridge_run as bridge

study=bridge.study
OUT=study.ROOT/'research/preflop-evolution/continuation/precision-weighted-20260916'


def fit(cases,power):
    assert power in [0.,.5,1.]
    weights=[(len(c['rows'])/100)**power for c in cases]
    assert all(w>0 for w in weights)
    encoded=[study.fit.features(c,dict(kind='shape')) for c in cases]
    weighted=[dict(c,mass=c['mass']*w) for c,w in zip(encoded,weights)]
    # fit_ridge divides its alpha by len(cases). Keep the unnormalized
    # penalty fixed as the total effective case weight changes.
    alpha=.1*len(cases)/sum(weights)
    model=study.pilot.fit_ridge(weighted,alpha)
    model.update(encoder=dict(kind='shape'),feature_names=encoded[0]['names'],
        precision_weight_power=power,effective_case_weight=sum(weights),base_ridge_penalty=.1)
    return model


def screen():
    original=study.fit.load_cases('train')+study.contexts('development')
    cases=original+bridge.contexts('training')
    assert len(original)==26 and len(cases)==62 and all(c['case']['partition']=='train' for c in cases)
    prior_path=study.ROOT/'research/preflop-evolution/continuation/nonlinear-residual-20260916/training-screen.json'
    prior=study.read(prior_path)['scores'][0]
    assert sorted(r['case'] for r in prior['cases'])==sorted(c['case']['id'] for c in original)
    sources=['tools/research/continuation_precision_weighted.py',
        'research/preflop-evolution/continuation/precision-weighted-20260916/README.md',
        'tools/research/continuation_overnight_fit.py','tools/research/range_value_pilot.py',
        str(prior_path.relative_to(study.ROOT)),str((bridge.OUT/'training/manifest.json').relative_to(study.ROOT))]
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={p:study.pilot.sha(study.ROOT/p) for p in sources},production_enabled=False))
    families=sorted({c['case']['family'] for c in cases});assert len(families)==4
    scores=[]
    for power in [0.,.5,1.]:
        rows=[]
        for family in families:
            model=fit([c for c in cases if c['case']['family']!=family],power)
            for c in original:
                if c['case']['family']==family:
                    rows.append(dict(case=c['case']['id'],family=family,**study.pilot.metrics(c,study.fit.predict(c,model))))
        means={f:float(np.mean([r['candidate'] for r in rows if r['family']==f])) for f in families}
        scores.append(dict(power=power,cases=rows,family_means=means,mean=float(np.mean(list(means.values())))))
        print(power,scores[-1]['mean'],flush=True)
    controls={'same_expanded_data':scores[0],'prior_26_case_data':prior}
    for score in scores:
        score['comparisons']={key:dict(improvement=1-score['mean']/control['mean'],
            worst_family_ratio=max(score['family_means'][f]/control['family_means'][f] for f in families))
            for key,control in controls.items()}
        score['eligible']=all(r['improvement']>=.05 and r['worst_family_ratio']<=1.05 for r in score['comparisons'].values())
    eligible=[s for s in scores[1:] if s['eligible']]
    winner=min(eligible,key=lambda s:s['mean']) if eligible else None
    study.freeze(OUT/'training-screen.json',dict(training_cases=62,validation_cases=26,scores=scores,selected=winner,
        production_enabled=False,note='Training-family selection only; both controls must pass.'))
    if winner:
        model=fit(cases,winner['power'])
        model.update(schema=2,production_enabled=False,training_case_ids=[c['case']['id'] for c in cases],training_families=families,
            selection_sha256=study.pilot.sha(OUT/'training-screen.json'))
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),frozen_at=study.night.now(),
            prospective_references_generated=0))
    print('Selected:',None if winner is None else winner['power'],flush=True)


if __name__=='__main__':screen()
