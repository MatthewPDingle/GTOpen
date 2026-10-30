"""Own future study stages; observe but never stop the already-running first trial.

Overlap its CPU audit with the independent GPU replication. Both audits gate
the unchanged fixed-profile evaluation. Stop on failure, without retries.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle

PREFIX='later-action-pipeline-v1'
FIRST='later-action-matched-first-v1'
SECOND='later-action-matched-replication-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
PROGRAMS={
    'replication':ROOT/'tools/research/hu_later_action_replication_concurrent_20260925.py',
    'training-review':ROOT/'tools/research/hu_later_action_training_review_20260925.py',
    'evaluation':ROOT/'tools/research/hu_later_action_complete_evaluation_20260925.py',
    'evaluation-review':ROOT/'tools/research/hu_later_action_complete_review_20260925.py'}


def training_finished(prefix):
    status=read(OUT/f'{prefix}-status.json');result=read(OUT/f'{prefix}-result.json')
    assert status['state']=='complete' and status['error'] is None and status['exit_code']==0
    assert result['passed'] and result['terminal'] and result['completed_iterations']==78
    assert result['registration_sha256']==sha(OUT/f'{prefix}-registration.json')
    return result


def audit_finished(prefix):
    audit=read(OUT/f'{prefix}-independent-review.json')
    assert audit['passed'] and audit['completed_updates']==78
    assert audit['source_result_sha256']==sha(OUT/f'{prefix}-result.json')
    assert audit['source_registration_sha256']==sha(OUT/f'{prefix}-registration.json')
    assert audit['readback_registration_sha256']==sha(OUT/f'{prefix}-readback-registration.json')


def main():
    assert sys.argv[1:]==['--run'] and idle() and not OTHER.exists()
    first_status=read(OUT/f'{FIRST}-status.json')
    assert first_status['state']=='running'
    borrowed=psutil.Process(first_status['controller_pid'])
    command=borrowed.cmdline();birth=borrowed.create_time()
    assert any(Path(s).name=='hu_later_action_matched_trial_20260925.py' for s in command)
    assert command[-2:]==['--run','first'] and LOCK.read_text().strip()==str(borrowed.pid)
    for prefix in (FIRST,SECOND):
        assert not (OUT/f'{prefix}-readback-registration.json').exists()
    assert not (OUT/f'{SECOND}-registration.json').exists()
    inputs={str(p):sha(p) for p in (ROOT/'tools/research').glob('*.py')}
    for p in (OUT/'LATER-ACTION-CONCURRENT-AUDIT-AMENDMENT.md',
              OUT/'LATER-ACTION-COMPARISON-OPERATIONS.md',OUT/f'{FIRST}-registration.json'):
        inputs[str(p)]=sha(p)
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,observed_first_controller=dict(pid=borrowed.pid,create_time=birth,command=command),
        stages=['observe-first','first-audit + GPU-replication','replication-audit',
                'evaluation-control','control-audit','heldout-study','study-audit'],
        initial_trainer_owned=False,automatic_retry=False,production_modified=False,
        scope='Scheduling only. No change to training/evaluation counts, seeds, algorithms, limits or conclusions.'))
    started=time.monotonic();records=[];children=[];stage='observe-first';error=None

    def status(state):
        p=OUT/f'{PREFIX}-status.json';tmp=p.with_suffix('.tmp')
        save(tmp,dict(state=state,stage=stage,controller_pid=os.getpid(),
            children=[dict(stage=c['name'],pid=c['process'].pid,exit_code=c['process'].poll()) for c in children],
            records=records,error=error,seconds=time.monotonic()-started,production_modified=False))
        tmp.replace(p)

    def verify_sources():
        for p,h in inputs.items():assert sha(p)==h,p

    def guard():
        assert idle() and not OTHER.exists(),'Production or other research activity'
        assert psutil.virtual_memory().available>20_000_000_000
        assert time.monotonic()-started<115200,'Overall sequence deadline'

    def launch(name,program,args,deadline):
        guard();verify_sources()
        env=os.environ.copy();env.update(PYTHONUNBUFFERED='1',OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
        log=(OUT/f'{PREFIX}-{name}.log').open('x')
        try:
            process=subprocess.Popen([sys.executable,str(program),*args],cwd=ROOT,env=env,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        finally:log.close()
        child=dict(name=name,process=process,started=time.monotonic(),deadline=deadline,recorded=False)
        children.append(child);status('running');return child

    def monitor(group):
        last=0.
        while True:
            guard();live=False
            for c in group:
                code=c['process'].poll()
                if code is None:
                    assert time.monotonic()-c['started']<c['deadline'],c['name']+' deadline'
                    live=True
                else:
                    assert code==0,c['name']+' failed; preserve evidence, no automatic retry'
                    if not c['recorded']:
                        records.append(dict(stage=c['name'],exit_code=code,seconds=time.monotonic()-c['started']))
                        c['recorded']=True
            if not live:break
            if time.monotonic()-last>30:status('running');last=time.monotonic()
            time.sleep(2)
        status('running')

    try:
        status('running');last=0.
        while borrowed.is_running():
            guard();assert borrowed.create_time()==birth
            assert time.monotonic()-started<22800,'First training observation deadline'
            if time.monotonic()-last>30:status('running');last=time.monotonic()
            time.sleep(2)
        training_finished(FIRST);assert not LOCK.exists();verify_sources()
        stage='first-audit + GPU-replication'
        # One CPU-only reader and one GPU owner, with separate output stores.
        replica=launch('replication',PROGRAMS['replication'],['--run','replication'],22800)
        audit=launch('first-audit',PROGRAMS['training-review'],['--prefix',FIRST],7500)
        monitor([replica,audit]);training_finished(SECOND);audit_finished(FIRST)
        assert not LOCK.exists()
        stage='replication-audit'
        audit=launch(stage,PROGRAMS['training-review'],['--prefix',SECOND],7500)
        monitor([audit]);audit_finished(SECOND)
        for mode in ('control','study'):
            prefix=f'later-action-complete-evaluation-{mode}-v1'
            stage='evaluation-'+mode
            child=launch(stage,PROGRAMS['evaluation'],['--'+mode],15000 if mode=='control' else 22800)
            monitor([child]);assert read(OUT/f'{prefix}-status.json')['state']=='complete'
            result=read(OUT/f'{prefix}-result.json');assert result['passed'] and result['complete']
            stage=mode+'-audit'
            child=launch(stage,PROGRAMS['evaluation-review'],[mode],7500)
            monitor([child]);review=read(OUT/f'{prefix}-independent-review.json')
            assert review['passed'] and review['source_result_sha256']==sha(OUT/f'{prefix}-result.json')
        verify_sources()
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),stages=records,
            seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False,
            scope='All scheduled training/audit/evaluation stages complete. Interpret scientific outcomes separately; no automatic deployment.'))
    except BaseException as exc:
        error=repr(exc);raise
    finally:
        # The initial trainer is borrowed, absent from children, and never killed.
        for child in children:
            process=child['process']
            if process.poll() is None:
                try:
                    descendants=psutil.Process(process.pid).children(recursive=True)
                    for p in reversed(descendants):
                        try:p.terminate()
                        except psutil.NoSuchProcess:pass
                    psutil.wait_procs(descendants,timeout=10)
                    process.terminate();process.wait(timeout=20)
                except psutil.NoSuchProcess:pass
            if LOCK.exists() and LOCK.read_text().strip()==str(process.pid):
                assert process.poll() is not None
                LOCK.unlink()
        status('stopped' if error else 'complete')


if __name__=='__main__':main()
