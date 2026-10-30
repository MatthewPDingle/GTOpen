"""Root-only build after accepted E020 server qualification and frozen D044 review."""
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
assert authorization['candidate'] == 'D044' and authorization['E020_accepted'] is True
assert authorization['E020_server_qualification_pass'] is True
assert authorization['independent_script_review_pass'] is True
for role in ['E020_acceptance', 'E020_server_qualification', 'D044_source_review', 'D044_script_review']:
    pin=authorization['prerequisites'][role]
    assert ar.sha256(Path(pin['path'])) == pin['sha256']
    assert authorization['evidence_sha256'][pin['path']] == pin['sha256']
assert authorization['independent_source_review_pass'] is True
owned = ('crates/solver/src/game.rs',)
assert set(authorization['candidate_sources']) == set(owned)
protocol_hash = 'f6565a31fccabb51e51ce9017026e7f5ba23e65c03e0a507f183ef6265aab58a'
out = ar.RESEARCH / 'runs/D044-build'
target = ar.RESEARCH / 'build-d044-constructor'
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
    design=ar.RESEARCH/'runs/D044-constructor-diagnostic'
    assert ar.sha256(design/'source-manifest.json')==json.loads((here/'protocol.json').read_text(encoding='utf-8'))['source_archive_sha256']
    for name,expected in json.loads((design/'source-manifest.json').read_text(encoding='utf-8'))['artifact_sha256'].items():
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
    assert all(current[name] != accepted[name] for name in owned), 'The reviewed game constructor diagnostic file must change'
    changed = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', 'crates/solver'], cwd=repo, text=True).splitlines()
    assert changed == sorted(owned), changed


def heartbeat():
    try:
        with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'), timeout=3):
            status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
            status.update(updated_at=ar.now(), stage='Building frozen D044 constructor diagnostic', active_experiment='D044',
                          activity='Accepted E020 server qualification and source/script review passed. Building temporary instrumentation; exact-state and timing-perturbation checks pending. No performance acceptance.')
            ar.atomic_json(ar.STATUS, status)
    except Exception as error:
        # Dashboard trouble must never release the GPU lock around a live compiler.
        try:
            with (out / 'heartbeat-errors.jsonl').open('a', encoding='utf-8') as log:
                log.write(json.dumps({'at': ar.now(), 'error': repr(error)}) + '\n')
        except Exception:
            pass


