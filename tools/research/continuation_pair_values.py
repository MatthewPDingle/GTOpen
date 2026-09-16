"""Fixed cached additive pair-value candidate; no production mutation."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import continuation_policy_refinement as study

OUT=study.ROOT/'research/preflop-evolution/continuation/pair-value-adjustments-20260916'
REGULARIZATION=.01


def probabilities(c,counts):
    weights=np.asarray(c['case']['weights'])
    weighted=counts[None,:,:]*weights[::-1,None,:]
    total=weighted.sum(axis=-1,keepdims=True)
    assert (total>0).all()
    return weighted/total


def features(c,counts):
    opponent=probabilities(c,counts)
    eye=np.eye(169)[None,:,:]
    sign=np.array([-1.,1.])[:,None,None]
    blend=min(c['case']['stack']/c['case']['pot']/8,1.)
    assert blend>=0
    return blend*np.concatenate([eye-opponent,sign*(eye+opponent)],axis=-1)


def pair_values(model,equity):
    a=np.asarray(model['hand_adjustment']);b=np.asarray(model['position_adjustment'])
    assert a.shape==b.shape==(169,) and np.isfinite([a,b]).all()
    transfer=a[:,None]-a[None,:]
    position=b[:,None]+b[None,:]
    return np.array([equity+transfer-position,equity+transfer+position])


def predict(c,model,counts=None,equity=None):
    if counts is None:counts,equity=study.pilot.matrices()
    opponent=probabilities(c,counts)
    pair=pair_values(model,equity)
    blend=min(c['case']['stack']/c['case']['pot']/8,1.)
    values=c['raw']+blend*((opponent*pair).sum(axis=-1)-c['raw'])
    assert np.isfinite(values).all() and abs((values*c['mass']).sum()-1)<1e-9
    return values


def fit(cases,counts,regularization=REGULARIZATION):
    assert regularization>=0 and cases
    xs=[];ys=[]
    for c in cases:
        weights=c['mass']*(c['observed']>0)
        assert weights.sum()>0
        root=np.sqrt(weights/weights.sum()/len(cases)).reshape(-1)
        xs.append(features(c,counts).reshape(-1,338)*root[:,None])
        ys.append(c['residual'].reshape(-1)*root)
    penalty=np.eye(338)*np.sqrt(regularization/169)
    coef=np.linalg.lstsq(np.concatenate([*xs,penalty]),np.concatenate([*ys,np.zeros(338)]),rcond=None)[0]
    coef[:169]-=coef[:169].mean()
    return dict(kind='additive_pair_values',hand_adjustment=coef[:169].tolist(),
        position_adjustment=coef[169:].tolist(),regularization=regularization,
        chance='compatible_pair',blend='min(SPR/8,1)',dtype='float64',device='cpu',production_enabled=False)


def screen():
    sources=[study.ROOT/'tools/research/continuation_pair_values.py',OUT/'README.md',
        study.ROOT/'tools/research/range_value_pilot.py',study.ROOT/'tools/research/continuation_overnight_fit.py',
        study.ROOT/'cache/realization_fit.json',study.ROOT/'cache/preflop_eq169.bin',
        study.night.OUT/'manifest.json',study.OUT/'development/manifest.json',
        OUT.parent/'recalibrated-priors-20260916/training-screen.json']
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in sources},production_enabled=False))
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    counts,equity=study.pilot.matrices()
    previous=study.read(OUT.parent/'recalibrated-priors-20260916/training-screen.json')
    previous_rows={c['case']:c for c in previous['cases']}
    assert set(previous_rows)=={c['case']['id'] for c in cases}
    families=sorted({c['case']['family'] for c in cases});rows=[]
    for family in families:
        model=fit([c for c in cases if c['case']['family']!=family],counts)
        for c in cases:
            if c['case']['family']!=family:continue
            prediction=predict(c,model,counts,equity)
            errors=study.pilot.metrics(c,prediction)
            control=previous_rows[c['case']['id']]
            assert control['family']==family and abs(control['balanced']-errors['balanced'])<1e-10
            rows.append(dict(case=c['case']['id'],family=family,**errors,n09=control['candidate'],
                predicted_min=float(prediction.min()),predicted_max=float(prediction.max()),
                mass_outside_zero_one=float((c['mass']*((prediction<0)|(prediction>1))).sum()/2)))
        print('Finished excluded family',family,flush=True)
    family_means={name:{f:float(np.mean([r[name] for r in rows if r['family']==f])) for f in families}
        for name in ['candidate','n09','balanced','raw']}
    means={name:float(np.mean(list(values.values()))) for name,values in family_means.items()}
    comparisons={name:dict(improvement=1-means['candidate']/means[name],
        worst_family_ratio=max(family_means['candidate'][f]/family_means[name][f] for f in families)) for name in ['n09','balanced']}
    eligible=(comparisons['n09']['improvement']>=.05 and comparisons['balanced']['improvement']>=.15
        and all(c['worst_family_ratio']<=1.05 for c in comparisons.values()))
    result=dict(cases=rows,family_means=family_means,means=means,comparisons=comparisons,eligible=eligible,
        production_enabled=False,note='Fixed training-family screen; no prospective outcomes or deployment evidence.')
    study.freeze(OUT/'training-screen.json',result)
    if eligible:
        model=fit(cases,counts)
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families)
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),
            frozen_at=study.night.now(),prospective_references_generated=0))
    print('Eligible:',eligible,'comparisons:',comparisons,flush=True)


if __name__=='__main__':screen()
