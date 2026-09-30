"""Recover only archive transport for two fully computed interrupted cycles."""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import json
from pathlib import Path
import time
import traceback
import psutil
from stack_context_archive_recovery_v1 import recover
from stack_context_cycle_archive_v1 import read,sha
from owned_columnar_evaluation_archive_v1 import durable,encoded
from stack_context_interruption_audit_v1 import absent,OUT,STORE

NAME='stack-context-archive-transport-recovery-v1'


def main():
    began=time.monotonic();absent();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    check=OUT/'stack-context-archive-recovery-check-v1-result.json';proof=read(check)
    assert proof['passed'] and proof['complete'] and len(proof['rejected'])==10
    for p,h in proof['inputs'].items():assert sha(p)==h
    audit_path=OUT/'stack-context-parallel-interruption-audit-v1-result.json';audit=read(audit_path)
    assert audit['read_only_audit_passed'] and audit['original_processes_absent']
    attempt=OUT/(NAME+'-attempt.json');result=OUT/(NAME+'-result.json');failure=OUT/(NAME+'-failure.json')
    assert not any(p.exists() for p in (attempt,result,failure))
    lock=STORE/(NAME+'.lock')
    durable(lock,encoded(dict(pid=os.getpid(),created=psutil.Process().create_time())))
    def guard():
        assert time.monotonic()-began<1800, 'Archive recovery time bound'
        assert psutil.virtual_memory().available>24_000_000_000 and psutil.disk_usage(STORE.anchor).free>40_000_000_000
    try:
        durable(attempt,encoded(dict(unix=time.time(),pid=os.getpid(),created=psutil.Process().create_time(),
            inputs={str(p):sha(p) for p in (Path(__file__),check,audit_path)},raw_retirement=False,
            new_native_calls=False,new_sampling=False,new_fits=False,maximum_seconds=1800,compression_workers=4)))
        expected={r['path']:r['sha256'] for r in audit['files']};arms={}
        for arm in ('A-baseline','B-relative'):
            state=audit['arms'][arm]
            assert state['complete_metric'] and state['complete_checkpoint_restored']
            dest=Path(state['archive']);raw=Path(state['raw'])
            assert sha(raw/'metrics.json')==state['metric_sha256']
            arms[arm]=recover(dest,root=STORE,token='stack-context-matched-learning-v1-new-evidence-only',
                expected=expected,guard=guard,workers=4)
            print(json.dumps(dict(arm=arm,stage='archive-transport-complete',**{k:v for k,v in arms[arm].items() if k!='index'})),flush=True)
        absent()
        value=dict(complete=True,passed=True,unix=time.time(),seconds=time.monotonic()-began,
            attempt_sha256=sha(attempt),arms=arms,raw_files_preserved=True,scientific_progress_published=False,
            native_calls=0,new_samples=0,new_fits=0,production_modified=False,original_stale_lock_preserved=True)
        durable(result,encoded(value));print(json.dumps({k:v for k,v in value.items() if k!='arms'}),flush=True)
    except BaseException as e:
        durable(failure,encoded(dict(error=repr(e),traceback=traceback.format_exc(),automatic_retry=False)));raise
    finally:
        if lock.exists() and read(lock)['pid']==os.getpid():lock.unlink()


if __name__=='__main__':main()
