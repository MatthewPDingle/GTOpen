"""Own the admitted compact study and its independent review; never retry."""
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from hu_paired_continuation_support_20260925 import LOCK,OTHER

PREFIX='later-action-compact-pipeline-v1'
STUDY='later-action-compact-evaluation-study-v1'


def main():
    assert sys.argv[1:]==['--run'] and idle() and not LOCK.exists() and not OTHER.exists()
    previous=read(OUT/'later-action-recovered-pipeline-v1-status.json')
    assert previous['state']=='stopped' and previous['stage']=='evaluation-study'
    assert not psutil.pid_exists(previous['controller_pid'])
    assert not (OUT/f'{STUDY}-registration.json').exists()
    inputs={str(p):sha(p) for p in (ROOT/'tools/research').glob('*.py')}
    for name in ('LATER-ACTION-COMPACT-STORAGE-AMENDMENT.md',
                 'later-action-recovered-pipeline-v1-status.json',
                 'later-action-recovered-pipeline-v1-evaluation-study.log',
                 'complete-evaluation-gzip6-control-v1-registration.json',
                 'complete-evaluation-gzip6-control-v1-result.json'):
        p=OUT/name;inputs[str(p)]=sha(p)
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,maximum_seconds=40000,automatic_retry=False,
        production_modified=False,stages=['evaluation-study','study-audit'],
        scope='Same untouched fresh test stream and comparison; qualified lossless archive compression only.'))
    start=time.monotonic();stage='starting';error=None;children=[];records=[]
    def guard():
        assert idle() and not OTHER.exists() and psutil.virtual_memory().available>20_000_000_000
        assert time.monotonic()-start<40000
    def verify():
        for path,h in inputs.items():assert sha(path)==h,path
    def status(state):
        path=OUT/f'{PREFIX}-status.json';tmp=path.with_suffix('.tmp')
        save(tmp,dict(state=state,stage=stage,controller_pid=os.getpid(),
            children=[dict(stage=c['name'],pid=c['process'].pid,exit_code=c['process'].poll()) for c in children],
            error=error,records=records,seconds=time.monotonic()-start,production_modified=False))
        tmp.replace(path)
    try:
        for stage,program,args,deadline in (
            ('evaluation-study','hu_later_action_compact_evaluation_20260925.py',['--study'],22800),
            ('study-audit','hu_later_action_compact_evaluation_review_20260925.py',['study'],7500)):
            guard();verify()
            env=os.environ.copy();env.update(PYTHONUNBUFFERED='1',OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
            with (OUT/f'{PREFIX}-{stage}.log').open('x') as log:
                process=subprocess.Popen([sys.executable,str(ROOT/'tools/research'/program),*args],cwd=ROOT,
                    env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            began=time.monotonic();children.append(dict(name=stage,process=process));last=0.
            while process.poll() is None:
                guard();assert time.monotonic()-began<deadline
                if time.monotonic()-last>30:status('running');last=time.monotonic()
                time.sleep(2)
            assert process.returncode==0,stage+' failed; preserve attempt and do not retry automatically'
            records.append(dict(stage=stage,seconds=time.monotonic()-began,exit_code=0))
            if stage=='evaluation-study':
                s=read(OUT/f'{STUDY}-status.json');r=read(OUT/f'{STUDY}-result.json')
                assert s['state']=='complete' and s['error'] is None and s['exit_code']==0
                assert r['passed'] and r['complete'] and r['deals']==65536
            else:
                a=read(OUT/f'{STUDY}-independent-review.json')
                assert a['passed'] and a['source_result_sha256']==sha(OUT/f'{STUDY}-result.json')
        verify();save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
            stages=records,seconds=time.monotonic()-start,production_modified=False,accuracy_qualified=False,
            scope='Execution and independent readback complete. Scientific interpretation remains separate.'))
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
