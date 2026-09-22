"""CPU-only fixed-data fit diagnosis; leaves the live GPU experiment alone."""
import hashlib
import json
import os
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from hu_sampled_neural_control_20260922 import geometry
from hu_sampled_neural_fallback_20260922 import highest_regret_fallback
from hu_sampled_neural_table_control_20260922 import sums

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-large-fit-cpu-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    assert idle()
    parent=OUT/'sampled-reservoir-capacity-v1-result.json';source=json.loads(parent.read_text());assert source['terminal']
    row=next(r for r in source['runs'] if r['case']==0 and r['seed']==17)
    snapshots=[ROOT/s['path'] for s in row['snapshots']]
    assert len(snapshots)==2 and all(sha(p)==s['sha256'] for p,s in zip(snapshots,row['snapshots']))
    fixture=OUT/'sampled-convergence-v1-fixture.json'
    paths=[Path(__file__),parent,fixture]+snapshots+[ROOT/'tools/research'/p for p in [
        'hu_sampled_neural_control_20260922.py','hu_sampled_neural_fallback_20260922.py',
        'hu_sampled_neural_table_control_20260922.py','loopback_research_validation.py']]
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    regpath=OUT/(PREFIX+'-registration.json');assert not regpath.exists()
    reg=dict(inputs=frozen,maximum_seconds=300,model_seeds=[991,20260922],
        fits=[dict(steps=128,batch_size=512),dict(steps=128,batch_size=8192),dict(steps=512,batch_size=8192)],
        architecture=[28,64,64,3],learning_rate=.003,
        source='Frozen case0 seed17 2048-update larger-reservoir table trajectory; no self-play changes.',
        scope='CPU float32 optimizer diagnosis only. Same per-player initialization for all fits within each seed. No GPU speed or strategic-convergence claim.',
        sampling='CPU Torch generator, seed + 1000003; not the CUDA RNG stream of previous fits.',
        stopping='Complete all 12 predeclared fits or stop on guard/deadline; no outcome-based extension.',
        no_gpu=True,production_modified=False)
    save(regpath,reg);started=time.monotonic();last_guard=0.;results=[]
    os.environ['CUDA_VISIBLE_DEVICES']=''
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    data=json.loads(fixture.read_text());x,mask,actors=geometry(data)
    features=torch.from_numpy(x);legal=torch.from_numpy(mask)
    for player,path in enumerate(snapshots):
        with np.load(path) as stored:indices=stored['ids'];values=stored['values']
        counts=np.bincount(indices,minlength=len(mask))
        means=np.divide(sums(indices,values,len(mask)),counts[:,None],out=np.zeros_like(mask,dtype=float),where=counts[:,None]>0)
        denominator=mask[indices].sum()
        irreducible=float((((values-means[indices])**2)*mask[indices]).sum()/denominator)
        ids=torch.from_numpy(indices);raw=torch.as_tensor(values,dtype=torch.float32)
        scale=raw.square().mean().sqrt().clamp_min(.01);targets=raw/scale
        ideal=highest_regret_fallback(means,mask)
        for initial in reg['model_seeds']:
            for fit in reg['fits']:
                began=time.monotonic();seed=initial+player;torch.manual_seed(seed)
                model=torch.nn.Sequential(torch.nn.Linear(28,64),torch.nn.ReLU(),torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,3))
                optimizer=torch.optim.Adam(model.parameters(),lr=reg['learning_rate'])
                rng=torch.Generator(device='cpu').manual_seed(seed+1000003)
                for step in range(fit['steps']):
                    now=time.monotonic();assert now-started<reg['maximum_seconds']
                    if now-last_guard>=2:
                        assert idle() and psutil.virtual_memory().available>=20_000_000_000
                        last_guard=now
                    selected=torch.randint(len(ids),(fit['batch_size'],),generator=rng)
                    info=ids[selected];ok=legal[info]
                    loss=((model(features[info])-targets[selected]).square()*ok).sum()/ok.sum()
                    optimizer.zero_grad(set_to_none=True);loss.backward();optimizer.step()
                with torch.no_grad():prediction=(model(features)*scale).numpy().astype(float)
                mse=float((((prediction[indices]-values)**2)*mask[indices]).sum()/denominator)
                excess=float((((prediction-means)**2)*mask*counts[:,None]).sum()/denominator)
                assert abs(mse-irreducible-excess)<1e-10
                inferred=highest_regret_fallback(prediction,mask);l1=np.abs(inferred-ideal).sum(axis=1)
                result=dict(player=player,initial_seed=initial,fit=fit,seconds=time.monotonic()-began,
                    excess_mean_fit_mse=excess,irreducible_empirical_variance=irreducible,
                    visitation_weighted_policy_l1=float(l1@counts/counts.sum()),
                    rows=[dict(key=data['information_keys'][i],count=int(counts[i]),target_means=means[i].tolist(),
                        prediction=prediction[i].tolist(),target_policy=ideal[i].tolist(),predicted_policy=inferred[i].tolist())
                        for i in range(len(mask)) if actors[i]==player and counts[i]>0])
                results.append(result);save(OUT/(PREFIX+'-result.json'),dict(terminal=False,results=results))
                print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    save(OUT/(PREFIX+'-result.json'),dict(terminal=True,results=results,seconds=time.monotonic()-started,
        inputs_verified=len(frozen),registration_sha256=sha(regpath),torch_version=torch.__version__,device='cpu',
        strategic_improvement_demonstrated=False,production_modified=False))

if __name__=='__main__':main()
