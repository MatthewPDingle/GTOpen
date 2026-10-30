"""Run all six fixed D065 diagnostic/control solves once, serially; no performance acceptance."""
import json, os, re, shutil, signal, subprocess, sys
from pathlib import Path

repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar

here = Path(__file__).resolve().parent
protocol_path = here / 'protocol.json'
assert ar.sha256(protocol_path) == 'UNSEALED_PROTOCOL_SHA256'
protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
authorization=json.loads((here/'authorization.json').read_text(encoding='utf-8'))
assert authorization['E020_accepted'] is True and authorization['E020_server_qualification_pass'] is True
assert authorization['independent_source_review_pass'] is True and authorization['independent_script_review_pass'] is True
assert authorization['evidence_sha256'][str(here/'scripts-manifest.json')]==ar.sha256(here/'scripts-manifest.json')
for path,h in authorization['evidence_sha256'].items(): assert ar.sha256(Path(path))==h
def interrupted(signum,_frame): raise KeyboardInterrupt(f'received signal {signum}')
for sig in [signal.SIGTERM,getattr(signal,'SIGBREAK',None)]:
    if sig is not None: signal.signal(sig,interrupted)
script_seal = json.loads((here / 'scripts-manifest.json').read_text(encoding='utf-8'))
assert script_seal['status'] == 'FROZEN_PROSPECTIVE_NOT_EXECUTED'
for name, expected in script_seal['script_sha256'].items():
    assert ar.sha256(here / name) == expected, name
for path, expected in script_seal['reference_sha256'].items():
    assert ar.sha256(Path(path)) == expected, path
assert protocol['order'] == ['D065B1', 'D065P1', 'D065P2', 'D065B2', 'D065B3', 'D065P3']
assert ar.sha256(ar.RESEARCH / 'binaries/E020-postflop_autoresearch.exe') == protocol['reference_binary_sha256']
assert ar.sha256(ar.RESEARCH / 'binaries/E020-postflop_autoresearch.manifest.json') == protocol['reference_manifest_sha256']
assert not (ar.RESEARCH / 'gpu-run.lock').exists(), 'Build or GPU work is still active'
assert json.loads((ar.RESEARCH / 'runs/D065-build/exit.json').read_text(encoding='utf-8'))['returncode'] == 0
current = ar.source_identity()['source_sha256']
binary_pins = {}
for name in ('D065-postflop_autoresearch',):
    manifest_path = ar.RESEARCH / 'binaries' / (name + '.manifest.json')
    binary_path = ar.RESEARCH / 'binaries' / (name + '.exe')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['source_sha256'] == current
    assert manifest['primary_protocol_sha256'] == ar.sha256(protocol_path)
    assert manifest['probe_authorization_sha256'] == ar.sha256(here / 'authorization.json')
    assert manifest['build_script_sha256'] == ar.sha256(here / 'build.py')
    assert ar.sha256(binary_path) == manifest['binary_sha256']
    binary_pins[name] = {'binary_sha256': ar.sha256(binary_path), 'manifest_sha256': ar.sha256(manifest_path)}
status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
for identity in protocol['order']:
    assert not (ar.RESEARCH / 'runs' / identity).exists(), identity
    assert not any(row['id'] == identity for row in status['experiments']), identity
out = ar.RESEARCH / 'runs/D065-execution'
out.mkdir(exist_ok=False)
env = os.environ.copy()
env.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None)
env.pop('POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE',None)
env.update(POSTFLOP_AUTORESEARCH_PROFILE='0', POSTFLOP_AUTORESEARCH_STORAGE='compressed', RAYON_NUM_THREADS='16')
ar.atomic_json(out / 'invocation.json', {'at': ar.now(), 'primary_protocol_sha256': ar.sha256(protocol_path),
    'script_sha256': ar.sha256(Path(__file__)), 'order': protocol['order'], 'source_sha256': current, 'candidate_binary_pins': binary_pins,
    'build_terminal_before_launch': True, 'accepted_performance_claim': False})


def run(identity, binary, kind, test, ordinary=False):
    assert ar.source_identity()['source_sha256'] == current, 'Source drift before run'
    for path,h in authorization['evidence_sha256'].items(): assert ar.sha256(Path(path))==h
    assert shutil.disk_usage(ar.RESEARCH).free>=50*1024**3
    def verify_binary():
        for path, expected in script_seal['reference_sha256'].items():
            assert ar.sha256(Path(path)) == expected, path
        for path, expected in authorization['evidence_sha256'].items():
            assert ar.sha256(Path(path)) == expected, path
        if binary in binary_pins:
            assert ar.sha256(ar.RESEARCH / 'binaries' / (binary + '.exe')) == binary_pins[binary]['binary_sha256']
            assert ar.sha256(ar.RESEARCH / 'binaries' / (binary + '.manifest.json')) == binary_pins[binary]['manifest_sha256']
        else:
            assert binary == 'E020-postflop_autoresearch'
            assert ar.sha256(ar.RESEARCH / 'binaries/E020-postflop_autoresearch.exe') == protocol['reference_binary_sha256']
            assert ar.sha256(ar.RESEARCH / 'binaries/E020-postflop_autoresearch.manifest.json') == protocol['reference_manifest_sha256']
    verify_binary()
    if kind == 'baseline':
        assert ar.sha256(ar.RESEARCH / 'binaries/E020-postflop_autoresearch.exe') == protocol['reference_binary_sha256']
        assert ar.sha256(ar.RESEARCH / 'binaries/E020-postflop_autoresearch.manifest.json') == protocol['reference_manifest_sha256']
    command = [sys.executable, 'tools/postflop_autoresearch.py', '--id', identity, '--title',
               'D065 instrumented full-readback diagnostic' if binary.startswith('D065-') else 'D065 ordinary accepted E020 diagnostic reference',
               '--kind', kind, '--binary', str(ar.RESEARCH / 'binaries' / (binary + '.exe')),
               '--build-manifest', str(ar.RESEARCH / 'binaries' / (binary + '.manifest.json')), '--test', test]
    if ordinary:
        command.append('--not-ignored')
    run_env=env.copy()
    run_env['POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE']='1' if binary.startswith('D065-') else '0'
    ar.atomic_json(out / (identity + '.invocation.json'), {'at': ar.now(), 'command': command, 'environment_overrides':{'POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE':run_env['POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE']}})
    print('Running', identity, flush=True)
    proc=None;fault=None;cleanup=None
    try:
        with (out / (identity + '.stdout.log')).open('xb') as stdout, (out / (identity + '.stderr.log')).open('xb') as stderr:
            proc=subprocess.Popen(command,cwd=repo,env=run_env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            proc.wait(timeout=900)
    except BaseException as error:
        fault=repr(error);cleanup=ar.cleanup_child(proc);raise
    finally:
        ar.atomic_json(out/(identity+'.exit.json'),{'at':ar.now(),'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
    assert proc.returncode == 0, identity
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


for identity, candidate in [('D065B1', False), ('D065P1', True), ('D065P2', True), ('D065B2', False), ('D065B3', False), ('D065P3', True)]:
    run(identity, 'D065-postflop_autoresearch' if candidate else 'E020-postflop_autoresearch', 'diagnostic', 'postflop_complete_cycle')
ar.atomic_json(out / 'complete.json', {'at': ar.now(), 'order': protocol['order'], 'accepted_performance_claim': False})
print('All fixed D065 runs complete; diagnostic exactness/usefulness assessment remains required.', flush=True)
