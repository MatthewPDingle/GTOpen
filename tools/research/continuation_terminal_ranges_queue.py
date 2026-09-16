"""Defer N37 build and read-only scan until the final GPU queue exits."""
import datetime as dt
import os
import subprocess
import sys
import time
import continuation_terminal_ranges as scan
import continuation_paired_blend_gpu as gpu

OUT=scan.OUT
DEADLINE=dt.datetime(2026,9,16,20,49,2,tzinfo=dt.timezone.utc)


def state(stage,**kw):
    scan.old.write(OUT/'queue-status.json',dict(stage=stage,pid=os.getpid(),updated=dt.datetime.now(dt.timezone.utc).isoformat(),production_enabled=False,**kw))
    print(stage,kw,flush=True)


def run():
    assert not (OUT/'queue-status.json').exists()
    scan.prepare()
    paths=[scan.ROOT/'crates/solver/Cargo.toml',scan.ROOT/'tools/research/continuation_terminal_ranges_queue.py',OUT/'input-freeze.json']
    scan.old.write(OUT/'build-input-freeze.json',dict(inputs={str(p.relative_to(scan.ROOT)).replace('\\','/'):scan.old.sha(p) for p in paths}))
    state('waiting_for_final_GPU_queue')
    while True:
        remaining=(DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()
        if remaining<300:state('deferred_deadline');return
        live=[p for p in gpu.control.transfer.original.queue.processes() if p['ProcessId']==45132]
        if not live:break
        assert 'continuation_final_night_queue.py' in (live[0]['CommandLine'] or '')
        time.sleep(10)
    end=scan.old.read(gpu.BASE/'final-queue-20260916/status.json')['stage']
    if end not in ['N35_gate_failed','complete','N36_deferred_deadline','deferred_N35_deadline']:
        state('deferred_final_queue_failure',final_stage=end);return
    gpu.control.idle()
    state('building_and_testing')
    with (OUT/'build.log').open('w',encoding='utf-8') as log:
        for cmd in ['test','build']:
            subprocess.run(['cargo',cmd,'--release','-p','solver','--features','preflop-research','--example','continuation_terminal_ranges','--target-dir','target/learned-interface-filtered','-j2'],cwd=scan.ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    if (DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()<180:state('deferred_after_build');return
    state('scanning')
    scan.run()
    state('complete')


if __name__=='__main__':
    try:run()
    except Exception as error:
        state('failed',error=str(error));raise
