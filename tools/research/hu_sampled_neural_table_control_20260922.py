"""Matched sampler/budget controls to localize neural approximation errors.

Finite tables are diagnostic baselines only, not proposed large-poker storage.
"""
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from loopback_research_validation import idle
from hu_sampled_convergence_fixture_20260922 import evaluate
from hu_sampled_neural_control_20260922 import (
    Reservoir, geometry, sample_batch, exact_average_increment,
    flat_policy, regret_policy, normalize_average)

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-neural-table-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def sums(ids, values, count):
    return np.stack([np.bincount(ids,weights=values[:,a],minlength=count) for a in range(3)],axis=1)


def main():
    # Sources/configuration fixed before the first baseline policy is trained.
    neural_reg=OUT/'sampled-neural-v1-registration.json'
    original=json.loads(neural_reg.read_text());config=original['config']
    fixture=ROOT/original['fixture'];data=json.loads(fixture.read_text())
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists() and idle()
    paths=[Path(__file__),neural_reg,fixture,ROOT/'tools/research/hu_sampled_neural_control_20260922.py',
        ROOT/'tools/research/hu_sampled_convergence_fixture_20260922.py',
        ROOT/'tools/research/hu_sampled_updates_oracle_20260922.py',
        ROOT/'tools/research/loopback_research_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    record=dict(inputs=frozen,created_at_unix=time.time(),config=config,
        variants=['all_visits_tabular','bounded_reservoir_means'],cases=[0,1],seeds=[17,31],
        maximum_seconds=300,purpose='Matched finite sampler/budget ablation; not scalable poker implementation',
        stopping='Same checkpoint target and iteration cap; preserve failed runs without retuning',
        no_gpu=True,production_modified=False)
    save(reg,record)
    start=time.monotonic();last_guard=0.;results=[]
    _,mask,actors=geometry(data);count=len(mask)
    for variant in record['variants']:
        for case in record['cases']:
            for seed in record['seeds']:
                began=time.monotonic();policy=mask/mask.sum(axis=1,keepdims=True)
                regrets=np.zeros_like(policy);average=np.zeros_like(policy);exact=np.zeros_like(policy)
                advantage_res=[Reservoir(config['reservoir_capacity'],seed+100*p) for p in range(2)]
                average_res=[Reservoir(config['reservoir_capacity'],seed+100*p+10000) for p in range(2)]
                rng=np.random.default_rng(seed+20000);checkpoints=[];streak=0
                for iteration in range(1,config['max_iterations']+1):
                    now=time.monotonic()
                    assert now-start<record['maximum_seconds'],'Deadline reached; retain existing outputs.'
                    if now-last_guard>=2:
                        assert idle(),'Production active; stopped only finite control.'
                        last_guard=now
                    exact+=exact_average_increment(data,policy)
                    for updater in range(2):
                        deals=rng.choice(24,size=config['traversals_per_player'],p=data['probabilities'])
                        uniforms=rng.random((len(deals),19))
                        adv,avg,_=sample_batch(data,case,policy,deals,uniforms,updater)
                        if variant=='bounded_reservoir_means':
                            advantage_res[updater].add(*adv);average_res[1-updater].add(*avg)
                        else:
                            regrets+=sums(*adv,count);average+=sums(*avg,count)
                    if variant=='bounded_reservoir_means':
                        regrets=sum((sums(r.ids,r.values,count) for r in advantage_res),np.zeros_like(policy))
                        average=sum((sums(r.ids,r.values,count) for r in average_res),np.zeros_like(policy))
                    # Dividing each row by its count would leave RM unchanged.
                    policy=regret_policy(regrets,mask)
                    if iteration in config['checkpoints']:
                        evaluated={}
                        for name,p in [('primary_average',normalize_average(average,mask)),
                                       ('exact_reach_average_diagnostic',normalize_average(exact,mask))]:
                            flat=flat_policy(data,p)
                            evaluated[name]=dict(evaluate(data,flat,case),policy=flat)
                        streak=streak+1 if evaluated['primary_average']['gap']<=config['target_gap'] else 0
                        checkpoints.append(dict(iteration=iteration,evaluations=evaluated,target_streak=streak))
                        if streak>=2:break
                result=dict(variant=variant,case=case,seed=seed,seconds=time.monotonic()-began,
                            target_reached_twice=streak>=2,checkpoints=checkpoints)
                results.append(result)
                save(OUT/(PREFIX+'-result.json'),dict(terminal=False,runs=results))
                print(json.dumps(dict(variant=variant,case=case,seed=seed,
                    final_gap=checkpoints[-1]['evaluations']['primary_average']['gap'],seconds=result['seconds'])),flush=True)
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    save(OUT/(PREFIX+'-result.json'),dict(terminal=True,runs=results,seconds=time.monotonic()-start,
        inputs_verified=len(frozen),registration_sha256=sha(reg),production_modified=False))


if __name__=='__main__':main()
