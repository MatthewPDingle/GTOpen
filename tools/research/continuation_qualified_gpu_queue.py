"""Sequence qualified N15/N17 checks after the current fresh-data evaluator."""
import datetime as dt
import json
import msvcrt
import os
import pathlib
import subprocess
import sys
import time
import continuation_night_queue as common

study=common.study
BASE=common.BASE
OUT=BASE/'qualified-gpu-queue-20260916'


def dependency_alive(snapshot,pid):
    matches=[p for p in snapshot if p['ProcessId']==pid]
    if not matches:return False
    assert len(matches)==1
    p=matches[0]
    assert p['Name'].lower() in ['python.exe','pythonw.exe'] and 'continuation_shrunk_queue.py' in (p['CommandLine'] or '').lower(), 'Dependency PID changed identity'
    return True


def state(stage,**fields):
    value=dict(stage=stage,controller_pid=os.getpid(),updated=study.night.now(),production_enabled=False,**fields)
    path=OUT/'status.json';temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n');temp.replace(path)
    print(stage,fields,flush=True)


def child(script,args,label,marker):
    if dt.datetime.now(dt.timezone.utc)>=common.bridge.DEADLINE:
        state('deadline_checkpoint');raise SystemExit(4)
    assert not study.night.live_busy(),'Live app is busy; queued GPU work deferred'
    if marker.exists():
        state('existing_result',result=str(marker.relative_to(study.ROOT)))
        return
    with (OUT/(label+'.log')).open('a') as log:
        p=subprocess.Popen([sys.executable,str(study.ROOT/'tools/research'/script),*args],cwd=study.ROOT,stdout=log,stderr=subprocess.STDOUT)
        state(label,active_child_pid=p.pid,command=script+' '+' '.join(args))
        code=p.wait()
    assert code==0,f'{label} exited {code}; inspect its log before resuming'
    assert marker.exists(),f'{label} produced no expected result'


def accuracy_ready(status,result):
    assert status['stage']=='checks_complete','Reference queue did not complete successfully'
    assert status['accuracy_screen_passed']==result['accuracy_screen_passed']
    return result['accuracy_screen_passed']


def run(pid):
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'run.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            study.freeze(OUT/'controller-freeze.json',dict(source_sha256=study.pilot.sha(pathlib.Path(__file__)),
                dependency_pid=pid,deadline_utc=common.bridge.DEADLINE.isoformat(),production_enabled=False,
                sequence=['N15 original double oracle','N17 double/mixed oracle','N17 repeated benchmark','N17 changed-policy check if runtime passes']))
            while dependency_alive(common.processes(),pid):
                if dt.datetime.now(dt.timezone.utc)>=common.bridge.DEADLINE:
                    state('deadline_checkpoint');return
                state('waiting_for_fresh_accuracy',dependency_pid=pid);time.sleep(30)
            status=study.read(BASE/'shrunk-residual-20260916/queue-status.json')
            result=study.read(BASE/'shrunk-residual-20260916/evaluation.json')
            if not accuracy_ready(status,result):
                state('rejected_accuracy_no_gpu',note='N15 failed its fixed fresh-data gate. No GPU candidates launched.');return
            child('continuation_shrunk_gpu.py',['oracle'],'n15_oracle',BASE/'shrunk-residual-gpu-20260916/oracle-check.json')
            assert study.read(BASE/'shrunk-residual-gpu-20260916/oracle-check.json')['passed']
            child('continuation_pair_reductions.py',['oracle'],'n17_oracle',BASE/'pair-reductions-20260916/oracle-check.json')
            assert study.read(BASE/'pair-reductions-20260916/oracle-check.json')['passed']
            child('continuation_pair_reductions.py',['benchmark'],'n17_benchmark',BASE/'pair-reductions-20260916/timing.json')
            timing=study.read(BASE/'pair-reductions-20260916/timing.json')
            if not timing['within_runtime_target']:
                state('runtime_target_missed',note='Review timings before selecting any further experiment; no transfer or deployment.');return
            remaining=(common.bridge.DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()
            if remaining<3600:
                state('insufficient_time_for_policy_transfer',remaining_seconds=remaining);return
            child('continuation_policy_transfer_optimized.py',['run','N17'],'n17_policy_transfer',
                BASE/'policy-transfer-optimized-20260916/N17/evaluation.json')
            transfer=study.read(BASE/'policy-transfer-optimized-20260916/N17/evaluation.json')
            state('qualified_checks_complete',transfer_accuracy_passed=transfer['accuracy_screen_passed'],
                note='Review, audit, reporting and push remain. No production deployment or goal completion.')
        except Exception as error:
            state('failed',error=str(error));raise
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':run(int(sys.argv[1]))
