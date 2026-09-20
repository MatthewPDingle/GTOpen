"""Follow the verified owner-long process; only then test the distinct reuse candidate."""
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
    prior=json.loads((OUT/'owner-download-v1-long-status.json').read_text())
    parent=psutil.Process(prior['pid'])
    assert parent.create_time()==prior['created'] and prior['step']=='running-500-iteration-qualification'
    assert parent.children(), 'No live qualification child'
    status=dict(step='waiting-for-owner-long',pid=os.getpid(),created=psutil.Process().create_time(),
        parent_pid=parent.pid,parent_created=parent.create_time())
    path=OUT/'reuse-download-v1-queue-status.json'
    with path.open('x') as f:json.dump(status,f,indent=2)
    def report():path.write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    started=time.monotonic()
    try:
        while True:
            try:parent.wait(timeout=30);break
            except psutil.TimeoutExpired:assert time.monotonic()-started<1800,'Wait expired; inspect without restarting'
        assert json.loads((OUT/'owner-download-v1-long-review.json').read_text())['passed']
        for name in ['storage_reuse_run_20260920.py','storage_reuse_review_20260920.py','storage_reuse_long_20260920.py']:
            status['step']=name;report()
            subprocess.run([sys.executable,str(ROOT/'tools/research'/name)],cwd=ROOT,check=True)
        status['step']='complete-reuse-small-and-long-gates-passed'
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report()

if __name__=='__main__':main()
