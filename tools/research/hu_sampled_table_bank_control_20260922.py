"""Long matched finite table controls: isolate reservoir error from neural fit."""
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
PREFIX='sampled-table-bank-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    source=OUT/'sampled-neural-bank-cached-v1-registration.json'
    registered=json.loads(source.read_text());config=registered['config']
    fixture=ROOT/registered['fixture'];data=json.loads(fixture.read_text())
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists() and idle()
    paths=[Path(__file__),source,fixture]+[ROOT/'tools/research'/p for p in [
        'hu_sampled_neural_control_20260922.py','hu_sampled_neural_fallback_20260922.py',
        'hu_sampled_neural_table_control_20260922.py','hu_sampled_convergence_fixture_20260922.py',
        'hu_sampled_updates_oracle_20260922.py','loopback_research_validation.py']]
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    record=dict(inputs=frozen,config=config,variants=['all_visits','bounded_reservoir_means'],
        cases=registered['cases'],seeds=registered['seeds'],maximum_seconds=300,
        primary='Exact own-reach average of played policies, matching the neural-bank target.',
        estimator='All-visit regrets or exact empirical per-information means from the same uniform-capacity reservoir.',
        matched='Traversal count, both-pass frozen updates, seeds, highest-regret fallback, ordinary iteration weights and checkpoints.',
        stopping='Exact summed gap <= .01 on two consecutive checkpoints, else 2048; no extension or outcome-dependent changes.',
        scope='Finite diagnostic only; per-information tables are not proposed physical-poker storage.',
        no_gpu=True,production_modified=False)
    save(reg,record);started=time.monotonic();last_guard=0.;results=[]
    _,mask,actors=geometry(data);count=len(mask)
    for variant in record['variants']:
        for case in record['cases']:
            for seed in record['seeds']:
                began=time.monotonic();policy=mask/mask.sum(axis=1,keepdims=True)
                regrets=np.zeros_like(policy);average=np.zeros_like(policy)
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
                        if variant=='bounded_reservoir_means':reservoirs[updater].add(*adv)
                        else:regrets+=sums(*adv,count)
                    if variant=='bounded_reservoir_means':
                        regrets=sum((sums(r.ids,r.values,count) for r in reservoirs),np.zeros_like(policy))
                    # Row counts are positive scalar factors; RM and argmax are unchanged.
                    policy=highest_regret_fallback(regrets,mask)
                    if iteration in config['checkpoints']:
                        flat=flat_policy(data,normalize_average(average,mask));ev=evaluate(data,flat,case)
                        streak=streak+1 if ev['gap']<=config['target_gap'] else 0
                        checkpoints.append(dict(iteration=iteration,evaluation=ev,average_policy=flat,target_streak=streak))
                        if streak>=2:break
                r=dict(variant=variant,case=case,seed=seed,seconds=time.monotonic()-began,
                    target_reached_twice=streak>=2,checkpoints=checkpoints)
                results.append(r);save(OUT/(PREFIX+'-result.json'),dict(terminal=False,runs=results))
                print(json.dumps(dict(variant=variant,case=case,seed=seed,iteration=iteration,
                    gap=checkpoints[-1]['evaluation']['gap'],target_reached_twice=streak>=2)),flush=True)
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
