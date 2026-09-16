"""One prospectively specified residual correction to cheap cached priors."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import continuation_pair_values as correction
import continuation_recalibrated_priors as prior

study=prior.study
OUT=prior.OUT.parent/'corrected-pair-priors-20260916'


def pair_values(model,equity):
    # Subtract equity because the correction helper includes it as its base.
    return prior.shares(np.asarray(model['priors']['class_base']),equity)+correction.pair_values(model['correction'],equity)-equity[None,:,:]


def predict(c,model,counts=None,equity=None):
    if counts is None:counts,equity=study.pilot.matrices()
    blend=min(c['case']['stack']/c['case']['pot']/8,1.)
    pred=c['raw']+blend*((correction.probabilities(c,counts)*pair_values(model,equity)).sum(axis=-1)-c['raw'])
    assert np.isfinite(pred).all() and abs((pred*c['mass']).sum()-1)<1e-9
    return pred


def fit(cases,counts,equity):
    base=prior.fit(cases,counts,equity)
    residual_cases=[dict(c,residual=c['raw']+c['residual']-prior.predict(c,base,counts,equity)) for c in cases]
    adjusted=correction.fit(residual_cases,counts)
    return dict(kind='corrected_pair_priors',priors=base,correction=adjusted,
        chance='compatible_pair',blend='min(SPR/8,1)',production_enabled=False)


def screen():
    paths=[study.ROOT/'tools/research/continuation_corrected_priors.py',OUT/'README.md',
        study.ROOT/'tools/research/continuation_recalibrated_priors.py',
        study.ROOT/'tools/research/continuation_pair_values.py',
        study.ROOT/'tools/research/range_value_pilot.py',study.ROOT/'tools/research/continuation_overnight_fit.py',
        study.ROOT/'cache/realization_fit.json',study.ROOT/'cache/preflop_eq169.bin',
        study.night.OUT/'manifest.json',study.OUT/'development/manifest.json',prior.OUT/'training-screen.json']
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},production_enabled=False))
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    previous={c['case']:c for c in study.read(prior.OUT/'training-screen.json')['cases']}
    assert set(previous)=={c['case']['id'] for c in cases}
    counts,equity=study.pilot.matrices();families=sorted({c['case']['family'] for c in cases});rows=[]
    for family in families:
        model=fit([c for c in cases if c['case']['family']!=family],counts,equity)
        for c in cases:
            if c['case']['family']!=family:continue
            control=study.pilot.metrics(c,prior.predict(c,model['priors'],counts,equity))
            assert abs(control['candidate']-previous[c['case']['id']]['candidate'])<1e-9,'Excluded-family N09 control changed'
            pred=predict(c,model,counts,equity)
            rows.append(dict(case=c['case']['id'],family=family,**study.pilot.metrics(c,pred),n09=control['candidate'],
                predicted_min=float(pred.min()),predicted_max=float(pred.max()),
                mass_outside_zero_one=float((c['mass']*((pred<0)|(pred>1))).sum()/2)))
        print('Finished excluded family',family,flush=True)
    family_means={name:{f:float(np.mean([r[name] for r in rows if r['family']==f])) for f in families}
        for name in ['candidate','n09','balanced','raw']}
    means={name:float(np.mean(list(values.values()))) for name,values in family_means.items()}
    comparisons={name:dict(improvement=1-means['candidate']/means[name],
        worst_family_ratio=max(family_means['candidate'][f]/family_means[name][f] for f in families)) for name in ['n09','balanced']}
    eligible=(comparisons['n09']['improvement']>=.05 and comparisons['balanced']['improvement']>=.15
        and all(v['worst_family_ratio']<=1.05 for v in comparisons.values()))
    study.freeze(OUT/'training-screen.json',dict(cases=rows,family_means=family_means,means=means,
        comparisons=comparisons,eligible=eligible,production_enabled=False,note='Both model stages exclude each validation family. Fixed training screen only.'))
    if eligible:
        model=fit(cases,counts,equity)
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families)
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),
            frozen_at=study.night.now(),prospective_references_generated=0))
    print('Eligible:',eligible,'comparisons:',comparisons,flush=True)


if __name__=='__main__':screen()
