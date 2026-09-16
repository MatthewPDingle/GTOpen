"""Fixed-budget strategy-stability diagnostic after all N17 qualification gates."""
import datetime as dt
import json
import math
import os
import sys
import time
from pathlib import Path

import continuation_policy_transfer_optimized as optimized

study=optimized.study
base=optimized.original.BASE
OUT=base/'policy-stability-20260916'


def changes(a,b):
    assert a['config']==b['config']
    assert [x['path'] for x in a['views']]==[x['path'] for x in b['views']]
    rows=[]
    for left,right in zip(a['views'],b['views']):
        x,y=left['view'],right['view']
        assert x['actor']==y['actor']
        assert [v['label'] for v in x['actions']]==[v['label'] for v in y['actions']]
        n=len(x['actions'])
        if not n:continue
        assert len(x['strategy'])==len(y['strategy'])==169*n
        assert len(x['reach'])==len(y['reach'])==169
        weights=[(x['reach'][h]+y['reach'][h])*.5*(6 if h//13==h%13 else 4 if h//13<h%13 else 12) for h in range(169)]
        assert all(math.isfinite(w) and w>=0 for w in weights) and sum(weights)>0
        tv=[.5*sum(abs(x['strategy'][k*169+h]-y['strategy'][k*169+h]) for k in range(n)) for h in range(169)]
        assert all(math.isfinite(v) and 0<=v<=1.00002 for v in tv)
        rows.append(dict(path=left['path'],actor=x['actor_pos'],
            max_action_frequency_change=max(abs(v['freq']-w['freq']) for v,w in zip(x['actions'],y['actions'])),
            weighted_hand_total_variation=sum(w*v for w,v in zip(weights,tv))/sum(weights),
            max_hand_total_variation=max(tv)))
    assert rows and all(math.isfinite(g) and g>=-1e-6 for g in b['gaps'])
    gap=sum(max(0,g) for g in b['gaps'])
    return dict(start=a['iteration'],end=b['iteration'],nodes=rows,gap_total_bb=gap,
        signal_passed=gap<=.005 and all(r['max_action_frequency_change']<=.01 and r['weighted_hand_total_variation']<=.01 for r in rows))


def idle():
    optimized.adapter().require_idle()
    for p in optimized.original.queue.processes():
        command=(p['CommandLine'] or '').lower()
        if p['ProcessId']!=os.getpid() and p['Name'].lower() in ['python.exe','pythonw.exe']:
            assert not any(t in command for t in ['continuation_qualified_gpu_queue.py','continuation_policy_stability.py run']), 'Research GPU still owned by another controller'
    assert dt.datetime.now(dt.timezone.utc)<optimized.original.bridge.DEADLINE


def run():
    idle()
    directory=optimized.OUT/'N17'
    assert study.read(directory/'evaluation.json')['accuracy_screen_passed'],'Changed-policy accuracy must pass'
    model,gpu,arm,kernel=optimized.selection('N17')
    OUT.mkdir(parents=True,exist_ok=True)
    if not (OUT/'protocol-freeze.json').exists():
        assert (optimized.original.bridge.DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()>=5400
    sources=[OUT/'README.md',Path(__file__),directory/'evaluation.json',directory/'protocol-freeze.json',kernel,
        model/'candidate.json',gpu/'timing.json',optimized.original.runtime.BIN]
    sources += [directory/a/'policy.gtop' for a in ['original','candidate']]
    hashes={str(p.resolve().relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in sources}
    hashes.update(study.read(gpu/'manifest.json')['files'])
    hashes.update(study.read(directory/'protocol-freeze.json')['files'])
    frozen=OUT/'protocol-freeze.json'
    if frozen.exists():
        record=study.read(frozen)
        assert record['variant']==arm and record['files']==hashes,'Frozen diagnostic inputs changed'
    else:
        study.freeze(frozen,dict(registered_at=study.night.now(),variant=arm,files=hashes,production_enabled=False))
    trajectory={a:[] for a in ['original','candidate']}
    previous={a:directory/a/'iteration-500.json' for a in trajectory}
    saves={a:directory/a/'policy.gtop' for a in trajectory}
    for iteration,order in [(1000,['original','candidate']),(1500,['candidate','original'])]:
        for action in order:
            folder=OUT/action/str(iteration);folder.mkdir(parents=True,exist_ok=True)
            output=folder/f'iteration-{iteration}.json'
            if not output.exists():
                idle();start=time.monotonic()
                optimized.original.runtime.command(['solve',saves[action],folder,action,500,kernel,'resume'],
                    folder/'run.log',optimized=action=='candidate',warm=0)
                study.night.dump(folder/'process-time.json',dict(seconds=time.monotonic()-start))
            result=study.read(output)
            assert result['iteration']==iteration and result['start_iteration']==iteration-500 and result['warmup_iterations']==0
            row=changes(study.read(previous[action]),result)
            row.update(learning_seconds=result['learning_seconds'],setup_seconds=result['setup_seconds'],
                process_seconds=study.read(folder/'process-time.json')['seconds'],snapshot_sha256=study.pilot.sha(output))
            trajectory[action].append(row);previous[action]=output;saves[action]=folder/'policy.gtop'
            study.night.dump(OUT/'progress.json',dict(trajectory=trajectory,updated=study.night.now(),production_enabled=False))
    signals={a:all(r['signal_passed'] for r in rows) for a,rows in trajectory.items()}
    study.night.dump(OUT/'result.json',dict(trajectory=trajectory,practical_stability=signals,
        additional_learning_seconds={a:sum(r['learning_seconds'] for r in rows) for a,rows in trajectory.items()},
        both_signals_passed=all(signals.values()),production_enabled=False,
        caveat='Limited inspected-node stability and frozen-value gaps do not establish full-game convergence. New ranges need their own accuracy audit.'))


if __name__=='__main__':
    assert sys.argv[1:]==['run']
    run()
