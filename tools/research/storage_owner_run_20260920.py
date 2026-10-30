"""Apply and qualify the frozen owner-only transfer candidate after the large pilot ends."""
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

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
EVIDENCE=OUT.parent/'representative-coverage-20260919'
SUB=OUT.parent/'conditional-hu-20260919/subtree.json'
LABEL='owner-download-v1'

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    pilot=read(OUT/'expansion-pilot-v1-status.json')
    if pilot['step']=='complete-awaiting-review':
        pilot_review=OUT/'expansion-pilot-v1-review.json'
        assert read(pilot_review)['passed']
    else:
        pilot_review=OUT/'expansion-pilot-v1-failure-review.json'
        failure=read(pilot_review)
        assert pilot['step']=='stopped-for-review' and failure['runtime_gate_passed'] is False
        assert failure['allow_small_transfer_experiment'] is True
        for p,h in failure['inputs_sha256'].items():assert sha(ROOT/p)==h,p
    try:assert psutil.Process(pilot['pid']).create_time()!=pilot['created'],'Pilot parent still alive'
    except psutil.NoSuchProcess:pass
    assert idle() and psutil.virtual_memory().available>=30_000_000_000
    for d in [OUT,EVIDENCE]:assert not (d/'running.lock').exists()
    proposal=read(OUT/'owner-download-v1-proposal.json')
    source=ROOT/proposal['source'];candidate=ROOT/proposal['candidate']
    assert sha(source)==proposal['source_sha256'] and sha(candidate)==proposal['candidate_sha256']
    assert read(OUT/'long-ram-v1-review.json')['passed']
    assert not (OUT/f'{LABEL}-build-freeze.json').exists()
    # Apply exactly the reviewed proposal; retain its pre-change source fingerprint.
    source.write_bytes(candidate.read_bytes())
    assert sha(source)==proposal['candidate_sha256']
    files=[p for p in (ROOT/'crates/solver/src').rglob('*') if p.suffix in ['.rs','.cu']]
    files += [ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',
        ROOT/'crates/solver/examples/integrated_continuation_stored.rs',SUB,OUT/'connected-three.json',
        OUT/'OWNER-DOWNLOAD-PROTOCOL.md',OUT/'owner-download-v1-proposal.json',Path(__file__),
        ROOT/'tools/research/storage_owner_review_20260920.py',pilot_review,
        ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
    with (OUT/f'{LABEL}-build-freeze.json').open('x') as f:json.dump(dict(inputs=inputs),f,indent=2)
    def verify():
        for p,h in inputs.items():assert sha(ROOT/p)==h,p
    env=os.environ.copy()
    env.update(CARGO_BUILD_JOBS='2',RAYON_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1')
    env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
    status=dict(step='starting',pid=os.getpid(),created=psutil.Process().create_time(),completed=[])
    def report():(OUT/f'{LABEL}-status.json').write_text(json.dumps(status,indent=2))
    child=None;owned={}
    def stop_owned():
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
    def build(name,args):
        nonlocal child
        status['step']='build-'+name;report();start=time.monotonic()
        command=['cargo',*args,'--locked','--release','-p','solver','--features','preflop-research',
            '--target-dir','target/ssd-connected-research','--message-format=json']
        logpath=OUT/f'{LABEL}-build-{name}.log'
        with logpath.open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            owned[child.pid]=psutil.Process(child.pid).create_time()
            while child.poll() is None:
                try:
                    for p in psutil.Process(child.pid).children(recursive=True):owned[p.pid]=p.create_time()
                except psutil.NoSuchProcess:pass
                assert time.monotonic()-start<600 and psutil.virtual_memory().available>=20_000_000_000,'Build time/memory limit'
                time.sleep(1)
            assert child.returncode==0,'Build failed; preserve diagnostic'
        verify();artifacts=[]
        for line in logpath.read_text().splitlines():
            try:r=json.loads(line)
            except json.JSONDecodeError:continue
            if r.get('reason')=='compiler-artifact' and r.get('executable'):artifacts.append(r)
        status.setdefault('build_seconds',{})[name]=time.monotonic()-start
        return artifacts
    def guarded(name,exe,args,budget):
        nonlocal child
        verify();assert idle()
        scratch=Path('S:/GTOpen-research')/(LABEL+'-'+name);assert not scratch.exists();scratch.mkdir()
        assert shutil.disk_usage(scratch).free>=100_000_000_000
        env.update(GTO_SSD_STUDY_DIR=str(scratch),GTO_STORAGE_RAM_BYTES=str(budget),
            GTO_STORAGE_WRITE_CAP=str(64*1024**3),GTO_RESEARCH_MAX_SECONDS='900',
            GTO_RESEARCH_PROTOCOL=str((OUT/'OWNER-DOWNLOAD-PROTOCOL.md').relative_to(ROOT)))
        status['step']=name;report()
        child=subprocess.Popen([sys.executable,'tools/research/loopback_research_validation.py',str(exe),
            LABEL+'-'+name,*args],cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
        owned[child.pid]=psutil.Process(child.pid).create_time()
        assert child.wait()==0,name+' failed; retain diagnostics'
        verify();status['completed'].append(name);report()
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    try:
        artifacts=build('fixture',['test','--lib','--no-run'])
        fixtures=[Path(r['executable']) for r in artifacts if r['target']['name']=='solver' and r['profile']['test']]
        assert len(fixtures)==1
        artifacts=build('connected',['build','--example','integrated_continuation_stored'])
        connected=[Path(r['executable']) for r in artifacts if r['target']['name']=='integrated_continuation_stored']
        assert len(connected)==1
        retained={}
        for name,p in [('fixture',fixtures[0]),('connected',connected[0])]:
            assert p.resolve().is_relative_to((ROOT/'target/ssd-connected-research').resolve())
            q=ROOT/'target/qualified-paging'/f'{LABEL}-{name}.exe';assert not q.exists()
            shutil.copyfile(p,q);assert sha(q)==sha(p);retained[name]=q
        with (OUT/f'{LABEL}-runtime-freeze.json').open('x') as f:
            json.dump(dict(inputs=inputs,executables={k:dict(path=str(p),sha256=sha(p)) for k,p in retained.items()}),f,indent=2)
        guarded('diagnostic',retained['fixture'],['gpu::continuation::storage::device_tests::direct_gpu_storage_preserves_720_full_state_passes',
            '--exact','--nocapture','--test-threads=1'],2**63)
        for name,budget in [('ram',2**63),('ssd',0)]:
            dest=OUT/f'{LABEL}-{name}-result.json';assert not dest.exists()
            guarded(name,retained['connected'],[str(SUB.relative_to(ROOT)),str((OUT/'connected-three.json').relative_to(ROOT)),
                str(dest.relative_to(ROOT)),'20'],budget)
        status['step']='complete-awaiting-review'
    except Exception as e:
        status.update(step='stopped-for-review',error=repr(e));raise
    finally:
        if child is not None and child.poll() is None:
            try:
                for p in psutil.Process(child.pid).children(recursive=True):owned[p.pid]=p.create_time()
            except psutil.NoSuchProcess:pass
            stop_owned()
        report();(OUT/'running.lock').unlink()
    print(json.dumps(status),flush=True)

if __name__=='__main__':main()
