"""Registered larger-reservoir finite control; no neural fitting or GPU work."""
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from hu_sampled_convergence_fixture_20260922 import evaluate
from hu_sampled_neural_control_20260922 import (
    Reservoir, geometry, sample_batch, exact_average_increment, flat_policy, normalize_average)
from hu_sampled_neural_fallback_20260922 import highest_regret_fallback
from hu_sampled_neural_table_control_20260922 import sums

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-reservoir-capacity-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    source=OUT/'sampled-neural-bank-cached-v1-registration.json'
    baseline=OUT/'sampled-table-bank-v1-result.json'
    previous=json.loads(source.read_text());config=dict(previous['config']);config['reservoir_capacity']=262144
    fixture=ROOT/previous['fixture'];data=json.loads(fixture.read_text())
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists() and idle()
    paths=[Path(__file__),source,fixture,baseline]+[ROOT/'tools/research'/p for p in [
        'hu_sampled_neural_control_20260922.py','hu_sampled_neural_fallback_20260922.py',
        'hu_sampled_neural_table_control_20260922.py','hu_sampled_convergence_fixture_20260922.py',
        'hu_sampled_updates_oracle_20260922.py','loopback_research_validation.py']]
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    record=dict(inputs=frozen,config=config,cases=[0,1],seeds=[17,31],maximum_seconds=600,
        hypothesis='An eightfold reservoir reduces sampling-estimator error versus 32768 retained examples without changing sampled CFR.',
        primary='Exact own-reach average of actually played policies; exact finite evaluator.',
        changes='Only retained-record capacity versus bounded_reservoir_means in sampled-table-bank-v1. Full-visit means collected only as diagnostic.',
        stopping='Summed gap <= .01 on two consecutive checkpoints, else 2048. No extensions.',
        scope='Finite diagnostic only; no physical poker training or production modifications.',
        no_gpu=True,production_modified=False)
    save(reg,record);started=time.monotonic();last_guard=0.;results=[]
    _,mask,actors=geometry(data);count=len(mask)
    for case in record['cases']:
        for seed in record['seeds']:
            began=time.monotonic();policy=mask/mask.sum(axis=1,keepdims=True);average=np.zeros_like(policy)
            all_sum=np.zeros_like(policy);all_count=np.zeros(count,dtype=np.int64)
            reservoirs=[Reservoir(config['reservoir_capacity'],seed+100*p) for p in range(2)]
            rng=np.random.default_rng(seed+20000);checkpoints=[];streak=0
            for iteration in range(1,config['max_iterations']+1):
                now=time.monotonic();assert now-started<record['maximum_seconds']
                if now-last_guard>=2:
                    assert idle() and psutil.virtual_memory().available>=20_000_000_000
                    last_guard=now
                average+=exact_average_increment(data,policy)
                for updater in range(2):
                    deals=rng.choice(24,size=config['traversals_per_player'],p=data['probabilities'])
                    uniforms=rng.random((len(deals),19))
                    adv,_,_=sample_batch(data,case,policy,deals,uniforms,updater)
                    reservoirs[updater].add(*adv)
                    all_sum+=sums(*adv,count);all_count+=np.bincount(adv[0],minlength=count)
                regret=sum((sums(r.ids,r.values,count) for r in reservoirs),np.zeros_like(policy))
                policy=highest_regret_fallback(regret,mask)
                if iteration in config['checkpoints']:
                    flat=flat_policy(data,normalize_average(average,mask));ev=evaluate(data,flat,case)
                    streak=streak+1 if ev['gap']<=config['target_gap'] else 0
                    retained_count=sum((np.bincount(r.ids,minlength=count) for r in reservoirs),np.zeros(count,dtype=np.int64))
                    retained_mean=regret/np.maximum(retained_count[:,None],1)
                    full_mean=all_sum/np.maximum(all_count[:,None],1)
                    occupied=retained_count>0
                    mse=float((((retained_mean-full_mean)**2*mask).sum(axis=1)*all_count).sum()/max(float((mask.sum(axis=1)*all_count).sum()),1.))
                    checkpoints.append(dict(iteration=iteration,evaluation=ev,average_policy=flat,target_streak=streak,
                        reservoirs=[r.summary() for r in reservoirs],full_visit_mean_diagnostic_mse=mse,
                        occupied_observations=int(occupied.sum()),seen_but_unretained_observations=int(((all_count>0)&~occupied).sum())))
                    if streak>=2:break
            snapshots=[]
            if case==0 and seed==17:
                for player,r in enumerate(reservoirs):
                    path=ROOT/'target/research-sampled'/f'{PREFIX}-case0-seed17-player{player}.npz';assert not path.exists()
                    np.savez_compressed(path,ids=r.ids,values=r.values,priorities=r.priorities,
                        all_sum=all_sum,all_count=all_count,iteration=iteration)
                    snapshots.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path),bytes=path.stat().st_size))
            r=dict(case=case,seed=seed,seconds=time.monotonic()-began,target_reached_twice=streak>=2,
                checkpoints=checkpoints,snapshots=snapshots)
            results.append(r);save(OUT/(PREFIX+'-result.json'),dict(terminal=False,runs=results))
            print(json.dumps(dict(case=case,seed=seed,iteration=iteration,gap=checkpoints[-1]['evaluation']['gap'],
                target_reached_twice=streak>=2,seconds=r['seconds'])),flush=True)
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    error=0.
    for r in results:
        for c in r['checkpoints']:
            p=c['average_policy']
            for a,b in zip(data['offsets'],data['offsets'][1:]):assert min(p[a:b])>=0 and abs(sum(p[a:b])-1)<1e-12
            error=max(error,abs(evaluate(data,p,r['case'])['gap']-c['evaluation']['gap']))
    assert error<1e-12
    save(OUT/(PREFIX+'-result.json'),dict(terminal=True,runs=results,seconds=time.monotonic()-started,
        inputs_verified=len(frozen),registration_sha256=sha(reg),maximum_evaluation_reconstruction_error=error,
        physical_poker_convergence_qualified=False,production_modified=False))

if __name__=='__main__':main()
