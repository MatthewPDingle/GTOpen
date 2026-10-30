"""Observe recovery jobs, then own the unchanged complete-policy comparison.

Borrowed training/audit processes are never terminated by this supervisor.
Once training completes, its full audit can overlap the first trial's audit.
"""
import os
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from hu_paired_continuation_support_20260925 import LOCK,OTHER

PREFIX='later-action-recovered-pipeline-v1'
FIRST='later-action-first-audit-recovery-v1'
SECOND='later-action-replication-volume-continuation-v1'


def audit_finished(prefix):
    rp,pp,rr,ap=[OUT/f'{prefix}-{s}.json' for s in ('registration','result','readback-registration','independent-review')]
    result,audit=read(pp),read(ap)
    assert result['passed'] and result['terminal'] and result['completed_iterations']==78
    assert audit['passed'] and audit['completed_updates']==78
    assert result['registration_sha256']==audit['source_registration_sha256']==sha(rp)
    assert audit['source_result_sha256']==sha(pp) and audit['readback_registration_sha256']==sha(rr)


def main():
    assert sys.argv[1:]==['--run'] and idle() and not OTHER.exists()
    adm=read(OUT/f'{SECOND}-admission.json')
    gpu=psutil.Process(adm['controller_pid'])
    assert any(Path(s).name=='hu_later_action_volume_continuation_20260925_v2.py' for s in gpu.cmdline())
    assert LOCK.read_text().strip()==str(gpu.pid)
    readers=[]
    for p in psutil.process_iter(['cmdline']):
        if any(Path(s).name=='hu_later_action_first_audit_recovery_20260925.py' for s in (p.info['cmdline'] or [])):
            readers.append(p)
    assert len(readers)==1;first=readers[0]
    borrowed=[dict(pid=p.pid,create_time=p.create_time(),command=p.cmdline()) for p in (gpu,first)]
    for mode in ('control','study'):
        assert not (OUT/f'later-action-recovered-evaluation-{mode}-v1-registration.json').exists()
    inputs={str(p):sha(p) for p in (ROOT/'tools/research').glob('*.py')}
    for p in (OUT/'LATER-ACTION-RECOVERED-EVALUATION-ROUTING.md',
              OUT/'LATER-ACTION-RECOVERY-AUDIT-OVERLAP.md',OUT/f'{SECOND}-registration.json'):
        inputs[str(p)]=sha(p)
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,borrowed_processes=borrowed,automatic_retry=False,
        borrowed_processes_owned=False,production_modified=False,maximum_seconds=115200,
        stages=['observe-GPU-recovery','replication-full-audit + first-audit',
                'evaluation-control','control-audit','heldout-study','study-audit'],
        scope='Recovered input identities and storage location only. Preserve full trials, fixed fresh deals and one-look analysis.'))
    started=time.monotonic();stage='observe-GPU-recovery';error=None;children=[];records=[]
    def guard():
        assert idle() and not OTHER.exists() and psutil.virtual_memory().available>20_000_000_000
        assert time.monotonic()-started<115200
    def verify():
        for p,h in inputs.items():assert sha(p)==h,p
    def status(state):
        path=OUT/f'{PREFIX}-status.json';tmp=path.with_suffix('.tmp')
        save(tmp,dict(state=state,stage=stage,controller_pid=os.getpid(),borrowed_processes=borrowed,
            children=[dict(stage=c['name'],pid=c['process'].pid,exit_code=c['process'].poll()) for c in children],
            error=error,records=records,seconds=time.monotonic()-started,production_modified=False))
        tmp.replace(path)
    def observe(process,identity):
        last=0.
        while process.is_running():
            guard();assert process.create_time()==identity['create_time']
            if time.monotonic()-last>30:status('running');last=time.monotonic()
            time.sleep(2)
    def launch(name,program,args,deadline):
        guard();verify()
        env=os.environ.copy();env.update(PYTHONUNBUFFERED='1',OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
        with (OUT/f'{PREFIX}-{name}.log').open('x') as log:
            process=subprocess.Popen([sys.executable,str(ROOT/'tools/research'/program),*args],cwd=ROOT,
                env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        child=dict(name=name,process=process,started=time.monotonic(),deadline=deadline)
        children.append(child);status('running');return child
    def monitor(child):
        last=0.
        while child['process'].poll() is None:
            guard();assert time.monotonic()-child['started']<child['deadline']
            if time.monotonic()-last>30:status('running');last=time.monotonic()
            time.sleep(2)
        assert child['process'].returncode==0,child['name']+' failed; no automatic retry'
        records.append(dict(stage=child['name'],seconds=time.monotonic()-child['started'],exit_code=0))
    try:
        status('running');observe(gpu,borrowed[0])
        terminal=read(OUT/f'{SECOND}-status.json');done=read(OUT/f'{SECOND}-result.json')
        assert terminal['state']=='complete' and terminal['error'] is None and terminal['exit_code']==0
        assert done['passed'] and done['terminal'] and done['completed_iterations']==78
        assert read(OUT/f'{SECOND}-prefix-audit-admission.json')['passed']
        assert not LOCK.exists()
        stage='replication-full-audit + first-audit'
        child=launch('replication-full-audit','hu_later_action_segmented_review_20260925.py',['--run'],7500)
        monitor(child);audit_finished(SECOND)
        observe(first,borrowed[1]);audit_finished(FIRST)
        for mode in ('control','study'):
            stage='evaluation-'+mode;prefix=f'later-action-recovered-evaluation-{mode}-v1'
            child=launch(stage,'hu_later_action_recovered_evaluation_20260925.py',['--'+mode],15000 if mode=='control' else 22800)
            monitor(child)
            assert read(OUT/f'{prefix}-status.json')['state']=='complete'
            result=read(OUT/f'{prefix}-result.json');assert result['passed'] and result['complete']
            stage=mode+'-audit'
            child=launch(stage,'hu_later_action_recovered_evaluation_review_20260925.py',[mode],7500)
            monitor(child);audit=read(OUT/f'{prefix}-independent-review.json')
            assert audit['passed'] and audit['source_result_sha256']==sha(OUT/f'{prefix}-result.json')
        verify()
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),stages=records,
            seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False,
            scope='Scheduled recovered trial and evaluation gates complete; scientific interpretation remains separate. No automatic deployment.'))
    except BaseException as exc:error=repr(exc);raise
    finally:
        for child in children:
            process=child['process']
            if process.poll() is None:
                try:
                    descendants=psutil.Process(process.pid).children(recursive=True)
                    for p in reversed(descendants):
                        try:p.terminate()
                        except psutil.NoSuchProcess:pass
                    psutil.wait_procs(descendants,timeout=10);process.terminate();process.wait(timeout=20)
                except psutil.NoSuchProcess:pass
            if LOCK.exists() and LOCK.read_text().strip()==str(process.pid):
                assert process.poll() is not None;LOCK.unlink()
        status('stopped' if error else 'complete')


if __name__=='__main__':main()
