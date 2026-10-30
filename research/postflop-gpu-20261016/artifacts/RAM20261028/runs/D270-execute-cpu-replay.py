import ctypes, json, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2
H=ROOT/'runs/D270-actual-metadata-CPU';P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1])
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
    for v in P['owned'].values():
        h.pin(v['source'],v['source_sha256'])
        assert Path(v['source']).read_bytes()[:v['candidate_prefix_bytes']]==(ROOT/'runs/E115-source-v2/candidate'/Path(v['source']).name).read_bytes()
def guard():
    assert h.ar.source_identity()['source_sha256']==P['accepted_source_sha256']|{n:v['source_sha256']for n,v in P['owned'].items()}
    targets=h.read(ROOT/'epoch/preexisting-target-artifacts.json')
    for n,v in targets.items():h.pin(h.REPO/n,v['sha256'])
    assert set(subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver','Cargo.lock'],cwd=h.REPO,text=True).splitlines())=={n for n,v in P['owned'].items()if v['original']}
    assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','crates/solver'],cwd=h.REPO,text=True).splitlines())==set(targets)|{n for n,v in P['owned'].items()if not v['original']}
    m=h.read(ROOT/'epoch/protected-main.json')
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=m['root'],text=True).strip()==m['git_head']
    for n,d in m['source_sha256'].items():h.pin(Path(m['root'])/n,d)
    h.pin(m['live_path'],m['live_sha256'])
class Memory(ctypes.Structure):
    _fields_=[('length',ctypes.c_uint32),('load',ctypes.c_uint32)]+[(n,ctypes.c_uint64)for n in['total_physical','available_physical','total_page','available_page','total_virtual','available_virtual','extended']]
def available():
    m=Memory();m.length=ctypes.sizeof(m);assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m));return m.available_physical
verify();h.custody();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert not Path(P['target']).exists()and not(H/'output').exists()
    assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']and available()>=P['required_available_RAM_bytes']
    assert not{k:v for k,v in h.env().items()if k in['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_TARGET_DIR']or k.startswith('CARGO_PROFILE_RELEASE_')or(k.startswith('CARGO_TARGET_')and k.endswith('_RUSTFLAGS'))}
    cmd=['cargo','test','--release','--locked','--offline','--target-dir',P['target'],'-p','solver','--features','continuation-transfer-research','--lib','--no-run','--message-format=json']
    fault=None
    try:
        for name,v in P['owned'].items():shutil.copyfile(v['source'],h.REPO/name)
        guard();h.child(cmd,O,'compile',1800);verify();guard()
        events=[json.loads(line)for line in(O/'compile.stdout.log').read_text(encoding='utf-8').splitlines()]
        assert any(x.get('reason')=='build-finished'and x.get('success')for x in events)
        tests=[x for x in events if x.get('reason')=='compiler-artifact'and x.get('executable')and x.get('profile',{}).get('test')and x['target']['name']=='solver']
        assert len(tests)==1 and tests[0]['fresh']is False
        path=Path(tests[0]['executable']);assert path.resolve().is_relative_to(Path(P['target']).resolve());exe=O/'actual-cpu-replay.exe';shutil.copyfile(path,exe)
        h.save(O/'build-manifest.json',{'at':h.now(),'source_sha256':h.ar.source_identity()['source_sha256'],'binary_sha256':h.sha(exe),'cargo_artifact':tests[0],'protocol_sha256':sys.argv[1],'GPU_executions':0})
    except BaseException as error:
        fault=repr(error);h.save(O/'compile-failure.json',{'at':h.now(),'error':fault,'native_executions':0});raise
    finally:
        for name,v in P['owned'].items():
            dest=h.REPO/name
            if v['original']:
                assert h.sha(dest)in[v['source_sha256'],v['original_sha256']];shutil.copyfile(v['original'],dest)
            elif dest.exists():
                h.pin(dest,v['source_sha256']);assert dest.resolve().is_relative_to(h.REPO.resolve());dest.unlink()
        h.custody();h.save(O/'restoration.json',{'at':h.now(),'accepted_main_live_protected_PTX_unchanged':True,'error':fault})
    assert available()>=P['required_available_RAM_bytes']
    h.child([str(exe),'--exact','gpu::d270_cpu_replay::production_metadata_replay','--nocapture','--test-threads=1'],O,'native',1800)
    verify();h.custody();assert sum(p.stat().st_size for p in(H/'output').iterdir())<=P['raw_output_reservation_bytes']
    h.child([sys.executable,str(ROOT/'runs/D270-root-replay.py'),sys.argv[1]],O,'reader',1800)
    verify();h.custody();h.save(O/'complete.json',{'at':h.now(),'root_report_sha256':h.sha(H/'root-report.json'),'all_owned_compilers_native_helpers_and_readers_terminal':True,'candidate_GPU_constructors_CUDA_APIs_kernels_solves_speed_samples':0,'accepted_main_live_protected_PTX_unchanged':True})
print('D270 full actual production metadata CPU replay passed; no GPU or speed qualification.',flush=True)
