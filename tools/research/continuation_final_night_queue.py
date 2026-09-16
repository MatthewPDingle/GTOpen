"""Finish registered diagnostics sequentially within the original night deadline."""
import datetime as dt
import os
from pathlib import Path
import subprocess
import sys
import time
import continuation_paired_blend_gpu as gpu

study=gpu.study
OUT=gpu.BASE/'final-queue-20260916'
N32_PID=11368

def remaining():return (gpu.control.transfer.original.bridge.DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()
def state(stage,**kwargs):
    study.night.dump(OUT/'status.json',dict(stage=stage,pid=os.getpid(),updated=study.night.now(),production_enabled=False,**kwargs));print(stage,kwargs,flush=True)

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'status.json').exists(),'Queue already started; inspect it before any restart'
    paths=[Path(__file__),study.ROOT/'tools/research/continuation_paired_blend_gpu.py',study.ROOT/'tools/research/continuation_paired_blend_prospective.py',
           gpu.OUT/'protocol-freeze.json',gpu.BASE/'paired-blend-prospective-20260916/implementation-freeze.json']
    study.freeze(OUT/'input-freeze.json',dict(inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},
                 registered_at=study.night.now(),wait_for_pid=N32_PID,deadline='2026-09-16T20:49:02+00:00',production_enabled=False))
    state('waiting_for_N32',wait_for_pid=N32_PID)
    while True:
        live=[p for p in gpu.control.transfer.original.queue.processes() if p['ProcessId']==N32_PID]
        status=study.read(gpu.BASE/'zero-fallback-20260916/status.json')
        if not live:
            assert status['stage']=='complete','N32 owner exited without completion; inspect instead of restarting'
            break
        assert 'continuation_zero_fallback.py run' in (live[0]['CommandLine'] or ''),'Owner identity changed'
        if remaining()<1800:state('deferred_N35_deadline');return
        time.sleep(10)
    if remaining()<1800:state('deferred_N35_deadline');return
    gpu.idle();state('N35_running')
    with (OUT/'N35.log').open('w',encoding='utf-8') as log:
        result=subprocess.run([sys.executable,str(study.ROOT/'tools/research/continuation_paired_blend_gpu.py'),'run'],cwd=study.ROOT,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:state('N35_failed',returncode=result.returncode);return
    result=study.read(gpu.OUT/'result.json')
    if not (result['changes']['blend']['signal_passed'] and result['desired_time_ratio_met']):
        state('N35_gate_failed',settling_signal=result['changes']['blend']['signal_passed'],time_ratio=result['learning_time_ratio']);return
    if remaining()<1200:state('N36_deferred_deadline');return
    state('N36_running')
    with (OUT/'N36.log').open('w',encoding='utf-8') as log:
        result=subprocess.run([sys.executable,str(study.ROOT/'tools/research/continuation_paired_blend_prospective.py'),'run'],cwd=study.ROOT,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:state('N36_checkpoint_or_failure',returncode=result.returncode);return
    state('complete',fresh_accuracy_passed=study.read(gpu.BASE/'paired-blend-prospective-20260916/evaluation.json')['accuracy_screen_passed'])

if __name__=='__main__':run()
