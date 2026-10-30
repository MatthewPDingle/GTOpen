import ctypes,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2
H=ROOT/'runs/D274-spot-observation';P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.pin(P['observed_path'],P['observed_sha256']);h.pin(P['baseline_path'],P['baseline_sha256'])
    for p,d in P['input_sha256'].items():h.pin(p,d)
def guard():
    assert h.ar.source_identity()['source_sha256']==P['accepted_source_sha256']|{P['owned_path']:P['observed_sha256']}
    assert subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver','Cargo.lock'],cwd=h.REPO,text=True).splitlines()==[P['owned_path']]
    m=h.read(ROOT/'epoch/protected-main.json');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=m['root'],text=True).strip()==m['git_head']
    for n,d in m['source_sha256'].items():h.pin(Path(m['root'])/n,d)
    h.pin(m['live_path'],m['live_sha256'])
    targets=h.read(ROOT/'epoch/preexisting-target-artifacts.json')
    for n,v in targets.items():h.pin(h.REPO/n,v['sha256'])
    assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','crates/solver'],cwd=h.REPO,text=True).splitlines())==set(targets)
class Memory(ctypes.Structure):
    _fields_=[('length',ctypes.c_uint32),('load',ctypes.c_uint32)]+[(n,ctypes.c_uint64)for n in['total','available','total_page','available_page','total_virtual','available_virtual','extended']]
def available():
    m=Memory();m.length=ctypes.sizeof(m);assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m));return m.available
verify();h.custody();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert not Path(P['target']).exists();assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']and available()>=P['required_available_RAM_bytes']
    assert not{k:v for k,v in h.env().items()if k in['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_TARGET_DIR']or k.startswith('CARGO_PROFILE_RELEASE_')or(k.startswith('CARGO_TARGET_')and k.endswith('_RUSTFLAGS'))}
    command=['cargo','test','--release','--locked','--offline','--target-dir',P['target'],'-p','solver','--lib','--no-run','--message-format=json'];fault=None
    try:
        shutil.copyfile(P['observed_path'],h.REPO/P['owned_path']);guard();h.child(command,O,'compile',1800);verify();guard()
        records=[json.loads(line)for line in(O/'compile.stdout.log').read_text(encoding='utf-8').splitlines()];assert any(x.get('reason')=='build-finished'and x.get('success')for x in records)
        tests=[x for x in records if x.get('reason')=='compiler-artifact'and x.get('executable')and x.get('profile',{}).get('test')and x['target']['name']=='solver'];assert len(tests)==1 and tests[0]['fresh']is False and tests[0]['features']==[]
        exe=O/'spot-observer.exe';source=Path(tests[0]['executable']);assert source.resolve().is_relative_to(Path(P['target']).resolve());shutil.copyfile(source,exe)
        h.save(O/'build-manifest.json',{'at':h.now(),'source_sha256':h.ar.source_identity()['source_sha256'],'binary_sha256':h.sha(exe),'cargo_artifact':tests[0],'protocol_sha256':sys.argv[1],'CPU_only_no_GPU_features':True})
    except BaseException as error:
        fault=repr(error);h.save(O/'compile-failure.json',{'at':h.now(),'error':fault,'native_cases':0});raise
    finally:
        assert h.sha(h.REPO/P['owned_path'])in[P['observed_sha256'],P['baseline_sha256']];shutil.copyfile(P['baseline_path'],h.REPO/P['owned_path']);h.custody();h.save(O/'restoration.json',{'at':h.now(),'accepted_main_live_protected_PTX_unchanged':True,'error':fault})
    for case in P['sequence']:
        verify();h.custody();h.ar.refuse_active(h.ar.live_status());assert available()>=P['required_available_RAM_bytes']and shutil.disk_usage(ROOT).free>=P['required_free_bytes']
        output=H/case['id'];assert not output.exists();os.environ['D274_OUTPUT']=str(output);os.environ['D274_ORDER']=case['order']
        h.save(O/(case['id']+'.environment.json'),{'D274_OUTPUT':str(output),'D274_ORDER':case['order'],'RAYON_NUM_THREADS':h.env()['RAYON_NUM_THREADS'],'affinity':'default','CPU_only':True})
        h.child([str(exe),'--exact','game::d274_observer::observe','--nocapture','--test-threads=1'],O,case['id'],1800)
        verify();h.custody();assert sum(p.stat().st_size for c in P['sequence']for p in(H/c['id']).glob('*')if p.is_file())<=P['raw_reservation_bytes']
    h.child([sys.executable,str(ROOT/'runs/D274-root-observation.py'),sys.argv[1]],O,'reader',1800)
    verify();h.custody();h.save(O/'complete.json',{'at':h.now(),'root_report_sha256':h.sha(H/'report.json'),'all_owned_compilers_native_CPU_and_readers_terminal':True,'new_GPU_CFR_solver_or_speed_samples':0,'accepted_main_live_protected_PTX_unchanged':True})
print('D274 fresh CPU-only observations and full Spot outputs verified.',flush=True)
