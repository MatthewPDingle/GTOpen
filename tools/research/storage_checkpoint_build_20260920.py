"""Apply the checkpoint proposal after phase diagnosis; qualify format and short trajectory."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle
from storage_phase_run_20260920 import ROOT,OUT,EVIDENCE,SUB,read,sha,phase_review
from storage_owner_review_20260920 import science
LABEL='checkpoint-v1'

def main():
    assert read(OUT/'phase-pilot-v1-review.json')['diagnostic_passed']
    prior=read(OUT/'phase-pilot-v1-status.json');assert prior['step']=='complete-diagnostic-reviewed'
    try:assert psutil.Process(prior['pid']).create_time()!=prior['created'],'Phase pilot still live'
    except psutil.NoSuchProcess:pass
    assert idle() and psutil.virtual_memory().available>=30_000_000_000
    for d in [OUT,EVIDENCE]:assert not (d/'running.lock').exists()
    phase=read(OUT/'phase-timing-v1-runtime-freeze.json')
    for p,h in phase['inputs'].items():assert sha(ROOT/p)==h,p
    assert sha(Path(phase['exe']))==phase['exe_sha256']
    assert not (OUT/f'{LABEL}-build-freeze.json').exists()
    proposal=read(OUT/f'{LABEL}-proposal.json')
    for name in ['disk','storage','example','helper']:
        spec=proposal[name];source=ROOT/spec['source'];candidate=ROOT/spec['candidate']
        assert sha(candidate)==spec['candidate_sha256']
        if name=='helper':assert not source.exists()
        else:assert sha(source)==spec['source_sha256'],name
    for name in ['disk','storage','example','helper']:
        spec=proposal[name];source=ROOT/spec['source'];source.parent.mkdir(exist_ok=True)
        source.write_bytes((ROOT/spec['candidate']).read_bytes())
    files=[p for p in (ROOT/'crates/solver/src').rglob('*') if p.suffix in ['.rs','.cu']]
    files += [ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',SUB,OUT/'connected-three.json',
        ROOT/proposal['example']['source'],ROOT/proposal['helper']['source'],OUT/f'{LABEL}-proposal.json',
        OUT/'RESUMABLE-STUDY-PROTOCOL.md',OUT/'phase-pilot-v1-review.json',OUT/'phase-timing-v1-runtime-freeze.json',
        Path(__file__),ROOT/'tools/research/storage_checkpoint_long_20260920.py',ROOT/'tools/research/storage_checkpoint_negative_20260920.py',
        ROOT/'tools/research/storage_phase_run_20260920.py',ROOT/'tools/research/storage_owner_review_20260920.py',
        ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py',
        OUT/'v2-resident-result.json',OUT/'reuse-download-v1-ram-result.json',OUT/'long-ram-v1-resident-result.json']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in files}
    freeze_path=OUT/f'{LABEL}-build-freeze.json'
    with freeze_path.open('x') as f:json.dump(dict(inputs=frozen),f,indent=2)
    def verify():
        for p,h in frozen.items():assert sha(ROOT/p)==h,p
    status=dict(step='building',pid=os.getpid(),created=psutil.Process().create_time())
    def report():(OUT/f'{LABEL}-status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    env=os.environ.copy()
    for k in ['GTO_RESUME_CHECKPOINT','GTO_SAVE_CHECKPOINT','GTO_RESTORED_COPY','GTO_CHECKPOINT_FORMAT_ROOT']:env.pop(k,None)
    env.update(CARGO_BUILD_JOBS='2',RAYON_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1')
    env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
    owned={};child=None
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    try:
        report();started=time.monotonic();logpath=OUT/f'{LABEL}-build.log'
        with logpath.open('x') as log:
            child=subprocess.Popen(['cargo','build','--example','integrated_continuation_stored','--locked','--release','-p','solver',
                '--features','preflop-research','--target-dir','target/ssd-connected-research','--message-format=json'],
                cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            owned[child.pid]=psutil.Process(child.pid).create_time()
            while child.poll() is None:
                try:
                    for p in psutil.Process(child.pid).children(recursive=True):owned[p.pid]=p.create_time()
                except psutil.NoSuchProcess:pass
                assert idle() and psutil.virtual_memory().available>=20_000_000_000 and time.monotonic()-started<600
                time.sleep(2)
            assert child.returncode==0,'Checkpoint build failed; preserve diagnostic'
        verify();artifacts=[]
        for line in logpath.read_text().splitlines():
            try:r=json.loads(line)
            except json.JSONDecodeError:continue
            if r.get('reason')=='compiler-artifact' and r.get('executable') and r['target']['name']=='integrated_continuation_stored':artifacts.append(Path(r['executable']))
        assert len(artifacts)==1 and artifacts[0].resolve().is_relative_to((ROOT/'target/ssd-connected-research').resolve())
        exe=ROOT/'target/qualified-paging'/f'{LABEL}-connected.exe';assert not exe.exists();shutil.copyfile(artifacts[0],exe)
        assert sha(exe)==sha(artifacts[0])
        identity_path=OUT/f'{LABEL}-identity.json'
        with identity_path.open('x') as f:json.dump(dict(executable_sha256=sha(exe),source_manifest_sha256=sha(freeze_path),
            subtree_sha256=sha(SUB),boards_sha256=sha(OUT/'connected-three.json')),f,indent=2)
        runtime=dict(inputs=frozen,exe=str(exe),exe_sha256=sha(exe),identity=str(identity_path),identity_sha256=sha(identity_path),
            build_seconds=time.monotonic()-started)
        with (OUT/f'{LABEL}-runtime-freeze.json').open('x') as f:json.dump(runtime,f,indent=2)
        env.update(GTO_STORAGE_RAM_BYTES=str(2**63),GTO_STORAGE_WRITE_CAP='0',GTO_STUDY_IDENTITY_FILE=str(identity_path),
            GTO_RESEARCH_MAX_SECONDS='900',GTO_RESEARCH_PROTOCOL=str((OUT/'RESUMABLE-STUDY-PROTOCOL.md').relative_to(ROOT)))
        for stage,args in [('format',[]),('20',[str(SUB.relative_to(ROOT)),str((OUT/'connected-three.json').relative_to(ROOT)),
            str((OUT/f'{LABEL}-20-result.json').relative_to(ROOT)),'20'])]:
            scratch=Path('S:/GTOpen-research')/(LABEL+'-'+stage);assert not scratch.exists();scratch.mkdir()
            assert shutil.disk_usage(scratch).free>=40_000_000_000
            env['GTO_SSD_STUDY_DIR']=str(scratch)
            if stage=='format':env['GTO_CHECKPOINT_FORMAT_ROOT']=str(scratch/'format')
            else:env.pop('GTO_CHECKPOINT_FORMAT_ROOT',None)
            status['step']=stage;report();assert idle()
            subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',str(exe),LABEL+'-'+stage,*args],cwd=ROOT,env=env,check=True)
            verify();assert sha(exe)==runtime['exe_sha256'] and sha(identity_path)==runtime['identity_sha256']
            guard=read(EVIDENCE/f'{LABEL}-{stage}-status.json');assert guard['exit_code']==0 and guard['error'] is None
            sample_path=EVIDENCE/f'{LABEL}-{stage}-resources.json'
            samples=read(sample_path) if sample_path.exists() else []
            if samples:
                assert min(s['free_host_bytes'] for s in samples)>=20_000_000_000 and min(s['free_gpu_bytes'] for s in samples)>=3_000_000_000
            else:assert stage=='format','No resource observations for GPU trajectory'
        lines=(EVIDENCE/f'{LABEL}-format.log').read_text().splitlines()
        probes=[json.loads(l.split('CHECKPOINT_FORMAT ',1)[1]) for l in lines if l.startswith('CHECKPOINT_FORMAT ')]
        assert len(probes)==1;probe=probes[0]
        assert all(probe[k] for k in ['f64_bits_exact','signed_zero_exact','existing_record_preserved']) and probe['rejected_cases']==8
        assert all(probe['canonical'][k] for k in ['f32_bits_exact','signed_zero_exact','existing_record_preserved']) and probe['canonical']['rejected_cases']==11
        r=read(OUT/f'{LABEL}-20-result.json');assert science(r)==science(read(OUT/'v2-resident-result.json'))
        assert r['resumed_iteration']==0 and r['storage']==read(OUT/'reuse-download-v1-ram-result.json')['storage']
        phases=phase_review((EVIDENCE/f'{LABEL}-20.log').read_text(),20,[1,20],r)
        review=dict(passed=True,format=probe,scientific_outputs_exact=True,phase_measurements=phases,
            result_sha256=sha(OUT/f'{LABEL}-20-result.json'),fresh_process_resume_qualified=False,production_ready=False)
        with (OUT/f'{LABEL}-review.json').open('x') as f:json.dump(review,f,indent=2)
        status['step']='complete-format-and-20-iteration-qualified'
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
