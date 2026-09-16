"""N38 fixed two-checkpoint extension, after N35 timing and N37 scans finish."""
import datetime as dt
import math
import os
from pathlib import Path
import sys
import time
import continuation_paired_blend_gpu as gpu

study=gpu.study
OUT=gpu.BASE/'blend-extension-repaired-20260916'
SOURCE=gpu.OUT/'blend/1000/policy.gtop'
DEADLINE=gpu.control.transfer.original.bridge.DEADLINE


def state(stage,**fields):
    study.night.dump(OUT/'status.json',dict(stage=stage,pid=os.getpid(),updated=study.night.now(),production_enabled=False,**fields))
    print(stage,fields,flush=True)


def prepare():
    OUT.mkdir(exist_ok=True)
    inputs=dict(study.read(gpu.OUT/'protocol-freeze.json')['inputs'])
    for p in [Path(__file__),OUT/'README.md',OUT/'REPAIR.md',OUT/'repair-inputs.json',SOURCE,gpu.OUT/'blend/750/iteration-750.json',gpu.OUT/'blend/1000/iteration-1000.json']:
        inputs[str(p.resolve().relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(p)
    for p,h in inputs.items():assert study.pilot.sha(study.ROOT/p)==h,p
    p=OUT/'protocol-freeze.json'
    if p.exists():assert study.read(p)['inputs']==inputs
    else:study.freeze(p,dict(registered_at=study.night.now(),inputs=inputs,start_iteration=1000,checkpoints=[1250,1500],
                            alpha=.25,additional_steps=500,production_enabled=False))


def run():
    prepare();assert not (OUT/'status.json').exists()
    state('waiting_for_N37')
    while True:
        remaining=(DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()
        if remaining<720:state('deferred_deadline');return
        live=[]
        for p in gpu.control.transfer.original.queue.processes():
            command=p['CommandLine'] or ''
            if p['Name'].lower() in ['learned_interface.exe','cargo.exe','rustc.exe','continuation_terminal_ranges.exe']:
                live.append(p)
            elif p['ProcessId']!=os.getpid() and p['Name'].lower() in ['python.exe','pythonw.exe'] and any(name in command for name in ['continuation_terminal_ranges_repair.py','continuation_final_night_queue.py','continuation_paired_blend_gpu.py run','continuation_paired_blend_prospective.py run','continuation_blend_extension.py run']):
                live.append(p)
        if not live:break
        time.sleep(10)
    assert study.read(gpu.BASE/'final-queue-20260916/status.json')['stage']=='N35_gate_failed','Unexpected final queue outcome'
    assert study.read(gpu.BASE/'terminal-ranges-repaired-20260916/status.json')['stage']=='complete','Inspect N37 failure; do not compete or silently skip'
    n35=study.read(gpu.OUT/'result.json')
    assert not n35['changes']['blend']['signal_passed']
    assert n35['changes']['blend']['gap_total_bb']>.005
    gpu.idle()
    previous=study.read(gpu.OUT/'blend/1000/iteration-1000.json');source=SOURCE;rows=[]
    for end in [1250,1500]:
        assert (DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()>420
        gpu.idle();state('learning',iteration=end)
        folder=OUT/str(end);folder.mkdir(exist_ok=True)
        assert not (folder/'policy.gtop').exists()
        gpu.runtime.command(['solve',source,folder,'candidate',250,gpu.NEW,'resume'],folder/'run.log',optimized=True,warm=0)
        s=study.read(folder/f'iteration-{end}.json')
        assert s['iteration']==end and s['start_iteration']==end-250 and s['warmup_iterations']==0
        assert all(math.isfinite(x) for x in s['gaps']+s['evs']) and abs(sum(s['evs']))<.0002
        r=gpu.stability.changes(previous,s)
        r.update(learning_seconds=s['learning_seconds'],snapshot_sha256=study.pilot.sha(folder/f'iteration-{end}.json'))
        rows.append(r);previous=s;source=folder/'policy.gtop'
    prepare()
    total=n35['learning_seconds']['blend']+sum(r['learning_seconds'] for r in rows)
    study.freeze(OUT/'result.json',dict(rows=rows,continued_from_N35=True,learning_seconds_since_common_500_start=total,
        N35_control_learning_seconds_to_1000=n35['learning_seconds']['control'],
        observed_work_ratio=total/n35['learning_seconds']['control'],production_enabled=False,
        caveat='Adaptive follow-up to a failed fixed screen, not a replacement gate. Same coefficients and alpha, no tuning or fresh accuracy claim. Checkpoints do not locate exact time-to-target. More work is explicitly charged; no deployment qualification.'))
    state('complete',final_gap_bb=rows[-1]['gap_total_bb'],observed_work_ratio=total/n35['learning_seconds']['control'])


if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    else:
        try:run()
        except Exception as error:
            state('failed',error=str(error));raise
