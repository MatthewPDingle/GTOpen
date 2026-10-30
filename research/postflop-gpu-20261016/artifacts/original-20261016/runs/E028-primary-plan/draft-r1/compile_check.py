"""Root-only compile checks; never run the feature tests or capacity examples."""
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
assert authorization['candidate'] == 'E028' and authorization['E020_accepted'] is True
assert authorization['E020_server_qualification_pass'] is True
assert authorization['independent_script_review_pass'] is True
for role in ['E020_acceptance', 'E020_server_qualification', 'E028_source_review', 'E028_script_review']:
    pin=authorization['prerequisites'][role]
    assert ar.sha256(Path(pin['path'])) == pin['sha256']
    assert authorization['evidence_sha256'][pin['path']] == pin['sha256']
assert authorization['independent_source_review_pass'] is True
owned = ('crates/solver/src/game.rs', 'crates/solver/src/gpu/continuation_capacity.rs', 'crates/solver/src/gpu/continuation_host_paging_tests.rs', 'crates/solver/src/gpu/continuation_paging.rs', 'crates/solver/src/gpu/continuation_ssd_paging_tests.rs', 'crates/solver/src/gpu/continuation_storage.rs', 'crates/solver/src/gpu/kernels.cu', 'crates/solver/src/gpu/mod.rs', 'crates/solver/src/gpu/plan.rs')
auxiliary = ('crates/solver/examples/continuation_storage_capacity.rs', 'crates/solver/examples/hu_context_capacity.rs')
all_owned = owned + auxiliary
assert set(authorization["candidate_sources"]) == set(owned)
assert set(authorization["auxiliary_sources"]) == set(auxiliary)
def auxiliary_identity(): return {name: ar.sha256(repo/name) for name in auxiliary}
protocol_hash = 'PENDING_PROTOCOL_HASH'
out = ar.RESEARCH / 'runs/E028-compile-check'
target = ar.RESEARCH / 'build-check-e028-research'
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
    design=ar.RESEARCH/'runs/E028-design'
    assert ar.sha256(design/'manifest.json')==json.loads((here/'protocol.json').read_text(encoding='utf-8'))['source_archive_sha256']
    for name,expected in json.loads((design/'manifest.json').read_text(encoding='utf-8'))['artifact_sha256'].items():
        assert ar.sha256(design/name)==expected,name
    for name, candidate in {**authorization['candidate_sources'], **authorization['auxiliary_sources']}.items():
        assert set(candidate) == {'path', 'sha256'}
        assert ar.sha256(Path(candidate['path'])) == candidate['sha256'], name
        assert ar.sha256(repo / name) == candidate['sha256'], name
        expected_map = 'candidate_owned_sha256' if name in owned else 'candidate_auxiliary_sha256'
        assert candidate['sha256'] == json.loads((here/'protocol.json').read_text(encoding='utf-8'))[expected_map][name]
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
    assert all(current[name] != accepted[name] for name in owned), 'All nine reviewed accepted-map source files must change'
    protocol = json.loads((here/'protocol.json').read_text(encoding='utf-8'))
    assert auxiliary_identity() == protocol['candidate_auxiliary_sha256']
    assert set(protocol['accepted_auxiliary_sha256']) == set(auxiliary)
    for name in auxiliary:
        assert ar.sha256(design/'base'/Path(name).name) == protocol['accepted_auxiliary_sha256'][name]
        assert protocol['candidate_auxiliary_sha256'][name] != protocol['accepted_auxiliary_sha256'][name]
    changed = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', 'crates/solver'], cwd=repo, text=True).splitlines()
    assert changed == sorted(all_owned), changed


def heartbeat():
    try:
        with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'), timeout=3):
            status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
            status.update(updated_at=ar.now(), stage='Compile-checking E028 research paths and capacity examples', active_experiment='E028',
                          activity='Compile-only research library tests and two capacity examples; no native test or example is executed. Fresh GPU-only build and fixed primary remain pending.')
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
    assert before['auxiliary_source_sha256']==auxiliary_identity()
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
    assert len(protocol['compile_only_commands'])==2
    out.mkdir(exist_ok=False);target.mkdir()
    before=ar.source_identity();before['auxiliary_source_sha256']=auxiliary_identity()
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
    example_records,example_exit=compile_one('capacity-examples',protocol['compile_only_commands'][1],env)
    examples=[x for x in example_records if x.get('reason')=='compiler-artifact' and x['target']['kind']==['example'] and x.get('executable')]
    assert len(examples)==2 and {x['target']['name'] for x in examples}=={'continuation_storage_capacity','hu_context_capacity'}
    solver_lib=[x for x in example_records if x.get('reason')=='compiler-artifact' and x['target']['name']=='solver' and x['target']['kind']==['lib'] and not x.get('profile',{}).get('test')]
    assert len(solver_lib)==1 and solver_lib[0]['fresh'] is False
    assert Path(solver_lib[0]['target']['src_path']).resolve()==(repo/'crates/solver/src/lib.rs').resolve()
    assert Path(solver_lib[0]['manifest_path']).resolve()==(repo/'crates/solver/Cargo.toml').resolve()
    artifacts=out/'artifacts';artifacts.mkdir()
    artifact_sha256={};artifact_records=[]
    for item in tests+examples:
        name=item['target']['name']
        assert item['fresh'] is False and {'gpu','preflop-research'}.issubset(item['features'])
        assert Path(item['manifest_path']).resolve()==(repo/'crates/solver/Cargo.toml').resolve()
        expected=repo/('crates/solver/src/lib.rs' if name=='solver' else 'crates/solver/examples/'+name+'.rs')
        assert Path(item['target']['src_path']).resolve()==expected.resolve()
        assert item['profile']['test'] is (name=='solver')
        binary=Path(item['executable']);destination=artifacts/('E028-research-'+name+'.exe')
        shutil.copyfile(binary,destination)
        assert ar.sha256(destination)==ar.sha256(binary)
        if name=='solver':
            data=destination.read_bytes()
            candidate_cuda=Path(authorization['candidate_sources']['crates/solver/src/gpu/kernels.cu']['path']).read_bytes()
            accepted_cuda=(ar.RESEARCH/'runs/E028-design/base/kernels.cu').read_bytes()
            assert candidate_cuda in data and accepted_cuda not in data,'Wrong embedded research unit CUDA'
        artifact_sha256[str(destination)]=ar.sha256(destination)
        artifact_records.append({'path':str(destination),'sha256':ar.sha256(destination),'cargo_artifact':item})
    verify()
    assert before['source_sha256']==ar.source_identity()['source_sha256']
    assert before['auxiliary_source_sha256']==auxiliary_identity()
    evidence={str(path):ar.sha256(path) for path in out.iterdir() if path.is_file()}
    record={**before,'candidate':'E028','status':'COMPILE_ONLY_CHECKS_PASSED','at':ar.now(),'authorization_sha256':sys.argv[1],
        'protocol_sha256':protocol_hash,'script_sha256':ar.sha256(Path(__file__)),'commands':[test_exit,example_exit],
        'target_dir':str(target),'source_copies':source_copies,'patch_sha256':ar.sha256(patch),'artifact_sha256':artifact_sha256,
        'artifacts':artifact_records,'solver_artifact':solver_lib[0],'evidence_sha256':evidence,'native_executions':0}
    ar.atomic_json(out/'complete.json',record)
    print('E028 feature compile checks terminal success; no native feature test or example run.',flush=True)
