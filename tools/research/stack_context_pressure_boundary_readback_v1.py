"""Independently read the completed storage-stop evidence, before admission."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import hashlib
import json
from pathlib import Path
import time
import traceback
import psutil
import stack_context_pressure_continuation_v1 as coordinator


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_bytes())


def main():
    out=coordinator.OUT
    attempt=out/(coordinator.NAME+'-boundary-readback-attempt.json')
    failure=out/(coordinator.NAME+'-boundary-readback-failure.json')
    assert not any(p.exists() for p in (attempt,failure,coordinator.READBACK))
    paths=(Path(__file__).resolve(),Path(coordinator.__file__).resolve(),coordinator.REVIEW,coordinator.CONTROL)
    inputs={str(p):sha(p) for p in paths};began=time.monotonic()
    coordinator.save(attempt,dict(inputs=inputs,scientific_fits=0,native_calls=0))
    try:
        review,control=read(coordinator.REVIEW),read(coordinator.CONTROL)
        assert review['complete'] and review['passed'] and control['complete'] and control['passed']
        assert control['coordinator_sha256']==sha(coordinator.__file__)
        assert review['original_registration_sha256']==coordinator.REG_SHA
        for record in (review,control):
            for path,digest in record['inputs'].items():assert sha(path)==digest,path
            inputs.update(record['inputs'])
        assert not coordinator.original.legacy.LOCK.exists() and not coordinator.original.legacy.OTHER.exists()
        assert not (out/'stack-context-completion-handoff-v3-owner.json').exists()
        for pid,created in (coordinator.OLD_PARENT,coordinator.OLD_HELPER,*coordinator.OLD_WORKERS.values()):
            try:p=psutil.Process(pid)
            except psutil.NoSuchProcess:continue
            assert abs(p.create_time()-created)>.01
        observed={};archives=0
        for arm,n in coordinator.COUNTS.items():
            folder=coordinator.STORE/arm;p=read(folder/'progress.json')
            outcome_path=coordinator.STORE/(coordinator.original.NAME+'-'+coordinator.INVOCATION+'-'+arm+'.json')
            outcome=read(outcome_path)
            assert p['completed_cycles']==n and len(p['updates'])==n
            assert sha(folder/'progress.json')==review['boundaries'][arm]['progress_sha256']==outcome['progress_sha256']
            assert outcome['stopped_at_complete_boundary'] is True and outcome['complete'] is False and not outcome.get('failed')
            assert outcome['pid']==coordinator.OLD_WORKERS[arm][0] and outcome['process_created']==coordinator.OLD_WORKERS[arm][1]
            assert not (folder/f'cycle-{n+1:04d}').exists() and not (folder/f'archive-{n+1:04d}').exists()
            assert p['checkpoint']==p['updates'][-1]['checkpoint']==review['boundaries'][arm]['checkpoint']
            assert [r['cycle'] for r in p['updates']]==list(range(1,n+1))
            for record in p['updates']:
                dest=coordinator.STORE/record['archive'];cp=folder/'objects'/record['checkpoint']['file']
                assert sha(cp)==record['checkpoint']['sha256']
                assert sha(dest/'index.json')==record['archive_index_sha256']
                assert sha(dest/'retired.json')==record['retirement_sha256']
                idx,retired,plan=(read(dest/q) for q in ('index.json','retired.json','plan.json'))
                assert retired['raw_files_remaining']==0 and retired['index_sha256']==sha(dest/'index.json')
                assert idx['plan_sha256']==sha(dest/'plan.json')
                assert retired['original_bytes']==sum(r['bytes'] for r in plan['members'])
                archives+=1
            observed[arm]=n
        failed=read(coordinator.original.FAILURE)
        assert failed['error']==coordinator.PRESSURE_ERROR and failed['invocation']==coordinator.INVOCATION
        exit_record=read(out/'stack-context-completion-handoff-v3-001-training-finished.json')
        assert exit_record['pid']==coordinator.OLD_PARENT[0] and exit_record['created']==coordinator.OLD_PARENT[1]
        assert exit_record['exit_code']==1 and exit_record['phase']=='training'
        result=dict(complete=True,passed=True,inputs=inputs,review_sha256=sha(coordinator.REVIEW),
            coordinator_sha256=sha(coordinator.__file__),all_prefixes_unchanged=True,
            actual_complete_boundaries=observed,checkpoint_archive_metadata_count=archives,
            preserved_operational_failure=True,no_partial_cycle_to_retry=True,owners_released=True,
            native_calls=0,scientific_fits=0,full_archive_payload_readback=False,
            full_training_complete=False,scientific_evaluation_complete=False,production_modified=False,
            seconds=time.monotonic()-began)
        coordinator.save(coordinator.READBACK,result);print(json.dumps({k:v for k,v in result.items() if k!='inputs'}))
    except BaseException as error:
        coordinator.save(failure,dict(error=repr(error),traceback=traceback.format_exc(),inputs=inputs,preserve_evidence=True));raise


if __name__=='__main__':main()
