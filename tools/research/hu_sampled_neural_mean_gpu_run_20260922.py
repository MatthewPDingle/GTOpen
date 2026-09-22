"""Finite GPU neural self-play with exact retained-data gradients; paired-method control."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from hu_sampled_neural_control_20260922 import Reservoir,geometry,sample_batch,exact_average_increment,normalize_average,flat_policy
from hu_sampled_neural_fallback_20260922 import highest_regret_fallback
from hu_sampled_neural_table_control_20260922 import sums
from hu_sampled_neural_bank_control_20260922 import save_bank
from hu_sampled_policy_bank_20260922 import average_bank
from hu_sampled_convergence_fixture_20260922 import evaluate

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-neural-mean-gpu-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def network():
    import torch
    return torch.nn.Sequential(torch.nn.Linear(28,64),torch.nn.ReLU(),torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,3)).cuda()

def fit(reservoir,features,mask,seed,steps):
    import torch
    torch.manual_seed(seed);model=network();opt=torch.optim.Adam(model.parameters(),lr=.003)
    raw=torch.as_tensor(reservoir.values,dtype=torch.float32)
    scale=raw.square().mean().sqrt().clamp_min(.01);targets=(raw/scale).numpy().astype(float)
    count=np.bincount(reservoir.ids,minlength=len(mask))
    means=sums(reservoir.ids,targets,len(mask))/np.maximum(count[:,None],1)
    expected=torch.as_tensor(means,dtype=torch.float32,device=features.device)
    weights=torch.as_tensor(mask*count[:,None],dtype=torch.float32,device=features.device);denominator=weights.sum()
    for _ in range(steps):
        loss=((model(features)-expected).square()*weights).sum()/denominator
        opt.zero_grad(set_to_none=True);loss.backward();opt.step()
    with torch.no_grad():prediction=(model(features)*scale).cpu().numpy().astype(float)
    state={k:v.detach().cpu().numpy().copy() for k,v in model.state_dict().items()}
    return prediction,dict(parameters=state,scale=float(scale))

def replay(path,data,features,mask,actors,played):
    import torch
    with np.load(path) as archive:stored={k:archive[k] for k in archive.files}
    iterations=int(stored['iterations']);assert iterations==len(played)
    recovered=[mask/mask.sum(axis=1,keepdims=True)];model=network();error=0.
    for t in range(iterations-1):
        policy=np.zeros_like(recovered[0])
        for player in range(2):
            model.load_state_dict({k:torch.as_tensor(stored[f'p{player}_{k}'][t]) for k in model.state_dict()})
            scale=torch.as_tensor(stored[f'p{player}_scales'][t])
            with torch.no_grad():prediction=(model(features)*scale).cpu().numpy().astype(float)
            candidate=highest_regret_fallback(prediction,mask);policy[actors==player]=candidate[actors==player]
        error=max(error,float(np.max(np.abs(policy-played[t+1]))));recovered.append(policy)
    assert error<1e-12
    return average_bank(data,recovered)[0],error

def worker(reg):
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    assert torch.cuda.is_available()
    data=json.loads((ROOT/reg['fixture']).read_text());config=reg['config'];x,mask,actors=geometry(data)
    features=torch.from_numpy(x).cuda()
    save(OUT/(PREFIX+'-environment.json'),dict(torch_version=torch.__version__,device=torch.cuda.get_device_name(),threads=2,deterministic_algorithms=True,tf32=False))
    for case in reg['cases']:
        for seed in reg['seeds']:
            began=time.monotonic();policy=mask/mask.sum(axis=1,keepdims=True);average=np.zeros_like(policy)
            reservoirs=[Reservoir(config['reservoir_capacity'],seed+100*p) for p in range(2)]
            rng=np.random.default_rng(seed+20000);snapshots=[[],[]];played=[];checkpoints=[];streak=0
            result_path=OUT/f'{PREFIX}-case{case}-seed{seed}.json'
            bank=ROOT/'target/research-sampled'/f'{PREFIX}-case{case}-seed{seed}.npz'
            for iteration in range(1,config['max_iterations']+1):
                played.append(policy.copy());average+=exact_average_increment(data,policy)
                for updater in range(2):
                    deals=rng.choice(24,size=config['traversals_per_player'],p=data['probabilities'])
                    uniforms=rng.random((len(deals),19));adv,_,_=sample_batch(data,case,policy,deals,uniforms,updater)
                    reservoirs[updater].add(*adv)
                for player in range(2):
                    prediction,state=fit(reservoirs[player],features,mask,seed+iteration*200003+player,config['advantage_train_steps'])
                    p=highest_regret_fallback(prediction,mask);policy[actors==player]=p[actors==player];snapshots[player].append(state)
                if iteration in config['checkpoints']:
                    diagnostic=normalize_average(average,mask);saved=save_bank(bank,snapshots,iteration)
                    saved['path']=str(bank.relative_to(ROOT))
                    inferred,replay_error=replay(bank,data,features,mask,actors,played)
                    mean_error=float(np.max(np.abs(inferred-diagnostic)));assert mean_error<1e-12
                    flat=flat_policy(data,inferred);ev=evaluate(data,flat,case)
                    streak=streak+1 if ev['gap']<=config['target_gap'] else 0
                    checkpoints.append(dict(iteration=iteration,seconds=time.monotonic()-began,evaluation=ev,average_policy=flat,
                        target_streak=streak,bank=saved,maximum_saved_model_replay_error=replay_error,
                        maximum_own_reach_average_error=mean_error,reservoirs=[r.summary() for r in reservoirs]))
                    result=dict(case=case,seed=seed,terminal=False,target_reached_twice=streak>=2,checkpoints=checkpoints)
                    save(result_path,result)
                    print(json.dumps(dict(case=case,seed=seed,iteration=iteration,gap=ev['gap'],seconds=time.monotonic()-began,replay_error=replay_error)),flush=True)
                    if streak>=2:break
            result.update(terminal=True,seconds=time.monotonic()-began);save(result_path,result)

def main():
    if len(sys.argv)>1:worker(json.loads(Path(sys.argv[1]).read_text()));return
    assert idle() and not LOCK.exists()
    assert not (LOCK.parent.parent/'symmetric-bridge-20260919/running.lock').exists()
    assert psutil.virtual_memory().available>=20_000_000_000
    gpu_free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
    assert gpu_free>=3_000_000_000
    source=OUT/'sampled-neural-mean-cpu-v1-registration.json';previous=json.loads(source.read_text())
    config=dict(previous['config']);config.update(reservoir_capacity=262144,advantage_train_steps=512)
    prerequisites=[OUT/p for p in ['sampled-reservoir-capacity-v1-result.json','sampled-mean-fit-cpu-v1-result.json']]
    assert all(json.loads(p.read_text())['terminal'] for p in prerequisites)
    physical_gpu=OUT/'sampled-physical-gpu-v1-review.json'
    first_cpu=OUT/'sampled-neural-mean-cpu-v1-case0-seed17.json'
    assert json.loads(physical_gpu.read_text())['passed']
    assert json.loads(first_cpu.read_text())['terminal'] and json.loads(first_cpu.read_text())['target_reached_twice']
    prerequisites += [physical_gpu,first_cpu,ROOT/'tools/research/hu_sampled_neural_mean_run_20260922.py']
    paths=[Path(__file__),source,ROOT/previous['fixture']]+prerequisites+[ROOT/'tools/research'/p for p in [
        'hu_sampled_neural_control_20260922.py','hu_sampled_neural_fallback_20260922.py','hu_sampled_neural_table_control_20260922.py',
        'hu_sampled_neural_bank_control_20260922.py','hu_sampled_policy_bank_20260922.py','hu_sampled_convergence_fixture_20260922.py',
        'hu_sampled_updates_oracle_20260922.py','loopback_research_validation.py']]
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths};regpath=OUT/(PREFIX+'-registration.json');assert not regpath.exists()
    reg=dict(inputs=frozen,fixture=previous['fixture'],config=config,cases=[0,1],seeds=[17,31],maximum_seconds=14400,
        primary='Exact finite best-response evaluation of the retained neural-model average, verified against independent own-reach averaging.',
        changes='262144 retained examples per player; 512 full empirical-mean gradient steps per fit; GPU float32 fitting. CPU normalization/grouping retained to match the paired CPU method. No learned average-policy network.',
        controls='Observable features only, preserved per-visit counts. Exact-gradient identity checked separately. Save and replay every played network at checkpoints.',
        stopping='Gap <= .01 at two consecutive checkpoints, else 2048 per run. Fixed four runs; no automatic extension or retry.',
        scope='Finite GPU strategic-method control against the independently registered CPU version. Device and optimizer-backend arithmetic can change trajectories; no bitwise CPU-strategy equality or physical-poker qualification is assumed.',
        no_gpu=False,production_modified=False)
    save(regpath,reg)
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    child=None;error=None;started=time.monotonic();next_resource=0.;samples=[]
    try:
        env=os.environ.copy();env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONUNBUFFERED='1',OMP_NUM_THREADS='2')
        with (OUT/(PREFIX+'.log')).open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__)),str(regpath)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2);elapsed=time.monotonic()-started
                assert elapsed<reg['maximum_seconds'] and idle(),'Deadline or production activity; stopping only this research child.'
                if elapsed>=next_resource:
                    free=psutil.virtual_memory().available;assert free>=20_000_000_000
                    gpu_free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
                    assert gpu_free>=3_000_000_000
                    samples.append(dict(seconds=elapsed,free_host_bytes=free,free_gpu_bytes=gpu_free));save(OUT/(PREFIX+'-resources.json'),samples);next_resource=elapsed+10
            assert child.returncode==0,f'Worker exited {child.returncode}; preserve available checkpoints.'
    except Exception as ex:error=str(ex);raise
    finally:
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
        save(OUT/(PREFIX+'-status.json'),dict(exit_code=child.returncode if child else None,error=error,seconds=time.monotonic()-started))
        LOCK.unlink()
    data=json.loads((ROOT/reg['fixture']).read_text());summaries=[];error=0.
    for case in reg['cases']:
        for seed in reg['seeds']:
            path=OUT/f'{PREFIX}-case{case}-seed{seed}.json';result=json.loads(path.read_text());assert result['terminal'];streak=0
            for i,c in enumerate(result['checkpoints']):
                p=c['average_policy']
                for a,b in zip(data['offsets'],data['offsets'][1:]):assert min(p[a:b])>=0 and abs(sum(p[a:b])-1)<1e-12
                gap=evaluate(data,p,case)['gap'];error=max(error,abs(gap-c['evaluation']['gap']))
                streak=streak+1 if gap<=config['target_gap'] else 0;assert c['target_streak']==streak
                assert c['maximum_saved_model_replay_error']<1e-12 and c['maximum_own_reach_average_error']<1e-12
                if i<len(result['checkpoints'])-1:assert streak<2
            last=result['checkpoints'][-1];assert result['target_reached_twice']==(streak>=2)
            if streak<2:assert last['iteration']==config['max_iterations']
            assert sha(ROOT/last['bank']['path'])==last['bank']['sha256']
            summaries.append(dict(case=case,seed=seed,iterations=last['iteration'],gap=last['evaluation']['gap'],target_reached_twice=streak>=2,result_sha256=sha(path)))
    assert error<1e-10 and all(sha(ROOT/p)==h for p,h in frozen.items())
    save(OUT/(PREFIX+'-review.json'),dict(implementation_checks_passed=True,inputs_verified=len(frozen),maximum_gap_reconstruction_error=error,
        runs=summaries,registration_sha256=sha(regpath),all_candidates_reached_target=all(r['target_reached_twice'] for r in summaries),
        physical_poker_convergence_qualified=False,production_modified=False))
    print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
