"""Separate convergence refinement; preserves all first-pass references."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import wizard_continuation_study as s

OUT=s.OUT/'precision'
BINARY=s.ROOT/'target/release/examples/wizard_continuation_precision.exe'


def prepare():
    assert s.read(s.OUT/'status.json')['stage']=='ready_for_review'
    parent=s.checked();f=s.read(s.OUT/'fixtures.json')
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'manifest.json').exists(),'Preserve precision manifest'
    jobs=[]
    for j in parent['jobs']:
        r=s.read(s.OUT/'jobs'/f"{j['id']}.json");s.validate(r,j,parent)
        gains=[h['br_ev_bb']-h['ev_bb'] for h in r['hands'][0] if h['hand'] in f['probes']]
        if max(gains)>parent['probe_br_gain_limit_bb']:jobs.append(j)
    paths=[BINARY,s.OUT/'manifest.json',OUT/'PROTOCOL.md',s.ROOT/'crates/solver/examples/wizard_continuation_precision.rs']
    m=dict(parent_manifest_id=parent['id'],jobs=jobs,target_gap_pct=.05,max_iterations=5000,
        probe_br_gain_limit_bb=.05,inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in paths})
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
    s.write(OUT/'manifest.json',m)
    print('Frozen',len(jobs),'precision jobs',flush=True)


def run():
    import msvcrt
    lock=(OUT/'run.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    m=s.read(OUT/'manifest.json')
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k!='id'},sort_keys=True).encode()).hexdigest()==m['id']
    for path,digest in m['inputs'].items():assert s.sha(s.ROOT/path)==digest
    env=dict(os.environ);env['PATH']=str(s.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    for i,j in enumerate(m['jobs']):
        dest=OUT/'jobs'/f"{j['id']}.json"
        if dest.exists():s.validate(s.read(dest),j,m);continue
        while not s.idle()[0]:
            s.write(OUT/'status.json',dict(stage='waiting_for_live_app',job=j['id']));time.sleep(30)
        s.write(OUT/'status.json',dict(stage='solving',job=j['id'],completed=i,total=len(m['jobs'])))
        with (OUT/(j['id']+'.log')).open('w') as log:
            subprocess.run([str(BINARY),'run',str(OUT/'manifest.json'),'1'],cwd=s.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        r=s.read(dest);s.validate(r,j,m)
        assert r['max_probe_br_gain_bb']<=m['probe_br_gain_limit_bb']
        print('Precision',i+1,'/',len(m['jobs']),j['id'],flush=True)
    s.summarize(use_precision=True)
    s.write(OUT/'status.json',dict(stage='ready_for_review',completed=len(m['jobs'])))


def pipeline():
    while True:
        stage=s.read(s.OUT/'status.json')['stage']
        if stage=='ready_for_review':break
        if stage=='failed':raise RuntimeError('First pass failed; inspect its status before continuing')
        time.sleep(15)
    if not (OUT/'manifest.json').exists():prepare()
    run()


if __name__=='__main__':
    try:
        {'prepare':prepare,'run':run,'pipeline':pipeline}[sys.argv[1]]()
    except Exception as error:
        if sys.argv[1] in ('run','pipeline'):s.write(OUT/'status.json',dict(stage='failed',error=str(error)))
        raise
