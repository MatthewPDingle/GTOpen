"""Build and run the preregistered four-way connected storage comparison."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/ssd-storage-20260920'
EVIDENCE = OUT.parent/'representative-coverage-20260919'
SUB = OUT.parent/'conditional-hu-20260919/subtree.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert json.loads((OUT/'ssd-paging-v1-review.json').read_text())['passed']
    assert json.loads((OUT/'physical-v1-result.json').read_text())['passed']
    assert idle()
    for p in [EVIDENCE/'running.lock',OUT.parent/'symmetric-bridge-20260919/running.lock']:
        assert not p.exists(), p
    with (OUT/'running.lock').open('x') as f:
        f.write(str(os.getpid()))
    status = dict(step='building',pid=os.getpid(),process_create_time=psutil.Process().create_time(),completed=[])
    child = None
    owned = {}
    def report():
        (OUT/'connected-v1-status.json').write_text(json.dumps(status,indent=2))
    def verify():
        for p,digest in inputs.items(): assert sha(ROOT/p) == digest, p
    try:
        files = [p for p in (ROOT/'crates/solver/src').rglob('*') if p.suffix in ['.rs','.cu']]
        files += [ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',SUB,
            OUT/'connected-three.json',OUT/'CONNECTED-PROTOCOL.md',Path(__file__),
            ROOT/'crates/solver/examples/integrated_continuation_stored.rs',
            ROOT/'crates/solver/examples/integrated_continuation_compact.rs',
            ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
        inputs = {str(p.relative_to(ROOT)):sha(p) for p in files}
        with (OUT/'connected-v1-build-freeze.json').open('x') as f:
            json.dump(dict(inputs=inputs,iterations=20,build_timeout=600,run_timeout=900,
                           max_strategy_write_bytes=128*1024**3),f,indent=2)
        env = os.environ.copy()
        env.update(CARGO_BUILD_JOBS='2',RAYON_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1')
        env['PATH'] = str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
        command = ['cargo','build','--locked','--release','-p','solver','--features','preflop-research',
                   '--example','integrated_continuation_stored','--example','integrated_continuation_compact',
                   '--target-dir','target/ssd-connected-research','--message-format=json']
        started = time.monotonic(); report()
        with (OUT/'connected-v1-build.log').open('x') as log:
            child = subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            owned[child.pid] = psutil.Process(child.pid).create_time()
            while child.poll() is None:
                try:
                    for p in psutil.Process(child.pid).children(recursive=True): owned[p.pid] = p.create_time()
                except psutil.NoSuchProcess:
                    pass
                assert time.monotonic()-started < 600, 'Build time limit'
                assert psutil.virtual_memory().available >= 20_000_000_000, 'Host memory reserve'
                time.sleep(1)
            assert child.returncode == 0, 'Build failed; retain diagnostic'
        status['build_seconds'] = time.monotonic()-started
        verify()
        bins = {name:ROOT/f'target/ssd-connected-research/release/examples/{name}.exe'
                for name in ['integrated_continuation_compact','integrated_continuation_stored']}
        with (OUT/'connected-v1-runtime-freeze.json').open('x') as f:
            json.dump(dict(inputs=inputs,executables={str(p):sha(p) for p in bins.values()}),f,indent=2)
        used_writes = 0
        for name,budget in [('resident',None),('ram',2**63),('ssd',0),('mixed',800_000_000)]:
            assert idle()
            verify()
            label='ssd-connected-v1-'+name
            scratch=Path('S:/GTOpen-research')/label
            assert not scratch.exists()
            scratch.mkdir(parents=True)
            assert shutil.disk_usage(scratch).free >= 100_000_000_000
            env.update(GTO_SSD_STUDY_DIR=str(scratch),GTO_STORAGE_RAM_BYTES=str(budget or 0),
                       GTO_STORAGE_WRITE_CAP=str(128*1024**3-used_writes),
                       GTO_RESEARCH_PROTOCOL=str((OUT/'CONNECTED-PROTOCOL.md').relative_to(ROOT)),
                       GTO_RESEARCH_MAX_SECONDS='900')
            exe=bins['integrated_continuation_compact' if budget is None else 'integrated_continuation_stored']
            result_path=OUT/(name+'-result.json')
            status['step']=name; report()
            # The research guard owns the test executable and stops it on production activity.
            child=subprocess.Popen([sys.executable,'tools/research/loopback_research_validation.py',str(exe),label,
                str(SUB.relative_to(ROOT)),str((OUT/'connected-three.json').relative_to(ROOT)),
                str(result_path.relative_to(ROOT)),'20'],cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
            code=child.wait()
            assert code==0, f'{name} failed; inspect preserved guard output'
            verify()
            if budget is not None:
                result=json.loads(result_path.read_text())
                used_writes += sum(e['write_bytes'] for e in result['storage']['entries'])
                assert used_writes<=128*1024**3
            status['completed'].append(name)
            status['strategy_bytes_written']=used_writes
            report()
        status['step']='complete-awaiting-review'
    except Exception as ex:
        status['step']='stopped-for-review';status['error']=repr(ex)
        raise
    finally:
        if child is not None and child.poll() is None:
            # Include current descendants, verify identities, and stop only our owned work.
            try:
                owned[child.pid]=psutil.Process(child.pid).create_time()
                for p in psutil.Process(child.pid).children(recursive=True): owned[p.pid]=p.create_time()
            except psutil.NoSuchProcess:
                pass
            targets=[]
            for pid,created in reversed(list(owned.items())):
                try:
                    p=psutil.Process(pid)
                    if p.create_time()==created:p.terminate();targets.append(p)
                except psutil.NoSuchProcess:
                    pass
            _,remaining=psutil.wait_procs(targets,timeout=5)
            for p in remaining:
                try:
                    if p.create_time()==owned[p.pid]:p.kill()
                except psutil.NoSuchProcess:
                    pass
        report()
        (OUT/'running.lock').unlink()
    print(json.dumps(status),flush=True)


if __name__=='__main__':
    main()
