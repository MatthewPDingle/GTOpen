"""Fit physical observation records once and reload weights in the poker walker.

CPU integration control only. Fixed synthetic behavior, no self-play or accuracy
qualification. Production and the ongoing neural comparisons are untouched.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import numpy as np
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-fit-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    assert idle()
    exe=ROOT/'target/release/examples/hu_sampled_physical_fit_control.exe'
    context=OUT/'bb-context-candidate.json';deals=OUT/'sampled-poker-v1-fixture.json'
    synthetic=OUT/'sampled-network-adapter-v1-fixture.json'
    prior=OUT/'sampled-network-adapter-v1-review.json';assert json.loads(prior.read_text())['passed']
    paths=[Path(__file__),exe,context,deals,synthetic,prior,ROOT/'tools/research/loopback_research_validation.py']+[ROOT/'crates/solver/examples'/p for p in [
        'hu_sampled_physical_fit_control.rs','research_sampled/state.rs','research_sampled/poker_reference_v1.rs',
        'research_sampled/observation_v1.rs','research_sampled/network_v1.rs','research_sampled/policy_walk_v1.rs']]
    frozen={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in paths}
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists()
    save(reg,dict(inputs=frozen,architecture=[269,64,64,4],model_seeds=[9101,9102],steps=128,learning_rate=.003,
        no_gpu=True,maximum_seconds=180,production_modified=False,
        sampling='16 frozen physical deals, both updaters, four independently seeded traversals per updater/deal. Frozen synthetic policies for all traversals.',
        training='Use every positive-tag advantage visit once. Group only identical canonical observable keys, preserving multiplicities and legal-action masks.',
        checks='Full-visit versus grouped loss gradients, within-observation variance decomposition, trained-weight Rust reload on every exported observation.',
        tolerances=dict(gradient=1e-10,loss_decomposition=1e-10,normalized_score=2e-5,policy=1e-4),
        scope='Fixed-data physical integration control. Fit loss is not strategic accuracy; no learned poker range is qualified.'))
    started=time.monotonic();data_path=OUT/(PREFIX+'-records.json')
    def invoke(mode,data,weights,destination):
        assert idle() and time.monotonic()-started<180
        r=subprocess.run([str(exe),mode,str(context),str(data),str(weights),str(destination)],cwd=ROOT,
                         timeout=120,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        assert r.returncode==0,r.stderr
    invoke('export',deals,synthetic,data_path)
    data=json.loads(data_path.read_text());observations=data['observations']
    features=np.zeros((len(observations),269),dtype=np.float32)
    masks=np.zeros((len(observations),4),dtype=np.float32)
    actors=np.array([r['actor'] for r in observations])
    for i,row in enumerate(observations):features[i,row['active_features']]=1;masks[i,:row['n']]=1
    os.environ['CUDA_VISIBLE_DEVICES']=''
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    x=torch.from_numpy(features);legal=torch.from_numpy(masks)
    def network():return torch.nn.Sequential(torch.nn.Linear(269,64),torch.nn.ReLU(),torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,4))
    def sums(ids,values):return np.stack([np.bincount(ids,weights=values[:,a],minlength=len(features)) for a in range(4)],axis=1)
    nets=[];metrics=[];expected=np.zeros((len(features),4));scales=[]
    for player in range(2):
        records=[r for r in data['records'] if r[1]==player and r[2]>0]
        ids=np.array([r[0] for r in records],dtype=np.int64);values=np.array([r[3] for r in records],dtype=np.float64)
        assert len(ids)>0 and np.all(actors[ids]==player) and np.all(values*(1-masks[ids])==0)
        count=np.bincount(ids,minlength=len(features));scale=max(.01,float(np.sqrt(np.mean(values**2))));targets=values/scale
        means=sums(ids,targets)/np.maximum(count[:,None],1);weights=masks*count[:,None];denom=float(weights.sum())
        torch.manual_seed(9101+player);model=network().double()
        full=((model(x.double()[ids])-torch.from_numpy(targets)).square()*legal.double()[ids]).sum()/denom
        full.backward();gradient=[p.grad.clone() for p in model.parameters()];model.zero_grad(set_to_none=True)
        grouped=((model(x.double())-torch.from_numpy(means)).square()*torch.from_numpy(weights)).sum()/denom
        grouped.backward();grad_error=max(float((a-p.grad).abs().max()) for a,p in zip(gradient,model.parameters()))
        variance=float((((targets-means[ids])**2)*masks[ids]).sum()/denom)
        loss_error=abs(float(full.detach())-float(grouped.detach())-variance)
        assert grad_error<1e-10 and loss_error<1e-10
        torch.manual_seed(9101+player);model=network();optimizer=torch.optim.Adam(model.parameters(),lr=.003)
        target=torch.as_tensor(means,dtype=torch.float32);weight=torch.as_tensor(weights,dtype=torch.float32)
        def loss():return ((model(x)-target).square()*weight).sum()/denom
        before=float(loss().detach())
        for step in range(128):
            if step%16==0:assert idle() and time.monotonic()-started<180
            current=loss();optimizer.zero_grad(set_to_none=True);current.backward();optimizer.step()
        after=float(loss().detach());assert math_finite(before,after) and after<before
        with torch.no_grad():scores=model(x).numpy().astype(float)
        expected[actors==player]=scores[actors==player]
        state=model.state_dict();net={}
        for i,layer in enumerate([0,2,4]):
            net[f'w{i}']=state[f'{layer}.weight'].numpy().flatten().tolist()
            net[f'b{i}']=state[f'{layer}.bias'].numpy().tolist()
        nets.append(net);scales.append(scale)
        metrics.append(dict(player=player,records=len(ids),unique_observations=int((count>0).sum()),
            duplicate_visits=len(ids)-int((count>0).sum()),gradient_error=grad_error,loss_decomposition_error=loss_error,
            normalized_fit_loss_before=before,normalized_fit_loss_after=after,scale=scale))
    weights_path=OUT/(PREFIX+'-weights.json')
    save(weights_path,dict(networks=nets,advantage_scales=scales,
        scope='Normalized advantage outputs. Positive per-player scale cancels in regret matching. Fixed-data fit only, not a learned equilibrium.'))
    replay_path=OUT/(PREFIX+'-replay.json');invoke('infer',data_path,weights_path,replay_path)
    replay=json.loads(replay_path.read_text())['rows'];score_error=0.;policy_error=0.
    for i,row in enumerate(replay):
        n=observations[i]['n'];s=expected[i];p=np.zeros(4);p[:n]=np.maximum(s[:n],0)
        if p.sum()>0:p/=p.sum()
        else:p[int(np.argmax(s[:n]))]=1.
        score_error=max(score_error,float(np.max(np.abs(s-row['scores']))))
        policy_error=max(policy_error,float(np.max(np.abs(p-row['policy']))))
    passed=score_error<2e-5 and policy_error<1e-4
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    result=dict(passed=passed,inputs_verified=len(frozen),traversals=len(data['traversals']),records=len(data['records']),
        observations=len(observations),phases=data['phases'],postflop_branches=data['postflop_branches'],fits=metrics,
        maximum_rust_score_error=score_error,maximum_rust_policy_error=policy_error,
        seconds=time.monotonic()-started,torch_version=torch.__version__,device='cpu',
        artifacts={p.name:sha(p) for p in [reg,data_path,weights_path,replay_path]},
        physical_poker_convergence_qualified=False,production_modified=False)
    save(OUT/(PREFIX+'-result.json'),result)
    print(json.dumps(result));assert passed

def math_finite(*values):return all(np.isfinite(v) for v in values)
if __name__=='__main__':main()
