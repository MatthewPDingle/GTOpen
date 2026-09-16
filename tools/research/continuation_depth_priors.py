"""Fixed depth-aware cached prior tables; training inputs only."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import torch
import continuation_recalibrated_priors as prior

study=prior.study
OUT=prior.OUT.parent/'depth-pair-priors-20260916'
KNOTS=np.array([1.,2.,4.,8.,16.,20.])
torch.set_num_threads(2)


def interpolation(spr):
    assert np.isfinite(spr) and spr>=0
    value=np.clip(spr,KNOTS[0],KNOTS[-1])
    upper=min(max(int(np.searchsorted(KNOTS,value,side='right')),1),len(KNOTS)-1)
    lower=upper-1
    fraction=(np.log(value)-np.log(KNOTS[lower]))/(np.log(KNOTS[upper])-np.log(KNOTS[lower]))
    return lower,upper,float(fraction)


def tables(model,equity):
    assert model['knots']==KNOTS.tolist()
    base=np.asarray(model['base_priors']);a=np.asarray(model['intercept']);b=np.asarray(model['slope'])
    assert base.shape==a.shape==b.shape==(169,) and np.isfinite([base,a,b]).all() and (base>0).all()
    return np.array([prior.shares(base*np.exp(a+np.log(s/8)*b),equity) for s in KNOTS])


def predict(c,model,counts=None,equity=None):
    if counts is None:counts,equity=study.pilot.matrices()
    spr=c['case']['stack']/c['case']['pot'];lo,hi,fraction=interpolation(spr)
    values=tables(model,equity);pair=values[lo]*(1-fraction)+values[hi]*fraction
    relative=(prior.opponent_probabilities(c,counts)*pair).sum(axis=-1)
    result=c['raw']+min(spr/8,1)*(relative-c['raw'])
    assert np.isfinite(result).all() and abs((result*c['mass']).sum()-1)<1e-9
    return result


def fit(cases,counts,equity):
    dtype=torch.float64;base=torch.tensor(prior.priors(),dtype=dtype);eq=torch.tensor(equity,dtype=dtype)
    opponent=torch.tensor(np.array([prior.opponent_probabilities(c,counts) for c in cases]),dtype=dtype)
    raw=torch.tensor(np.array([c['raw'] for c in cases]),dtype=dtype)
    target=torch.tensor(np.array([c['raw']+c['residual'] for c in cases]),dtype=dtype)
    mass=torch.tensor(np.array([c['mass'] for c in cases]),dtype=dtype)
    spr=[c['case']['stack']/c['case']['pot'] for c in cases]
    brackets=[interpolation(s) for s in spr]
    lower=torch.tensor([v[0] for v in brackets]);upper=torch.tensor([v[1] for v in brackets])
    fraction=torch.tensor([v[2] for v in brackets],dtype=dtype)[:,None,None,None]
    blend=torch.tensor([min(s/8,1) for s in spr],dtype=dtype)[:,None,None]
    logdepth=torch.tensor(np.log(KNOTS/8),dtype=dtype)[:,None]
    d0=torch.nn.Parameter(torch.zeros(169,dtype=dtype));d1=torch.nn.Parameter(torch.zeros(169,dtype=dtype))
    optimizer=torch.optim.Adam([d0,d1],lr=.02)
    for _ in range(600):
        optimizer.zero_grad();a=d0-d0.mean();b=d1-d1.mean()
        q=base[None,:]*torch.exp(a[None,:]+logdepth*b[None,:]);adjusted=[]
        for position in [.92,1.08]:
            numer=eq[None,:,:]*q[:,:,None]*position
            other=(1-eq[None,:,:])*q[:,None,:]*(2-position)
            adjusted.append(numer/(numer+other))
        pair=torch.stack(adjusted,dim=1)
        mixed=pair[lower]*(1-fraction)+pair[upper]*fraction
        relative=(opponent*mixed).sum(dim=-1)
        pred=raw+blend*(relative-raw)
        loss=((pred-target).square()*mass).sum()/(2*len(cases))+.001*a.square().mean()+.01*b.square().mean()
        assert torch.isfinite(loss)
        loss.backward();optimizer.step()
    return dict(kind='depth_pair_priors',base_priors=base.tolist(),intercept=(d0-d0.mean()).detach().tolist(),
        slope=(d1-d1.mean()).detach().tolist(),knots=KNOTS.tolist(),steps=600,learning_rate=.02,
        regularization=dict(intercept=.001,slope=.01),chance='compatible_pair',blend='min(SPR/8,1)',
        dtype='float64',device='cpu',production_enabled=False)


def screen():
    paths=[study.ROOT/'tools/research/continuation_depth_priors.py',OUT/'README.md',
        study.ROOT/'tools/research/continuation_recalibrated_priors.py',
        study.ROOT/'tools/research/range_value_pilot.py',study.ROOT/'tools/research/continuation_overnight_fit.py',
        study.ROOT/'cache/realization_fit.json',study.ROOT/'cache/preflop_eq169.bin',
        study.night.OUT/'manifest.json',study.OUT/'development/manifest.json',prior.OUT/'training-screen.json']
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},production_enabled=False))
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    controls={c['case']:c for c in study.read(prior.OUT/'training-screen.json')['cases']}
    assert set(controls)=={c['case']['id'] for c in cases}
    counts,equity=study.pilot.matrices();families=sorted({c['case']['family'] for c in cases});rows=[]
    for family in families:
        model=fit([c for c in cases if c['case']['family']!=family],counts,equity)
        for c in cases:
            if c['case']['family']!=family:continue
            errors=study.pilot.metrics(c,predict(c,model,counts,equity));control=controls[c['case']['id']]
            assert control['family']==family and abs(control['balanced']-errors['balanced'])<1e-10
            rows.append(dict(case=c['case']['id'],family=family,**errors,n09=control['candidate']))
        print('Finished excluded family',family,flush=True)
    family_means={name:{f:float(np.mean([r[name] for r in rows if r['family']==f])) for f in families}
        for name in ['candidate','n09','balanced','raw']}
    means={name:float(np.mean(list(values.values()))) for name,values in family_means.items()}
    comparisons={name:dict(improvement=1-means['candidate']/means[name],
        worst_family_ratio=max(family_means['candidate'][f]/family_means[name][f] for f in families)) for name in ['n09','balanced']}
    eligible=(comparisons['n09']['improvement']>=.05 and comparisons['balanced']['improvement']>=.15
        and all(v['worst_family_ratio']<=1.05 for v in comparisons.values()))
    study.freeze(OUT/'training-screen.json',dict(cases=rows,family_means=family_means,means=means,
        comparisons=comparisons,eligible=eligible,production_enabled=False,note='One fixed depth-aware training-family screen; no prospective outcomes.'))
    if eligible:
        model=fit(cases,counts,equity)
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families)
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),
            frozen_at=study.night.now(),prospective_references_generated=0))
    print('Eligible:',eligible,'comparisons:',comparisons,flush=True)


if __name__=='__main__':screen()
