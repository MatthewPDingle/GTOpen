"""Post-hoc optimizer diagnostic on a frozen, reproducible training reservoir.

No self-play policy is changed and no new convergence claim is made. Separate
unavoidable sampled-target noise from error in fitting each observable mean.
"""
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
from hu_sampled_neural_control_20260922 import (
    Reservoir,geometry,sample_batch,regret_policy,normalize_average,flat_policy)
from hu_sampled_neural_table_control_20260922 import sums

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-neural-fit-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def collect(data,config):
    # Reproduce the already recorded bounded-table trajectory, without looking
    # at neural fits or optimizing the self-play trajectory for this probe.
    _,mask,actors=geometry(data);count=len(mask);seed=17;case=0
    policy=mask/mask.sum(axis=1,keepdims=True)
    advantages=[Reservoir(config['reservoir_capacity'],seed+100*p) for p in range(2)]
    averages=[Reservoir(config['reservoir_capacity'],seed+100*p+10000) for p in range(2)]
    rng=np.random.default_rng(seed+20000)
    previous=json.loads((OUT/'sampled-neural-table-v1-result.json').read_text())
    reference=next(r for r in previous['runs'] if r['variant']=='bounded_reservoir_means' and r['case']==case and r['seed']==seed)
    expected={c['iteration']:c for c in reference['checkpoints']}
    for iteration in range(1,257):
        for updater in range(2):
            deals=rng.choice(24,size=config['traversals_per_player'],p=data['probabilities'])
            uniforms=rng.random((len(deals),19))
            adv,avg,_=sample_batch(data,case,policy,deals,uniforms,updater)
            advantages[updater].add(*adv);averages[1-updater].add(*avg)
        regrets=sum((sums(r.ids,r.values,count) for r in advantages),np.zeros_like(policy))
        average=sum((sums(r.ids,r.values,count) for r in averages),np.zeros_like(policy))
        policy=regret_policy(regrets,mask)
        if iteration in expected:
            assert np.max(np.abs(np.asarray(flat_policy(data,normalize_average(average,mask)))-
                expected[iteration]['evaluations']['primary_average']['policy']))<1e-14
    return advantages


def worker(reg):
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False
    data=json.loads((ROOT/reg['fixture']).read_text())
    config=reg['config'];reservoirs=collect(data,config)
    x,mask,actors=geometry(data)
    features=torch.as_tensor(x,device='cuda');legal=torch.as_tensor(mask,device='cuda')
    results=[]
    for player,res in enumerate(reservoirs):
        np.savez_compressed(OUT/f'{PREFIX}-player{player}-reservoir.npz',ids=res.ids,values=res.values,priorities=res.priorities)
        counts=np.bincount(res.ids,minlength=len(mask))
        means=np.divide(sums(res.ids,res.values,len(mask)),counts[:,None],
                        out=np.zeros_like(x[:,:3],dtype=float),where=counts[:,None]>0)
        denominator=mask[res.ids].sum()
        irreducible=float((((res.values-means[res.ids])**2)*mask[res.ids]).sum()/denominator)
        ids=torch.as_tensor(res.ids,device='cuda')
        raw=torch.as_tensor(res.values,dtype=torch.float32,device='cuda')
        scale=raw.square().mean().sqrt().clamp_min(.01);targets=raw/scale
        for variant in reg['fits']:
            began=time.monotonic();torch.manual_seed(991+player)
            net=torch.nn.Sequential(torch.nn.Linear(28,64),torch.nn.ReLU(),torch.nn.Linear(64,64),
                                    torch.nn.ReLU(),torch.nn.Linear(64,3)).cuda()
            opt=torch.optim.Adam(net.parameters(),lr=.003)
            rng=torch.Generator(device='cuda').manual_seed(1000994+player)
            for _ in range(variant['steps']):
                sampled=torch.randint(len(ids),(variant['batch_size'],),generator=rng,device='cuda')
                info=ids[sampled];ok=legal[info]
                loss=((net(features[info])-targets[sampled]).square()*ok).sum()/ok.sum()
                opt.zero_grad(set_to_none=True);loss.backward();opt.step()
            with torch.no_grad():prediction=(net(features)*scale).cpu().numpy().astype(float)
            mse=float((((prediction[res.ids]-res.values)**2)*mask[res.ids]).sum()/denominator)
            excess=float((((prediction-means)**2)*mask*counts[:,None]).sum()/denominator)
            assert abs(mse-irreducible-excess)<1e-10
            ideal=regret_policy(means,mask);predicted=regret_policy(prediction,mask)
            l1=np.abs(ideal-predicted).sum(axis=1)
            result=dict(player=player,fit=variant,seconds=time.monotonic()-began,
                reservoir_mse=mse,irreducible_empirical_variance=irreducible,excess_mean_fit_mse=excess,
                visitation_weighted_policy_l1=float(l1@counts/counts.sum()),
                rows=[dict(key=data['information_keys'][i],count=int(counts[i]),
                    target_means=means[i].tolist(),prediction=prediction[i].tolist(),
                    target_policy=ideal[i].tolist(),predicted_policy=predicted[i].tolist(),policy_l1=float(l1[i]))
                    for i in range(len(mask)) if actors[i]==player and counts[i]>0])
            results.append(result)
            save(OUT/(PREFIX+'-result.json'),dict(terminal=False,results=results))
            print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
    save(OUT/(PREFIX+'-result.json'),dict(terminal=True,results=results,
        purpose='Post-hoc fit diagnostic, not a self-play or strategic improvement result',production_modified=False))


