"""Run the predeclared E033 unit screen and all six primary solves once, serially."""
import json, os, re, shutil, signal, subprocess, sys
from pathlib import Path

repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar

here = Path(__file__).resolve().parent
protocol_path = here / 'protocol.json'
assert ar.sha256(protocol_path) == '35699be1ddbd6fce1fddb1f01dd91449d3b7b89c1aafe7334fadd9b5c12b3135'
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
assert protocol['order'] == ['V033-unit', 'B104', 'E033R1', 'E033R2', 'B105', 'B106', 'E033R3']
assert ar.sha256(ar.RESEARCH / 'binaries/E020-postflop_autoresearch.exe') == protocol['reference_binary_sha256']
assert ar.sha256(ar.RESEARCH / 'binaries/E020-postflop_autoresearch.manifest.json') == protocol['reference_manifest_sha256']
assert not (ar.RESEARCH / 'gpu-run.lock').exists(), 'Build or GPU work is still active'
assert json.loads((ar.RESEARCH / 'runs/E033-build/exit.json').read_text(encoding='utf-8'))['returncode'] == 0
current = ar.source_identity()['source_sha256']
binary_pins = {}
for name in ('E033-solver', 'E033-postflop_autoresearch'):
    manifest_path = ar.RESEARCH / 'binaries' / (name + '.manifest.json')
    binary_path = ar.RESEARCH / 'binaries' / (name + '.exe')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['source_sha256'] == current
    assert manifest['primary_protocol_sha256'] == ar.sha256(protocol_path)
    assert manifest['probe_authorization_sha256'] == ar.sha256(here / 'authorization.json')
    assert manifest['build_script_sha256'] == ar.sha256(here / 'build.py')
    assert manifest['accepted_cuda_present'] is True and manifest['unchanged_cuda_sha256'] == protocol['accepted_kernel_sha256']
    assert manifest['cleanup_source_present'] is True and manifest['cleanup_source_sha256']==protocol['cleanup_source_sha256']
    check_path=ar.RESEARCH/'runs/E033-compile-check/complete.json'
    assert manifest['compile_check_sha256']==ar.sha256(check_path)
    check_record=json.loads(check_path.read_text(encoding='utf-8'))
    assert check_record['status']=='COMPILE_ONLY_CHECKS_PASSED' and check_record['native_executions']==0
    assert check_record['authorization_sha256']==ar.sha256(here/'authorization.json')
    assert check_record['source_sha256']==current and check_record['protocol_sha256']==ar.sha256(protocol_path)
    for path,h in check_record['artifact_sha256'].items(): assert ar.sha256(Path(path))==h
    for path,h in check_record['evidence_sha256'].items(): assert ar.sha256(Path(path))==h
    assert manifest['source_matches_prebuild'] is True
    assert manifest['cargo_artifact']['fresh'] is False and manifest['solver_artifact']['fresh'] is False
    assert ar.sha256(binary_path) == manifest['binary_sha256']
    binary_pins[name] = {'binary_sha256': ar.sha256(binary_path), 'manifest_sha256': ar.sha256(manifest_path)}
status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
for identity in protocol['order']:
    assert not (ar.RESEARCH / 'runs' / identity).exists(), identity
    assert not any(row['id'] == identity for row in status['experiments']), identity
out = ar.RESEARCH / 'runs/E033-primary-execution'
out.mkdir(exist_ok=False)
env = os.environ.copy()
env.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None)
env.update(POSTFLOP_AUTORESEARCH_PROFILE='0', POSTFLOP_AUTORESEARCH_STORAGE='compressed', RAYON_NUM_THREADS='16')
ar.atomic_json(out / 'invocation.json', {'at': ar.now(), 'primary_protocol_sha256': ar.sha256(protocol_path),
    'script_sha256': ar.sha256(Path(__file__)), 'order': protocol['order'], 'source_sha256': current, 'candidate_binary_pins': binary_pins,
    'build_terminal_before_launch': True, 'accepted_performance_claim': False})


