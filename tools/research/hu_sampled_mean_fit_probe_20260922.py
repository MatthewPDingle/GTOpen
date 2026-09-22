"""Exact empirical-mean gradients: fixed-data CPU diagnostic, no policy training."""
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
PREFIX='sampled-mean-fit-cpu-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    assert idle()
    parent=OUT/'sampled-reservoir-capacity-v1-result.json';source=json.loads(parent.read_text());assert source['terminal']
    row=next(r for r in source['runs'] if r['case']==0 and r['seed']==17)
    snapshots=[ROOT/s['path'] for s in row['snapshots']]
    assert all(sha(p)==s['sha256'] for p,s in zip(snapshots,row['snapshots']))
    fixture=OUT/'sampled-convergence-v1-fixture.json'
    paths=[Path(__file__),parent,fixture,OUT/'sampled-large-fit-cpu-v1-result.json']+snapshots+[ROOT/'tools/research'/p for p in [
        'hu_sampled_neural_control_20260922.py','hu_sampled_neural_fallback_20260922.py',
        'hu_sampled_neural_table_control_20260922.py','loopback_research_validation.py']]
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths};regpath=OUT/(PREFIX+'-registration.json');assert not regpath.exists()
    reg=dict(inputs=frozen,maximum_seconds=300,model_seeds=[991,20260922],steps=[128,512,2048],
        architecture=[28,64,64,3],learning_rate=.003,
        scope='Fixed-data CPU float32 fits; no strategic improvement or GPU timing claim.',
        objective='Count-weighted empirical mean MSE. Equivalent gradient to full retained per-visit squared error; omitted variance is parameter independent.',
        representation='Same observable features; repeated observations grouped only within the retained dataset, with exact multiplicities. No lookup embeddings or privileged inputs.',
        controls='Full 262144-record versus grouped double-precision loss/gradient comparison for both players before fitting.',
        stopping='All 12 fixed fits or guard/deadline; no outcome-based extension.',no_gpu=True,production_modified=False)
    save(regpath,reg);started=time.monotonic();last_guard=0.;results=[];controls=[]
    os.environ['CUDA_VISIBLE_DEVICES']=''
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    def network():return torch.nn.Sequential(torch.nn.Linear(28,64),torch.nn.ReLU(),torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,3))
    data=json.loads(fixture.read_text());x,mask,actors=geometry(data)
    features=torch.from_numpy(x);legal=torch.from_numpy(mask)
    for player,path in enumerate(snapshots):
        with np.load(path) as stored:indices=stored['ids'];values=stored['values']
        counts=np.bincount(indices,minlength=len(mask));means=sums(indices,values,len(mask))/np.maximum(counts[:,None],1)
        ids=torch.from_numpy(indices);raw=torch.as_tensor(values,dtype=torch.float32)
        scale=raw.square().mean().sqrt().clamp_min(.01);targets=raw/scale
        empirical=sums(indices,targets.numpy().astype(float),len(mask))/np.maximum(counts[:,None],1)
        weighted_mask=mask*counts[:,None];denominator=float(weighted_mask.sum())
        torch.manual_seed(991+player);reference=network().double();fd=features.double()
        full=((reference(fd[ids])-targets.double()).square()*legal[ids]).sum()/denominator
        full.backward();full_grad=[p.grad.detach().clone() for p in reference.parameters()];reference.zero_grad(set_to_none=True)
        grouped=((reference(fd)-torch.from_numpy(empirical)).square()*torch.from_numpy(weighted_mask)).sum()/denominator
        grouped.backward()
        gradient_error=max(float((a-p.grad).abs().max()) for a,p in zip(full_grad,reference.parameters()))
        variance=float((((targets.numpy().astype(float)-empirical[indices])**2)*mask[indices]).sum()/denominator)
        loss_error=abs(float(full.detach())-float(grouped.detach())-variance)
        assert gradient_error<1e-10 and loss_error<1e-10
        controls.append(dict(player=player,records=len(ids),occupied_observations=int((counts>0).sum()),maximum_gradient_error=gradient_error,loss_decomposition_error=loss_error))
        del reference,full,grouped,full_grad,fd
        mean_target=torch.as_tensor(empirical,dtype=torch.float32);weights=torch.as_tensor(weighted_mask,dtype=torch.float32)
        ideal=highest_regret_fallback(means,mask)
        for initial in reg['model_seeds']:
            for steps in reg['steps']:
                began=time.monotonic();torch.manual_seed(initial+player);model=network();opt=torch.optim.Adam(model.parameters(),lr=reg['learning_rate'])
                for step in range(steps):
                    now=time.monotonic();assert now-started<reg['maximum_seconds']
                    if now-last_guard>=2:
                        assert idle() and psutil.virtual_memory().available>=20_000_000_000;last_guard=now
                    loss=((model(features)-mean_target).square()*weights).sum()/denominator
                    opt.zero_grad(set_to_none=True);loss.backward();opt.step()
                with torch.no_grad():prediction=(model(features)*scale).numpy().astype(float)
                excess=float((((prediction-means)**2)*weighted_mask).sum()/denominator)
                inferred=highest_regret_fallback(prediction,mask);l1=np.abs(inferred-ideal).sum(axis=1)
                result=dict(player=player,initial_seed=initial,steps=steps,seconds=time.monotonic()-began,
                    excess_mean_fit_mse=excess,visitation_weighted_policy_l1=float(l1@counts/counts.sum()),
                    rows=[dict(key=data['information_keys'][i],count=int(counts[i]),target_means=means[i].tolist(),prediction=prediction[i].tolist(),
                        target_policy=ideal[i].tolist(),predicted_policy=inferred[i].tolist()) for i in range(len(mask)) if actors[i]==player and counts[i]>0])
                results.append(result);save(OUT/(PREFIX+'-result.json'),dict(terminal=False,controls=controls,results=results))
                print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    save(OUT/(PREFIX+'-result.json'),dict(terminal=True,controls=controls,results=results,seconds=time.monotonic()-started,
        inputs_verified=len(frozen),registration_sha256=sha(regpath),torch_version=torch.__version__,device='cpu',
        strategic_improvement_demonstrated=False,production_modified=False))

if __name__=='__main__':main()
