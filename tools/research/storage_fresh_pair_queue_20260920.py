"""Start the preregistered fresh comparison only after the verified reuse queue finishes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'

def main():
    prior=json.loads((OUT/'reuse-download-v1-queue-status.json').read_text())
    parent=psutil.Process(prior['pid'])
    assert parent.create_time()==prior['created'] and prior['step']=='storage_reuse_long_20260920.py'
    assert parent.children(), 'Expected qualification process is not live'
    status=dict(step='waiting-for-reuse-qualification',pid=os.getpid(),created=psutil.Process().create_time(),
        parent_pid=parent.pid,parent_created=parent.create_time())
    path=OUT/'storage-fresh-pair-v1-queue-status.json'
    with path.open('x') as f:json.dump(status,f,indent=2)
    def report():path.write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    start=time.monotonic()
    try:
        while True:
            try:parent.wait(timeout=30);break
            except psutil.TimeoutExpired:assert time.monotonic()-start<1800,'Qualification wait expired; do not restart'
        assert json.loads((OUT/'reuse-download-v1-queue-status.json').read_text())['step']=='complete-reuse-small-and-long-gates-passed'
        status['step']='fresh-timing';report()
        subprocess.run([sys.executable,str(ROOT/'tools/research/storage_fresh_pair_20260920.py')],cwd=ROOT,check=True)
        status['step']='complete-fresh-timing-reviewed'
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report()

if __name__=='__main__':main()
