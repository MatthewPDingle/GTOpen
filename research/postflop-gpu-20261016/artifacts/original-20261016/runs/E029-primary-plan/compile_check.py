"""Root-only feature library compile check; never run the feature tests."""
import json, os, shutil, signal, subprocess, sys, time
from pathlib import Path

repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar

here = Path(__file__).resolve().parent
assert len(sys.argv) == 2, 'Provide the independently reviewed authorization.json SHA256'
authorization_path = here / 'authorization.json'
assert ar.sha256(authorization_path) == sys.argv[1]
authorization = json.loads(authorization_path.read_text(encoding='utf-8'))

assert authorization['direct_up_show_exact_pass'] is True
_direct_pin=authorization['prerequisites']['direct_up_show_terminal_review']
_direct_path=Path(_direct_pin['path'])
assert _direct_path.resolve()==Path(r'S:\GTOpen-research\postflop-gpu-20261016\comparisons\E029-direct-independent-review\validation.json').resolve()
assert authorization['evidence_sha256'][str(_direct_path)]==_direct_pin['sha256']
assert __import__('hashlib').sha256(_direct_path.read_bytes()).hexdigest()==_direct_pin['sha256']
_direct=json.loads(_direct_path.read_text(encoding='utf-8'))
assert _direct['id']=='E029-direct' and _direct['verdict']=='PASS_EXACT_COMPLETE_UP_SHOW_COMPARISON'
assert _direct['exactness_pass'] is True and _direct['numerical_validation']=='executed'
assert _direct['baseline_cuda_sha256']=='075651690d59ede225c17ff9674662e040d40460a5e2b5436fd6fa7d4f5d663b'
assert _direct['candidate_cuda_sha256']=='bf865236270454e13fb7dd2deaf85146310aa364abbc47e00df47bcb0a391841'
assert _direct['prepared_manifest_sha256']=='cedcda1d63a2ebf6bbefa166a4de17cbcc5a7500acc1dbc602339ba967e46ec8'
assert (_direct['baseline_physical_threads'],_direct['candidate_physical_threads'],_direct['logical_scan_threads'])==(128,128,128)
assert _direct['comparison_pairs']==152 and _direct['kernel_launches']==304
assert _direct['performance_measurement'] is False and _direct['candidate_accepted'] is False
assert authorization['candidate'] == 'E029' and authorization['E020_accepted'] is True
assert authorization['E020_server_qualification_pass'] is True
assert authorization['independent_script_review_pass'] is True
for role in ['E020_acceptance', 'E020_server_qualification', 'E029_source_review', 'E029_script_review']:
    pin=authorization['prerequisites'][role]
    assert ar.sha256(Path(pin['path'])) == pin['sha256']
    assert authorization['evidence_sha256'][pin['path']] == pin['sha256']
assert authorization['independent_source_review_pass'] is True
owned = ('crates/solver/src/game.rs', 'crates/solver/src/gpu/continuation_capacity.rs', 'crates/solver/src/gpu/kernels.cu', 'crates/solver/src/gpu/mod.rs', 'crates/solver/src/gpu/plan.rs')
all_owned = owned
assert set(authorization["candidate_sources"]) == set(owned)
protocol_hash = '6d129fe4448741cd1612089bbdcc56e02cf5940d5b2d04a611203feed2470165'
out = ar.RESEARCH / 'runs/E029-compile-check'
target = ar.RESEARCH / 'build-check-e029-research'
def interrupted(signum, _frame): raise KeyboardInterrupt(f'received signal {signum}')
for sig in [signal.SIGTERM, getattr(signal,'SIGBREAK',None)]:
    if sig is not None: signal.signal(sig,interrupted)


