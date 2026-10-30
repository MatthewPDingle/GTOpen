"""Build exact real-type observer with restoration, then run one CPU-only mapping test."""
import json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/E127-host-control';P=h.read(H/'protocol.json');O=H/'execution';T=Path(P['target'])
assert len(sys.argv)==2
def verify():
    h.pin(H/'protocol.json',sys.argv[1])
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
def active_guard():
    assert h.ar.source_identity()['source_sha256']==P['accepted_source_sha256']|P['candidate_owned_sha256']
    assert set(subprocess.check_output(['git','diff','--name-only','HEAD','--','Cargo.lock','crates/solver'],cwd=h.REPO,text=True).splitlines())==set(P['tracked_owned_paths'])
    old=h.read(h.EPOCH/'preexisting-target-artifacts.json')
    assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','crates/solver'],cwd=h.REPO,text=True).splitlines())==set(old)|set(P['new_owned_paths'])
    for name,value in old.items():h.pin(h.REPO/name,value['sha256'])
    main=h.read(h.EPOCH/'protected-main.json')
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main['root'],text=True).strip()==main['git_head']
    for name,digest in main['source_sha256'].items():h.pin(Path(main['root'])/name,digest)
    h.pin(main['live_path'],main['live_sha256'])
verify();h.custody();O.mkdir(exist_ok=False);assert not T.exists()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    command=['cargo','test','--release','--offline','--locked','--target-dir',str(T),'-p','solver','--features','preflop-research','--lib','--no-run','--message-format=json']
    error=None
    try:
        for name,value in P['owned'].items():shutil.copyfile(value['candidate'],h.REPO/name)
        active_guard();h.child(command,O,'cargo',1800);verify();active_guard()
        records=[json.loads(line)for line in(O/'cargo.stdout.log').read_text(encoding='utf-8').splitlines()]
        artifacts=[x for x in records if x.get('reason')=='compiler-artifact'and x.get('profile',{}).get('test')and x.get('executable')and x['target']['name']=='solver']
        assert len(artifacts)==1 and artifacts[0]['features']==P['features']and not artifacts[0]['fresh']
        artifact=artifacts[0];binary=ROOT/'binaries/E127-host-control.exe';assert not binary.exists();shutil.copyfile(artifact['executable'],binary)
        manifest={**h.ar.source_identity(),'candidate':'E127-host-control','binary_sha256':h.sha(binary),'artifact':artifact,'build_protocol_sha256':sys.argv[1],'build_at':h.now(),'observer_only':True,'GPU_application_kernels':0}
        h.save(binary.with_suffix('.manifest.json'),manifest)
        h.save(O/'build.json',{'at':h.now(),'binary':str(binary),'binary_sha256':h.sha(binary),'manifest_sha256':h.sha(binary.with_suffix('.manifest.json')),'source':manifest['source_sha256'],'GPU_application_kernels':0})
    except BaseException as failure:
        error=repr(failure);h.save(O/'build-failure.json',{'at':h.now(),'error':error});raise
    finally:
        for name,value in P['owned'].items():
            path=h.REPO/name;assert path.resolve().is_relative_to(h.REPO.resolve())
            if value['base']is None:
                if path.exists():h.pin(path,value['candidate_sha256']);path.unlink()
            else:
                assert h.sha(path)in[value['base_sha256'],value['candidate_sha256']];shutil.copyfile(value['base'],path)
        h.custody();h.save(O/'restoration.json',{'at':h.now(),'accepted_source_restored':True,'main_live_protected_PTX_unchanged':True,'error':error})
    os.environ['E127_HOST_INPUTS']=str(H/'cases.json');os.environ['E127_HOST_OUTPUT']=str(O/'raw')
    try:h.child([str(binary),P['test_name'],'--exact','--ignored','--nocapture','--test-threads=1'],O,'control',1200)
    finally:os.environ.pop('E127_HOST_INPUTS',None);os.environ.pop('E127_HOST_OUTPUT',None)
    verify();h.custody();h.child([sys.executable,str(ROOT/'runs/E127-read-host-control.py'),sys.argv[1]],O,'reader',1200);verify();h.custody()
print(json.dumps({'host_report_sha256':h.sha(H/'report.json'),'GPU_appkernels':0}),flush=True)
