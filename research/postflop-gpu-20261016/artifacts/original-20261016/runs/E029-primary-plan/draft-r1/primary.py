"""Run the predeclared E029 unit screen and all six primary solves once, serially."""
import json, os, re, shutil, signal, subprocess, sys
from pathlib import Path

repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar

here = Path(__file__).resolve().parent
protocol_path = here / 'protocol.json'
assert ar.sha256(protocol_path) == 'PENDING_PROTOCOL_HASH'
protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
authorization=json.loads((here/'authorization.json').read_text(encoding='utf-8'))

assert authorization['direct_up_show_exact_pass'] is True
_direct_pin=authorization['prerequisites']['direct_up_show_terminal_review']
_direct_path=Path(_direct_pin['path'])
assert _direct_path.resolve()==Path(r'S:\GTOpen-research\postflop-gpu-20261016\comparisons\E029-direct-independent-reviewalidation.json').resolve()
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
assert protocol['order'] == ['V028-unit', 'B095', 'E029R1', 'E029R2', 'B096', 'B097', 'E029R3']
assert ar.sha256(ar.RESEARCH / 'binaries/E020-postflop_autoresearch.exe') == protocol['reference_binary_sha256']
assert ar.sha256(ar.RESEARCH / 'binaries/E020-postflop_autoresearch.manifest.json') == protocol['reference_manifest_sha256']
assert not (ar.RESEARCH / 'gpu-run.lock').exists(), 'Build or GPU work is still active'
assert json.loads((ar.RESEARCH / 'runs/E029-build/exit.json').read_text(encoding='utf-8'))['returncode'] == 0
current = ar.source_identity()['source_sha256']
compile_check = json.loads((ar.RESEARCH/'runs/E029-compile-check/complete.json').read_text(encoding='utf-8'))
assert compile_check['status'] == 'COMPILE_ONLY_CHECKS_PASSED' and compile_check['native_executions'] == 0
assert compile_check['source_sha256'] == current
assert compile_check['authorization_sha256'] == ar.sha256(here/'authorization.json')
assert compile_check['protocol_sha256'] == ar.sha256(protocol_path)
assert [r['returncode'] for r in compile_check['commands']] == [0]
for path,h in {**compile_check['evidence_sha256'], **compile_check['artifact_sha256']}.items(): assert ar.sha256(Path(path)) == h
binary_pins = {}
for name in ('E029-solver', 'E029-postflop_autoresearch'):
    manifest_path = ar.RESEARCH / 'binaries' / (name + '.manifest.json')
    binary_path = ar.RESEARCH / 'binaries' / (name + '.exe')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['source_sha256'] == current
    assert manifest['compile_check_sha256'] == ar.sha256(ar.RESEARCH/'runs/E029-compile-check/complete.json')
    assert manifest['primary_protocol_sha256'] == ar.sha256(protocol_path)
    assert manifest['probe_authorization_sha256'] == ar.sha256(here / 'authorization.json')
    assert manifest['build_script_sha256'] == ar.sha256(here / 'build.py')
    assert manifest['expected_cuda_present'] is True and manifest['accepted_cuda_absent'] is True
    assert manifest['source_matches_prebuild'] is True
    assert manifest['cargo_artifact']['fresh'] is False and manifest['solver_artifact']['fresh'] is False
    assert ar.sha256(binary_path) == manifest['binary_sha256']
    binary_pins[name] = {'binary_sha256': ar.sha256(binary_path), 'manifest_sha256': ar.sha256(manifest_path)}
status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
for identity in protocol['order']:
    assert not (ar.RESEARCH / 'runs' / identity).exists(), identity
    assert not any(row['id'] == identity for row in status['experiments']), identity
out = ar.RESEARCH / 'runs/E029-primary-execution'
out.mkdir(exist_ok=False)
env = os.environ.copy()
env.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None)
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
               'E029 showdown complement-only zeroing candidate' if kind == 'candidate' else ('Accepted E020 reference' if kind == 'baseline' else 'E029 GPU solver unit screen'),
               '--kind', kind, '--binary', str(ar.RESEARCH / 'binaries' / (binary + '.exe')),
               '--build-manifest', str(ar.RESEARCH / 'binaries' / (binary + '.manifest.json')), '--test', test]
    if ordinary:
        command.append('--not-ignored')
    ar.atomic_json(out / (identity + '.invocation.json'), {'at': ar.now(), 'command': command})
    print('Running', identity, flush=True)
    proc=None;fault=None;cleanup=None
    try:
        with (out / (identity + '.stdout.log')).open('xb') as stdout, (out / (identity + '.stderr.log')).open('xb') as stderr:
            proc=subprocess.Popen(command,cwd=repo,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            proc.wait(timeout=900)
    except BaseException as error:
        fault=repr(error);cleanup=ar.cleanup_child(proc);raise
    finally:
        ar.atomic_json(out/(identity+'.exit.json'),{'at':ar.now(),'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
    assert proc.returncode == 0, identity
    report = json.loads((ar.RESEARCH / 'runs' / identity / 'report.json').read_text(encoding='utf-8'))
    assert report['status'] == 'measured' and report['returncode'] == 0, identity
    assert report['test_pass_count'] == (protocol['expected_unit_passed'] if ordinary else 1), identity
    if ordinary:
        raw = (ar.RESEARCH / 'runs' / identity / 'stdout.log').read_text(encoding='utf-8')
        summaries = re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;', raw)
        assert summaries == [(str(protocol['expected_unit_passed']), '0', str(protocol['expected_unit_ignored']), '0', '0')], summaries
    verify_binary()
    assert ar.source_identity()['source_sha256'] == current, 'Source drift during run'
    print('Completed', identity, flush=True)


run('V028-unit', 'E029-solver', 'validation', '*', True)
for identity, candidate in [('B095', False), ('E029R1', True), ('E029R2', True), ('B096', False), ('B097', False), ('E029R3', True)]:
    run(identity, 'E029-postflop_autoresearch' if candidate else 'E020-postflop_autoresearch', 'candidate' if candidate else 'baseline', 'postflop_complete_cycle')
ar.atomic_json(out / 'complete.json', {'at': ar.now(), 'order': protocol['order'], 'accepted_performance_claim': False})
print('All predeclared E029 primary runs complete; independent comparison remains required.', flush=True)