def verify():
    assert ar.sha256(authorization_path) == sys.argv[1]
    assert ar.sha256(here / 'protocol.json') == protocol_hash
    for name, expected in authorization['evidence_sha256'].items():
        assert ar.sha256(Path(name)) == expected, name
    script_seal = json.loads((here / 'scripts-manifest.json').read_text(encoding='utf-8'))
    assert script_seal['status'] == 'FROZEN_PROSPECTIVE_NOT_EXECUTED'
    assert authorization['evidence_sha256'][str(here / 'scripts-manifest.json')] == ar.sha256(here / 'scripts-manifest.json')
    for name, expected in script_seal['script_sha256'].items():
        assert ar.sha256(here / name) == expected, name
    for path, expected in script_seal['reference_sha256'].items():
        assert ar.sha256(Path(path)) == expected, path
    design=ar.RESEARCH/'runs/E029-design'
    assert ar.sha256(design/'manifest.json')==json.loads((here/'protocol.json').read_text(encoding='utf-8'))['source_archive_sha256']
    for name,expected in json.loads((design/'manifest.json').read_text(encoding='utf-8'))['artifact_sha256'].items():
        assert ar.sha256(design/name)==expected,name
    for name, candidate in authorization['candidate_sources'].items():
        assert set(candidate) == {'path', 'sha256'}
        assert ar.sha256(Path(candidate['path'])) == candidate['sha256'], name
        assert ar.sha256(repo / name) == candidate['sha256'], name
        assert candidate['sha256'] == json.loads((here/'protocol.json').read_text(encoding='utf-8'))['candidate_owned_sha256'][name]
    accepted_path = ar.RESEARCH / 'binaries/E020-postflop_autoresearch.manifest.json'
    assert ar.sha256(accepted_path) == '37bb96c45ecaae02dab11ddfb43d8e46e842dacaed7df8edbad2264b31cb3768'
    accepted = json.loads(accepted_path.read_text(encoding='utf-8'))['source_sha256']
    current = ar.source_identity()['source_sha256']
    assert len(accepted) == 162 and set(current) == set(accepted)
    for name, expected in accepted.items():
        if name not in owned:
            assert current[name] == expected, name
    expected_owned = json.loads((here / 'protocol.json').read_text(encoding='utf-8'))['accepted_owned_sha256']
    assert {name: accepted[name] for name in owned} == expected_owned
    assert all(current[name] != accepted[name] for name in owned), 'All five reviewed accepted-map source files must change'
    changed = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', 'crates/solver'], cwd=repo, text=True).splitlines()
    assert changed == sorted(all_owned), changed


def heartbeat():
    try:
        with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'), timeout=3):
            status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
            status.update(updated_at=ar.now(), stage='Compile-checking E029 research library paths', active_experiment='E029',
                          activity='Compile-only research library tests; no native test is executed. Fresh GPU-only build and fixed primary remain pending.')
            ar.atomic_json(ar.STATUS, status)
    except Exception as error:
        # Dashboard trouble must never release the GPU lock around a live compiler.
        try:
            with (out / 'heartbeat-errors.jsonl').open('a', encoding='utf-8') as log:
                log.write(json.dumps({'at': ar.now(), 'error': repr(error)}) + '\n')
        except Exception:
            pass


def compile_one(label, command, env):
    log, err = out/(label+'.jsonl'), out/(label+'.stderr.log')
    heartbeat()
    print('Compile-only', label, flush=True)
    process=None; fault=None; cleanup=None; started=time.monotonic()
    try:
        with log.open('xb') as stdout, err.open('xb') as stderr:
            process=subprocess.Popen(command,cwd=repo,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            while True:
                try:
                    code=process.wait(timeout=10)
                    break
                except subprocess.TimeoutExpired:
                    heartbeat()
                    if time.monotonic()-started >= 1800: raise TimeoutError('Fixed1800s compile timeout')
    except BaseException as error:
        fault=repr(error);cleanup=ar.cleanup_child(process);raise
    finally:
        ar.atomic_json(out/(label+'.exit.json'),{'at':ar.now(),'returncode':process.returncode if process else None,'command':command,'error':fault,'cleanup':cleanup})
    assert code==0,err.read_text(encoding='utf-8',errors='replace')[-8000:]
    verify()
    assert before['source_sha256']==ar.source_identity()['source_sha256']
    records=[json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()]
    assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in records)
    for item in records:
        if item.get('reason')=='compiler-artifact':
            for filename in item.get('filenames',[])+([item['executable']] if item.get('executable') else []):
                assert Path(filename).resolve().is_relative_to(target.resolve()),filename
    return records,{'label':label,'returncode':code,'command':command,'exit_sha256':ar.sha256(out/(label+'.exit.json'))}


