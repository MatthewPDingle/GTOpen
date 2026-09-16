"""N32 controlled zero-own-reach continuation experiment, research only."""
import datetime as dt
import math
import os
from pathlib import Path
import sys
import time
import continuation_chance_control as control
import continuation_full_precision as full
import continuation_policy_stability as stability

study=control.study
BASE=control.BASE
OUT=BASE/'zero-fallback-20260916'
SOURCE=BASE/'policy-stability-20260916/candidate/1500/policy.gtop'
OLD=control.KERNEL
NEW=OUT/'interface.cu'
GUARD='bool learned=use_learned && sprs[nd]>=1. && sprs[nd]<=20. && totals[0]>0. && totals[1]>0.;'
REPLACEMENT='bool learned=use_learned && sprs[nd]>=1. && sprs[nd]<=20.;'

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    source=OLD.read_bytes();assert source.count(GUARD.encode())==1
    changed=source.replace(GUARD.encode(),REPLACEMENT.encode())
    if NEW.exists(): assert NEW.read_bytes()==changed
    else:NEW.write_bytes(changed)
    snapshot=study.read(BASE/'policy-stability-20260916/candidate/1500/iteration-1500.json')
    assert snapshot['iteration']==1500 and snapshot['config'].get('ante',0)==0
    inputs=dict(study.read(control.FULL/'manifest.json')['files'])
    for p in [Path(__file__),OUT/'README.md',OLD,NEW,SOURCE,
              BASE/'zero-reach-20260916/result.json',BASE/'policy-stability-20260916/candidate/1500/iteration-1500.json']:
        inputs[str(p.resolve().relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(p)
    for path,expected in inputs.items():assert study.pilot.sha(study.ROOT/path)==expected,path
    freeze=OUT/'protocol-freeze.json'
    record=dict(inputs=inputs,steps_per_arm=500,start_iteration=1500,order=['control','uniform_prior'],
                interesting_gap_reduction=.25,desired_gap_bb=.005,production_enabled=False)
    if freeze.exists():assert {k:study.read(freeze)[k] for k in record}==record
    else:study.freeze(freeze,dict(registered_at=study.night.now(),**record))

def state(stage,**kwargs):
    study.night.dump(OUT/'status.json',dict(stage=stage,controller_pid=os.getpid(),updated=study.night.now(),production_enabled=False,**kwargs))
    print(stage,kwargs,flush=True)

def remaining():return (control.transfer.original.bridge.DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()

def run():
    prepare();assert not (OUT/'result.json').exists()
    state('waiting_for_N21')
    while True:
        status=study.read(BASE/'flop-menu-20260916/status.json')
        if status['stage']=='complete':
            # The completion write precedes the parent's process exit by a moment.
            time.sleep(2);break
        if remaining()<2400:state('deferred_deadline');return
        if status['stage']=='failed':raise RuntimeError('N21 failed; inspect its owner before continuing')
        time.sleep(10)
    control.idle()
    if remaining()<2400:state('deferred_deadline');return
    state('positive_reach_parity')
    oracle=OUT/'oracle';oracle.mkdir(exist_ok=True)
    for label,kernel in [('control',OLD),('uniform_prior',NEW)]:
        target=oracle/f'{label}.json'
        assert not target.exists()
        control.transfer.original.runtime.command(['evaluate',SOURCE,target,'candidate',kernel],oracle/f'{label}.log',optimized=True,warm=0)
    parity=full.action_difference(study.read(oracle/'control.json'),study.read(oracle/'uniform_prior.json'))
    assert parity['max_action_difference_bb']==0.,parity
    study.freeze(OUT/'oracle-parity.json',parity)
    state('sparse_safety')
    for n in [2,3,8]:
        target=oracle/f'zero-{n}.json'
        control.transfer.original.runtime.command(['oracle',target,NEW,'candidate',n,'zeros'],oracle/f'zero-{n}.log',optimized=True,warm=0)
        data=study.read(target)
        assert all(math.isfinite(x) for x in data['gaps']+data['evs']) and abs(sum(data['evs']))<.0002
        for row in data['frontier']['rows']:
            for hand in row['hands']:
                assert all(math.isfinite(x) for x in hand['action_values_counterfactual_bb'])
    rows=[]
    for arm,kernel in [('control',OLD),('uniform_prior',NEW)]:
        control.idle()
        assert remaining()>900,'Insufficient reserved time for next bounded arm'
        state('learning',arm=arm)
        folder=OUT/arm;folder.mkdir(exist_ok=True)
        assert not (folder/'policy.gtop').exists()
        control.transfer.original.runtime.command(['solve',SOURCE,folder,'candidate',500,kernel,'resume'],folder/'run.log',optimized=True,warm=0)
        s=study.read(folder/'iteration-2000.json')
        assert s['iteration']==2000 and s['start_iteration']==1500 and s['warmup_iterations']==0
        assert all(math.isfinite(x) for x in s['gaps']+s['evs']) and abs(sum(s['evs']))<.0002
        changes=stability.changes(study.read(BASE/'policy-stability-20260916/candidate/1500/iteration-1500.json'),s)
        rows.append(dict(arm=arm,gap_total_bb=sum(s['gaps']),learning_seconds=s['learning_seconds'],gaps=s['gaps'],changes=changes,
                         snapshot_sha256=study.pilot.sha(folder/'iteration-2000.json')))
    prepare()
    ratio=rows[1]['gap_total_bb']/rows[0]['gap_total_bb']
    study.freeze(OUT/'result.json',dict(rows=rows,gap_ratio=ratio,interesting_reduction=ratio<=.75,
                 reaches_desired_gap=rows[1]['gap_total_bb']<=.005,production_enabled=False,
                 caveat='One same-start bounded continuation comparison, not repeated timing, a full-game equilibrium proof or deployment qualification. Uniform own-range prior at zero reach remains an assumption.'))
    state('complete',gap_ratio=ratio)

if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
