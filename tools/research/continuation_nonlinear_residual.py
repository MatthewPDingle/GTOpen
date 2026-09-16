"""Fixed CPU-only nonlinear residual screen; no evaluation-data access."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import math
import numpy as np
import torch
import continuation_policy_refinement as study

torch.set_num_threads(2)
OUT=study.ROOT/'research/preflop-evolution/continuation/nonlinear-residual-20260916'


def inputs(c,base):
    encoded=study.fit.features(c,base['encoder'])
    assert encoded['names']==base['feature_names']
    z=(encoded['x']-np.array(base['mean']))/np.array(base['scale'])
    clipped=(abs(z)>6).any(axis=-1)
    return np.clip(z,-6,6),float((clipped*c['mass']).sum()/2)


class Residual(torch.nn.Module):
    def __init__(self,width,seed):
        super().__init__()
        gen=torch.Generator(device='cpu').manual_seed(seed)
        self.weight=torch.nn.Parameter(torch.randn(104,width,generator=gen,dtype=torch.float64)/math.sqrt(104))
        self.bias=torch.nn.Parameter(torch.zeros(width,dtype=torch.float64))
        self.output=torch.nn.Parameter(torch.zeros(width,dtype=torch.float64))

    def forward(self,x,mass):
        raw=torch.relu(x@self.weight+self.bias)@self.output
        return raw-(raw*mass).sum(dim=(1,2),keepdim=True)/2

    def export(self):
        return {k:v.detach().cpu().numpy().tolist() for k,v in self.state_dict().items()}


def predict(c,model):
    base=model['base'];x,_=inputs(c,base);residual=np.zeros((2,169))
    for net in model['networks']:
        raw=np.maximum(0,x@np.array(net['weight'])+np.array(net['bias']))@np.array(net['output'])
        residual+=(raw-(raw*c['mass']).sum()/2)/len(model['networks'])
    result=study.fit.predict(c,base)+residual
    assert np.isfinite(result).all() and abs((result*c['mass']).sum()-1)<1e-9
    return result


def fit(cases,width,penalty):
    assert all((c['mass']*(c['observed']==0)).sum()<1e-12 for c in cases)
    base=study.fit.fit(cases,'shape',.1)
    x=torch.tensor(np.array([inputs(c,base)[0] for c in cases]),device='cpu',dtype=torch.float64)
    mass=torch.tensor(np.array([c['mass'] for c in cases]),device='cpu',dtype=torch.float64)
    y=torch.tensor(np.array([c['raw']+c['residual'] for c in cases]),device='cpu',dtype=torch.float64)
    baseline=torch.tensor(np.array([study.fit.predict(c,base) for c in cases]),device='cpu',dtype=torch.float64)
    networks=[];losses=[]
    for seed in [90210,20260916]:
        network=Residual(width,seed)
        optimizer=torch.optim.Adam(network.parameters(),lr=.01)
        for step in range(500):
            optimizer.zero_grad()
            error=baseline+network(x,mass)-y
            loss=(error.square()*mass).sum()/(2*len(cases))
            objective=loss+penalty*network.output.square().sum()+.001*(network.weight.square().mean()+network.bias.square().mean())
            assert torch.isfinite(objective)
            objective.backward();optimizer.step()
        with torch.no_grad():
            mse=float(((baseline+network(x,mass)-y).square()*mass).sum()/(2*len(cases)))
        networks.append(network.export());losses.append(dict(seed=seed,training_mse=mse))
    return dict(base=base,networks=networks,width=width,output_penalty=penalty,seeds=[90210,20260916],losses=losses,
        production_enabled=False,torch_version=torch.__version__,device='cpu',dtype='float64',steps=500)


def screen():
    sources=['tools/research/continuation_nonlinear_residual.py',
        'research/preflop-evolution/continuation/nonlinear-residual-20260916/README.md',
        'tools/research/continuation_overnight_fit.py','tools/research/range_value_pilot.py',
        str((study.OUT/'development/manifest.json').relative_to(study.ROOT))]
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={p:study.pilot.sha(study.ROOT/p) for p in sources},production_enabled=False))
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    families=sorted({c['case']['family'] for c in cases});assert len(families)==4
    scores=[]
    for width,penalty in [(0,0),(8,.01),(8,.1),(16,.01),(16,.1)]:
        rows=[]
        for family in families:
            training=[c for c in cases if c['case']['family']!=family]
            model=fit(training,width,penalty) if width else dict(base=study.fit.fit(training,'shape',.1),networks=[])
            for c in cases:
                if c['case']['family']==family:
                    rows.append(dict(case=c['case']['id'],family=family,clipped_mass_fraction=inputs(c,model['base'])[1],
                        **study.pilot.metrics(c,predict(c,model))))
            print('Finished',width,penalty,family,flush=True)
        means={f:float(np.mean([r['candidate'] for r in rows if r['family']==f])) for f in families}
        scores.append(dict(width=width,output_penalty=penalty,cases=rows,family_means=means,mean=float(np.mean(list(means.values())))))
        study.night.dump(OUT/'progress.json',dict(completed_choices=len(scores),scores=scores,production_enabled=False))
    control=scores[0]
    for score in scores:
        score['improvement']=1-score['mean']/control['mean']
        score['worst_family_ratio']=max(score['family_means'][f]/control['family_means'][f] for f in families)
        score['eligible']=score['improvement']>=.05 and score['worst_family_ratio']<=1.05
    eligible=[r for r in scores[1:] if r['eligible']]
    winner=min(eligible,key=lambda r:r['mean']) if eligible else None
    study.freeze(OUT/'training-screen.json',dict(cases=26,scores=scores,selected=winner,production_enabled=False,
        note='Training-family selection only. No evaluation labels were read.'))
    if winner:
        model=fit(cases,winner['width'],winner['output_penalty'])
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families,
            selection_sha256=study.pilot.sha(OUT/'training-screen.json'))
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),frozen_at=study.night.now(),
            prospective_references_generated=0))
    print('Selected:',None if winner is None else [winner['width'],winner['output_penalty']],flush=True)


if __name__=='__main__':screen()
