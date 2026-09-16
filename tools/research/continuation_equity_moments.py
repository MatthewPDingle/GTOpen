"""Fixed additional range-shape information from equity distribution moments."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import continuation_policy_refinement as study

OUT=study.ROOT/'research/preflop-evolution/continuation/equity-moments-20260916'


def moments(c,counts,equity):
    w=np.asarray(c['case']['weights'])
    weighted=counts[None,:,:]*w[::-1,None,:]
    den=weighted.sum(axis=-1,keepdims=True)
    assert (den>0).all()
    probability=weighted/den
    return np.stack([(probability*equity[None,:,:]**power).sum(axis=-1) for power in [2,3,4]],axis=-1)


def features(c,counts,equity):
    original=study.fit.features(c,dict(kind='shape'))
    values=moments(c,counts,equity)
    pair=np.array([a==b for a,b,_ in study.pilot.PARTS])
    suited=np.array([s for _,_,s in study.pilot.PARTS])
    modifiers=[('equity',c['raw']),('pair',pair),('suited',suited),
        ('ip',np.array([0.,1.])[:,None]),('log_spr',np.log1p(c['case']['stack']/c['case']['pot']))]
    columns=[];names=list(original['names'])
    for k,power in enumerate([2,3,4]):
        value=values[:,:,k];name=f'eq_m{power}'
        columns.append(value);names.append(name)
        for label,modifier in modifiers:
            columns.append(value*modifier);names.append(name+'*'+label)
    result=dict(original,x=np.concatenate([original['x'],np.stack(columns,axis=-1)],axis=-1),names=names)
    assert result['x'].shape==(2,169,122) and len(set(names))==122
    return result


def fit(cases,counts,equity):
    encoded=[features(c,counts,equity) for c in cases]
    model=study.pilot.fit_ridge(encoded,.1)
    model.update(encoder=dict(kind='shape_equity_moments'),feature_names=encoded[0]['names'],
        powers=[2,3,4],alpha=.1,production_enabled=False)
    return model


def predict(c,model,counts=None,equity=None):
    if counts is None:counts,equity=study.pilot.matrices()
    assert model['encoder']['kind']=='shape_equity_moments' and model['powers']==[2,3,4]
    encoded=features(c,counts,equity);assert encoded['names']==model['feature_names']
    return study.pilot.predict(encoded,model)


def screen():
    # Heavy work is explicitly kept out of the currently running timing pass.
    queue_path=OUT.parent/'night-shift-20260916/queue-status.json'
    if queue_path.exists():
        assert study.read(queue_path)['stage'] not in ['runtime_benchmark','prior_gpu_benchmark'],'Timing is active; wait for the reference stage'
    paths=[study.ROOT/'tools/research/continuation_equity_moments.py',OUT/'README.md',
        study.ROOT/'tools/research/continuation_policy_refinement.py',
        study.ROOT/'tools/research/continuation_overnight.py',
        study.ROOT/'tools/research/continuation_checkpoint.py',
        study.ROOT/'tools/research/continuation_overnight_fit.py',study.ROOT/'tools/research/range_value_pilot.py',
        study.ROOT/'cache/preflop_eq169.bin',study.ROOT/'cache/realization_fit.json',
        study.night.OUT/'manifest.json',study.OUT/'development/manifest.json',
        OUT.parent/'nonlinear-residual-20260916/training-screen.json']
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},production_enabled=False))
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    counts,equity=study.pilot.matrices();families=sorted({c['case']['family'] for c in cases});rows=[]
    recorded=study.read(OUT.parent/'nonlinear-residual-20260916/training-screen.json')['scores'][0]
    old_rows={c['case']:c for c in recorded['cases']}
    assert set(old_rows)=={c['case']['id'] for c in cases}
    for family in families:
        training=[c for c in cases if c['case']['family']!=family]
        model=fit(training,counts,equity);control=study.fit.fit(training,'shape',.1)
        for c in cases:
            if c['case']['family']!=family:continue
            original=study.pilot.metrics(c,study.fit.predict(c,control))['candidate']
            assert abs(original-old_rows[c['case']['id']]['candidate'])<1e-9,'Original control changed'
            rows.append(dict(case=c['case']['id'],family=family,**study.pilot.metrics(c,predict(c,model,counts,equity)),original=original))
        print('Finished moment-feature excluded family',family,flush=True)
    means={f:float(np.mean([r['candidate'] for r in rows if r['family']==f])) for f in families}
    mean=float(np.mean(list(means.values())));improvement=1-mean/recorded['mean']
    worst=max(means[f]/recorded['family_means'][f] for f in families)
    eligible=improvement>=.05 and worst<=1.05
    study.freeze(OUT/'training-screen.json',dict(cases=rows,family_means=means,mean=mean,
        improvement=improvement,worst_family_ratio=worst,eligible=eligible,production_enabled=False,
        note='Fixed 122-feature training-family screen on original 26 cases; no evaluation labels.'))
    if eligible:
        model=fit(cases,counts,equity)
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families)
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),
            frozen_at=study.night.now(),prospective_references_generated=0))
    print('Moment-feature eligible:',eligible,'improvement',improvement,'worst-family ratio',worst,flush=True)


if __name__=='__main__':screen()
