"""Fixed cheap pairwise-prior calibration, isolated from production caches."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import torch
import continuation_policy_refinement as study

torch.set_num_threads(2)
OUT=study.ROOT/'research/preflop-evolution/continuation/recalibrated-priors-20260916'


def priors():
    q=np.array(study.read(study.ROOT/'cache/realization_fit.json')['class_base'])
    assert q.shape==(169,) and np.isfinite(q).all() and (q>0).all()
    return q


def shares(q,equity):
    values=[]
    for position in [.92,1.08]:
        a=equity*q[:,None]*position
        b=(1-equity)*q[None,:]*(2-position)
        values.append(a/(a+b))
    return np.array(values)


def opponent_probabilities(c,counts):
    w=np.array(c['case']['weights'])
    weighted=counts[None,:,:]*w[::-1,None,:]
    return weighted/weighted.sum(axis=-1,keepdims=True)


def predict(c,model,counts=None,equity=None):
    if counts is None:counts,equity=study.pilot.matrices()
    probabilities=opponent_probabilities(c,counts)
    relative=(probabilities*shares(np.array(model['class_base']),equity)).sum(axis=-1)
    blend=min(c['case']['stack']/c['case']['pot']/8,1.)
    result=c['raw']+blend*(relative-c['raw'])
    assert np.isfinite(result).all() and abs((result*c['mass']).sum()-1)<1e-9
    return result


def fit(cases,counts,equity):
    base=torch.tensor(priors(),dtype=torch.float64)
    eq=torch.tensor(equity,dtype=torch.float64)
    probabilities=torch.tensor(np.array([opponent_probabilities(c,counts) for c in cases]),dtype=torch.float64)
    raw=torch.tensor(np.array([c['raw'] for c in cases]),dtype=torch.float64)
    target=torch.tensor(np.array([c['raw']+c['residual'] for c in cases]),dtype=torch.float64)
    mass=torch.tensor(np.array([c['mass'] for c in cases]),dtype=torch.float64)
    blend=torch.tensor([min(c['case']['stack']/c['case']['pot']/8,1.) for c in cases],dtype=torch.float64)[:,None,None]
    delta=torch.nn.Parameter(torch.zeros(169,dtype=torch.float64))
    optimizer=torch.optim.Adam([delta],lr=.02)
    for step in range(600):
        optimizer.zero_grad();centered=delta-delta.mean();q=base*torch.exp(centered)
        adjusted=[]
        for position in [.92,1.08]:
            a=eq*q[:,None]*position;b=(1-eq)*q[None,:]*(2-position)
            adjusted.append(a/(a+b))
        relative=(probabilities*torch.stack(adjusted)).sum(dim=-1)
        pred=raw+blend*(relative-raw)
        mse=((pred-target).square()*mass).sum()/(2*len(cases))
        loss=mse+.001*centered.square().mean()
        assert torch.isfinite(loss)
        loss.backward();optimizer.step()
    q=(base*torch.exp(delta-delta.mean())).detach().numpy()
    return dict(class_base=q.tolist(),steps=600,learning_rate=.02,regularization=.001,
        position_factors=[.92,1.08],blend='min(SPR/8,1)',chance='compatible_pair',
        dtype='float64',device='cpu',torch_version=torch.__version__,production_enabled=False)


def screen():
    sources=[study.ROOT/'tools/research/continuation_recalibrated_priors.py',OUT/'README.md',
        study.ROOT/'tools/research/range_value_pilot.py',study.ROOT/'tools/research/continuation_overnight_fit.py',
        study.ROOT/'cache/realization_fit.json',study.ROOT/'cache/preflop_eq169.bin',
        study.night.OUT/'manifest.json',study.OUT/'development/manifest.json']
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in sources},production_enabled=False))
    cases=study.fit.load_cases('train')+study.contexts('development');assert len(cases)==26
    assert all(c['case']['partition']=='train' for c in cases)
    counts,equity=study.pilot.matrices();old=dict(class_base=priors().tolist())
    families=sorted({c['case']['family'] for c in cases});rows=[]
    for family in families:
        model=fit([c for c in cases if c['case']['family']!=family],counts,equity)
        for c in cases:
            if c['case']['family']!=family:continue
            errors=study.pilot.metrics(c,predict(c,model,counts,equity))
            errors['paired_old_priors']=study.pilot.metrics(c,predict(c,old,counts,equity))['candidate']
            rows.append(dict(case=c['case']['id'],family=family,**errors))
        print('Finished excluded family',family,flush=True)
    family_means={name:{f:float(np.mean([r[name] for r in rows if r['family']==f])) for f in families}
        for name in ['candidate','paired_old_priors','balanced','raw']}
    means={name:float(np.mean(list(values.values()))) for name,values in family_means.items()}
    comparisons={name:dict(improvement=1-means['candidate']/means[name],
        worst_family_ratio=max(family_means['candidate'][f]/family_means[name][f] for f in families)) for name in ['paired_old_priors','balanced']}
    eligible=(comparisons['paired_old_priors']['improvement']>=.05 and comparisons['balanced']['improvement']>=.15
        and all(r['worst_family_ratio']<=1.05 for r in comparisons.values()))
    result=dict(cases=rows,family_means=family_means,means=means,comparisons=comparisons,eligible=eligible,
        production_enabled=False,note='Training-family screen only; one fixed calibration, no test labels.')
    study.freeze(OUT/'training-screen.json',result)
    if eligible:
        model=fit(cases,counts,equity)
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families)
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),frozen_at=study.night.now(),prospective_references_generated=0))
    print('Eligible:',eligible,'comparisons:',comparisons,flush=True)


if __name__=='__main__':screen()
