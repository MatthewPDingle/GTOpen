"""Qualify phase logging after fresh timing; leave production and numeric math unchanged."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle
from storage_owner_review_20260920 import science

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
EVIDENCE=OUT.parent/'representative-coverage-20260919'
SUB=OUT.parent/'conditional-hu-20260919/subtree.json'
LABEL='phase-timing-v1'

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def phase_review(log, iterations, checkpoints, result):
    rows=[json.loads(l.split('STUDY_PHASE ',1)[1]) for l in log.splitlines() if l.startswith('STUDY_PHASE ')]
    expected=[('construction_complete',None)]
    for t in range(1,iterations+1):
        expected.append(('iteration_complete',t))
        if t in checkpoints:expected += [('evaluation_start',t),('evaluation_complete',t)]
    assert [(r['phase'],r.get('iteration')) for r in rows]==expected
    elapsed=[r['elapsed_seconds'] for r in rows]
    assert all(math.isfinite(x) and x>=0 for x in elapsed) and elapsed==sorted(elapsed)
    training=[r['iteration_seconds'] for r in rows if r['phase']=='iteration_complete']
    assert all(math.isfinite(x) and x>=0 for x in training)
    totals=result['phase_timing']
    assert all(math.isfinite(x) and x>=0 for x in totals.values())
    assert totals['setup_seconds']==rows[0]['elapsed_seconds']
    assert abs(sum(training)-totals['training_seconds'])<1e-8
    assert totals['evaluation_seconds']==rows[-1]['evaluation_seconds']
    assert sum(totals.values())<=result['records'][-1]['elapsed_seconds']+.001
    evaluations=[]
    for i,r in enumerate(rows):
        if r['phase']=='evaluation_start':evaluations.append(rows[i+1]['elapsed_seconds']-r['elapsed_seconds'])
    return dict(totals=totals,iteration_seconds=training,evaluation_seconds=evaluations)

def main():
    fresh=read(OUT/'storage-fresh-pair-v1-review.json')
    assert fresh['correctness_passed'] and fresh['repeatable_fixture_improvement'] and not fresh['inconclusive']
    assert fresh['selected_candidate']=='reuse-download-v1'
    prior=read(OUT/'storage-fresh-pair-v1-status.json');assert prior['step']=='complete-reviewed'
    try:assert psutil.Process(prior['pid']).create_time()!=prior['created'],'Fresh comparison is still live'
    except psutil.NoSuchProcess:pass
    assert idle() and psutil.virtual_memory().available>=30_000_000_000
    for d in [OUT,EVIDENCE]:assert not (d/'running.lock').exists()
    proposal=read(OUT/'phase-timing-v1-proposal.json')
    source=ROOT/proposal['source'];candidate=ROOT/proposal['candidate']
    assert sha(source)==proposal['source_sha256'] and sha(candidate)==proposal['candidate_sha256']
    storage=ROOT/'crates/solver/src/gpu/continuation_storage.rs'
    assert sha(storage)==read(OUT/'reuse-download-v1-proposal.json')['candidate_sha256']
    assert not (OUT/f'{LABEL}-build-freeze.json').exists()
    source.write_bytes(candidate.read_bytes())
    files=[p for p in (ROOT/'crates/solver/src').rglob('*') if p.suffix in ['.rs','.cu']]
    files += [source,ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',SUB,OUT/'connected-three.json',
        OUT/'PHASE-TIMING-PROTOCOL.md',OUT/'PHASE-PILOT-PROTOCOL.md',OUT/'phase-timing-v1-proposal.json',Path(__file__),
        OUT/'storage-fresh-pair-v1-review.json',OUT/'reuse-download-v1-long-review.json',OUT/'reuse-download-v1-proposal.json',
        OUT/'v2-resident-result.json',ROOT/'tools/research/storage_owner_review_20260920.py',
        ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in files}
    with (OUT/f'{LABEL}-build-freeze.json').open('x') as f:json.dump(dict(inputs=frozen),f,indent=2)
    def verify():
        for p,h in frozen.items():assert sha(ROOT/p)==h,p
    status=dict(step='building',pid=os.getpid(),created=psutil.Process().create_time())
    def report():(OUT/f'{LABEL}-status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    env=os.environ.copy();env.update(CARGO_BUILD_JOBS='2',RAYON_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1')
    env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
    owned={};child=None
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    try:
        report();started=time.monotonic();buildlog=OUT/f'{LABEL}-build.log'
        with buildlog.open('x') as log:
            child=subprocess.Popen(['cargo','build','--example','integrated_continuation_stored','--locked','--release','-p','solver',
                '--features','preflop-research','--target-dir','target/ssd-connected-research','--message-format=json'],
                cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            owned[child.pid]=psutil.Process(child.pid).create_time()
            while child.poll() is None:
                try:
                    for p in psutil.Process(child.pid).children(recursive=True):owned[p.pid]=p.create_time()
                except psutil.NoSuchProcess:pass
                assert time.monotonic()-started<600 and psutil.virtual_memory().available>=20_000_000_000
                assert idle(),'Production active during research build'
                time.sleep(2)
            assert child.returncode==0,'Build failed; preserve evidence'
        verify();artifacts=[]
        for line in buildlog.read_text().splitlines():
            try:r=json.loads(line)
            except json.JSONDecodeError:continue
            if r.get('reason')=='compiler-artifact' and r.get('executable') and r['target']['name']=='integrated_continuation_stored':artifacts.append(Path(r['executable']))
        assert len(artifacts)==1 and artifacts[0].resolve().is_relative_to((ROOT/'target/ssd-connected-research').resolve())
        exe=ROOT/'target/qualified-paging'/f'{LABEL}-connected.exe';assert not exe.exists()
        shutil.copyfile(artifacts[0],exe);assert sha(exe)==sha(artifacts[0])
        runtime=dict(inputs=frozen,exe=str(exe),exe_sha256=sha(exe),build_seconds=time.monotonic()-started)
        with (OUT/f'{LABEL}-runtime-freeze.json').open('x') as f:json.dump(runtime,f,indent=2)
        scratch=Path('S:/GTOpen-research')/LABEL;assert not scratch.exists();scratch.mkdir()
        destination=OUT/f'{LABEL}-result.json';assert not destination.exists()
        env.update(GTO_SSD_STUDY_DIR=str(scratch),GTO_STORAGE_RAM_BYTES=str(2**63),GTO_STORAGE_WRITE_CAP='0',
            GTO_RESEARCH_MAX_SECONDS='900',GTO_RESEARCH_PROTOCOL=str((OUT/'PHASE-TIMING-PROTOCOL.md').relative_to(ROOT)))
        status['step']='qualifying-20-iterations';report()
        subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',str(exe),LABEL,str(SUB.relative_to(ROOT)),
            str((OUT/'connected-three.json').relative_to(ROOT)),str(destination.relative_to(ROOT)),'20'],cwd=ROOT,env=env,check=True)
        verify();assert sha(exe)==runtime['exe_sha256']
        r=read(destination);assert science(r)==science(read(OUT/'v2-resident-result.json'))
        assert r['manifest']==read(OUT/'connected-three.json') and [x['iteration'] for x in r['records']]==[1,20]
        original=read(OUT/'reuse-download-v1-ram-result.json')['storage'];assert r['storage']==original
        guard=read(EVIDENCE/f'{LABEL}-status.json');assert guard['exit_code']==0 and guard['error'] is None
        samples=read(EVIDENCE/f'{LABEL}-resources.json')
        assert min(x['free_host_bytes'] for x in samples)>=20_000_000_000 and min(x['free_gpu_bytes'] for x in samples)>=3_000_000_000
        phases=phase_review((EVIDENCE/f'{LABEL}.log').read_text(),20,[1,20],r)
        review=dict(passed=True,scientific_outputs_exact=True,phase_measurements=phases,result_sha256=sha(destination),
            production_ready=False,scope='Instrumentation exactness on three development boards; not strategic accuracy or broad performance.')
        with (OUT/f'{LABEL}-review.json').open('x') as f:json.dump(review,f,indent=2)
        status['step']='complete-instrumentation-qualified'
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:
        if child is not None and child.poll() is None:
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

if __name__=='__main__':main()
