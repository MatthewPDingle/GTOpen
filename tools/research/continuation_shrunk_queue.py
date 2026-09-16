"""Wait for the current research queue, then evaluate the frozen N15 model."""
import datetime as dt
import json
import msvcrt
import os
import subprocess
import sys
import time
import continuation_night_queue as previous

study=previous.study
OUT=previous.BASE/'shrunk-residual-20260916'


def dependency_alive(snapshot,pid):
    rows=[p for p in snapshot if p['ProcessId']==pid]
    if not rows:return False
    assert len(rows)==1
    p=rows[0]
    assert p['Name'].lower() in ['python.exe','pythonw.exe'] and 'continuation_night_queue.py' in (p['CommandLine'] or '').lower(),'Dependency PID has changed identity'
    return True


def state(stage,**fields):
    result=dict(stage=stage,controller_pid=os.getpid(),updated=study.night.now(),production_enabled=False,**fields)
    path=OUT/'queue-status.json';temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');temp.replace(path)
    print(stage,fields,flush=True)


def run(pid):
    with (OUT/'queue.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            assert study.read(OUT/'training-screen.json')['eligible']
            assert study.pilot.sha(OUT/'candidate.json')==study.read(OUT/'evaluation-registration.json')['candidate_sha256']
            while dependency_alive(previous.processes(),pid):
                if dt.datetime.now(dt.timezone.utc)>=previous.bridge.DEADLINE:
                    state('deadline_checkpoint');return
                state('waiting_for_prior_queue',dependency_pid=pid);time.sleep(30)
            assert study.read(previous.OUT/'queue-status.json')['stage']=='queued_checks_complete','Previous queue did not complete successfully'
            if dt.datetime.now(dt.timezone.utc)>=previous.bridge.DEADLINE:
                state('deadline_checkpoint');return
            if not (OUT/'evaluation.json').exists():
                with (OUT/'queue-evaluation.log').open('a') as log:
                    child=subprocess.Popen([sys.executable,str(study.ROOT/'tools/research/continuation_shrunk_evaluation.py'),'run'],
                        cwd=study.ROOT,stdout=log,stderr=subprocess.STDOUT)
                    state('prospective_evaluation',active_child_pid=child.pid)
                    code=child.wait()
                assert code==0,f'N15 evaluation exited {code}; inspect its log before retrying'
            result=study.read(OUT/'evaluation.json')
            state('checks_complete',accuracy_screen_passed=result['accuracy_screen_passed'],
                note='No deployment or goal completion. Review and qualified GPU implementation/runtime checks remain.')
        except Exception as error:
            state('failed',error=str(error));raise
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':run(int(sys.argv[1]))
