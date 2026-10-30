"""Build a reviewed two-file E020 after root seals resource and source-review approval."""
import json, os, shutil, subprocess, sys
from pathlib import Path

repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar

here = Path(__file__).resolve().parent
assert len(sys.argv) == 2, 'Provide the independently reviewed authorization.json SHA256'
authorization_path = here / 'authorization.json'
assert ar.sha256(authorization_path) == sys.argv[1]
authorization = json.loads(authorization_path.read_text(encoding='utf-8'))
assert authorization['candidate'] == 'E020' and authorization['resource_probe_pass'] is True
assert authorization['independent_source_review_pass'] is True
owned = ('crates/solver/src/gpu/kernels.cu', 'crates/solver/src/gpu/mod.rs')
assert set(authorization['candidate_sources']) == set(owned)
protocol_hash = 'b5fa09fac0e0e4b652fe1479e5749cc2b1bfd023fe9b30c923b0d79ea46d6b2b'
out = ar.RESEARCH / 'runs/E020-build'


def verify():
    assert ar.sha256(authorization_path) == sys.argv[1]
    assert ar.sha256(here / 'protocol.json') == protocol_hash
    for name, expected in authorization['evidence_sha256'].items():
        assert ar.sha256(Path(name)) == expected, name
    script_seal = json.loads((here / 'scripts-manifest.json').read_text(encoding='utf-8'))
    assert script_seal['independent_script_review_pass'] is True
    assert authorization['evidence_sha256'][str(here / 'scripts-manifest.json')] == ar.sha256(here / 'scripts-manifest.json')
    for name, expected in script_seal['script_sha256'].items():
        assert ar.sha256(here / name) == expected, name
    for name, candidate in authorization['candidate_sources'].items():
        assert set(candidate) == {'path', 'sha256'}
        assert ar.sha256(Path(candidate['path'])) == candidate['sha256'], name
        assert ar.sha256(repo / name) == candidate['sha256'], name
    accepted_path = ar.RESEARCH / 'binaries/E015-postflop_autoresearch.manifest.json'
    assert ar.sha256(accepted_path) == '934c29e800d180397ee330340d425f1084078c24831ba87c4de5e74729821fd2'
    accepted = json.loads(accepted_path.read_text(encoding='utf-8'))['source_sha256']
    current = ar.source_identity()['source_sha256']
    assert len(accepted) == 162 and set(current) == set(accepted)
    for name, expected in accepted.items():
        if name not in owned:
            assert current[name] == expected, name
    expected_owned = json.loads((here / 'protocol.json').read_text(encoding='utf-8'))['accepted_owned_sha256']
    assert {name: accepted[name] for name in owned} == expected_owned
    assert all(current[name] != accepted[name] for name in owned), 'Both reviewed owned files must change'
    changed = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', 'crates/solver'], cwd=repo, text=True).splitlines()
    assert changed == sorted(owned), changed


def heartbeat():
    try:
        with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'), timeout=3):
            status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
            status.update(updated_at=ar.now(), stage='Building frozen E020 showdown-position cache candidate', active_experiment='E020',
                          activity='No-launch resource probe and source review passed. Building the two-file candidate; native numerical accuracy, complete-solve speed and broader qualification remain pending.')
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
    assert shutil.disk_usage(ar.RESEARCH).free >= 50 * 1024**3
    verify()
    for name in ('E020-solver', 'E020-postflop_autoresearch'):
        assert not (ar.RESEARCH / 'binaries' / (name + '.exe')).exists()
        assert not (ar.RESEARCH / 'binaries' / (name + '.manifest.json')).exists()
    out.mkdir(exist_ok=False)
    before = ar.source_identity()
    ar.atomic_json(out / 'source-before.json', before)
    source_copies = {}
    for name, output in zip(owned, ('candidate.cu', 'candidate-mod.rs')):
        destination = out / output
        shutil.copyfile(repo / name, destination)
        source_copies[name] = {'path': str(destination), 'sha256': ar.sha256(destination)}
    patch = out / 'candidate.patch'
    patch.write_bytes(subprocess.check_output(['git', 'diff', '--binary', 'HEAD', '--', *owned], cwd=repo))
    command = ['cargo', 'test', '--release', '-p', 'solver', '--features', 'gpu', '--lib', '--test', 'postflop_autoresearch', '--no-run', '--message-format=json']
    env = os.environ.copy()
    env.update(CARGO_TARGET_DIR=str(ar.RESEARCH / 'build'), RAYON_NUM_THREADS='16')
    log, err = out / 'build.jsonl', out / 'build.stderr.log'
    heartbeat()
    print('Building source-frozen E020; no GPU tests run in this step.', flush=True)
    process = None
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
    artifacts = []
    for line in log.read_text(encoding='utf-8').splitlines():
        item = json.loads(line)
        if item.get('reason') == 'compiler-artifact' and item.get('profile', {}).get('test') and item.get('executable') and item['target']['name'] in ('solver', 'postflop_autoresearch'):
            artifacts.append(item)
    assert len(artifacts) == 2 and {a['target']['name'] for a in artifacts} == {'solver', 'postflop_autoresearch'}
    for item in artifacts:
        name = item['target']['name']
        destination = ar.RESEARCH / 'binaries' / ('E020-' + name + '.exe')
        assert not destination.exists()
        shutil.copyfile(item['executable'], destination)
        manifest = {**before, 'candidate': 'E020', 'binary_sha256': ar.sha256(destination), 'built_at': ar.now(),
                    'build_command': command, 'build_log': str(log), 'build_log_sha256': ar.sha256(log),
                    'build_stderr_log': str(err), 'build_stderr_sha256': ar.sha256(err),
                    'patch': str(patch), 'patch_sha256': ar.sha256(patch), 'source_matches_prebuild': True,
                    'build_script_sha256': ar.sha256(Path(__file__)), 'primary_protocol_sha256': protocol_hash,
                    'probe_authorization_sha256': sys.argv[1], 'probe_evidence_sha256': authorization['evidence_sha256'],
                    'candidate_sources': authorization['candidate_sources'], 'source_copies': source_copies,
                    'prerequisite_scope': 'No-launch resource probe and independent source review; not numerical proof',
                    'change': 'Only up_show integer card-position shared cache and the two matching show_shared sizing expressions; float source order, ABI, launch dimensions and all other host behavior unchanged.'}
        ar.atomic_json(destination.with_suffix('.manifest.json'), manifest)
        print(name, manifest['binary_sha256'], flush=True)
    print('E020 build terminal success. Root must observe process exit before starting primary tests.', flush=True)
