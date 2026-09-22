"""Numerical backend control with deliberately noisy repeated visible records.

The altered targets are synthetic fixtures, not poker outcomes or a candidate.
CPU mode does not use CUDA. CUDA mode requires the exclusive research lock.
"""
import argparse
import json
import os
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_physical_fit_v1 import grouped_rows,export_network
from sampled_visible_initialization_v1 import features,fresh_visible_network
from sampled_visible_hybrid_fit_v1 import PreparedObjective,fit
from sampled_visible_hybrid_checkpoint_v1 import read_object

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--device',choices=('cpu','cuda'),required=True)
    device=parser.parse_args().device;prefix=f'sampled-visible-hybrid-fit-{device}-control-v1'
    store=Path('S:/GTOpen-research')/prefix
    assert idle() and not store.exists()
    if device=='cuda':assert not LOCK.exists() and not OTHER.exists()
    started=time.monotonic();acquired=False;error=None
    if device=='cuda':
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
    try:
        os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
        import torch
        torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        def guard():
            assert time.monotonic()-started<180 and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert psutil.disk_usage('S:/').free>=40_000_000_000
            if device=='cuda':assert torch.cuda.mem_get_info()[0]>=3_000_000_000
        guard()
        previous_path=OUT/'sampled-visible-hybrid-checkpoint-control-v1-result.json'
        previous_reg=OUT/'sampled-visible-hybrid-checkpoint-control-v1-registration.json'
        previous=json.loads(previous_path.read_text());assert previous['passed']
        assert previous['registration_sha256']==sha(previous_reg)
        for p,h in previous['artifacts'].items():assert sha(p)==h
        objects=Path('S:/GTOpen-research/sampled-visible-hybrid-checkpoint-control-v1/objects')
        checkpoint=json.loads(read_object(objects,previous['continued_checkpoint']))
        context_path=OUT/'bb-context-candidate.json';context=context_path.read_text()
        inputs=[previous_path,previous_reg,context_path,Path(__file__),objects/previous['continued_checkpoint']['file'],
            *[objects/r['file'] for r in checkpoint['reservoirs']],
            *[ROOT/'tools/research'/name for name in ('sampled_visible_hybrid_fit_v1.py',
                'sampled_visible_initialization_v1.py','sampled_visible_poker_features_v1.py',
                'sampled_visible_hybrid_checkpoint_v1.py','sampled_physical_fit_v1.py',
                'sampled_physical_reservoir_v1.py')]]
        reg=dict(inputs={str(p):sha(p) for p in inputs},device=device,steps=8,seed=19393,
            chunk_size=13,gradient_tolerance=1e-5,loss_tolerance=1e-5,parameter_tolerance=1e-5,
            perturbation='Duplicate each old record with +/- 0.17*(1+i%7), alternating signs across legal actions; preserve visible observation and zero illegal targets.',
            scope='Synthetic noisy-repeat fixture; numerical objective/gradient/optimizer checks only. No new deals or poker-strength claim.',production_modified=False)
        regpath=OUT/f'{prefix}-registration.json';save(regpath,reg);store.mkdir()
        results=[];artifacts={}
        for player,ref in enumerate(checkpoint['reservoirs']):
            guard();read_object(objects,ref);old=PhysicalReservoir.load(objects/ref['file'],context)
            reservoir=PhysicalReservoir(2*old.size,player,19395+player,context)
            for i in range(old.size):
                n=int(old.arity[i]);delta=np.zeros(4)
                delta[:n]=.17*(1+i%7)*np.where(np.arange(n)%2==0,1.,-1.)
                obs=dict(hi=str(old.keys[i,0]),lo=str(old.keys[i,1]),actor=player,n=n,active_features=old.active[i].astype(int).tolist())
                for sign in (-1,1):reservoir.add(obs,old.values[i]+sign*delta,1)
            path=store/f'player-{player}.npz';reservoir.save(path);artifacts[str(path)]=sha(path)
            grouped=grouped_rows(reservoir);assert grouped['variance']>0
            cpu_model=fresh_visible_network(reg['seed']+player)
            rawx=torch.as_tensor(features([dict(active_features=a.tolist()) for a in reservoir.active[:reservoir.size]]))
            rawy=torch.as_tensor(reservoir.values[:reservoir.size]/grouped['scale'],dtype=torch.float32)
            legal=torch.as_tensor(np.arange(4)[None,:]<reservoir.arity[:reservoir.size,None])
            loss=((cpu_model(rawx)-rawy).square()*legal).sum()/grouped['denominator']
            loss.backward();raw_gradients=[p.grad.detach().clone() for p in cpu_model.parameters()]
            prepared=PreparedObjective(grouped,device,guard)
            candidate=fresh_visible_network(reg['seed']+player).to(device)
            grouped_loss=prepared.objective(candidate,reg['chunk_size'],guard,backward=True)
            gradient_error=max(float((a-p.grad.detach().cpu()).abs().max()) for a,p in zip(raw_gradients,candidate.parameters()))
            loss_error=abs(float(loss.detach())-grouped['variance']-grouped_loss)
            assert gradient_error<reg['gradient_tolerance'] and loss_error<reg['loss_tolerance']
            state=torch.random.get_rng_state().clone()
            actual,metric=fit(reservoir,seed=reg['seed']+player,steps=reg['steps'],device=device,chunk_size=reg['chunk_size'],guard=guard)
            repeat,_=fit(reservoir,seed=reg['seed']+player,steps=reg['steps'],device=device,chunk_size=reg['chunk_size'],guard=guard)
            assert actual==repeat and torch.equal(state,torch.random.get_rng_state())
            # Full tensor loop independently accumulates the entire grouped loss.
            reference=fresh_visible_network(reg['seed']+player).to(device)
            optimizer=torch.optim.Adam(reference.parameters(),lr=.003)
            x=torch.as_tensor(features([dict(active_features=a.tolist()) for a in grouped['active']]),device=device)
            target=torch.as_tensor(grouped['targets'],dtype=torch.float32,device=device)
            weights=torch.as_tensor((np.arange(4)[None,:]<grouped['arity'][:,None])*grouped['counts'][:,None],dtype=torch.float32,device=device)
            for _ in range(reg['steps']):
                optimizer.zero_grad(set_to_none=True)
                objective=((reference(x)-target).square()*weights).sum()/grouped['denominator']
                objective.backward();optimizer.step()
            expected=export_network(reference)
            parameter_error=max(float(np.max(abs(np.asarray(actual[k])-expected[k]))) for k in actual)
            assert parameter_error<reg['parameter_tolerance']
            learned=int(np.count_nonzero(np.asarray(actual['w0']).reshape(64,302)[:,269:]));assert learned>0
            results.append(dict(player=player,old_visits=old.size,retained=reservoir.size,grouped=len(grouped['active']),
                within_observation_variance=grouped['variance'],raw_grouped_gradient_error=gradient_error,
                raw_grouped_loss_error=loss_error,full_tensor_parameter_error=parameter_error,
                repeat_parameters_exact=True,unchanged_global_rng=True,learned_new_columns=learned,metric=metric))
        guard()
        for p,h in reg['inputs'].items():assert sha(p)==h
        output=dict(passed=True,registration_sha256=sha(regpath),device=device,records=results,
            artifacts=artifacts,seconds=time.monotonic()-started,accuracy_qualified=False,production_modified=False)
        save(OUT/f'{prefix}-result.json',output);print(json.dumps(output),flush=True)
    except Exception as exc:error=repr(exc);raise
    finally:
        save(OUT/f'{prefix}-status.json',dict(state='stopped' if error else 'complete',error=error,production_modified=False))
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
