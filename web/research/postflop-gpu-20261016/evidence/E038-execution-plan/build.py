"""Build only: frozen E038 variants, serialized, with exact source restoration."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'))
import common as previous
ar=previous.ar
read,sha,pin,save,now,child=previous.read,previous.sha,previous.pin,previous.save,previous.now,previous.child
assert len(sys.argv)==2,'Supply frozen protocol SHA256'
pin(HERE/'protocol.json',sys.argv[1]);P=read(HERE/'protocol.json')
ROOT=ar.RESEARCH;REPO=ar.REPO;OWNED='crates/solver/src/gpu/arena.rs'
BASE=read(P['baseline']['path'])['source_sha256']
OUT=ROOT/'runs/E038-build';BIN=ROOT/'binaries'

def verify():
    pin(HERE/'protocol.json',sys.argv[1])
    for p,h in P['input_sha256'].items():pin(p,h)

def guard(arena_hash):
    assert ar.source_identity()['source_sha256']==BASE|{OWNED:arena_hash},'source drift'
    main=read(P['protected_main_path']);mp=Path(main['root'])
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=mp,text=True).strip()==main['git_head']
    for n,h in main['source_sha256'].items():pin(mp/n,h)
    for n in main['absent_research_paths']:assert not (mp/n).exists(),n
    pin(main['live_path'],main['live_sha256'])
    for n,v in P['protected_ptx'].items():pin(REPO/n,v['sha256'])
    changed=subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=REPO,text=True).splitlines()
    assert set(changed)==({OWNED} if arena_hash!=BASE[OWNED] else set())

verify()
with ar.exclusive_lock(ROOT/'gpu-run.lock'):
    previous.custody();ar.refuse_active(ar.live_status())
    assert not OUT.exists();OUT.mkdir()
    for phase in P['build_phases']:
        assert not Path(phase['target']).exists()
        for name in phase['outputs'].values():
            assert not (BIN/(name+'.exe')).exists()
            assert not (BIN/(name+'.manifest.json')).exists()
    for phase in P['build_phases']:
        verify();previous.custody();ar.refuse_active(ar.live_status())
        assert shutil.disk_usage(ROOT).free>=54*1024**3
        out=OUT/phase['id'];out.mkdir();target=Path(phase['target']);target.mkdir()
        archive=Path(phase['source']);arena_hash=phase['source_sha256'];pin(archive,arena_hash)
        e=previous.env()
        forbidden={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET'}
        assert not {k:v for k,v in e.items() if k in forbidden or k.startswith('CARGO_PROFILE_RELEASE_') or (k.startswith('CARGO_TARGET_') and k.endswith('_RUSTFLAGS'))}
        e['CARGO_TARGET_DIR']=str(target)
        cmd=['cargo','test','--release','--locked','--offline','-p','solver','--features',phase['features'],'--lib']
        if phase['integration']:cmd+=['--test','postflop_autoresearch']
        cmd+=['--no-run','--message-format=json']
        save(out/'before.json',{'at':now(),'accepted_source_sha256':BASE,'protocol_sha256':sys.argv[1],'target_previously_absent':True})
        fault=None
        try:
            shutil.copyfile(archive,REPO/OWNED);shutil.copyfile(archive,out/'arena.rs');guard(arena_hash)
            child(cmd,out,'cargo',e,1800)
            verify();guard(arena_hash)
            records=[json.loads(line) for line in (out/'cargo.stdout.log').read_text(encoding='utf-8').splitlines()]
            assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in records)
            artifacts=[x for x in records if x.get('reason')=='compiler-artifact']
            for x in artifacts:
                for f in x.get('filenames',[])+([x['executable']] if x.get('executable') else []):assert Path(f).resolve().is_relative_to(target.resolve())
            deps={f:sha(f) for x in artifacts for f in x.get('filenames',[]) if Path(f).is_file() and Path(f).suffix in ['.rlib','.rmeta','.lib','.dll']}
            tests=[x for x in artifacts if x.get('profile',{}).get('test') and x.get('executable') and x['target']['name'] in phase['outputs']]
            assert {x['target']['name'] for x in tests}==set(phase['outputs']) and len(tests)==len(phase['outputs'])
            expected_features=['gpu','preflop-research'] if phase['features']=='preflop-research' else ['gpu']
            pins={}
            for x in tests:
                assert x['fresh'] is False and x['features']==expected_features
                name=x['target']['name'];src=Path(x['executable']);dest=BIN/(phase['outputs'][name]+'.exe')
                expected_src=REPO/('crates/solver/src/lib.rs' if name=='solver' else 'crates/solver/tests/postflop_autoresearch.rs')
                assert Path(x['target']['src_path']).resolve()==expected_src.resolve()
                assert Path(x['manifest_path']).resolve()==(REPO/'crates/solver/Cargo.toml').resolve()
                cuda=(REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();assert cuda in src.read_bytes()
                shutil.copyfile(src,dest)
                manifest={**ar.source_identity(),'candidate':'E038','phase':phase['id'],'binary_sha256':sha(dest),'built_at':now(),'build_command':cmd,'cargo_artifact':x,'dependency_artifact_sha256':deps,'source_copies':{OWNED:{'path':str(out/'arena.rs'),'sha256':arena_hash}},'build_log':str(out/'cargo.stdout.log'),'build_log_sha256':sha(out/'cargo.stdout.log'),'protocol_sha256':sys.argv[1],'build_script_sha256':sha(HERE/'build.py'),'control_only':phase['control'],'candidate_accepted':False}
                save(dest.with_suffix('.manifest.json'),manifest)
                pins[str(dest)]=sha(dest);pins[str(dest.with_suffix('.manifest.json'))]=sha(dest.with_suffix('.manifest.json'))
            save(out/'complete.json',{'at':now(),'source_sha256':BASE|{OWNED:arena_hash},'command':cmd,'returncode':0,'artifact_sha256':pins,'dependency_sha256':deps,'stdout_sha256':sha(out/'cargo.stdout.log'),'stderr_sha256':sha(out/'cargo.stderr.log'),'native_executions':0})
        except BaseException as exc:
            fault=repr(exc);raise
        finally:
            actual=sha(REPO/OWNED);assert actual in [BASE[OWNED],arena_hash],'unexpected source; preserve for inspection'
            shutil.copyfile(P['accepted_arena_path'],REPO/OWNED)
            previous.custody()
            save(out/'restoration.json',{'at':now(),'accepted162_exact':True,'main_live_ptx_unchanged':True,'error':fault})
        print(phase['id'],'build terminal; accepted E020 restored.',flush=True)
    save(OUT/'complete.json',{'at':now(),'phases':[p['id'] for p in P['build_phases']],'protocol_sha256':sys.argv[1],'all_compilers_terminal':True,'accepted162_restored':True,'native_executions':0,'evidence_sha256':{str(p):sha(p) for p in OUT.rglob('*.json')}})
print('All E038 builds terminal. No native tests have run.',flush=True)
