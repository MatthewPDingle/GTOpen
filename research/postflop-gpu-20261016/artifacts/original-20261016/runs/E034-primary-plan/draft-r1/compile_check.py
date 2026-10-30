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

assert authorization['candidate'] == 'E034' and authorization['E020_accepted'] is True
assert authorization['E020_server_qualification_pass'] is True
assert authorization['independent_script_review_pass'] is True
for role in ['E020_acceptance', 'E020_server_qualification', 'E034_source_review', 'E034_script_review', 'D064_terminal_review', 'E033_failure_cleanup']:
    pin=authorization['prerequisites'][role]
    assert ar.sha256(Path(pin['path'])) == pin['sha256']
    assert authorization['evidence_sha256'][pin['path']] == pin['sha256']
assert authorization['independent_source_review_pass'] is True
_d064=authorization['prerequisites']['D064_terminal_review']
assert Path(_d064['path']).resolve()==(ar.RESEARCH/'comparisons/D064-terminal-review/report.json').resolve()
_d064_record=json.loads(Path(_d064['path']).read_text(encoding='utf-8'))
assert _d064_record['id']=='D064' and _d064_record['terminal_audit_pass'] is True
assert _d064_record['verdict']=='PASS_SCOPED_CAPTURED_NODE_ATTRIBUTE_TERMINAL_AUDIT'
assert _d064_record['stream_and_retained_node_semantics_exact'] is True and _d064_record['cleanup_pass'] is True

_failure=authorization['prerequisites']['E033_failure_cleanup']
assert Path(_failure['path']).resolve()==(ar.RESEARCH/'runs/E033-cleanup/report.json').resolve()
_failure_record=json.loads(Path(_failure['path']).read_text(encoding='utf-8'))
assert _failure_record['id']=='E033' and _failure_record['status']=='REJECTED_AT_UNIT_GATE'
assert _failure_record['accepted_sources_restored'] is True and _failure_record['no_retry_or_timing'] is True
assert all(_failure_record['timed_runs_absent'].values()) and len(_failure_record['timed_runs_absent'])==6

changed_sources = ('crates/solver/src/gpu/mod.rs',)
new_sources = ('crates/solver/src/gpu/cache_policy.rs',)
owned = changed_sources + new_sources
all_owned = owned
assert set(authorization['candidate_sources']) == set(owned)
protocol_hash = 'UNSEALED_PROTOCOL_SHA256'
out = ar.RESEARCH / 'runs/E034-compile-check'
target = ar.RESEARCH / 'build-check-e034-research'
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
    design=ar.RESEARCH/'runs/E034-design'
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
    assert len(accepted) == 162 and len(current) == 163
    assert set(current) == set(accepted) | set(new_sources)
    for name, expected in accepted.items():
        if name not in changed_sources:
            assert current[name] == expected, name
    expected_owned = json.loads((here / 'protocol.json').read_text(encoding='utf-8'))['accepted_owned_sha256']
    assert {name: accepted[name] for name in changed_sources} == expected_owned
    assert all(current[name] != accepted[name] for name in changed_sources)
    assert not (set(new_sources) & set(accepted))
    tracked = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', 'crates/solver'], cwd=repo, text=True).splitlines()
    untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--', 'crates/solver'], cwd=repo, text=True).splitlines()
    preserved = json.loads((here/'protocol.json').read_text(encoding='utf-8'))['preexisting_target_artifacts']
    assert set(preserved) == {'crates/solver/target/research-fixtures/postflop-latest.ptx', 'crates/solver/target/research-fixtures/preflop-latest.ptx'}
    for name, pin in preserved.items():
        assert name not in accepted and name not in current, name
        assert ar.sha256(repo/name) == pin['sha256'] and (repo/name).stat().st_size == pin['bytes'], name
    assert set(tracked) | (set(untracked) - set(preserved)) == set(owned), (tracked, untracked)



def heartbeat():
    try:
        with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'), timeout=3):
            status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
            status.update(updated_at=ar.now(), stage='Compile-checking E034 research library paths', active_experiment='E034',
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
    shutil.copyfile(ar.RESEARCH/'runs/E034-design/candidate.patch', patch)
    assert ar.sha256(patch) == ar.sha256(ar.RESEARCH/'runs/E034-design/candidate.patch')
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
        binary=Path(item['executable']);destination=artifacts/('E034-research-'+name+'.exe')
        shutil.copyfile(binary,destination)
        assert ar.sha256(destination)==ar.sha256(binary)
        if name=='solver':
            data=destination.read_bytes()
            accepted_cuda=(repo/'crates/solver/src/gpu/kernels.cu').read_bytes()
            assert ar.sha256(repo/'crates/solver/src/gpu/kernels.cu')==protocol['accepted_kernel_sha256']
            cleanup_source=Path(protocol['cleanup_source_path'])
            assert ar.sha256(cleanup_source)==protocol['cleanup_source_sha256']
            assert accepted_cuda in data and cleanup_source.read_bytes() in data,'Missing accepted numerical CUDA or E034 cleanup source'
        artifact_sha256[str(destination)]=ar.sha256(destination)
        artifact_records.append({'path':str(destination),'sha256':ar.sha256(destination),'cargo_artifact':item})
    verify()
    assert before['source_sha256']==ar.source_identity()['source_sha256']
    evidence={str(path):ar.sha256(path) for path in out.iterdir() if path.is_file()}
    record={**before,'candidate':'E034','status':'COMPILE_ONLY_CHECKS_PASSED','at':ar.now(),'authorization_sha256':sys.argv[1],
        'protocol_sha256':protocol_hash,'script_sha256':ar.sha256(Path(__file__)),'commands':[test_exit],
        'target_dir':str(target),'source_copies':source_copies,'patch_sha256':ar.sha256(patch),'artifact_sha256':artifact_sha256,
        'artifacts':artifact_records,'evidence_sha256':evidence,'native_executions':0}
    ar.atomic_json(out/'complete.json',record)
    print('E034 feature compile checks terminal success; no native feature test run.',flush=True)