def main():
    if len(sys.argv)>1:
        worker(json.loads(Path(sys.argv[1]).read_text()));return
    assert idle() and not LOCK.exists()
    assert not (LOCK.parent.parent/'symmetric-bridge-20260919/running.lock').exists()
    reg_path=OUT/(PREFIX+'-registration.json');assert not reg_path.exists()
    original_path=OUT/'sampled-neural-v1-registration.json';original=json.loads(original_path.read_text())
    paths=[Path(__file__),original_path,ROOT/original['fixture'],
        OUT/'sampled-neural-table-v1-result.json',
        ROOT/'tools/research/hu_sampled_neural_control_20260922.py',
        ROOT/'tools/research/hu_sampled_neural_table_control_20260922.py',
        ROOT/'tools/research/hu_sampled_convergence_fixture_20260922.py',
        ROOT/'tools/research/hu_sampled_updates_oracle_20260922.py',
        ROOT/'tools/research/loopback_research_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    reg=dict(inputs=frozen,created_at_unix=time.time(),maximum_seconds=180,
        fixture=original['fixture'],config=original['config'],
        fits=[dict(steps=128,batch_size=512),dict(steps=128,batch_size=8192),dict(steps=1024,batch_size=8192)],
        source='Frozen case0 seed17 bounded-table trajectory; all saved checkpoints must replay exactly',
        purpose='Post-hoc optimizer diagnosis. Same initial model per player; fixed data. No self-play accuracy claim.',
        no_automatic_retry=True)
    save(reg_path,reg)
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    child=None;error=None;start=time.monotonic();samples=[];next_resource=0
    try:
        env=os.environ.copy();env['CUBLAS_WORKSPACE_CONFIG']=':4096:8';env['PYTHONUNBUFFERED']='1'
        with (OUT/(PREFIX+'.log')).open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__)),str(reg_path)],cwd=ROOT,env=env,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2);elapsed=time.monotonic()-start
                assert elapsed<reg['maximum_seconds'] and idle(),'Deadline or production activity; no retry.'
                if elapsed>=next_resource:
                    host=psutil.virtual_memory().available
                    gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
                    samples.append(dict(seconds=elapsed,free_host_bytes=host,free_gpu_bytes=gpu))
                    save(OUT/(PREFIX+'-resources.json'),samples);next_resource=elapsed+10
                    assert host>=20_000_000_000 and gpu>=3_000_000_000,'Resource reserve reached.'
            assert child.returncode==0,f'Worker exited {child.returncode}; retain failure.'
    except Exception as ex:error=str(ex);raise
    finally:
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
        save(OUT/(PREFIX+'-status.json'),dict(exit_code=child.returncode if child else None,error=error,seconds=time.monotonic()-start))
        LOCK.unlink()
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    result=json.loads((OUT/(PREFIX+'-result.json')).read_text());assert result['terminal']
    save(OUT/(PREFIX+'-review.json'),dict(passed=True,inputs_verified=len(frozen),
        registration_sha256=sha(reg_path),result_sha256=sha(OUT/(PREFIX+'-result.json')),
        reservoir_sha256={f'player{p}':sha(OUT/f'{PREFIX}-player{p}-reservoir.npz') for p in range(2)},
        strategic_improvement_demonstrated=False,production_modified=False))


if __name__=='__main__':main()
