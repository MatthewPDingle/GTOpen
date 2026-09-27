"""Resume the originally specified follow-up after audited operational repairs.

The completed original failures are retained. Stages use separately qualified
audit identity and inventory corrections; training design and endpoint stay
unchanged. This queue ends after the two-generation prefixes and their audits.
"""
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER
from board_prefix_followup_queue_v1 import require_result

NAME='board-prefix-followup-recovery-v2'
ORIGINAL='board-prefix-followup-queue-v1'
STAGES=(
    ('board_matched_readback_v2.py',['--mode','control','--workers','8'],'board-sequence-readback-control-v1',False,1860),
    ('board_training_bank_cuda_control_v1.py',['--run'],'board-training-bank-cuda-control-v1',True,660),
    ('board_prefix_resource_wrapper_v1.py',['--run'],'board-root-matched-prefix-v1',True,14520),
    ('board_matched_readback_v2.py',['--mode','prefix','--workers','8'],'board-matched-prefix-readback-v1',False,3720),
)


def main():
    began=time.monotonic(); rp=OUT/f'{NAME}-registration.json'
    old_rp=OUT/f'{ORIGINAL}-registration.json'; old_failure=OUT/f'{ORIGINAL}-failure.json'
    assert not rp.exists() and not (OUT/f'{ORIGINAL}-result.json').exists()
    failure=read(old_failure)
    assert not failure['passed'] and failure['registration_sha256']==sha(old_rp)
    assert failure['stages_completed']==[]
    for p,h in read(old_rp)['inputs'].items(): assert sha(p)==h,p
    required=('weighted-complete-evaluation-queue-v1','board-training-pipeline-queue-v2',
              'board-pipeline-query-recovery-v1','board-training-pipeline-readback-v2')
    paths=[old_rp,old_failure,OUT/'BOARD-PREFIX-FOLLOWUP-RECOVERY.md',
           OUT/'BOARD-ROOT-MATCHED-STUDY-PLAN.md',*Path(__file__).parent.glob('*.py')]
    for prefix in required:
        value,path=require_result(prefix); paths.extend((path,OUT/f'{prefix}-registration.json'))
        if prefix=='board-training-pipeline-queue-v2':
            for r in value['stages']: assert sha(r['result'])==r['sha256']
    review,review_path=require_result('board-training-pipeline-readback-v1')
    assert review['completion_recovery_result_sha256']==sha(OUT/'board-training-pipeline-readback-v2-result.json')
    assert review['generations']==2 and review['boards_checked']==8 and review['physical_roots_checked']==1024
    paths.extend((review_path,OUT/'board-training-pipeline-readback-v1-registration.json'))
    for prefix in ('board-prefix-resource-wrapper-control-v1','global-research-inventory-control-v2'):
        path=OUT/f'{prefix}-result.json'; proof=read(path); assert proof['passed']
        for p,h in proof['inputs'].items(): assert sha(p)==h,p
        paths.append(path)
    for _,_,prefix,_,_ in STAGES:
        assert not any((OUT/f'{prefix}-{suffix}.json').exists() for suffix in ('registration','result','failure'))
    inputs={str(p):sha(p) for p in paths}
    atomic_json(rp,dict(inputs=inputs,stages=STAGES,maximum_seconds=86400,
        original_registration=str(old_rp),original_registration_sha256=sha(old_rp),
        completed_initial_readback=str(review_path),completed_initial_readback_sha256=sha(review_path),
        scope='Explicit recovery after completed upstream checks; no automatic retry, full training, or deployment.',
        prefix_generations_per_arm=2,full_training_queued=False,production_modified=False))
    completed=[dict(script='board_training_pipeline_readback_v2.py',result=str(review_path),sha256=sha(review_path))]
    child=None; last_wait=None
    def deadline(): assert time.monotonic()-began<86400
    def sources():
        for p,h in inputs.items(): assert sha(p)==h,p
    def available(gpu):
        if not production_available() or psutil.virtual_memory().available<=28_000_000_000:return False
        if psutil.cpu_percent(interval=1)>=30 or LOCK.exists() or OTHER.exists():return False
        if gpu:
            if psutil.disk_usage('S:/').free<=50*2**30:return False
            probe=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
                capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
            if probe.returncode:return False
            util,free=map(float,probe.stdout.strip().splitlines()[0].split(','))
            if util>=10 or free<=6000:return False
        return True
    try:
        for script,args,prefix,gpu,limit in STAGES:
            while True:
                deadline()
                if available(gpu):break
                if last_wait!=prefix:
                    print(json.dumps(dict(waiting_for_resources=prefix,gpu_stage=gpu)),flush=True);last_wait=prefix
                time.sleep(30)
            sources()
            for r in completed:assert sha(r['result'])==r['sha256']
            assert not (OUT/f'{prefix}-registration.json').exists() and not (OUT/f'{prefix}-result.json').exists()
            logpath=OUT/f'{NAME}-{prefix}.log'
            print(json.dumps(dict(starting=script,args=args,log=str(logpath))),flush=True)
            with logpath.open('x',encoding='utf-8') as log:
                child=subprocess.Popen([sys.executable,str(ROOT/'tools/research'/script),*args],cwd=ROOT,
                    stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                atomic_json(OUT/f'{NAME}-child.json',dict(pid=child.pid,created=psutil.Process(child.pid).create_time(),
                    script=script,output_prefix=prefix),replace=True)
                assert child.wait(timeout=min(limit,86400-(time.monotonic()-began)))==0,'Stage failed: '+str(logpath)
            child=None
            result,path=require_result(prefix)
            if prefix=='board-sequence-readback-control-v1':assert result['reader_version']==2 and result['agrees_with_bounded_audit']
            if prefix=='board-root-matched-prefix-v1':
                assert result['prefix_generations_per_arm']==2
                wrapper,wp=require_result('board-prefix-resource-wrapper-v1')
                assert wrapper['prefix_result_sha256']==sha(path) and wrapper['dependency_restored']
                completed.append(dict(script='board_prefix_resource_wrapper_v1.py',result=str(wp),sha256=sha(wp)))
            if prefix=='board-matched-prefix-readback-v1':
                assert result['mode']=='prefix' and result['reader_version']==2 and all(a['generations']==2 for a in result['arms'])
            completed.append(dict(script=script,result=str(path),sha256=sha(path)))
            print(json.dumps(dict(completed=script)),flush=True)
        sources()
        value=dict(passed=True,registration_sha256=sha(rp),stages=completed,seconds=time.monotonic()-began,
            full_training_queued=False,production_modified=False,full_storage_admission_and_analysis_pending=True)
        result_path=OUT/f'{NAME}-result.json';atomic_json(result_path,value)
        atomic_json(OUT/f'{ORIGINAL}-result.json',dict(value,registration_sha256=sha(old_rp),
            completion_recovery_registration=str(rp),completion_recovery_registration_sha256=sha(rp),
            completion_recovery_result=str(result_path),completion_recovery_result_sha256=sha(result_path),
            original_failure=str(old_failure),original_failure_sha256=sha(old_failure)))
    except BaseException as error:
        atomic_json(OUT/f'{NAME}-failure.json',dict(passed=False,registration_sha256=sha(rp),error=repr(error),
            stages_completed=completed,seconds=time.monotonic()-began,production_modified=False))
        raise
    finally:
        if child is not None and child.poll() is None:
            owner=psutil.Process(child.pid);descendants=owner.children(recursive=True)
            for process in reversed(descendants):
                try:process.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20);psutil.wait_procs(descendants,timeout=20)


if __name__=='__main__':main()
