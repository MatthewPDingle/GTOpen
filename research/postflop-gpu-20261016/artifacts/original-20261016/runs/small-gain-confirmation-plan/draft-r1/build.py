"""Root only: five serialized fresh builds, restoring accepted source after every arm."""
import os, shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
assert len(sys.argv)==2,'Provide root authorization SHA256'
AUTH=sys.argv[1];authorization=verify(AUTH)

def compile_arm(c,mode,out):
    target=ROOT/f'build-small-gain-{c.lower()}-{mode}'
    assert not target.exists(),target
    target.mkdir()
    e=env()
    keys={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET'}
    overrides={k:v for k,v in e.items() if k in keys or k.startswith('CARGO_PROFILE_RELEASE_') or (k.startswith('CARGO_TARGET_') and k.endswith('_RUSTFLAGS'))}
    assert not overrides,overrides
    e['CARGO_TARGET_DIR']=str(target)
    command=['cargo','test','--release','--locked','--offline','-p','solver','--features','preflop-research' if mode=='feature' else 'gpu','--lib']
    if mode=='primary':command+=['--test','postflop_autoresearch']
    command+=['--no-run','--message-format=json']
    save(out/(mode+'.environment.json'),{'target':str(target),'previously_absent':True,'overrides':overrides,'RAYON_NUM_THREADS':'16','rustc':ar.read_command(['rustc','-Vv']),'cargo':ar.read_command(['cargo','-V'])})
    child(command,out,mode,e,P['build_timeout_seconds'])
    custody(c);verify(AUTH)
    records=[json.loads(x) for x in (out/(mode+'.stdout.log')).read_text(encoding='utf-8').splitlines()]
    assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in records)
    for x in records:
        if x.get('reason')=='compiler-artifact':
            for f in x.get('filenames',[])+([x['executable']] if x.get('executable') else []):assert Path(f).resolve().is_relative_to(target.resolve()),f
    artifacts=[x for x in records if x.get('reason')=='compiler-artifact' and x.get('profile',{}).get('test') and x.get('executable') and x['target']['name'] in ['solver','postflop_autoresearch']]
    assert {x['target']['name'] for x in artifacts}==({'solver'} if mode=='feature' else {'solver','postflop_autoresearch'})
    assert len(artifacts)==(1 if mode=='feature' else 2)
    if mode=='primary':
        libs=[x for x in records if x.get('reason')=='compiler-artifact' and x['target']['name']=='solver' and not x.get('profile',{}).get('test')]
        assert len(libs)==1 and libs[0]['fresh'] is False and libs[0]['features']==['gpu']
    dependencies={f:sha(f) for x in records if x.get('reason')=='compiler-artifact' for f in x.get('filenames',[]) if Path(f).is_file() and Path(f).suffix in ['.rlib','.rmeta','.lib','.dll']}
    cuda=(REPO/'crates/solver/src/gpu/kernels.cu').read_bytes()
    old=(SOURCE/'E007/base/kernels.cu').read_bytes()
    pins={}
    for x in artifacts:
        name=x['target']['name'];source='crates/solver/src/lib.rs' if name=='solver' else 'crates/solver/tests/postflop_autoresearch.rs'
        assert x['fresh'] is False and x['features']==(['gpu','preflop-research'] if mode=='feature' else ['gpu'])
        assert Path(x['target']['src_path']).resolve()==(REPO/source).resolve()
        assert Path(x['manifest_path']).resolve()==(REPO/'crates/solver/Cargo.toml').resolve()
        original=Path(x['executable']);data=original.read_bytes()
        assert cuda in data,'Complete compiled source CUDA missing'
        if c not in ['E020','E032']:assert old not in data,'Complete accepted CUDA unexpectedly present'
        pins[str(original)]=sha(original)
        if mode=='primary':
            dest=ROOT/'binaries'/f'SG-{c}-{name}.exe';assert not dest.exists()
            shutil.copyfile(original,dest)
            manifest={**ar.source_identity(),'candidate':f'SG-{c}','historical_hypothesis':c,'binary_sha256':sha(dest),'built_at':now(),'build_command':command,'cargo_artifact':x,'solver_artifact':libs[0],'target_dir':str(target),'dependency_artifact_sha256':dependencies,'candidate_cuda_present':True,'candidate_cuda_sha256':hashlib.sha256(cuda).hexdigest(),'accepted_cuda_preserved':c in ['E020','E032'],'source_matches_prebuild':True,'source_copies':{n:{'path':str(out/('candidate-'+Path(n).name)),'sha256':expected(c)[n]} for n in P['arms'][c]['owned_sources']},'build_log':str(out/(mode+'.stdout.log')),'build_log_sha256':sha(out/(mode+'.stdout.log')),'build_script_sha256':sha(HERE/'build.py'),'primary_protocol_sha256':sha(HERE/'protocol.json'),'authorization_sha256':AUTH,'feature_complete_sha256':sha(out/'feature.complete.json'),'fresh_family_build':True,'candidate_accepted':False}
            save(dest.with_suffix('.manifest.json'),manifest)
            pins[str(dest)]=sha(dest);pins[str(dest.with_suffix('.manifest.json'))]=sha(dest.with_suffix('.manifest.json'))
    save(out/(mode+'.complete.json'),{'at':now(),'mode':mode,'source_sha256':expected(c),'command':command,'returncode':0,'target':str(target),'native_executions':0,'artifact_sha256':pins,'dependency_sha256':dependencies,'authorization_sha256':AUTH,'protocol_sha256':sha(HERE/'protocol.json'),'build_script_sha256':sha(HERE/'build.py'),'stdout_sha256':sha(out/(mode+'.stdout.log')),'stderr_sha256':sha(out/(mode+'.stderr.log'))})

