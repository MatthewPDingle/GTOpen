"""Wait for the verified live fresh timing process, then qualify and diagnose phases."""
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
    prior=json.loads((OUT/'storage-fresh-pair-v1-status.json').read_text())
    parent=psutil.Process(prior['pid'])
    assert parent.create_time()==prior['created'] and prior['step'] in ['a1','b1','b2','a2']
    assert any('storage_fresh_pair_20260920.py' in a for a in parent.cmdline())
    assert parent.children(),'Fresh comparison has no live child'
    status=dict(step='waiting-for-fresh-timing',pid=os.getpid(),created=psutil.Process().create_time(),
        parent_pid=parent.pid,parent_created=parent.create_time())
    path=OUT/'phase-pipeline-v1-status.json'
    with path.open('x') as f:json.dump(status,f,indent=2)
    def report():path.write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    started=time.monotonic()
    try:
        while True:
            try:parent.wait(timeout=30);break
            except psutil.TimeoutExpired:assert time.monotonic()-started<6100,'Observation deadline; inspect same process, do not restart'
        assert json.loads((OUT/'storage-fresh-pair-v1-status.json').read_text())['step']=='complete-reviewed'
        for name in ['storage_phase_run_20260920.py','storage_phase_pilot_20260920.py']:
            status['step']=name;report()
            subprocess.run([sys.executable,str(ROOT/'tools/research'/name)],cwd=ROOT,check=True)
        status['step']='complete-phase-diagnostic-reviewed'
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report()

if __name__=='__main__':main()
