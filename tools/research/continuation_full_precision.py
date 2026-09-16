"""Independently qualify N17's double source after rejecting mixed arithmetic."""
import datetime as dt
import os
import statistics
import subprocess
import sys
from pathlib import Path

import continuation_pair_reductions as pair

study=pair.study
runtime=pair.runtime
BASE=pair.OUT.parent
OUT=BASE/'full-precision-20260916'


def idle():
    pair.mixed.transfer.require_idle()
    for p in pair.mixed.transfer.queue.processes():
        if p['ProcessId']==os.getpid() or p['Name'].lower() not in ['python.exe','pythonw.exe']:continue
        assert not any(t in (p['CommandLine'] or '').lower() for t in ['continuation_qualified_gpu_queue.py',
            'continuation_pair_reductions.py oracle','continuation_pair_reductions.py benchmark',
            'continuation_full_precision.py run','continuation_policy_stability.py run',
            'continuation_policy_transfer_optimized.py run']), 'Another controller owns research GPU'
    assert dt.datetime.now(dt.timezone.utc)<runtime.guard.DEADLINE


def state(stage,**fields):
    study.night.dump(OUT/'status.json',dict(stage=stage,controller_pid=os.getpid(),updated=study.night.now(),production_enabled=False,**fields))
    print(stage,fields,flush=True)


def prepare():
    idle();pair.export();pair.double.qualified()
    assert study.read(pair.OUT/'oracle-check.json')['passed']
    assert study.read(pair.double.OUT/'oracle-check.json')['passed']
    OUT.mkdir(parents=True,exist_ok=True);folder=OUT/'double';folder.mkdir(exist_ok=True)
    target=folder/'interface.cu';source=(pair.OUT/'double/interface.cu').read_bytes()
    if target.exists():assert target.read_bytes()==source
    else:target.write_bytes(source)
    files=dict(study.read(pair.OUT/'manifest.json')['files'])
    paths=[Path(__file__),OUT/'README.md',target,pair.OUT/'oracle-check.json',pair.double.OUT/'oracle-check.json',
        pair.double.shrunk.OUT/'evaluation.json',BASE/'qualified-gpu-queue-20260916/status.json']
    for arm in ['original','double']:paths.append(pair.OUT/f'repeat-0/{arm}/policy.gtop')
    files.update({str(p.resolve().relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths})
    study.freeze(OUT/'manifest.json',dict(files=files,candidate_sha256=study.pilot.sha(pair.double.shrunk.OUT/'candidate.json'),production_enabled=False))


def action_difference(a,b):
    assert a['iteration']==b['iteration'] and len(a['rows'])==len(b['rows']) and a['rows']
    maximum=0.;values=0
    import math
    for x,y in zip(a['rows'],b['rows']):
        assert x['node']==y['node'] and x['actor']==y['actor'] and x['actions']==y['actions'] and len(x['hands'])==len(y['hands'])
        for h,j in zip(x['hands'],y['hands']):
            assert h['class_index']==j['class_index'] and h['actor_reach']==j['actor_reach'] and h['average_probabilities']==j['average_probabilities']
            av=h['action_values_counterfactual_bb'];bv=j['action_values_counterfactual_bb']
            assert len(av)==len(bv)
            for left,right in zip(av,bv):
                assert math.isfinite(left) and math.isfinite(right)
                maximum=max(maximum,abs(left-right));values+=1
    assert values>0
    return dict(max_action_difference_bb=maximum,values=values,passed=maximum<=2e-6)


def oracle():
    rows=[]
    for arm in ['original','double']:
        folder=OUT/('oracle-'+arm);folder.mkdir(exist_ok=True)
        for variant,kernel in [('validated',pair.double.OUT/'warp/interface.cu'),('candidate',OUT/'double/interface.cu')]:
            output=folder/(variant+'.json')
            if not output.exists():
                idle();runtime.command(['evaluate',pair.OUT/f'repeat-0/{arm}/policy.gtop',output,'candidate',kernel],folder/(variant+'.log'))
        result=action_difference(study.read(folder/'validated.json'),study.read(folder/'candidate.json'))
        result['policy']=arm;rows.append(result)
        study.night.dump(folder/'comparison.json',result)
        assert result['passed'],'Full-precision action-value tolerance failed'
    study.freeze(OUT/'oracle-check.json',dict(passed=True,comparisons=rows,source_oracle_sha256=study.pilot.sha(pair.OUT/'oracle-check.json'),production_enabled=False))


def benchmark():
    assert study.read(OUT/'oracle-check.json')['passed']
    source=study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop';rows=[]
    for repeat,order in enumerate([['original','candidate'],['candidate','original'],['original','candidate']]):
        for arm in order:
            folder=OUT/f'repeat-{repeat}'/arm;folder.mkdir(parents=True,exist_ok=True);path=folder/'iteration-150.json'
            if not path.exists():
                idle();runtime.command(['solve',source,folder,arm,100,OUT/'double/interface.cu'],folder/'run.log',optimized=arm=='candidate',warm=50)
            result=study.read(path)
            assert result['iteration']==150 and result['start_iteration']==result['warmup_iterations']==50
            rows.append(dict(repeat=repeat,arm=arm,seconds_per_iteration=result['learning_seconds']/100,
                setup_seconds=result['setup_seconds'],total_seconds=result['total_seconds'],sha256=study.pilot.sha(path)))
        root=OUT/f'repeat-{repeat}'
        check=pair.double.warp.saves.compare(runtime.OUT/f'repeat-{repeat}/original/policy.gtop',root/'original/policy.gtop')
        study.night.dump(root/'original-state-parity.json',check);assert check['all_numeric_entries_equal']
        if repeat:
            check=pair.double.warp.saves.compare(OUT/'repeat-0/candidate/policy.gtop',root/'candidate/policy.gtop')
            study.night.dump(root/'candidate-repeat-parity.json',check);assert check['all_numeric_entries_equal']
        print('N20 repeat',repeat+1,'passed',flush=True)
    medians={a:statistics.median(r['seconds_per_iteration'] for r in rows if r['arm']==a) for a in ['original','candidate']}
    study.night.dump(OUT/'timing.json',dict(repeats=rows,median_seconds_per_iteration=medians,variant='double',
        overhead_vs_original=medians['candidate']/medians['original']-1,
        within_runtime_target=medians['candidate']<=1.1*medians['original'],production_enabled=False))


def run():
    prepare()
    try:
        state('oracle');oracle()
        state('benchmark');benchmark()
        if not study.read(OUT/'timing.json')['within_runtime_target']:
            state('runtime_target_missed');return
        if (runtime.guard.DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()<3600:
            state('insufficient_time_for_policy_transfer');return
        state('policy_transfer')
        with (OUT/'policy-transfer.log').open('a') as log:
            subprocess.run([sys.executable,str(study.ROOT/'tools/research/continuation_policy_transfer_optimized.py'),'run','N20'],cwd=study.ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        result=study.read(BASE/'policy-transfer-optimized-20260916/N20/evaluation.json')
        state('checks_complete',transfer_accuracy_passed=result['accuracy_screen_passed'])
    except Exception as error:
        state('failed',error=str(error));raise


if __name__=='__main__':
    assert sys.argv[1:]==['run']
    run()