with ar.exclusive_lock(ar.RESEARCH/'gpu-run.lock'):
    ar.refuse_active(ar.live_status())
    assert shutil.disk_usage(ar.RESEARCH).free>=54*1024**3
    assert not target.exists(), 'Fresh compile-check target required'
    verify()
    protocol=json.loads((here/'protocol.json').read_text(encoding='utf-8'))
    assert len(protocol['compile_only_commands'])==1
    out.mkdir(exist_ok=False);target.mkdir()
    before=ar.source_identity()
    ar.atomic_json(out/'source-before.json',before)
    source_copies={}
    for name in all_owned:
        destination=out/('candidate-'+Path(name).name)
        shutil.copyfile(repo/name,destination)
        source_copies[name]={'path':str(destination),'sha256':ar.sha256(destination)}
    patch=out/'candidate.patch'
    patch.write_bytes(subprocess.check_output(['git','diff','--binary','HEAD','--',*all_owned],cwd=repo))
    env=os.environ.copy()
    override_keys={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET'}
    overrides={k:v for k,v in env.items() if k in override_keys or k.startswith('CARGO_PROFILE_RELEASE_') or (k.startswith('CARGO_TARGET_') and k.endswith('_RUSTFLAGS'))}
    assert not overrides,('Unregistered compiler overrides',overrides)
    env.update(CARGO_TARGET_DIR=str(target),RAYON_NUM_THREADS='16')
    env['PATH']=str(ar.NVRTC)+os.pathsep+env.get('PATH','')
    ar.atomic_json(out/'build-environment.json',{'target_dir':str(target),'target_previously_absent':True,'compiler_override_absence':overrides,'RAYON_NUM_THREADS':'16','rustc':ar.read_command(['rustc','-Vv']),'cargo':ar.read_command(['cargo','-V'])})
    test_records,test_exit=compile_one('lib-tests',protocol['compile_only_commands'][0],env)
    tests=[x for x in test_records if x.get('reason')=='compiler-artifact' and x['target']['name']=='solver' and x['target']['kind']==['lib'] and x.get('profile',{}).get('test') and x.get('executable')]
    assert len(tests)==1 and tests[0]['fresh'] is False
    artifacts=out/'artifacts';artifacts.mkdir()
    artifact_sha256={};artifact_records=[]
    for item in tests:
        name=item['target']['name'];assert name=='solver'
        assert item['fresh'] is False and item['features']==['gpu','preflop-research']
        assert Path(item['manifest_path']).resolve()==(repo/'crates/solver/Cargo.toml').resolve()
        expected=repo/'crates/solver/src/lib.rs'
        assert Path(item['target']['src_path']).resolve()==expected.resolve()
        assert item['profile']['test'] is (name=='solver')
        binary=Path(item['executable']);destination=artifacts/('E029-research-'+name+'.exe')
        shutil.copyfile(binary,destination)
        assert ar.sha256(destination)==ar.sha256(binary)
        if name=='solver':
            data=destination.read_bytes()
            candidate_cuda=Path(authorization['candidate_sources']['crates/solver/src/gpu/kernels.cu']['path']).read_bytes()
            accepted_cuda=(ar.RESEARCH/'runs/E029-design/base/crates/solver/src/gpu/kernels.cu').read_bytes()
            assert candidate_cuda in data and accepted_cuda not in data,'Wrong embedded research unit CUDA'
        artifact_sha256[str(destination)]=ar.sha256(destination)
        artifact_records.append({'path':str(destination),'sha256':ar.sha256(destination),'cargo_artifact':item})
    verify()
    assert before['source_sha256']==ar.source_identity()['source_sha256']
    evidence={str(path):ar.sha256(path) for path in out.iterdir() if path.is_file()}
    record={**before,'candidate':'E029','status':'COMPILE_ONLY_CHECKS_PASSED','at':ar.now(),'authorization_sha256':sys.argv[1],
        'protocol_sha256':protocol_hash,'script_sha256':ar.sha256(Path(__file__)),'commands':[test_exit],
        'target_dir':str(target),'source_copies':source_copies,'patch_sha256':ar.sha256(patch),'artifact_sha256':artifact_sha256,
        'artifacts':artifact_records,'evidence_sha256':evidence,'native_executions':0}
    ar.atomic_json(out/'complete.json',record)
    print('E029 feature compile checks terminal success; no native feature test run.',flush=True)
