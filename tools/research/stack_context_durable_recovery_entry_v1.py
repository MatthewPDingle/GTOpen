"""Demand-started Windows task: recover once, then run the unchanged trainer once.

No trigger, self-restart, scientific retry or production access is added.
Windows Task Scheduler owns this process, independently of Codex's job tree.
"""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
import hashlib
import json
import subprocess
import time
import traceback
import psutil

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-context-durable-recovery-entry-v1'


def save(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    admission=OUT/(NAME+'-admission.json');spec=json.loads(admission.read_bytes())
    for p,h in spec['inputs'].items():assert sha(Path(p))==h,p
    attempt=OUT/(NAME+'-attempt.json');result=OUT/(NAME+'-result.json')
    assert not attempt.exists() and not result.exists()
    save(attempt,dict(pid=os.getpid(),created=psutil.Process().create_time(),unix=time.time(),
        admission_sha256=sha(admission),parents=[dict(pid=p.pid,name=p.name()) for p in psutil.Process().parents()]))
    phases=[]
    try:
        for phase,script,args in (
            ('recovery','stack_context_interrupted_cycle_recovery_v1.py',[]),
            ('parallel-training','stack_context_parallel_continuation_v2.py',['--run'])):
            with (OUT/(NAME+'-'+phase+'-stdout.log')).open('x',encoding='utf-8') as stdout,\
                 (OUT/(NAME+'-'+phase+'-stderr.log')).open('x',encoding='utf-8') as stderr:
                child=subprocess.Popen(['C:/Program Files/Python312/python.exe','-B',str(ROOT/'tools/research'/script),*args],
                    cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
                record=dict(phase=phase,pid=child.pid,created=psutil.Process(child.pid).create_time(),unix=time.time())
                save(OUT/(NAME+'-'+phase+'-started.json'),record)
                code=child.wait();record.update(exit_code=code,finished_unix=time.time());phases.append(record)
                assert code==0,phase+' failed; evidence retained and no retry'
            if phase=='recovery':
                proof=json.loads((OUT/'stack-context-interrupted-cycle-recovery-v1-result.json').read_bytes())
                assert proof['complete'] and proof['passed'] and proof['original_parallel_v2_compatible']
                assert not (ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock').exists()
        save(result,dict(complete=True,unix=time.time(),phases=phases,
            note='Inspect trainer terminal status: a deferred admission or complete-boundary stop is not full study completion.',
            automatic_retry=False,production_modified=False))
    except BaseException as e:
        save(OUT/(NAME+'-failure.json'),dict(error=repr(e),traceback=traceback.format_exc(),phases=phases,automatic_retry=False))
        raise


if __name__=='__main__':main()
