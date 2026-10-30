"""Bounded constructor validation and CPU-only forest payload audit."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
PROTOCOL=OUT/'CAPACITY-PROTOCOL.md'
SUB=ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
FULL=ROOT/'research/preflop-evolution/representative-coverage-20260919/combined-population-164.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert idle()
    assert json.loads((OUT/'connected-v2-review.json').read_text())['passed']
    assert not (OUT/'running.lock').exists()
    lock=(OUT/'running.lock').open('x');lock.write(str(os.getpid()));lock.close()
    status=dict(step='building',pid=os.getpid(),created=psutil.Process().create_time())
    def report():(OUT/'capacity-v1-status.json').write_text(json.dumps(status,indent=2))
    inputs=[p for p in (ROOT/'crates/solver/src').rglob('*') if p.suffix in ['.rs','.cu']]
    inputs += [ROOT/'crates/solver/Cargo.toml',ROOT/'Cargo.toml',ROOT/'Cargo.lock',
        ROOT/'crates/solver/examples/continuation_storage_capacity.rs',Path(__file__),PROTOCOL,SUB,FULL,OUT/'connected-three.json',
        ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    def verify():
        for p,h in frozen.items():assert sha(ROOT/p)==h,p
    child=None;owned={}
    try:
        with (OUT/'capacity-v1-freeze.json').open('x') as f:json.dump(dict(inputs=frozen),f,indent=2)
        env=os.environ.copy();env.update(CARGO_BUILD_JOBS='2',RAYON_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1')
        env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
        report();started=time.monotonic()
        with (OUT/'capacity-v1-build.log').open('x') as log:
            child=subprocess.Popen(['cargo','build','--locked','--release','-p','solver','--features','preflop-research',
                '--example','continuation_storage_capacity','--target-dir','target/ssd-connected-research'],cwd=ROOT,env=env,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            owned[child.pid]=psutil.Process(child.pid).create_time()
            while child.poll() is None:
                try:
                    for p in psutil.Process(child.pid).children(recursive=True):owned[p.pid]=p.create_time()
                except psutil.NoSuchProcess:pass
                assert time.monotonic()-started<600,'Build time limit'
                assert psutil.virtual_memory().available>=20_000_000_000,'Host reserve'
                time.sleep(1)
            assert child.returncode==0,'Build failed'
        verify()
        exe=ROOT/'target/ssd-connected-research/release/examples/continuation_storage_capacity.exe'
        with (OUT/'capacity-v1-runtime-freeze.json').open('x') as f:json.dump(dict(inputs=frozen,exe=str(exe),sha256=sha(exe)),f,indent=2)
        env.update(GTO_RESEARCH_PROTOCOL=str(PROTOCOL.relative_to(ROOT)),GTO_RESEARCH_MAX_SECONDS='900')
        for mode,manifest in [('device',OUT/'connected-three.json'),('cpu',FULL)]:
            assert idle();verify();status['step']=mode;report()
            child=subprocess.Popen([sys.executable,'tools/research/loopback_research_validation.py',str(exe),
                'storage-capacity-v1-'+mode,str(SUB.relative_to(ROOT)),str(manifest.relative_to(ROOT)),
                str((OUT/('capacity-v1-'+mode+'.json')).relative_to(ROOT)),mode],cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
            assert child.wait()==0,mode+' failed'
            verify()
        status['step']='complete-awaiting-review'
    except Exception as e:
        status.update(step='stopped-for-review',error=repr(e));raise
    finally:
        if child is not None and child.poll() is None:
            try:
                owned[child.pid]=psutil.Process(child.pid).create_time()
                for p in psutil.Process(child.pid).children(recursive=True):owned[p.pid]=p.create_time()
            except psutil.NoSuchProcess:pass
            targets=[]
            for pid,created in reversed(list(owned.items())):
                try:
                    p=psutil.Process(pid)
                    if p.create_time()==created:p.terminate();targets.append(p)
                except psutil.NoSuchProcess:pass
            _,live=psutil.wait_procs(targets,timeout=5)
            for p in live:
                try:
                    if p.create_time()==owned[p.pid]:p.kill()
                except psutil.NoSuchProcess:pass
        report();(OUT/'running.lock').unlink()
    print(json.dumps(status),flush=True)

if __name__=='__main__':main()
