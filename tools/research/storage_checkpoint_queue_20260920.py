"""Serialize checkpoint qualification behind the verified phase-diagnostic pipeline."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from storage_phase_run_20260920 import ROOT,OUT,read,sha

def main():
    prior=read(OUT/'phase-pipeline-v1-status.json');parent=psutil.Process(prior['pid'])
    assert parent.create_time()==prior['created']
    assert prior['step'] in ['waiting-for-fresh-timing','storage_phase_run_20260920.py','storage_phase_pilot_20260920.py']
    assert any('storage_phase_queue_20260920.py' in a for a in parent.cmdline())
    proposal=read(OUT/'checkpoint-v1-proposal.json')
    files=[Path(__file__),OUT/'checkpoint-v1-proposal.json',OUT/'RESUMABLE-STUDY-PROTOCOL.md',
        ROOT/'tools/research/storage_checkpoint_build_20260920.py',ROOT/'tools/research/storage_checkpoint_long_20260920.py',
        ROOT/'tools/research/storage_checkpoint_negative_20260920.py']
    files += [ROOT/proposal[n]['candidate'] for n in ['disk','storage','example','helper']]
    hashes={str(p.relative_to(ROOT)):sha(p) for p in files}
    with (OUT/'checkpoint-pipeline-v1-freeze.json').open('x') as f:json.dump(dict(inputs=hashes),f,indent=2)
    status=dict(step='waiting-for-phase-diagnostic',pid=os.getpid(),created=psutil.Process().create_time(),
        parent_pid=parent.pid,parent_created=parent.create_time())
    path=OUT/'checkpoint-pipeline-v1-status.json'
    with path.open('x') as f:json.dump(status,f,indent=2)
    def report():path.write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    started=time.monotonic()
    try:
        while True:
            try:parent.wait(timeout=30);break
            except psutil.TimeoutExpired:assert time.monotonic()-started<5400,'Phase observation deadline; inspect without restarting'
        assert read(OUT/'phase-pipeline-v1-status.json')['step']=='complete-phase-diagnostic-reviewed'
        assert read(OUT/'phase-pilot-v1-review.json')['diagnostic_passed']
        for name in ['storage_checkpoint_build_20260920.py','storage_checkpoint_long_20260920.py']:
            for p,h in hashes.items():assert sha(ROOT/p)==h,p
            status['step']=name;report()
            subprocess.run([sys.executable,str(ROOT/'tools/research'/name)],cwd=ROOT,check=True)
        status['step']='complete-checkpoint-resume-qualified'
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report()

if __name__=='__main__':main()
