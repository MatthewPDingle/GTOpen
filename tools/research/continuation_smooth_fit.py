"""N22 fixed training-only sensitivity penalty; unchanged inference shape."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import copy
import datetime as dt
import sys
from pathlib import Path
import numpy as np
import torch
import continuation_range_sensitivity as sensitivity
import continuation_shrunk_residual as shrunk

network=sensitivity.network
study=network.study
OUT=network.OUT.parent/'smooth-fit-20260916'
STRENGTHS=[0.,.0001,.001,.01]
DEADLINE=dt.datetime(2026,9,16,20,49,2,tzinfo=dt.timezone.utc)
torch.set_num_threads(2)


def masks():
    return [np.array([a==b and a>=8 for a,b,s in study.pilot.PARTS]),
        np.array([a!=b and not s and min(a,b)>=8 for a,b,s in study.pilot.PARTS]),
        np.array([s and 0<a-b<=2 for a,b,s in study.pilot.PARTS])]


def variants(c,counts,eq):
    result=[]
    for side in [0,1]:
        for mask in masks():
            w,tv=sensitivity.perturb(c['case']['weights'],side,mask,.01)
            assert tv>0
            case=dict(copy.deepcopy(c['case']),weights=w.tolist())
            result.append((sensitivity.context(case,counts,eq),tv))
    return result


def standardized(c,base):
    x=study.fit.features(c,base['encoder'])['x']
    return (x-np.array(base['mean']))/np.array(base['scale'])


def centered(z,mass):
    return z-(z*mass[...,None]).sum(axis=(0,1))/2


def penalty(cases,base,altered):
    matrix=np.zeros((104,104))
    for c in cases:
        z=centered(standardized(c,base),c['mass'])
        for v,tv in altered[c['case']['id']]:
            delta=(centered(standardized(v,base),v['mass'])-z).reshape(-1,104)/tv
            w=c['mass'].ravel()/(2*len(cases)*6)
            matrix+=delta.T@(w[:,None]*delta)
    np.testing.assert_allclose(matrix,matrix.T,atol=1e-8,rtol=1e-12)
    return matrix


def linear(cases,base,regularizer,strength):
    if strength==0:return copy.deepcopy(base)
    z=np.concatenate([standardized(c,base).reshape(-1,104) for c in cases])
    y=np.concatenate([c['residual'].ravel() for c in cases])
    w=np.concatenate([(c['mass']*(c['observed']>0)).ravel()/2 for c in cases]);w/=w.sum()
    ridge=np.eye(104)*.1/len(cases);ridge[0,0]=1e-10
    result=copy.deepcopy(base)
    result['coef']=np.linalg.solve(z.T@(w[:,None]*z)+ridge+strength*regularizer,z.T@(w*y)).tolist()
    return result


def fit_residual(cases,base):
    x=torch.tensor(np.array([network.inputs(c,base)[0] for c in cases]),device='cpu',dtype=torch.float64)
    mass=torch.tensor(np.array([c['mass'] for c in cases]),device='cpu',dtype=torch.float64)
    y=torch.tensor(np.array([c['raw']+c['residual'] for c in cases]),device='cpu',dtype=torch.float64)
    baseline=torch.tensor(np.array([study.fit.predict(c,base) for c in cases]),device='cpu',dtype=torch.float64)
    networks=[]
    for seed in [90210,20260916]:
        model=network.Residual(8,seed);optimizer=torch.optim.Adam(model.parameters(),lr=.01)
        for step in range(500):
            if step%50==0:assert dt.datetime.now(dt.timezone.utc)<DEADLINE,'Research deadline reached'
            optimizer.zero_grad()
            loss=((baseline+model(x,mass)-y).square()*mass).sum()/(2*len(cases))
            objective=loss+.1*model.output.square().sum()+.001*(model.weight.square().mean()+model.bias.square().mean())
            assert torch.isfinite(objective)
            objective.backward();optimizer.step()
        networks.append(model.export())
    return shrunk.shrink(dict(base=base,networks=networks,width=8,output_penalty=.1,
        seeds=[90210,20260916],dtype='float64',device='cpu',steps=500,production_enabled=False))


def responsiveness(c,model,altered):
    before=network.predict(c,model)
    return float(np.mean([(c['mass']*np.abs(network.predict(v,model)-before)).sum()/2/tv for v,tv in altered]))


def gate(means,responses,control_means,control_responses,linear_mean):
    mean=float(np.mean(list(means.values())));control=float(np.mean(list(control_means.values())))
    response=float(np.mean(list(responses.values())));baseline=float(np.mean(list(control_responses.values())))
    worst=max(means[f]/control_means[f] for f in means)
    worst_response=max(responses[f]/control_responses[f] for f in responses)
    return dict(mean=mean,ratio_vs_n15=mean/control,worst_family_ratio=worst,
        improvement_vs_linear=1-mean/linear_mean,response_mean=response,response_ratio=response/baseline,
        worst_response_family_ratio=worst_response,
        eligible=mean/control<=1.05 and worst<=1.05 and 1-mean/linear_mean>=.05 and response/baseline<=.75 and worst_response<=1.)


def prepare():
    paths=[Path(__file__),OUT/'README.md',Path(sensitivity.__file__),Path(network.__file__),Path(shrunk.__file__),
        study.ROOT/'tools/research/continuation_overnight_fit.py',study.ROOT/'tools/research/range_value_pilot.py',
        study.night.OUT/'manifest.json',study.OUT/'development/manifest.json',
        shrunk.OUT/'training-screen.json',network.OUT/'training-screen.json',
        study.ROOT/'cache/preflop_eq169.bin',study.ROOT/'cache/realization_fit.json']
    inputs={str(p.resolve().relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths}
    frozen=OUT/'implementation-freeze.json'
    if frozen.exists():assert study.read(frozen)['inputs']==inputs
    else:study.freeze(frozen,dict(registered_at=study.night.now(),inputs=inputs,strengths=STRENGTHS,production_enabled=False))


def run():
    sensitivity.timing.require_no_timing();prepare()
    for p in sensitivity.timing.queue.processes():
        command=(p['CommandLine'] or '').lower()
        if p['Name'].lower() in ['python.exe','pythonw.exe']:
            assert 'continuation_policy_stability.py run' not in command,'Keep practical-stability timing isolated'
            if 'continuation_full_precision.py run' in command:
                assert study.read(OUT.parent/'full-precision-20260916/status.json')['stage']=='policy_transfer','GPU timing may still be active'
    assert not (OUT/'training-screen.json').exists(),'Fixed screen already complete'
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    counts,eq=study.pilot.matrices();altered={c['case']['id']:variants(c,counts,eq) for c in cases}
    families=sorted({c['case']['family'] for c in cases});scores={s:[] for s in STRENGTHS}
    control=study.read(shrunk.OUT/'training-screen.json')
    expected={c['case']:c['candidate'] for c in control['cases']}
    for family in families:
        training=[c for c in cases if c['case']['family']!=family]
        base=study.fit.fit(training,'shape',.1);regularizer=penalty(training,base,altered)
        for strength in STRENGTHS:
            model=fit_residual(training,linear(training,base,regularizer,strength))
            for c in cases:
                if c['case']['family']!=family:continue
                error=study.pilot.metrics(c,network.predict(c,model))['candidate']
                if strength==0:assert abs(error-expected[c['case']['id']])<1e-9,'N15 control changed'
                scores[strength].append(dict(case=c['case']['id'],family=family,candidate=error,
                    response=responsiveness(c,model,altered[c['case']['id']])))
            study.night.dump(OUT/'progress.json',dict(family=family,strength=strength,rows=scores,updated=study.night.now(),controller_pid=os.getpid(),production_enabled=False))
            print('Completed family',family,'strength',strength,flush=True)
    aggregate=lambda rows,key:{f:float(np.mean([r[key] for r in rows if r['family']==f])) for f in families}
    linear_mean=study.read(network.OUT/'training-screen.json')['scores'][0]['mean']
    results=[]
    for strength,rows in scores.items():
        means=aggregate(rows,'candidate');responses=aggregate(rows,'response')
        results.append(dict(strength=strength,cases=rows,family_means=means,family_response=responses,
            **gate(means,responses,aggregate(scores[0.],'candidate'),aggregate(scores[0.],'response'),linear_mean)))
    eligible=[r for r in results if r['strength']>0 and r['eligible']]
    winner=min(eligible,key=lambda r:r['mean']) if eligible else None
    study.freeze(OUT/'training-screen.json',dict(scores=results,selected=winner,control_reproduced=True,production_enabled=False))
    if winner:
        base=study.fit.fit(cases,'shape',.1);regularizer=penalty(cases,base,altered)
        model=fit_residual(cases,linear(cases,base,regularizer,winner['strength']))
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families,
            sensitivity_strength=winner['strength'],selection_sha256=study.pilot.sha(OUT/'training-screen.json'))
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),frozen_at=study.night.now(),prospective_references_generated=0))
    print('Selected',None if winner is None else winner['strength'],flush=True)


if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
