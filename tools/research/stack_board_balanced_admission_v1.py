"""Bounded resource wait, followed by one owned scientific attempt at most."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse,hashlib,json,subprocess,sys,time,traceback,uuid
from pathlib import Path
import psutil
from board_prefix_publication_v1 import atomic_json
from owned_windows_job_v1 import OwnedJob
from river_matched_training_pilot_v1 import available

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-board-balanced-admission-v1';STATUS=OUT/(NAME+'-status.json');MANIFEST=OUT/(NAME+'.json')
OWNER=OUT/(NAME+'-owner.json');STORE=Path('S:/GTOpen-research/stack-board-balanced-learning-v1')
REG=OUT/'stack-board-balanced-learning-v1-registration.json'
PREPARED=OUT/'stack-board-balanced-learning-v1-prepared.json'
RESULT=OUT/'stack-board-balanced-learning-v1-result.json'
RUNNER=ROOT/'tools/research/stack_board_balanced_run_v1.py'
ATTEMPT=STORE/'gpu-attempt.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def status(state,**values):
    doc=dict(state=state,pid=os.getpid(),process_created=psutil.Process().create_time(),unix=time.time(),**values)
    atomic_json(STATUS,doc,replace=True);print(json.dumps(doc),flush=True)

def main(wait_seconds):
    assert 30<=wait_seconds<=14400
    assert not any(p.exists() for p in (OWNER,MANIFEST,RESULT,ATTEMPT))
    prepared=read(PREPARED)
    assert prepared['passed'] and prepared['complete'] and prepared['registration_sha256']==sha(REG)
    assert not prepared['training_started'] and not prepared['test_labels_prepared']
    inputs={str(p):sha(p) for p in (Path(__file__),RUNNER,REG,PREPARED)}
    identity=dict(pid=os.getpid(),process_created=psutil.Process().create_time())
    with OWNER.open('x') as stream:json.dump(identity,stream)
    began=time.monotonic();launches=0
    try:
        atomic_json(MANIFEST,dict(inputs=inputs,maximum_admission_wait_seconds=wait_seconds,
            polling_seconds=30,scientific_attempt_retries=0,hidden_owned_child=True))
        while True:
            assert not RESULT.exists() and not ATTEMPT.exists(),'Never retry an already started scientific attempt'
            for p,h in inputs.items():assert sha(p)==h,p
            if time.monotonic()-began>=wait_seconds:
                status('admission_wait_expired',training_started=False);return
            ready,probe=available()
            if not ready:
                status('waiting_for_resources',training_started=False,elapsed=time.monotonic()-began,gpu=probe)
                time.sleep(min(30,max(0,wait_seconds-(time.monotonic()-began))));continue
            launches+=1;log=OUT/(NAME+f'-launch-{launches}.log')
            # The child blocks before importing research sources until ownership is confirmed.
            bootstrap="import sys,runpy; from pathlib import Path; assert sys.stdin.readline().strip()=='OWNED_START'; p=sys.argv[1]; sys.path.insert(0,str(Path(p).parent)); sys.argv=[p,'--run']; runpy.run_path(p,run_name='__main__')"
            with log.open('xb') as stream,OwnedJob() as job:
                child=subprocess.Popen([sys.executable,'-B','-c',bootstrap,str(RUNNER)],
                    stdin=subprocess.PIPE,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                try:
                    job.assign(child)
                    status('launching_admitted_comparison',child_pid=child.pid,log=str(log),gpu=probe)
                    child.communicate(b'OWNED_START\n',timeout=3800)
                    accounting=job.accounting();assert accounting['active_processes']==0
                    if child.returncode:raise RuntimeError(f'Research child exited {child.returncode}; inspect {log}; do not retry')
                except BaseException:
                    job.close()
                    if child.poll() is None:child.wait(timeout=10)
                    raise
            if RESULT.exists():
                result=read(RESULT);assert result['passed'] and result['complete']
                status('comparison_complete',result_sha256=sha(RESULT),job=accounting,independent_readback_pending=True);return
            assert not ATTEMPT.exists(),'Started comparison ended without a result; do not retry'
            status('admission_changed_before_start',training_started=False)
    except BaseException as error:
        atomic_json(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        status('terminal_error',error=repr(error),training_started=ATTEMPT.exists());raise
    finally:
        assert read(OWNER)==identity;OWNER.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--wait-seconds',type=int,default=14400)
    main(parser.parse_args().wait_seconds)
