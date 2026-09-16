"""N23 fixed training-data weights; no held-out outcomes or runtime changes."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import copy
import datetime as dt
import sys
from pathlib import Path
import numpy as np
import torch
import continuation_smooth_fit as smooth
import continuation_bridge_run as bridge

network=smooth.network
study=smooth.study
OUT=smooth.OUT.parent/'weighted-expanded-20260916'
WEIGHTS=[0.,.05,.2]
torch.set_num_threads(2)


def weights_for(cases,original_ids,extra_weight):
    assert extra_weight in WEIGHTS
    result=np.array([1. if c['case']['id'] in original_ids else extra_weight for c in cases])
    assert result.sum()>0
    return result


def weighted_base(cases,weights):
    assert len(cases)==len(weights) and np.all(weights>0)
    encoded=[study.fit.features(c,dict(kind='shape')) for c in cases]
    data=[dict(c,mass=c['mass']*w) for c,w in zip(encoded,weights)]
    alpha=.1*len(cases)/float(weights.sum())
    model=study.pilot.fit_ridge(data,alpha)
    model.update(encoder=dict(kind='shape'),feature_names=encoded[0]['names'])
    return model


def fit(cases,original_ids,extra_weight):
    weights=weights_for(cases,original_ids,extra_weight)
    selected=[c for c,w in zip(cases,weights) if w>0];weights=weights[weights>0];cases=selected
    if extra_weight==0:return smooth.shrunk.shrink(network.fit(cases,8,.1))
    base=weighted_base(cases,weights)
    x=torch.tensor(np.array([network.inputs(c,base)[0] for c in cases]),dtype=torch.float64)
    mass=torch.tensor(np.array([c['mass'] for c in cases]),dtype=torch.float64)
    y=torch.tensor(np.array([c['raw']+c['residual'] for c in cases]),dtype=torch.float64)
    baseline=torch.tensor(np.array([study.fit.predict(c,base) for c in cases]),dtype=torch.float64)
    training_mass=mass*torch.tensor(weights[:,None,None],dtype=torch.float64)
    networks=[]
    for seed in [90210,20260916]:
        model=network.Residual(8,seed);optimizer=torch.optim.Adam(model.parameters(),lr=.01)
        for step in range(500):
            if step%50==0:assert dt.datetime.now(dt.timezone.utc)<smooth.DEADLINE,'Research deadline reached'
            optimizer.zero_grad()
            error=baseline+model(x,mass)-y
            loss=(error.square()*training_mass).sum()/(2*weights.sum())
            objective=loss+.1*model.output.square().sum()+.001*(model.weight.square().mean()+model.bias.square().mean())
            assert torch.isfinite(objective)
            objective.backward();optimizer.step()
        networks.append(model.export())
    return smooth.shrunk.shrink(dict(base=base,networks=networks,width=8,output_penalty=.1,seeds=[90210,20260916],
        steps=500,dtype='float64',device='cpu',production_enabled=False,effective_case_weight=float(weights.sum())))


def prepare():
    paths=[Path(__file__),OUT/'README.md',Path(smooth.__file__),Path(network.__file__),Path(smooth.sensitivity.__file__),
        Path(bridge.__file__),study.ROOT/'tools/research/continuation_overnight_fit.py',study.ROOT/'tools/research/range_value_pilot.py',
        study.night.OUT/'manifest.json',study.OUT/'development/manifest.json',bridge.OUT/'training/manifest.json',
        smooth.shrunk.OUT/'training-screen.json',network.OUT/'training-screen.json',smooth.OUT/'training-screen.json',
        study.ROOT/'cache/preflop_eq169.bin',study.ROOT/'cache/realization_fit.json']
    inputs={str(p.resolve().relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths}
    p=OUT/'implementation-freeze.json'
    if p.exists():assert study.read(p)['inputs']==inputs
    else:study.freeze(p,dict(registered_at=study.night.now(),inputs=inputs,extra_weights=WEIGHTS,production_enabled=False))


def run():
    smooth.sensitivity.timing.require_no_timing();prepare()
    for p in smooth.sensitivity.timing.queue.processes():
        command=(p['CommandLine'] or '').lower()
        if p['Name'].lower() in ['python.exe','pythonw.exe']:
            assert 'continuation_validation_queue.py run' not in command,'Pause the waiting follow-on queue before this CPU screen'
            assert 'continuation_policy_stability.py run' not in command,'Keep timing isolated'
            if 'continuation_full_precision.py run' in command:
                assert study.read(OUT.parent/'full-precision-20260916/status.json')['stage']=='policy_transfer'
    assert not (OUT/'training-screen.json').exists()
    original=study.fit.load_cases('train')+study.contexts('development');extra=bridge.contexts('training')
    cases=original+extra;assert len(original)==26 and len(cases)==62
    assert all(c['case']['partition']=='train' for c in cases)
    ids={c['case']['id'] for c in original};families=sorted({c['case']['family'] for c in cases})
    counts,eq=study.pilot.matrices();altered={c['case']['id']:smooth.variants(c,counts,eq) for c in original}
    control=study.read(smooth.shrunk.OUT/'training-screen.json');expected={c['case']:c['candidate'] for c in control['cases']}
    prior_response=study.read(smooth.OUT/'training-screen.json')['scores'][0]
    scores={w:[] for w in WEIGHTS}
    for family in families:
        training=[c for c in cases if c['case']['family']!=family]
        assert not any(c['case']['family']==family for c in training)
        for weight in WEIGHTS:
            model=fit(training,ids,weight)
            for c in original:
                if c['case']['family']!=family:continue
                error=study.pilot.metrics(c,network.predict(c,model))['candidate']
                if weight==0:assert abs(error-expected[c['case']['id']])<1e-9,'N15 control changed'
                scores[weight].append(dict(case=c['case']['id'],family=family,candidate=error,
                    response=smooth.responsiveness(c,model,altered[c['case']['id']])))
            study.night.dump(OUT/'progress.json',dict(family=family,weight=weight,scores=scores,updated=study.night.now(),controller_pid=os.getpid(),production_enabled=False))
            print('Completed family',family,'weight',weight,flush=True)
    aggregate=lambda rows,key:{f:float(np.mean([r[key] for r in rows if r['family']==f])) for f in families}
    baseline=aggregate(scores[0.],'candidate');responses=aggregate(scores[0.],'response')
    assert all(abs(responses[f]-prior_response['family_response'][f])<1e-9 for f in families)
    linear_mean=study.read(network.OUT/'training-screen.json')['scores'][0]['mean']
    results=[]
    for weight,rows in scores.items():
        means=aggregate(rows,'candidate');response=aggregate(rows,'response')
        results.append(dict(weight=weight,cases=rows,family_means=means,family_response=response,
            **smooth.gate(means,response,baseline,responses,linear_mean)))
    eligible=[r for r in results if r['weight']>0 and r['eligible']]
    winner=min(eligible,key=lambda r:r['mean']) if eligible else None
    study.freeze(OUT/'training-screen.json',dict(scores=results,selected=winner,control_reproduced=True,production_enabled=False))
    if winner:
        model=fit(cases,ids,winner['weight'])
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families,
            extra_training_weight=winner['weight'],selection_sha256=study.pilot.sha(OUT/'training-screen.json'))
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),frozen_at=study.night.now(),prospective_references_generated=0))
    print('Selected',None if winner is None else winner['weight'],flush=True)


if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
