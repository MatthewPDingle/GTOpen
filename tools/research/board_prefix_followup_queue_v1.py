"""Advance already specified qualifications and the two-generation prefix.

Wait for the identified live pipeline queue. No retries, full-study launch,
production writes or promotion. Each study keeps its own admission checks.
"""
import argparse
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

PREFIX='board-prefix-followup-queue-v1'
UPSTREAM='board-training-pipeline-queue-v2'
STAGES=(
    ('board_training_pipeline_readback_v1.py',['--workers','8'],'board-training-pipeline-readback-v1',False,1860),
    ('board_matched_readback_v1.py',['--mode','control','--workers','8'],'board-sequence-readback-control-v1',False,1860),
    ('board_training_bank_cuda_control_v1.py',['--run'],'board-training-bank-cuda-control-v1',True,660),
    ('board_matched_prefix_v2.py',['--run'],'board-root-matched-prefix-v1',True,14520),
    ('board_matched_readback_v1.py',['--mode','prefix','--workers','8'],'board-matched-prefix-readback-v1',False,3720),
)


def require_result(prefix):
    path=OUT/f'{prefix}-result.json';rp=OUT/f'{prefix}-registration.json'
    value=read(path);reg=read(rp)
    assert value['passed'] and value['registration_sha256']==sha(rp),prefix
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    return value,path


def main(upstream_pid,check_ready=False):
    process=psutil.Process(upstream_pid)
    assert process.is_running() and any('board_training_pipeline_queue_v2.py' in x for x in process.cmdline())
    upstream=dict(pid=process.pid,created=process.create_time(),command=process.cmdline())
    assert (OUT/f'{UPSTREAM}-registration.json').exists()
    assert not (OUT/f'{UPSTREAM}-failure.json').exists()
    outputs=[OUT/f'{s[2]}-result.json' for s in STAGES]
    assert not any(p.exists() for p in outputs),'Preserve completed stages; do not duplicate this queue'
    for _,_,prefix,_,_ in STAGES:
        assert not (OUT/f'{prefix}-registration.json').exists(),'Inspect existing stage before continuing: '+prefix
    rp=OUT/f'{PREFIX}-registration.json'
    assert not rp.exists()
    if check_ready:
        print(json.dumps(dict(ready_to_queue=True,upstream=upstream,stages=[s[0] for s in STAGES],
            prefix_generations_per_arm=2,full_training_queued=False,work_started=False)))
        return
    paths=[OUT/f'{UPSTREAM}-registration.json',OUT/'BOARD-ROOT-MATCHED-STUDY-PLAN.md',
        OUT/'BOARD-TRAINING-BANK-READINESS.md',OUT/'BOARD-PREFIX-FOLLOWUP-PLAN.md',
        *Path(__file__).parent.glob('*.py')]
    inputs={str(p):sha(p) for p in paths}
    atomic_json(rp,dict(inputs=inputs,upstream=upstream,stages=STAGES,maximum_seconds=86400,
        policy='Wait for the original process and passed results; no retries, upstream termination, full study or production deployment.',
        prefix_generations_per_arm=2,full_training_queued=False,production_modified=False))
    began=time.monotonic();child=None;completed=[];last_wait=None
    def deadline():assert time.monotonic()-began<86400,'Follow-up queue deadline reached'
    def sources():
        for p,h in inputs.items():assert sha(p)==h,p
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
        while not (OUT/f'{UPSTREAM}-result.json').exists():
            deadline()
            assert process.is_running() and process.create_time()==upstream['created'],'Original pipeline queue ended without result'
            assert not (OUT/f'{UPSTREAM}-failure.json').exists(),'Upstream reported failure'
            time.sleep(30)
        value,_=require_result(UPSTREAM)
        for record in value['stages']:assert sha(record['result'])==record['sha256'],record['result']
        require_result('weighted-complete-evaluation-queue-v1')
        for script,args,prefix,gpu,limit in STAGES:
            while True:
                deadline()
                if available(gpu):break
                if last_wait!=prefix:
                    print(json.dumps(dict(waiting_for_resources=prefix,gpu_stage=gpu)),flush=True);last_wait=prefix
                time.sleep(30)
            sources()
            for record in completed:assert sha(record['result'])==record['sha256'],record['result']
            # A competing or interrupted invocation is a reason to stop, not retry.
            assert not (OUT/f'{prefix}-registration.json').exists()
            assert not (OUT/f'{prefix}-result.json').exists()
            logpath=OUT/f'{PREFIX}-{prefix}.log'
            print(json.dumps(dict(starting=script,args=args,log=str(logpath))),flush=True)
            with logpath.open('x',encoding='utf-8') as log:
                child=subprocess.Popen([sys.executable,str(ROOT/'tools/research'/script),*args],cwd=ROOT,
                    stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                remaining=86400-(time.monotonic()-began)
                assert remaining>0
                assert child.wait(timeout=min(limit,remaining))==0,'Stage failed; inspect '+str(logpath)
            child=None
            result,path=require_result(prefix)
            if prefix=='board-sequence-readback-control-v1':assert result['agrees_with_bounded_audit']
            if prefix=='board-root-matched-prefix-v1':assert result['prefix_generations_per_arm']==2
            if prefix=='board-matched-prefix-readback-v1':
                assert result['mode']=='prefix' and all(a['generations']==2 for a in result['arms'])
            completed.append(dict(script=script,result=str(path),sha256=sha(path)))
            print(json.dumps(dict(completed=script)),flush=True)
        sources()
        atomic_json(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),stages=completed,
            seconds=time.monotonic()-began,full_training_queued=False,production_modified=False,
            full_storage_admission_and_analysis_pending=True))
    except BaseException as exc:
        atomic_json(OUT/f'{PREFIX}-failure.json',dict(passed=False,registration_sha256=sha(rp),error=repr(exc),
            stages_completed=completed,seconds=time.monotonic()-began,production_modified=False))
        raise
    finally:
        # Only terminate this invocation's still-running direct child and its
        # descendants. The upstream queue, user workloads and servers are untouched.
        if child is not None and child.poll() is None:
            owner=psutil.Process(child.pid)
            descendants=owner.children(recursive=True)
            for p in reversed(descendants):
                try:p.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--upstream-pid',type=int,required=True)
    parser.add_argument('--check-ready',action='store_true');options=parser.parse_args()
    main(options.upstream_pid,options.check_ready)
