"""Run the immutable qualified binaries for a longer changing-range comparison."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import psutil
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
SUB=ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert idle() and json.loads((OUT/'connected-v2-review.json').read_text())['passed']
    assert not (OUT/'running.lock').exists()
    prior=json.loads((OUT/'connected-v2-runtime-freeze.json').read_text())
    exes={}
    for path,h in prior['executables'].items():
        p=ROOT/'target/qualified-paging'/('ssd-connected-v2-'+Path(path).name)
        assert sha(p)==h
        exes['ram' if 'stored' in p.name else 'resident']=p
    inputs=[Path(__file__),SUB,OUT/'connected-three.json',OUT/'LONG-RAM-PROTOCOL.md',OUT/'connected-v2-runtime-freeze.json',OUT/'connected-v2-review.json',
        ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    with (OUT/'long-ram-v1-freeze.json').open('x') as f:json.dump(dict(inputs=frozen,binaries={str(p):sha(p) for p in exes.values()},iterations=500),f,indent=2)
    def verify():
        for p,h in frozen.items():assert sha(ROOT/p)==h,p
        for path,h in prior['executables'].items():assert sha(ROOT/'target/qualified-paging'/('ssd-connected-v2-'+Path(path).name))==h
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    status=dict(step='starting',pid=os.getpid(),created=psutil.Process().create_time(),completed=[])
    def report():(OUT/'long-ram-v1-status.json').write_text(json.dumps(status,indent=2))
    env=os.environ.copy();env.update(RAYON_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1',GTO_STORAGE_RAM_BYTES=str(2**63),
        GTO_STORAGE_WRITE_CAP='0',GTO_RESEARCH_MAX_SECONDS='1800',GTO_RESEARCH_PROTOCOL=str((OUT/'LONG-RAM-PROTOCOL.md').relative_to(ROOT)))
    env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
    child=None
    try:
        for name,exe in exes.items():
            verify();assert idle();status['step']=name;report()
            scratch=Path('S:/GTOpen-research')/('long-ram-v1-'+name);assert not scratch.exists();scratch.mkdir()
            env['GTO_SSD_STUDY_DIR']=str(scratch)
            dest=OUT/f'long-ram-v1-{name}-result.json';assert not dest.exists()
            child=subprocess.Popen([sys.executable,'tools/research/loopback_research_validation.py',str(exe),'long-ram-v1-'+name,
                str(SUB.relative_to(ROOT)),str((OUT/'connected-three.json').relative_to(ROOT)),str(dest.relative_to(ROOT)),'500'],
                cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
            assert child.wait()==0,name+' failed; retain evidence'
            verify();status['completed'].append(name)
        status['step']='complete-awaiting-review'
    except Exception as e:
        status.update(step='stopped-for-review',error=repr(e));raise
    finally:
        if child is not None and child.poll() is None:
            # Guard normally owns cleanup; only clean this process's verified live tree on parent failure.
            try:
                parent=psutil.Process(child.pid);targets=parent.children(recursive=True)+[parent]
                identities={p.pid:p.create_time() for p in targets}
                for p in reversed(targets):
                    if p.create_time()==identities[p.pid]:p.terminate()
                _,live=psutil.wait_procs(targets,timeout=5)
                for p in live:
                    if p.create_time()==identities[p.pid]:p.kill()
            except psutil.NoSuchProcess:pass
        report();(OUT/'running.lock').unlink()
    print(json.dumps(status),flush=True)

if __name__=='__main__':main()
