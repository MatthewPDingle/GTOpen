"""Wait for spare resources, qualify four CUDA scorers, then continue once.

No trial retries. A resource-only deferred command has not begun an attempt.
Heavy workloads take priority; normal browser/video activity is allowed.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import psutil
import stack_context_parallel_continuation_v2 as runner
from sampled_physical_root_evaluation_v1 import save, sha
from board_prefix_publication_v1 import atomic_json

NAME='stack-context-parallel-admission-v2'
OUT=runner.legacy.OUT
ATTEMPT,STATUS,RESULT,FAILURE=(OUT/(NAME+s+'.json') for s in ('-attempt','-status','-result','-failure'))
CHECK=Path(__file__).with_name('stack_context_parallel_continuation_check_v2.py')
TRAINER=Path(runner.__file__).resolve()


def status(stage, **values):
    atomic_json(STATUS,dict(stage=stage,pid=os.getpid(),process_created=psutil.Process().create_time(),
        unix=time.time(),**values),replace=True)


def invoke(path, args, phase, deadline, inputs):
    runner.legacy.verify(inputs)
    log=OUT/(NAME+'-'+phase+'.log')
    with log.open('xb') as stream:
        child=subprocess.Popen([sys.executable,'-B',str(path),*args], stdout=stream,stderr=subprocess.STDOUT,
            cwd=str(runner.legacy.ROOT),creationflags=subprocess.CREATE_NO_WINDOW)
        status(phase,child_pid=child.pid,child_created=psutil.Process(child.pid).create_time(),log=str(log))
        # An admitted scientific invocation may continue beyond the admission
        # deadline. Its own original scientific/resource bounds still apply.
        while child.poll() is None:
            time.sleep(30)
        runner.require(child.returncode==0, 'Child exited abnormally: '+phase+'; preserve evidence, no retry')
        return log


def main():
    runner.require(not any(p.exists() for p in (ATTEMPT,RESULT,FAILURE)), 'Existing helper; verify it rather than duplicate')
    runner.known_failure()
    cpu=OUT/(runner.NAME+'-check-cpu-result.json'); proof=runner.legacy.read(cpu)
    runner.require(proof['passed'] and proof['complete'] and proof['runner_sha256']==sha(TRAINER), 'CPU recovery qualification required')
    runner.legacy.verify(proof['inputs'])
    paths={Path(__file__).resolve(),CHECK,TRAINER,cpu,runner.PLAN,runner.DIAGNOSIS,runner.legacy.FAILURE,runner.legacy.REG}
    inputs={str(p):sha(p) for p in paths}
    deadline=min(time.time()+12*3600,runner.legacy.read(runner.legacy.ATTEMPT)['admitted_unix']+72*3600)
    save(ATTEMPT,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),inputs=inputs,
        started_unix=time.time(),admission_deadline_unix=deadline,policy='share light desktop/video, yield to heavier work',
        scientific_retry_allowed=False,production_modified=False))
    try:
        stable=0; phase_number=0
        while time.time()<deadline:
            runner.require(not runner.FAILURE.exists() and not runner.RESULT.exists(), 'Terminal continuation outcome')
            ready,gpu=runner.legacy.available()
            ready=ready and psutil.virtual_memory().available>40_000_000_000 and gpu['free_bytes']>12_000_000_000
            stable=stable+1 if ready else 0
            status('waiting-for-spare-resources',admission_deadline_unix=deadline,probe=gpu,
                ready_samples=stable,control_complete=runner.CONTROL.exists(),training_started=False)
            if stable<3:
                time.sleep(30);continue
            phase_number+=1
            if not runner.CONTROL.exists():
                for suffix in ('-attempt','-failure'):
                    runner.require(not (OUT/(runner.NAME+'-check'+suffix+'.json')).exists(), 'Started check requires review, no retry')
                invoke(CHECK,[],'cuda-check-'+str(phase_number),deadline,inputs)
                if not runner.CONTROL.exists():
                    runner.require(not (OUT/(runner.NAME+'-check-attempt.json')).exists(), 'Check started without success')
                    stable=0;continue
            runner.require(runner.legacy.read(runner.CONTROL)['passed'], 'CUDA check failed')
            invoke(TRAINER,['--run'],'training-'+str(phase_number),deadline,inputs)
            if not runner.AMENDMENT.exists():
                stable=0;continue  # Read-only resource admission deferred.
            final=runner.legacy.read(runner.STATUS)
            runner.require(not runner.legacy.LOCK.exists() and final['stage'] in
                ('complete-boundary-awaiting-resume','training-complete-awaiting-fresh-evaluation'), 'Unverified terminal boundary')
            save(RESULT,dict(complete=True,helper_finished=True,training_stage=final['stage'],
                continuation_status_sha256=sha(runner.STATUS),training_complete=runner.RESULT.exists(),
                original_failure_preserved=True,scientific_retry=False,production_modified=False))
            status('helper-finished',training_stage=final['stage']);return
        save(RESULT,dict(helper_finished=True,admission_expired=True,training_started=False,production_modified=False))
        status('admission-expired',training_started=False)
    except BaseException as error:
        save(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),automatic_retry_allowed=False,
            preserve_evidence=True,production_modified=False))
        status('terminal-failure-needs-review');raise


if __name__=='__main__':main()
