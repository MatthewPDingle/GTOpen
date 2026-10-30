"""One registered sequence of correctness gates, then a 20-iteration feasibility trial.

No unattended long strategic run is authorized by this script: inspect the
trial's resource/timing evidence and preregister that run separately.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import psutil

ROOT=Path(__file__).resolve().parents[2]
SYM=ROOT/'research/preflop-evolution/symmetric-bridge-20260919'
PAGED=ROOT/'research/preflop-evolution/representative-coverage-20260919'
PY=sys.executable
SUB='research/preflop-evolution/conditional-hu-20260919/subtree.json'
COMPACT='target/release/examples/integrated_continuation_compact.exe'
PAGING='target/release/examples/integrated_continuation_paged.exe'
UNIT='target/release/deps/continuation_paging-313e4a6bc05c90c6.exe'
frozen={}

def record(step, **extra):
    (PAGED/'validation-queue-status.json').write_text(json.dumps(dict(step=step,
        updated_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),**extra),indent=2))
    print(step,flush=True)

def run(step, *args):
    for name,digest in frozen.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, f'Queued input changed: {name}'
    record(step)
    subprocess.run([PY,*args],cwd=ROOT,check=True)

def main():
    global frozen
    lock=PAGED/'validation-queue.lock'
    with lock.open('x') as f:f.write(str(os.getpid()))
    try:
        files=[COMPACT,PAGING,UNIT,SUB,'crates/solver/src/gpu/continuation_paging.rs',
               'crates/solver/tests/continuation_paging.rs',
               'crates/solver/examples/integrated_continuation_paged.rs',
               'tools/research/paged_continuation_validation.py','tools/research/paged_continuation_review.py',
               'tools/research/connected_symmetry_review.py',
               'research/preflop-evolution/representative-coverage-20260919/report-47.json']
        frozen={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}
        registration=PAGED/'validation-queue-freeze.json';assert not registration.exists()
        registration.write_text(json.dumps(dict(inputs=frozen,pid=os.getpid(),
            plan='Finish current AB explicit; AB compact and review; paging unit; paging two-board 2000 and review; report47 20-iteration trial. Stop on any failed gate.'),indent=2))
        record('waiting-for-owned-ab-explicit')
        deadline=time.monotonic()+1800
        while not (SYM/'connected-ab-explicit-status.json').exists():
            assert time.monotonic()<deadline,'Existing AB run exceeded bounded wait'
            pid=int((SYM/'running.lock').read_text())
            proc=psutil.Process(pid)
            assert 'connected-ab-explicit' in ' '.join(proc.cmdline()),'Unexpected research owner'
            time.sleep(5)
        assert json.loads((SYM/'connected-ab-explicit-status.json').read_text())['exit_code']==0
        # The guard writes status just before releasing its process lock.
        for _ in range(10):
            if not (SYM/'running.lock').exists():break
            time.sleep(.5)
        run('ab-compact','tools/research/symmetric_bridge_validation.py',COMPACT,'connected-ab-compact',SUB,
            str((SYM/'connected-ab-compact.json').relative_to(ROOT)),str((SYM/'connected-ab-compact-result.json').relative_to(ROOT)),'2000')
        run('ab-review','tools/research/connected_symmetry_review.py','ab')
        run('paging-unit','tools/research/paged_continuation_validation.py',UNIT,'paging-unit','--nocapture','--test-threads=1')
        run('paging-two','tools/research/paged_continuation_validation.py',PAGING,'paged-two',SUB,
            'research/preflop-evolution/integrated-coverage-20260919/old-two-orbits.json',
            str((PAGED/'paged-two-result.json').relative_to(ROOT)),'2000')
        run('paging-two-review','tools/research/paged_continuation_review.py')
        run('report47-trial','tools/research/paged_continuation_validation.py',PAGING,'report47-trial',SUB,
            str((PAGED/'report-47.json').relative_to(ROOT)),str((PAGED/'report47-trial-result.json').relative_to(ROOT)),'20')
        record('complete-awaiting-trial-review')
    except Exception as ex:
        record('failed',error=str(ex));raise
    finally:
        lock.unlink()

if __name__=='__main__':main()