with ar.exclusive_lock(ROOT/'gpu-run.lock'):
    ar.refuse_active(ar.live_status());custody()
    assert shutil.disk_usage(ROOT).free>=P['build_disk_reserve_gib']*1024**3
    assert not BUILD.exists();BUILD.mkdir()
    for c in P['build_order']:
        for mode in ['feature','primary']:assert not (ROOT/f'build-small-gain-{c.lower()}-{mode}').exists()
        for n in ['solver','postflop_autoresearch']:
            for ext in ['exe','manifest.json']:assert not (ROOT/'binaries'/f'SG-{c}-{n}.{ext}').exists()
    for c in P['build_order']:
        verify(AUTH);custody();ar.refuse_active(ar.live_status())
        assert shutil.disk_usage(ROOT).free>=P['build_disk_reserve_gib']*1024**3
        out=BUILD/c;out.mkdir();owned=P['arms'][c]['owned_sources'];fault=None
        save(out/'before.json',{'at':now(),'source_sha256':BASE,'authorization_sha256':AUTH})
        try:
            for n in owned:
                archive=SOURCE/c/'candidate'/Path(n).name;pin(archive,expected(c)[n])
                shutil.copyfile(archive,REPO/n);shutil.copyfile(archive,out/('candidate-'+Path(n).name))
            custody(c)
            save(out/'activation.json',{'at':now(),'source_sha256':expected(c),'owned_sources':owned})
            if owned:shutil.copyfile(SOURCE/c/'candidate.patch',out/'candidate.patch')
            compile_arm(c,'feature',out)
            compile_arm(c,'primary',out)
        except BaseException as error:
            fault=repr(error);raise
        finally:
            # Child cleanup has completed inside the lock before restoration.
            restored=[]
            for n in owned:
                actual=sha(REPO/n)
                assert actual in [BASE[n],expected(c)[n]],('Unexpected source bytes; stop for root custody',n)
                if actual!=BASE[n]:shutil.copyfile(SOURCE/c/'base'/Path(n).name,REPO/n)
                pin(REPO/n,BASE[n]);restored.append(n)
            custody()
            save(out/'restoration.json',{'at':now(),'restored_sources':restored,'accepted162_exact':True,'main_live_ptx_unchanged':True,'error':fault})
        print(c,'feature and primary builds terminal; accepted source restored.',flush=True)
    custody()
    evidence={str(p):sha(p) for p in BUILD.rglob('*.json')}
    save(BUILD/'complete.json',{'at':now(),'build_order':P['build_order'],'all_compilers_terminal':True,'accepted162_restored':True,'authorization_sha256':AUTH,'protocol_sha256':sha(HERE/'protocol.json'),'evidence_sha256':evidence,'native_executions':0})
print('All five builds complete. Root must observe terminal exit before units/timing.',flush=True)
