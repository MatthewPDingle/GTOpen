"""Wait for the verified running resource pilot, then review before owner-transfer tests."""
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
    pilot=json.loads((OUT/'expansion-pilot-v1-status.json').read_text())
    parent=psutil.Process(pilot['pid'])
    assert pilot['step']=='running' and parent.create_time()==pilot['created']
    assert any('ssd-connected-v2-integrated_continuation_stored' in p.name() for p in parent.children(recursive=True)), 'Expected pilot child is not live'
    status=dict(step='waiting-for-verified-pilot',pid=os.getpid(),created=psutil.Process().create_time(),
        pilot_pid=parent.pid,pilot_created=parent.create_time())
    path=OUT/'owner-download-v1-queue-status.json'
    with path.open('x') as f:json.dump(status,f,indent=2)
    def report():path.write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    started=time.monotonic()
    try:
        while True:
            try:parent.wait(timeout=30);break
            except psutil.TimeoutExpired:
                assert time.monotonic()-started<1800,'Queue wait expired; do not restart pilot'
        assert json.loads((OUT/'expansion-pilot-v1-status.json').read_text())['step']=='complete-awaiting-review', 'Pilot failed; inspect preserved evidence before candidate'
        for name in ['storage_expansion_pilot_review_20260920.py','storage_owner_run_20260920.py','storage_owner_review_20260920.py']:
            status['step']=name;report()
            subprocess.run([sys.executable,str(ROOT/'tools/research'/name)],cwd=ROOT,check=True)
        status['step']='complete-owner-small-gates-passed'
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report()

if __name__=='__main__':main()
