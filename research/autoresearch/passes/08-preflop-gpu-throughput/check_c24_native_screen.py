"""Verify the first native-layout pair before publishing provisional timing."""
import hashlib
import json
import math
from pathlib import Path

P = Path(__file__).resolve().parent
R = P / 'raw'
ROOT = P.parents[3]

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

protocol = read(R / 'c24-native-screen-protocol.json')
assert protocol['baseline_verified'] and protocol['rounds'] == 3 and protocol['cap_seconds'] == 300
records = []
for name in ['c24-native-build-v1', 'c24-current-control-screen1', 'c24-current-candidate-screen1']:
    record = read(R / (name + '-exit.json'))
    assert record['returncode'] == 0 and record['reason'] is None and record['seconds'] < 300
    for file, digest in record['inputs'].items():
        assert sha(file) == digest, file
    for file, digest in record['solver_source_files'].items():
        assert sha(ROOT / file) == digest, file
    records.append(record)
assert all(x['solver_source_files'] == records[0]['solver_source_files'] for x in records)
assert records[1]['exe_sha256'] == records[2]['exe_sha256'] == protocol['exe_sha256']
for file, item in read(P / 'artifacts/c24-benchmark-source-map.json').items():
    assert sha(ROOT / file) == sha(P / item['archive']) == item['sha256']

control = read(R / 'c24-current-control-screen1-bench.json')
candidate = read(R / 'c24-current-candidate-screen1-bench.json')
assert sha(R / 'c24-current-control-screen1-bench.json') == protocol['baseline_sha256']
for key in ['arena_entries', 'arena_fingerprint', 'batch', 'budget_mb', 'hu_cache', 'samples',
            'nodes', 'initial_iteration', 'iteration', 'input', 'initial_buffers']:
    assert control[key] == candidate[key], key
assert (control['batch'], control['hu_cache'], control['samples'], control['nodes'],
        control['initial_iteration'], control['iteration']) == (4, 1, 1024, 5704840, 53, 56)
assert control['arena_entries'] == 1928235582
assert not control['packed'] and candidate['packed']
assert control['static_cdf'] is None and candidate['static_cdf']['row_stride'] == 333
assert len(control['rows']) == len(candidate['rows']) == 3
for i, (a, b) in enumerate(zip(control['rows'], candidate['rows'])):
    for key in ['index', 'iteration', 'warmup', 'evs', 'gaps']:
        assert a[key] == b[key], (i, key)
    assert a['iteration'] == 54 + i and a['warmup'] == (i < 2)
    assert all(math.isfinite(v) for k in ['evs', 'gaps'] for v in a[k])
for x in [control, candidate]:
    assert len(x['final_buffers']) == 46
    assert sum(x['final_buffers'].values()) + (x['static_cdf'] or {}).get('static_bytes', 0) == x['final_device_bytes']
assert control['initial_buffers'] == control['final_buffers']
assert [k for k in control['final_buffers'] if control['final_buffers'][k] != candidate['final_buffers'][k]] == ['d_mw_cdf']
saved_bytes = control['final_device_bytes'] - candidate['final_device_bytes']
assert saved_bytes == 1792219820
for file in ['candidate.cu', 'candidate.ptx', 'resources.json']:
    assert sha(R / 'c24-native-artifacts-v1' / file) == sha(R / 'c24-integrated-v1' / file), file

ratio = candidate['complete_seconds'] / control['complete_seconds']
result = dict(verified=True, admitted=ratio <= .99, retained=False,
    status=f'Provisional native timing: {(1-ratio)*100:.2f}% less complete time; full repeats pending',
    exact_checkpoints_and_arena=True, complete_state_fingerprint=control['arena_fingerprint'],
    full_solver_integrated=True, normal_app_integrated=False, pairs=1, rounds=3,
    control_seconds=control['complete_seconds'], candidate_seconds=candidate['complete_seconds'],
    complete_ratio=ratio, saved_device_bytes=saved_bytes,
    fixture='current', baseline='ordinary native four-sample path',
    exe_sha256=records[1]['exe_sha256'],
    scope='One shortened native-layout pair. Exact checkpoint values and full-arena fingerprint; no retention, deployment or convergence-speed claim.')
(R / 'c24-native-screen-verified.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
(R / 'c24-verified.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result))
