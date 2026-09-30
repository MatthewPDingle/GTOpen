"""Read back qualification controls and verify the durable live trainer."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
import psutil

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE=Path('S:/GTOpen-research/stack-context-matched-learning-v1')
NAME='stack-context-recovery-consumer-checks-readback-v1'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_bytes())


def main():
    result=OUT/(NAME+'-result.json')
    assert not result.exists()
    controls=('stack-context-interruption-provenance-check-v1',
        'stack-context-interruption-readback-v1','stack-context-continuation-evaluation-check-v2',
        'stack-context-final-bank-throughput-v2-check','stack-context-matched-readback-check-v4')
    evidence={};inputs={str(Path(__file__).resolve()):sha(__file__)}
    for prefix in controls:
        path=OUT/(prefix+'-result.json');proof=read(path)
        assert proof['complete'] and proof['passed']
        assert not (OUT/(prefix+'-failure.json')).exists()
        for source,digest in proof['inputs'].items():assert sha(source)==digest,source
        inputs[str(path)]=sha(path)
        evidence[prefix]=dict(sha256=sha(path),seconds=proof['seconds'],
            rejected_corruptions=len(proof.get('negative_cases',proof.get('rejected',[]))))
    start=read(OUT/'stack-context-durable-recovery-entry-v1-parallel-training-started.json')
    process=psutil.Process(start['pid'])
    assert abs(process.create_time()-start['created'])<.001 and 'stack_context_parallel_continuation_v2.py' in ' '.join(process.cmdline())
    parent=process.parent()
    assert parent.pid==84788 and abs(parent.create_time()-1790752536.9318762)<.001
    assert 'stack_context_durable_recovery_entry_v1.py' in ' '.join(parent.cmdline())
    status=read(OUT/'stack-context-parallel-continuation-v2-status.json')
    assert status['pid']==process.pid and abs(status['process_created']-process.create_time())<.001
    assert time.time()-status['unix']<60 and status['stage']=='parallel-training'
    arms=[]
    for row in status['arms']:
        worker=psutil.Process(row['pid'])
        assert row['alive'] and worker.ppid()==process.pid and 'multiprocessing.spawn' in ' '.join(worker.cmdline())
        progress=read(STORE/row['arm']/'progress.json')
        arms.append(dict(arm=row['arm'],pid=worker.pid,created=worker.create_time(),
            completed_cycles=progress['completed_cycles'],last_checkpoint=progress['checkpoint']))
    assert len(arms)==4
    lock=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
    assert lock.read_text()==str(process.pid)
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,memory.free',
        '--format=csv,noheader,nounits'],text=True).strip()
    value=dict(complete=True,passed=True,unix=time.time(),inputs=inputs,controls=evidence,
        total_negative_cases=sum(r['rejected_corruptions'] for r in evidence.values()),
        trainer=dict(pid=process.pid,created=process.create_time(),parent_pid=parent.pid,
            parent_created=parent.create_time(),arms=arms,fresh_status_unix=status['unix']),
        gpu_snapshot_csv=gpu,qualification_only=True,full_training_complete=False,
        actual_final_bank_cuda_check_complete=False,scientific_evaluation_complete=False,
        new_scientific_deals=False,fitting=False,native_execution=False,production_modified=False)
    with result.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,sort_keys=True,allow_nan=False);stream.write('\n')
    print(json.dumps(dict(passed=True,total_negative_cases=value['total_negative_cases'],
        completed_cycles={r['arm']:r['completed_cycles'] for r in arms},trainer_pid=process.pid,gpu_snapshot_csv=gpu)),flush=True)


if __name__=='__main__':main()
