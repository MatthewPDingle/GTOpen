"""Finite learned-advantage control with a retained neural iteration bank.

Remove the separate average-policy approximation, retaining the frozen max-v1
advantage training and sampling trajectory. No physical poker qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from hu_sampled_neural_control_20260922 import (
    Reservoir,geometry,sample_batch,exact_average_increment,normalize_average,flat_policy)
from hu_sampled_neural_fallback_20260922 import highest_regret_fallback
from hu_sampled_policy_bank_20260922 import average_bank
from hu_sampled_convergence_fixture_20260922 import evaluate


def network():
    import torch
    return torch.nn.Sequential(torch.nn.Linear(28,64),torch.nn.ReLU(),
        torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,3)).cuda()


def fit_advantage(reservoir,features,mask,seed,steps):
    """Same operations/seeds as frozen v1 fit, additionally retain parameters."""
    import torch
    torch.manual_seed(seed)
    model=network();optimizer=torch.optim.Adam(model.parameters(),lr=.003)
    ids=torch.as_tensor(reservoir.ids,device='cuda')
    targets=torch.as_tensor(reservoir.values,dtype=torch.float32,device='cuda')
    scale=targets.square().mean().sqrt().clamp_min(.01);targets=targets/scale
    rng=torch.Generator(device='cuda').manual_seed(seed+1000003)
    for _ in range(steps):
        selected=torch.randint(len(ids),(512,),generator=rng,device='cuda')
        information=ids[selected];legal=mask[information]
        pred=model(features[information])
        loss=((pred-targets[selected]).square()*legal).sum()/legal.sum()
        optimizer.zero_grad(set_to_none=True);loss.backward();optimizer.step()
    with torch.no_grad():prediction=model(features)*scale
    state={k:v.detach().cpu().numpy().copy() for k,v in model.state_dict().items()}
    return prediction.cpu().numpy().astype(np.float64),dict(parameters=state,scale=float(scale.cpu()))


def save_bank(path,snapshots,iterations):
    """Initial uniform policy is implicit. Last trained model is not yet played."""
    arrays={'iterations':np.array(iterations,dtype=np.int64),'uniform_initial':np.array(True)}
    assert all(len(s)==iterations for s in snapshots)
    for player in range(2):
        retained=snapshots[player][:iterations-1]
        arrays[f'p{player}_scales']=np.array([s['scale'] for s in retained],dtype=np.float32)
        if retained:
            for key in retained[0]['parameters']:
                arrays[f'p{player}_{key}']=np.stack([s['parameters'][key] for s in retained])
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.partial.npz')
    np.savez_compressed(temporary,**arrays);temporary.replace(path)
    return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,
        parameter_payload_bytes=sum(s['parameters'][k].nbytes for p in snapshots for s in p[:iterations-1] for k in s['parameters']),
        retained_neural_models=2*(iterations-1),initial_uniform_policy=True)


def replay_bank(path,data,features,mask,actors,played):
    """Reload actual saved weights; match all played policies before averaging."""
    import torch
    with np.load(path) as stored:
        iterations=int(stored['iterations']);assert iterations==len(played)
        recovered=[mask/mask.sum(axis=1,keepdims=True)]
        model=network();error=0.
        for t in range(iterations-1):
            policy=np.zeros_like(recovered[0])
            for player in range(2):
                state={k:torch.as_tensor(stored[f'p{player}_{k}'][t],device='cuda') for k in model.state_dict()}
                model.load_state_dict(state)
                scale=torch.as_tensor(stored[f'p{player}_scales'][t],device='cuda')
                with torch.no_grad():pred=(model(features)*scale).cpu().numpy().astype(np.float64)
                candidate=highest_regret_fallback(pred,mask)
                policy[actors==player]=candidate[actors==player]
            error=max(error,float(np.max(np.abs(policy-played[t+1]))))
            recovered.append(policy)
    assert error<1e-12,'Saved neural bank did not reproduce played policies.'
    averaged,_=average_bank(data,recovered)
    return averaged,error


def run(data,case,seed,reg):
    import torch
    config=reg['config'];start=time.monotonic()
    x,mask,actors=geometry(data);features=torch.as_tensor(x,device='cuda');legal=torch.as_tensor(mask,device='cuda')
    policy=mask/mask.sum(axis=1,keepdims=True);exact_average=np.zeros_like(policy)
    reservoirs=[Reservoir(config['reservoir_capacity'],seed+100*p) for p in range(2)]
    snapshots=[[],[]];played=[];rng=np.random.default_rng(seed+20000);checkpoints=[];streak=0
    reference=json.loads(Path(reg['reference_prefix']+f'-case{case}-seed{seed}.json').read_text())
    reference_at={c['iteration']:c for c in reference['checkpoints']}
    output=Path(reg['output_prefix']+f'-case{case}-seed{seed}.json')
    bank_path=Path(reg['bank_prefix']+f'-case{case}-seed{seed}.npz')
    for iteration in range(1,config['max_iterations']+1):
        played.append(policy.copy());exact_average+=exact_average_increment(data,policy)
        for updater in range(2):
            deals=rng.choice(24,size=config['traversals_per_player'],p=data['probabilities'])
            uniforms=rng.random((len(deals),19))
            adv,_,_=sample_batch(data,case,policy,deals,uniforms,updater)
            reservoirs[updater].add(*adv)
        for player in range(2):
            prediction,state=fit_advantage(reservoirs[player],features,legal,
                seed+iteration*200003+player,config['advantage_train_steps'])
            candidate=highest_regret_fallback(prediction,mask)
            policy[actors==player]=candidate[actors==player];snapshots[player].append(state)
        if iteration in config['checkpoints']:
            diagnostic=normalize_average(exact_average,mask)
            bank_average,_=average_bank(data,played)
            average_error=float(np.max(np.abs(bank_average-diagnostic)))
            assert average_error<1e-12
            reference_error=None
            if iteration in reference_at:
                expected=reference_at[iteration]['evaluations']['exact_reach_average_diagnostic']['policy']
                reference_error=float(np.max(np.abs(np.array(flat_policy(data,diagnostic))-expected)))
                assert reference_error<1e-10,'Changed the max-v1 learning trajectory at a shared checkpoint.'
            saved=save_bank(bank_path,snapshots,iteration)
            replayed,replay_error=replay_bank(bank_path,data,features,mask,actors,played)
            assert np.max(np.abs(replayed-bank_average))<1e-12
            flat=flat_policy(data,replayed);ev=evaluate(data,flat,case)
            streak=streak+1 if ev['gap']<=config['target_gap'] else 0
            c=dict(iteration=iteration,seconds=time.monotonic()-start,evaluation=ev,average_policy=flat,
                target_streak=streak,bank=saved,maximum_own_reach_average_error=average_error,
                maximum_saved_model_replay_error=replay_error,max_v1_prefix_error=reference_error,
                advantage_reservoirs=[r.summary() for r in reservoirs])
            checkpoints.append(c)
            partial=dict(case=case,seed=seed,checkpoints=checkpoints,target_reached_twice=streak>=2,terminal=False)
            output.write_text(json.dumps(partial,indent=2)+'\n',encoding='utf-8',newline='\n')
            print(json.dumps(dict(case=case,seed=seed,iteration=iteration,gap=ev['gap'],seconds=c['seconds'],
                                 bank_bytes=saved['bytes'],replay_error=replay_error)),flush=True)
            if streak>=2:break
    partial['terminal']=True;partial['seconds']=time.monotonic()-start
    output.write_text(json.dumps(partial,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('registration');args=parser.parse_args()
    reg=json.loads(Path(args.registration).read_text())
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False
    data=json.loads(Path(reg['fixture']).read_text())
    environment=dict(torch_version=torch.__version__,cuda_version=torch.version.cuda,gpu=torch.cuda.get_device_name(0),
                     deterministic_algorithms=True,tf32=False,cpu_threads=torch.get_num_threads())
    Path(reg['output_prefix']+'-environment.json').write_text(json.dumps(environment,indent=2)+'\n',encoding='utf-8',newline='\n')
    for case in reg['cases']:
        for seed in reg['seeds']:run(data,case,seed,reg)


if __name__=='__main__':main()
