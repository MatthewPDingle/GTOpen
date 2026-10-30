"""Fresh E110 Cargo builds with exact restoration,including new module/dependency edges."""
import sys,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E110-build-plan';P=h.read(H/'protocol.json');BASE=P['accepted_source_sha256'];OUT=ROOT/'runs/E110-final-build'
def verify():
    h.pin(H/'protocol.json',sys.argv[1])
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
def guard():
    assert h.ar.source_identity()['source_sha256']==BASE|P['candidate_owned_sha256']
    m=h.read(h.EPOCH/'protected-main.json');main=Path(m['root']);assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()==m['git_head']
    for name,digest in m['source_sha256'].items():h.pin(main/name,digest)
    for name in m['absent_research_paths']:assert not(main/name).exists()
    h.pin(m['live_path'],m['live_sha256'])
    targets=h.read(h.EPOCH/'preexisting-target-artifacts.json')
    for name,value in targets.items():h.pin(h.REPO/name,value['sha256'])
    assert set(subprocess.check_output(['git','diff','--name-only','HEAD','--','Cargo.lock','crates/solver'],cwd=h.REPO,text=True).splitlines())==set(P['tracked_owned_paths'])
    assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','crates/solver'],cwd=h.REPO,text=True).splitlines())==set(targets)|set(P['new_owned_paths'])
verify();h.custody();OUT.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    for phase in P['phases']:
        assert Path(phase['target'])==ROOT/('build-e110-final-'+phase['id'])
        assert not Path(phase['target']).exists()
        for stem in phase['outputs'].values():assert not(ROOT/'binaries'/(stem+'.exe')).exists() and not(ROOT/'binaries'/(stem+'.manifest.json')).exists()
    for phase in P['phases']:
        verify();h.custody();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
        out=OUT/phase['id'];out.mkdir();target=Path(phase['target']);target.mkdir();env=h.env()
        forbidden={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET','CARGO_TARGET_DIR'}
        assert not{k:v for k,v in env.items() if k in forbidden or k.startswith('CARGO_PROFILE_RELEASE_') or(k.startswith('CARGO_TARGET_') and k.endswith('_RUSTFLAGS'))}
        cmd=['cargo','test','--release','--locked','--offline','--target-dir',str(target),'-p','solver','--features',phase['features'],'--lib']
        if phase['integration']:cmd+=['--test','postflop_autoresearch']
        cmd+=['--no-run','--message-format=json'];fault=None
        try:
            for name,value in P['owned'].items():shutil.copyfile(value['candidate'],h.REPO/name);shutil.copyfile(value['candidate'],out/Path(name).name)
            guard();h.child(cmd,out,'cargo',1800);verify();guard()
            records=[json.loads(x) for x in (out/'cargo.stdout.log').read_text(encoding='utf-8').splitlines()];assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in records)
            artifacts=[x for x in records if x.get('reason')=='compiler-artifact']
            for record in artifacts:
                for path in record.get('filenames',[])+([record['executable']] if record.get('executable') else []):assert Path(path).resolve().is_relative_to(target.resolve())
            dependencies={p:h.sha(p) for x in artifacts for p in x.get('filenames',[]) if Path(p).is_file() and Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
            tests=[x for x in artifacts if x.get('profile',{}).get('test') and x.get('executable') and x['target']['name'] in phase['outputs']]
            assert len(tests)==len(phase['outputs']) and {x['target']['name'] for x in tests}==set(phase['outputs']);pins={}
            for test in tests:
                assert test['fresh'] is False and test['features']==phase['expected_features'];name=test['target']['name'];binary=ROOT/'binaries'/(phase['outputs'][name]+'.exe')
                expected=h.REPO/('crates/solver/src/lib.rs' if name=='solver' else 'crates/solver/tests/postflop_autoresearch.rs');assert Path(test['target']['src_path']).resolve()==expected.resolve()
                data=Path(test['executable']).read_bytes();assert (h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes() in data and b'partial += (float)value;' in data
                shutil.copyfile(test['executable'],binary)
                manifest={**h.ar.source_identity(),'candidate':'E110','measurement_epoch':'RAM20261028','phase':phase['id'],'binary_sha256':h.sha(binary),'built_at':h.now(),'build_command':cmd,'cargo_artifact':test,'dependency_artifact_sha256':dependencies,'source_copies':{n:{'path':str(out/Path(n).name),'sha256':v['candidate_sha256']} for n,v in P['owned'].items()},'build_log_sha256':h.sha(out/'cargo.stdout.log'),'build_protocol_sha256':sys.argv[1],'build_script_sha256':h.sha(__file__),'candidate_accepted':False,'control_only':phase['id']=='feature'}
                h.save(binary.with_suffix('.manifest.json'),manifest)
                for path in [binary,binary.with_suffix('.manifest.json')]:pins[str(path)]=h.sha(path)
            h.save(out/'complete.json',{'at':h.now(),'source_sha256':BASE|P['candidate_owned_sha256'],'command':cmd,'returncode':0,'artifact_sha256':pins,'dependency_sha256':dependencies,'stdout_sha256':h.sha(out/'cargo.stdout.log'),'stderr_sha256':h.sha(out/'cargo.stderr.log'),'native_executions':0})
        except BaseException as error:
            fault=repr(error);h.save(out/'failure.json',{'at':h.now(),'error':fault,'native_executions':0});raise
        finally:
            for name,value in P['owned'].items():
                path=h.REPO/name;assert path.resolve().is_relative_to(h.REPO.resolve())
                if value['base'] is None:
                    if path.exists():h.pin(path,value['candidate_sha256']);path.unlink()
                else:
                    assert h.sha(path) in [value['base_sha256'],value['candidate_sha256']];shutil.copyfile(value['base'],path)
            h.custody();h.save(out/'restoration.json',{'at':h.now(),'accepted_source_restored':True,'only_verified_owned_new_module_removed':True,'main_live_protected_PTX_unchanged':True,'error':fault})
        print(phase['id'],'terminal;accepted E080restored.',flush=True)
    h.save(OUT/'complete.json',{'at':h.now(),'all_compilers_terminal':True,'native_executions':0,'build_protocol_sha256':sys.argv[1],'evidence_sha256':{str(p):h.sha(p) for p in OUT.rglob('*.json')}})
print('E110 fresh integrated builds complete;no native solver orspeed samples yet.',flush=True)