with ar.exclusive_lock(ar.RESEARCH / 'gpu-run.lock'):
    ar.refuse_active(ar.live_status())
    assert shutil.disk_usage(ar.RESEARCH).free >= 54 * 1024**3
    assert not target.exists(), 'Fresh D044 target required; no clean/reuse workaround'
    verify()
    for name in ('D044-postflop_autoresearch',):
        assert not (ar.RESEARCH / 'binaries' / (name + '.exe')).exists()
        assert not (ar.RESEARCH / 'binaries' / (name + '.manifest.json')).exists()
    out.mkdir(exist_ok=False)
    target.mkdir()
    before = ar.source_identity()
    ar.atomic_json(out / 'source-before.json', before)
    source_copies = {}
    for name, output in zip(owned, ('candidate-game.rs',)):
        destination = out / output
        shutil.copyfile(repo / name, destination)
        source_copies[name] = {'path': str(destination), 'sha256': ar.sha256(destination)}
    patch = out / 'candidate.patch'
    patch.write_bytes(subprocess.check_output(['git', 'diff', '--binary', 'HEAD', '--', *owned], cwd=repo))
    command = ['cargo', 'test', '--release', '--locked', '--offline', '-p', 'solver', '--features', 'gpu', '--test', 'postflop_autoresearch', '--no-run', '--message-format=json']
    env = os.environ.copy()
    override_keys={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET'}
    overrides={k:v for k,v in env.items() if k in override_keys or k.startswith('CARGO_PROFILE_RELEASE_') or (k.startswith('CARGO_TARGET_') and k.endswith('_RUSTFLAGS'))}
    assert not overrides, ('Unregistered compiler overrides',overrides)
    env.update(CARGO_TARGET_DIR=str(target), RAYON_NUM_THREADS='16')
    env['PATH']=str(ar.NVRTC)+os.pathsep+env.get('PATH','')
    ar.atomic_json(out/'build-environment.json',{'target_dir':str(target),'target_previously_absent':True,'compiler_override_absence':overrides,'RAYON_NUM_THREADS':'16','rustc':ar.read_command(['rustc','-Vv']),'cargo':ar.read_command(['cargo','-V'])})
    log, err = out / 'build.jsonl', out / 'build.stderr.log'
    heartbeat()
    print('Building source-frozen D044; no GPU tests run in this step.', flush=True)
    process = None
    started=time.monotonic()
    fault = None
    cleanup = None
    try:
        with log.open('xb') as stdout, err.open('xb') as stderr:
            process = subprocess.Popen(command, cwd=repo, env=env, stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
            while True:
                try:
                    code = process.wait(timeout=10)
                    break
                except subprocess.TimeoutExpired:
                    heartbeat()
                    if time.monotonic()-started >= 1800: raise TimeoutError('Fixed1800s build timeout')
    except BaseException as error:
        fault = repr(error)
        cleanup = ar.cleanup_child(process)  # Owned process tree, still inside the GPU lock.
        raise
    finally:
        ar.atomic_json(out / 'exit.json', {'returncode': process.returncode if process else None, 'at': ar.now(),
                                         'command': command, 'error': fault, 'cleanup': cleanup})
    assert code == 0, err.read_text(encoding='utf-8', errors='replace')[-8000:]
    verify()
    assert before['source_sha256'] == ar.source_identity()['source_sha256']
    records=[json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()]
    assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in records)
    for item in records:
        if item.get('reason')=='compiler-artifact':
            for filename in item.get('filenames',[])+([item['executable']] if item.get('executable') else []):
                assert Path(filename).resolve().is_relative_to(target.resolve()), filename
    solver_lib=[x for x in records if x.get('reason')=='compiler-artifact' and x['target']['name']=='solver' and x['target']['kind']==['lib'] and not x.get('profile',{}).get('test')]
    assert len(solver_lib)==1 and solver_lib[0]['fresh'] is False
    assert Path(solver_lib[0]['target']['src_path']).resolve()==(repo/'crates/solver/src/lib.rs').resolve()
    assert Path(solver_lib[0]['manifest_path']).resolve()==(repo/'crates/solver/Cargo.toml').resolve()
    dependencies={f:ar.sha256(Path(f)) for x in records if x.get('reason')=='compiler-artifact' for f in x.get('filenames',[]) if Path(f).is_file() and Path(f).suffix in {'.rlib','.rmeta','.lib','.dll'}}
    artifacts = []
    for line in log.read_text(encoding='utf-8').splitlines():
        item = json.loads(line)
        if item.get('reason') == 'compiler-artifact' and item.get('profile', {}).get('test') and item.get('executable') and item['target']['name'] == 'postflop_autoresearch':
            artifacts.append(item)
    assert len(artifacts) == 1 and artifacts[0]['target']['name'] == 'postflop_autoresearch'
    for item in artifacts:
        name = item['target']['name']
        assert item['fresh'] is False
        assert Path(item['manifest_path']).resolve()==(repo/'crates/solver/Cargo.toml').resolve()
        expected_src=repo/('crates/solver/src/lib.rs' if name=='solver' else 'crates/solver/tests/postflop_autoresearch.rs')
        assert Path(item['target']['src_path']).resolve()==expected_src.resolve()
        destination = ar.RESEARCH / 'binaries' / ('D044-' + name + '.exe')
        assert not destination.exists()
        shutil.copyfile(item['executable'], destination)
        data=destination.read_bytes()
        accepted_cuda=(ar.RESEARCH/'runs/D037-showdown-cache-design/candidate/kernels.cu').read_bytes()
        assert ar.sha256(ar.RESEARCH/'runs/D037-showdown-cache-design/candidate/kernels.cu')==json.loads((here/'protocol.json').read_text(encoding='utf-8'))['accepted_kernel_sha256']
        assert accepted_cuda in data and b'SPOT_CONSTRUCTOR_PROFILE' in data, 'Missing accepted CUDA or diagnostic marker'
        assert ar.sha256(destination)!=json.loads((here/'protocol.json').read_text(encoding='utf-8'))['reference_binary_sha256']
        manifest = {**before, 'candidate': 'D044', 'binary_sha256': ar.sha256(destination), 'built_at': ar.now(),
                    'build_command': command,'cargo_artifact':item,'solver_artifact':solver_lib[0],'dependency_artifact_sha256':dependencies,'target_dir':str(target),'accepted_cuda_present':True,'diagnostic_marker_present':True, 'build_log': str(log), 'build_log_sha256': ar.sha256(log),
                    'build_stderr_log': str(err), 'build_stderr_sha256': ar.sha256(err),
                    'patch': str(patch), 'patch_sha256': ar.sha256(patch), 'source_matches_prebuild': True,
                    'build_script_sha256': ar.sha256(Path(__file__)), 'primary_protocol_sha256': protocol_hash,
                    'probe_authorization_sha256': sys.argv[1], 'probe_evidence_sha256': authorization['evidence_sha256'],
                    'candidate_sources': authorization['candidate_sources'], 'source_copies': source_copies,
                    'prerequisite_scope': 'Accepted E020, completed server qualification and independent D044 source/script review; not numerical proof',
                    'change': 'Time unchanged Spot tree/river-table/symmetry construction stages and constructor envelope. Evaluator, CUDA, math, call order and errors unchanged. Diagnostic only, no performance acceptance.'}
        ar.atomic_json(destination.with_suffix('.manifest.json'), manifest)
        print(name, manifest['binary_sha256'], flush=True)
    print('D044 build terminal success. Root must observe process exit before starting primary tests.', flush=True)