def verify_policy_markers(raw, candidate, plan):
    lines = raw.splitlines()
    assert 'E033_CACHE_CLEANUP_ERROR' not in raw, 'Cleanup failure marker'
    policy = [(i, json.loads(line.split('E033_CACHE_POLICY ', 1)[1]))
              for i, line in enumerate(lines) if 'E033_CACHE_POLICY ' in line]
    if not candidate:
        assert policy == [], 'Baseline unexpectedly contains candidate policy markers'
        return []
    assert len(policy) == 6, 'Require exactly three enabled and three clean markers'
    stages = [(i, json.loads(line.split('AUTORESEARCH_STAGE ', 1)[1]))
              for i, line in enumerate(lines) if 'AUTORESEARCH_STAGE ' in line]
    verified = []
    for fixture, owned_bytes, window_bytes in [('rainbow',5387252,5387136),('two-tone',5387252,5387136),('river',132,128)]:
        def position(stage):
            found = [i for i, row in stages if row.get('fixture_id') == fixture and row.get('stage') == stage]
            assert len(found) == 1, (fixture, stage, found)
            return found[0]
        start, build, ready, stop = [position(s) for s in ['fixture_start','build_complete','gpu_ready','timing_complete']]
        checks = [(i,r) for i,r in stages if r.get('fixture_id')==fixture and r.get('stage')=='convergence_check']
        assert checks and checks[-1][1]['iteration']==plan['expected_stops'][fixture]
        assert start < build < ready < checks[-1][0] < stop
        rows = [(i,r) for i,r in policy if start < i < stop]
        assert len(rows)==2 and [r['stage'] for _,r in rows]==['enabled','clean'], fixture
        assert build < rows[0][0] < ready and checks[-1][0] < rows[1][0] < stop, fixture
        for _, row in rows:
            assert set(row)=={'stage','enabled','owned_bytes','window_bytes','normalized_lines','cleanup_complete','errors'}
            assert row['enabled'] is True and row['errors'] is False, fixture
            assert row['owned_bytes']==owned_bytes and row['window_bytes']==window_bytes, fixture
            assert row['normalized_lines']==(0 if row['stage']=='enabled' else window_bytes//128), fixture
            assert row['cleanup_complete'] is (row['stage']=='clean'), fixture
            verified.append({'fixture_id':fixture,**row})
    assert [r for _,r in policy]==[{k:v for k,v in r.items() if k!='fixture_id'} for r in verified], 'Policy markers outside fixed fixture order'
    return verified



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
               'E033 scoped cache policy candidate' if kind == 'candidate' else ('Accepted E020 reference' if kind == 'baseline' else 'E033 GPU solver unit screen'),
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
        assert 'E033_CACHE_CLEANUP_ERROR' not in raw, 'Unit cleanup failure marker'
        summaries = re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;', raw)
        assert summaries == [(str(protocol['expected_unit_passed']), '0', str(protocol['expected_unit_ignored']), '0', '0')], summaries
        for test_name in protocol['expected_new_unit_tests']:
            assert re.search(r'(?m)^test '+re.escape(test_name)+r' \.\.\. ', raw), test_name
    if not ordinary:
        raw = (ar.RESEARCH / 'runs' / identity / 'stdout.log').read_text(encoding='utf-8')
        policy = verify_policy_markers(raw, kind=='candidate', protocol)
        ar.atomic_json(out/(identity+'.policy-markers.json'), {'run_id':identity,'candidate':kind=='candidate','markers':policy,'enabled_and_timed_cleanup_verified':kind=='candidate'})
    verify_binary()
    assert ar.source_identity()['source_sha256'] == current, 'Source drift during run'
    print('Completed', identity, flush=True)


run('V033-unit', 'E033-solver', 'validation', '*', True)
for identity, candidate in [('B104', False), ('E033R1', True), ('E033R2', True), ('B105', False), ('B106', False), ('E033R3', True)]:
    run(identity, 'E033-postflop_autoresearch' if candidate else 'E020-postflop_autoresearch', 'candidate' if candidate else 'baseline', 'postflop_complete_cycle')
ar.atomic_json(out / 'complete.json', {'at': ar.now(), 'order': protocol['order'], 'accepted_performance_claim': False})
print('All predeclared E033 primary runs complete; independent comparison remains required.', flush=True)
