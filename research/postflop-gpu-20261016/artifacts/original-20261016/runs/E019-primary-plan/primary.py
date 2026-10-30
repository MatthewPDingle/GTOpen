"""Run the predeclared E019 unit screen and all six primary solves once, serially."""
import json, os, re, subprocess, sys
from pathlib import Path

repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar

here = Path(__file__).resolve().parent
protocol_path = here / 'protocol.json'
assert ar.sha256(protocol_path) == 'c74dfd6cbd57804c1fd8e9bad65744a8ab2b525f3e6aa230b5ed46c6959b1fba'
protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
assert protocol['order'] == ['V019-unit', 'B059', 'E019R1', 'E019R2', 'B060', 'B061', 'E019R3']
assert ar.sha256(ar.RESEARCH / 'binaries/E015-postflop_autoresearch.exe') == protocol['reference_binary_sha256']
assert ar.sha256(ar.RESEARCH / 'binaries/E015-postflop_autoresearch.manifest.json') == protocol['reference_manifest_sha256']
assert not (ar.RESEARCH / 'gpu-run.lock').exists(), 'Build or GPU work is still active'
assert json.loads((ar.RESEARCH / 'runs/E019-build/exit.json').read_text(encoding='utf-8'))['returncode'] == 0
current = ar.source_identity()['source_sha256']
binary_pins = {}
for name in ('E019-solver', 'E019-postflop_autoresearch'):
    manifest_path = ar.RESEARCH / 'binaries' / (name + '.manifest.json')
    binary_path = ar.RESEARCH / 'binaries' / (name + '.exe')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['source_sha256'] == current
    assert ar.sha256(binary_path) == manifest['binary_sha256']
    binary_pins[name] = {'binary_sha256': ar.sha256(binary_path), 'manifest_sha256': ar.sha256(manifest_path)}
status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
for identity in protocol['order']:
    assert not (ar.RESEARCH / 'runs' / identity).exists(), identity
    assert not any(row['id'] == identity for row in status['experiments']), identity
out = ar.RESEARCH / 'runs/E019-primary-execution'
out.mkdir(exist_ok=False)
env = os.environ.copy()
env.update(POSTFLOP_AUTORESEARCH_PROFILE='0', POSTFLOP_AUTORESEARCH_STORAGE='compressed', RAYON_NUM_THREADS='16')
ar.atomic_json(out / 'invocation.json', {'at': ar.now(), 'primary_protocol_sha256': ar.sha256(protocol_path),
    'script_sha256': ar.sha256(Path(__file__)), 'order': protocol['order'], 'source_sha256': current, 'candidate_binary_pins': binary_pins,
    'build_terminal_before_launch': True, 'accepted_performance_claim': False})


def run(identity, binary, kind, test, ordinary=False):
    assert ar.source_identity()['source_sha256'] == current, 'Source drift before run'
    def verify_binary():
        if binary in binary_pins:
            assert ar.sha256(ar.RESEARCH / 'binaries' / (binary + '.exe')) == binary_pins[binary]['binary_sha256']
            assert ar.sha256(ar.RESEARCH / 'binaries' / (binary + '.manifest.json')) == binary_pins[binary]['manifest_sha256']
    verify_binary()
    if kind == 'baseline':
        assert ar.sha256(ar.RESEARCH / 'binaries/E015-postflop_autoresearch.exe') == protocol['reference_binary_sha256']
        assert ar.sha256(ar.RESEARCH / 'binaries/E015-postflop_autoresearch.manifest.json') == protocol['reference_manifest_sha256']
    command = [sys.executable, 'tools/postflop_autoresearch.py', '--id', identity, '--title',
               'E019 exact fold-reduction candidate' if kind == 'candidate' else ('Accepted E015 reference' if kind == 'baseline' else 'E019 GPU solver unit screen'),
               '--kind', kind, '--binary', str(ar.RESEARCH / 'binaries' / (binary + '.exe')),
               '--build-manifest', str(ar.RESEARCH / 'binaries' / (binary + '.manifest.json')), '--test', test]
    if ordinary:
        command.append('--not-ignored')
    ar.atomic_json(out / (identity + '.invocation.json'), {'at': ar.now(), 'command': command})
    print('Running', identity, flush=True)
    with (out / (identity + '.stdout.log')).open('xb') as stdout, (out / (identity + '.stderr.log')).open('xb') as stderr:
        completed = subprocess.run(command, cwd=repo, env=env, stdout=stdout, stderr=stderr)
    ar.atomic_json(out / (identity + '.exit.json'), {'at': ar.now(), 'returncode': completed.returncode})
    assert completed.returncode == 0, identity
    report = json.loads((ar.RESEARCH / 'runs' / identity / 'report.json').read_text(encoding='utf-8'))
    assert report['status'] == 'measured' and report['returncode'] == 0, identity
    assert report['test_pass_count'] == (84 if ordinary else 1), identity
    if ordinary:
        raw = (ar.RESEARCH / 'runs' / identity / 'stdout.log').read_text(encoding='utf-8')
        summaries = re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;', raw)
        assert summaries == [('84', '0', '4', '0', '0')], summaries
    verify_binary()
    assert ar.source_identity()['source_sha256'] == current, 'Source drift during run'
    print('Completed', identity, flush=True)


run('V019-unit', 'E019-solver', 'validation', '*', True)
for identity, candidate in [('B059', False), ('E019R1', True), ('E019R2', True), ('B060', False), ('B061', False), ('E019R3', True)]:
    run(identity, 'E019-postflop_autoresearch' if candidate else 'E015-postflop_autoresearch', 'candidate' if candidate else 'baseline', 'postflop_complete_cycle')
ar.atomic_json(out / 'complete.json', {'at': ar.now(), 'order': protocol['order'], 'accepted_performance_claim': False})
print('All predeclared E019 primary runs complete; independent comparison remains required.', flush=True)
