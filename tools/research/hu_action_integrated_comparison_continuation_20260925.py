"""Wait for the live matched sequence; run the predeclared comparisons once.

Never restarts or interrupts the watched training controller. No checkpoint
selection, wider-response evaluation, or production deployment is performed.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle

PREFIX='action-integrated-comparison-continuation-v1'
WATCH='action-integrated-matched-sequence-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def identity(pid):
    p=psutil.Process(pid)
    return dict(pid=pid,created=p.create_time(),command=p.cmdline())


def alive(wanted):
    try:return identity(wanted['pid'])==wanted
    except psutil.NoSuchProcess:return False


def verify(inputs):
    for p,h in inputs.items():assert sha(p)==h,p


def main():
    assert sys.argv[1:]==['--run']
    rp=OUT/f'{PREFIX}-registration.json'
    assert not rp.exists(), 'Preserve earlier continuation attempts'
    wrp=OUT/f'{WATCH}-registration.json';wsp=OUT/f'{WATCH}-status.json'
    watched_reg,state=read(wrp),read(wsp)
    watched_hash=sha(wrp)
    assert state['state']=='running'
    watched=identity(state['controller_pid'])
    assert '--run' in watched['command']
    assert any(Path(p).name=='hu_action_integrated_matched_sequence_20260925.py' for p in watched['command'])
    assert alive(watched)
    stages=[]
    for trial in ('first','replication'):
        stages.extend([(trial+'-endpoint','hu_action_integrated_exact_20260925.py',[trial],1320),
                       (trial+'-endpoint-readback','hu_action_integrated_exact_review_20260925.py',[trial],1320)])
    stages.append(('complete-class-comparison','hu_action_integrated_seed_comparison_20260925.py',[],120))
    paths=[Path(__file__).resolve(),wrp,OUT/'ACTION-INTEGRATED-ENDPOINT-COMPARISON-PLAN.md']
    paths.extend(ROOT/'tools/research'/script for _,script,_,_ in stages)
    inputs={**watched_reg['inputs'],**{str(p):sha(p) for p in paths}}
    verify(inputs)
    wait_deadline=watched['created']+sum(stage[4] for stage in watched_reg['stages'])+600
    save(rp,dict(inputs=inputs,watched_controller=watched,watched_registration_sha256=watched_hash,
        wait_deadline_epoch_seconds=wait_deadline,stages=stages,automatic_retry=False,
        production_modified=False,accuracy_qualified=False,
        scope='Run already specified endpoints, their independent readers and full class comparisons after both training audits. No wider study or deployment.'))
    started=time.monotonic();records=[];current='waiting-for-matched-training';child=None
    owned_lock=False;error=None
    def status(state,**extra):
        path=OUT/f'{PREFIX}-status.json';tmp=path.with_suffix('.tmp')
        save(tmp,dict(state=state,controller_pid=os.getpid(),stage=current,stages=records,
            worker_pid=child.pid if child else None,watched_pid=watched['pid'],
            seconds=time.monotonic()-started,production_modified=False,**extra))
        tmp.replace(path)
    status('running')
    try:
        last_status=0.
        while alive(watched):
            assert time.time()<wait_deadline,'Watched sequence exceeded its combined budgets'
            assert sha(wrp)==watched_hash
            if time.monotonic()-last_status>30:
                progress=read(wsp)
                status('running',watched_stage=progress['stage'],
                    completed_training_updates=progress.get('completed_training_updates'))
                last_status=time.monotonic()
            time.sleep(5)
        terminal=read(wsp);completed=read(OUT/f'{WATCH}-result.json')
        assert terminal['state']=='complete' and terminal['error'] is None
        assert completed['passed'] and completed['registration_sha256']==sha(wrp)
        assert len(completed['stages'])==4 and all(r['exit_code']==0 for r in completed['stages'])
        assert [r['stage'] for r in completed['stages']]==[
            'first-training','first-readback','replication-training','replication-readback']
        records.append(dict(stage='matched-training-and-audits',result_sha256=sha(OUT/f'{WATCH}-result.json')))
        for name,script,args,deadline in stages:
            current=name;verify(inputs)
            assert idle() and not LOCK.exists() and not OTHER.exists()
            if name.endswith('readback') or name=='complete-class-comparison':
                with LOCK.open('x') as stream:stream.write(str(os.getpid()))
                owned_lock=True
                assert not OTHER.exists()
            before=time.monotonic()
            env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',
                CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONUNBUFFERED='1')
            with (OUT/f'{PREFIX}-{name}.log').open('x') as log:
                child=subprocess.Popen([sys.executable,str(ROOT/'tools/research'/script),*args],
                    cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                status('running')
                while child.poll() is None:
                    assert time.monotonic()-before<deadline,name+' deadline'
                    assert idle() and not OTHER.exists()
                    try:child.wait(timeout=5)
                    except subprocess.TimeoutExpired:pass
            assert child.returncode==0,f'{name} exit {child.returncode}; preserve log'
            if name=='complete-class-comparison':
                output=OUT/'action-integrated-seed-comparison-v1-result.json'
            else:
                suffix='independent-review' if name.endswith('readback') else 'result'
                output=OUT/f'action-integrated-{args[0]}-exact-v1-{suffix}.json'
            result=read(output);assert result['passed']
            records.append(dict(stage=name,exit_code=0,seconds=time.monotonic()-before,
                result=str(output),sha256=sha(output)))
            if owned_lock:
                assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink();owned_lock=False
            print(json.dumps(records[-1]),flush=True)
        verify(inputs)
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
            stages=records,seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False,
            next_step='Interpret all complete-class comparisons and conflicting results. Broader call/raise evaluation needs a separate protocol.'))
    except BaseException as exc:
        error=repr(exc);raise
    finally:
        # The watched sequence is never a child of this controller and is never stopped here.
        if child is not None and child.poll() is None:
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
            if LOCK.read_text().strip()==str(child.pid):LOCK.unlink()
        status('stopped' if error else 'complete',error=error)


if __name__=='__main__':main()
