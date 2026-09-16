"""N24: same paired-card interface, unchanged ordinary continuation values."""
import datetime as dt
import math
import os
import sys
from pathlib import Path
import continuation_policy_transfer_optimized as transfer

study=transfer.study
BASE=transfer.original.BASE
OUT=BASE/'chance-control-20260916'
FULL=BASE/'full-precision-20260916'
SOURCE=FULL/'repeat-0/original/policy.gtop'
KERNEL=FULL/'double/interface.cu'


def validate(snapshot,iteration,start):
    assert snapshot['model']=='balanced'
    assert snapshot['iteration']==iteration and snapshot['start_iteration']==start and snapshot['warmup_iterations']==0
    assert all(math.isfinite(x) for x in snapshot['gaps']+snapshot['evs'])
    assert min(snapshot['gaps'])>=-1e-6 and abs(sum(snapshot['evs']))<.0002


def idle():
    transfer.adapter().require_idle()
    for p in transfer.original.queue.processes():
        if p['ProcessId']==os.getpid():continue
        command=(p['CommandLine'] or '').lower()
        if p['Name'].lower() in ['python.exe','pythonw.exe']:
            assert not any(token in command for token in ['continuation_validation_queue.py run','continuation_full_precision.py run',
                'continuation_policy_stability.py run','continuation_flop_menu.py run','continuation_chance_control.py run',
                'continuation_smooth_fit.py run','continuation_weighted_expanded.py run']),'Another research owner remains active'


def prepare():
    transfer.selection('N20')
    oracle=study.read(BASE/'pair-reductions-20260916/oracle-check.json')
    assert oracle['passed']
    balanced=[r for r in oracle['comparisons'] if r['variant']=='double' and '-balanced' in r['case']]
    assert len(balanced)==6 and max(r['max_action_change_bb'] for r in balanced)<2e-6
    assert study.pilot.sha(KERNEL)==study.pilot.sha(BASE/'pair-reductions-20260916/double/interface.cu')
    paths=[Path(__file__),OUT/'README.md',KERNEL,SOURCE,transfer.original.runtime.BIN,
        BASE/'pair-reductions-20260916/oracle-check.json',FULL/'manifest.json',
        transfer.OUT/'N20/original/iteration-500.json',transfer.OUT/'N20/candidate/iteration-500.json']
    inputs={str(p.resolve().relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths}
    inputs.update(study.read(FULL/'manifest.json')['files'])
    freeze=OUT/'protocol-freeze.json'
    if freeze.exists():assert study.read(freeze)['inputs']==inputs
    else:study.freeze(freeze,dict(registered_at=study.night.now(),inputs=inputs,production_enabled=False))


def report():
    rows=[];comparisons=[]
    for iteration in [150,500]:
        control=study.read(OUT/str(iteration)/f'iteration-{iteration}.json')
        validate(control,iteration,0 if iteration==150 else 150)
        original_path=FULL/'repeat-0/original/iteration-150.json' if iteration==150 else transfer.OUT/'N20/original/iteration-500.json'
        candidate_path=FULL/'repeat-0/candidate/iteration-150.json' if iteration==150 else transfer.OUT/'N20/candidate/iteration-500.json'
        snapshots={'ordinary':study.read(original_path),'paired_balanced':control,'learned':study.read(candidate_path)}
        assert all(r['config']==control['config'] for r in snapshots.values())
        for arm,snapshot in snapshots.items():
            rows.append(dict(iteration=iteration,arm=arm,frozen_value_gap_bb=sum(snapshot['gaps']),evs=snapshot['evs']))
        paths=[r['path'] for r in control['views']]
        assert len(paths)==17 and all([r['path'] for r in s['views']]==paths for s in snapshots.values())
        for index,path in enumerate(paths):
            views={arm:s['views'][index]['view'] for arm,s in snapshots.items()}
            actions=[a['label'] for a in views['paired_balanced']['actions']]
            assert all([a['label'] for a in v['actions']]==actions for v in views.values())
            comparisons.append(dict(iteration=iteration,path=path,actor=views['paired_balanced']['actor_pos'],actions=actions,
                frequencies={arm:[a['freq'] for a in view['actions']] for arm,view in views.items()}))
    result=dict(checked_at=study.night.now(),rows=rows,nodes=comparisons,production_enabled=False,
        caveat='Separate approximate continuation games at equal work; diagnostic only, not full-game exploitability, accuracy, repeated runtime or convergence proof.')
    result['snapshots']={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in [
        OUT/'150/iteration-150.json',OUT/'500/iteration-500.json',FULL/'repeat-0/original/iteration-150.json',
        FULL/'repeat-0/candidate/iteration-150.json',transfer.OUT/'N20/original/iteration-500.json',transfer.OUT/'N20/candidate/iteration-500.json']}
    study.night.dump(OUT/'result.json',result)
    lines=['# Paired-card control at equal work','',result['caveat'],'',
        '| Iteration | Path | Summed frozen-value gap (bb) |','|---|---|---:|']
    for row in rows:lines.append(f"| {row['iteration']} | {row['arm']} | {row['frozen_value_gap_bb']:.6f} |")
    (OUT/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    print('\n'.join(lines),flush=True)


def run():
    idle();prepare()
    if not (OUT/'150/iteration-150.json').exists():
        assert (transfer.original.bridge.DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()>=1200
    source=SOURCE
    for iteration,steps in [(150,150),(500,350)]:
        folder=OUT/str(iteration);folder.mkdir(parents=True,exist_ok=True)
        if not (folder/f'iteration-{iteration}.json').exists():
            idle()
            args=['solve',source,folder,'balanced',steps,KERNEL]
            if iteration==500:args.append('resume')
            transfer.original.runtime.command(args,folder/'run.log',optimized=True,warm=0)
        validate(study.read(folder/f'iteration-{iteration}.json'),iteration,0 if iteration==150 else 150)
        source=folder/'policy.gtop'
    report()


if __name__=='__main__':{'prepare':prepare,'run':run,'report':report}[sys.argv[1]]()
