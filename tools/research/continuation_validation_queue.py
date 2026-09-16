"""Sequence frozen N20/N19/N21 validation without overlapping GPU owners."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import datetime as dt
import msvcrt
import subprocess
import sys
import time
from pathlib import Path
import continuation_policy_transfer_optimized as transfer

study=transfer.study
BASE=transfer.original.BASE
OUT=BASE/'validation-queue-20260916'
DEADLINE=transfer.original.bridge.DEADLINE


def state(stage,**extra):
    study.night.dump(OUT/'status.json',dict(stage=stage,controller_pid=os.getpid(),updated=study.night.now(),production_enabled=False,**extra))


def enough_time(now):
    return (DEADLINE-now).total_seconds()>=5400


def qualified(status,evaluation,audit):
    return status.get('stage')=='checks_complete' and status.get('transfer_accuracy_passed') is True \
        and evaluation.get('accuracy_screen_passed') is True and audit.get('audited_references')==200 \
        and audit.get('physical_bounds_passed') is True and audit.get('all_references_after_freeze') is True


def child(label,args):
    assert dt.datetime.now(dt.timezone.utc)<DEADLINE,'Deadline reached before next validation stage'
    state(label)
    with (OUT/(label+'.log')).open('a',encoding='utf-8') as log:
        process=subprocess.Popen([sys.executable,*args],cwd=study.ROOT,stdout=log,stderr=subprocess.STDOUT)
        state(label,active_child_pid=process.pid)
        code=process.wait()
    if code:raise RuntimeError(f'{label} child {process.pid} exited {code}; inspect its log, do not restart blindly')


def run(parent):
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'run.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            while True:
                processes=transfer.original.queue.processes()
                for p in processes:
                    if p['ProcessId']==os.getpid():continue
                    command=(p['CommandLine'] or '').lower()
                    if p['Name'].lower() in ['python.exe','pythonw.exe']:
                        assert 'continuation_validation_queue.py run' not in command,'Another validation queue exists'
                owner=next((p for p in processes if p['ProcessId']==parent),None)
                if owner is None:break
                assert owner['Name'].lower()=='python.exe' and 'continuation_full_precision.py run' in (owner['CommandLine'] or '').lower(),'Parent identity changed'
                state('waiting_for_N20',parent_pid=parent)
                if dt.datetime.now(dt.timezone.utc)>=DEADLINE:
                    state('deadline_checkpoint',parent_pid=parent);return
                time.sleep(30)
            assert not any('continuation_smooth_fit.py run' in (p['CommandLine'] or '').lower() for p in transfer.original.queue.processes()),'CPU fitting must finish before timing'
            finished=study.read(BASE/'full-precision-20260916/status.json')
            assert finished['stage']=='checks_complete','N20 did not finish successfully; inspect its status'
            child('reference_audit',['tools/research/continuation_transfer_audit.py','N20'])
            child('hand_groups',['tools/research/continuation_hand_diagnostics.py','N20'])
            evaluation=study.read(transfer.OUT/'N20/evaluation.json');audit=study.read(transfer.OUT/'N20/reference-audit.json')
            if not qualified(finished,evaluation,audit):
                child('report',['tools/research/continuation_night_report.py'])
                state('qualification_failed',accuracy_passed=evaluation['accuracy_screen_passed'],physical_bounds_passed=audit['physical_bounds_passed']);return
            if enough_time(dt.datetime.now(dt.timezone.utc)):
                if not (BASE/'policy-stability-20260916/result.json').exists():
                    child('practical_stability',['tools/research/continuation_policy_stability.py','run','N20'])
            else:
                child('report',['tools/research/continuation_night_report.py'])
                state('insufficient_time_for_stability');return
            if enough_time(dt.datetime.now(dt.timezone.utc)):
                child('flop_menu',['tools/research/continuation_flop_menu.py','run'])
                menu='executed'
            else:menu='deferred_less_than_90_minutes_remain'
            child('report',['tools/research/continuation_night_report.py'])
            state('checks_complete',flop_menu=menu)
        except BaseException as error:
            state('failed',error=str(error));raise
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':
    assert len(sys.argv)==3 and sys.argv[1]=='run'
    run(int(sys.argv[2]))
