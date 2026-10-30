"""Run the two predeclared matched trials and their full audits, once, in order.

No retries, checkpoint choice, wider evaluation, or production deployment.
Each training controller independently remeasures global storage before launch.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from reboot_research_idle_v1 import idle

PREFIX='action-integrated-matched-sequence-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
TRAINER=ROOT/'tools/research/hu_action_integrated_matched_trial_20260925.py'
READER=ROOT/'tools/research/hu_action_integrated_trial_review_20260925.py'


def main():
    assert sys.argv[1:]==['--run'] and idle()
    assert not LOCK.exists() and not OTHER.exists()
    registration=OUT/f'{PREFIX}-registration.json'
    assert not registration.exists(), 'Preserve earlier attempts'
    control='action-integrated-joint-gpu-control-v1'
    cp=OUT/f'{control}-independent-review.json'
    assert read(cp)['passed'] and read(cp)['completed_updates']==2
    paths=[Path(__file__).resolve(),TRAINER,READER,cp,
        ROOT/'tools/research/hu_action_integrated_fresh_review_20260925.py',
        OUT/'ROOT-ACTION-INTEGRATED-TRAINING-PLAN.md',
        OUT/'ACTION-INTEGRATED-TRAINING-OPERATIONS.md']
    inputs={str(p):sha(p) for p in paths}
    stages=[]
    for trial in ('first','replication'):
        stages.extend([(trial,'training',str(TRAINER),['--run',trial],22800),
                       (trial,'readback',str(READER),[trial],7320)])
    save(registration,dict(inputs=inputs,stages=stages,production_modified=False,
        automatic_retry=False,checkpoint_selection=False,
        scope='Both predeclared matched training trials and independent readbacks only. No strength claim.'))
    started=time.monotonic();records=[];child=None;error=None;owned_lock=False;current=None
    def status(state,**extra):
        path=OUT/f'{PREFIX}-status.json';tmp=path.with_suffix('.tmp')
        save(tmp,dict(state=state,controller_pid=os.getpid(),stage=current,
            worker_pid=child.pid if child else None,stages=records,
            seconds=time.monotonic()-started,production_modified=False,**extra))
        tmp.replace(path)
    try:
        for trial,kind,program,arguments,deadline in stages:
            current=f'{trial}-{kind}'
            for p,h in inputs.items(): assert sha(p)==h,p
            assert idle() and not LOCK.exists() and not OTHER.exists()
            name='action-integrated-fresh-pilot-v1' if trial=='first' else 'action-integrated-replication-v1'
            if kind=='readback':
                terminal=read(OUT/f'{name}-status.json')
                result=read(OUT/f'{name}-result.json')
                assert terminal['state']=='complete' and terminal['error'] is None and terminal['exit_code']==0
                assert result['passed'] and result['terminal'] and result['completed_iterations']==78
                assert result['registration_sha256']==sha(OUT/f'{name}-registration.json')
                with LOCK.open('x') as stream:stream.write(str(os.getpid()))
                owned_lock=True
                assert not OTHER.exists()
            before=time.monotonic()
            env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',
                CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONUNBUFFERED='1')
            with (OUT/f'{PREFIX}-{current}.log').open('x') as log:
                child=subprocess.Popen([sys.executable,program,*arguments],cwd=ROOT,env=env,
                    stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                status('running')
                last_status=0.
                while child.poll() is None:
                    assert time.monotonic()-before<deadline, f'{current} deadline'
                    assert idle() and not OTHER.exists()
                    if time.monotonic()-last_status>30:
                        latest=Path('T:/GTOpen-research')/name/'latest.json'
                        status('running',completed_training_updates=read(latest)['completed_iterations'] if latest.exists() else 0)
                        last_status=time.monotonic()
                    try:child.wait(timeout=5)
                    except subprocess.TimeoutExpired:pass
            assert child.returncode==0,f'{current} exit {child.returncode}; preserve log'
            path=OUT/f'{name}-result.json'
            if kind=='readback':
                path=OUT/f'{name}-independent-review.json';review=read(path)
                assert review['passed'] and review['completed_updates']==78
                assert review['source_result_sha256']==sha(OUT/f'{name}-result.json')
                assert LOCK.read_text().strip()==str(os.getpid())
                LOCK.unlink();owned_lock=False
            records.append(dict(stage=current,seconds=time.monotonic()-before,
                exit_code=child.returncode,result=str(path),sha256=sha(path)))
            print(json.dumps(records[-1]),flush=True)
        for p,h in inputs.items():assert sha(p)==h,p
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(registration),
            stages=records,seconds=time.monotonic()-started,accuracy_qualified=False,production_modified=False))
    except BaseException as exc:
        error=repr(exc);raise
    finally:
        if child is not None and child.poll() is None:
            # Stop only this controller's known child tree, never a production PID.
            try:
                descendants=psutil.Process(child.pid).children(recursive=True)
                for p in reversed(descendants):
                    try:p.terminate()
                    except psutil.NoSuchProcess:pass
                psutil.wait_procs(descendants,timeout=10)
                child.terminate();child.wait(timeout=20)
            except psutil.NoSuchProcess:pass
        if owned_lock:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
        elif child is not None and child.poll() is not None and LOCK.exists():
            # A terminated training controller may not execute its Python finally.
            if LOCK.read_text().strip()==str(child.pid):LOCK.unlink()
        status('stopped' if error else 'complete',error=error)


if __name__=='__main__':main()
