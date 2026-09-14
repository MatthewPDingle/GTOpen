"""Independently audit completed full C24 pairs, keeping comparison gates open."""
import functools
import hashlib
import json
import math
import statistics
from pathlib import Path

P = Path(__file__).resolve().parent
R = P / 'raw'
ROOT = P.parents[3]
read = lambda path: json.loads(path.read_text(encoding='utf-8'))

@functools.cache
def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def audit(role, pair):
    name = f'c24-current-{role}-full{pair}'
    receipt = read(R / (name + '-exit.json'))
    assert receipt['returncode'] == 0 and receipt['reason'] is None and receipt['seconds'] <= 600
    assert receipt['exe_sha256'] == read(R / 'c24-native-frozen.json')['sha256']
    for file, digest in receipt['inputs'].items():
        assert sha(file) == digest, file
    for file, digest in receipt['solver_source_files'].items():
        assert sha(str(ROOT / file)) == digest, file
    x = read(R / (name + '-bench.json'))
    assert (x['batch'], x['budget_mb'], x['hu_cache'], x['samples'], x['nodes'],
            x['initial_iteration'], x['iteration']) == (4, 23911, 1, 1024, 5704840, 53, 59)
    assert x['arena_entries'] == 1928235582 and len(x['rows']) == 6
    for i, row in enumerate(x['rows']):
        assert row['iteration'] == 54+i and row['warmup'] == (i < 2)
        assert all(math.isfinite(v) for key in ['gaps', 'evs'] for v in row[key])
    assert x['packed'] == (role == 'candidate')
    assert len(x['final_buffers']) == 46
    assert sum(x['final_buffers'].values()) + (x['static_cdf'] or {}).get('static_bytes', 0) == x['final_device_bytes']
    return x

for file, item in read(P / 'artifacts/c24-benchmark-source-map.json').items():
    assert sha(str(ROOT / file)) == sha(str(P / item['archive'])) == item['sha256']
for file in ['candidate.cu', 'candidate.ptx', 'resources.json']:
    assert sha(str(R / 'c24-native-artifacts-v1' / file)) == sha(str(R / 'c24-integrated-v1' / file))

pairs = []
reference = None
screen = read(R / 'c24-current-control-screen1-bench.json')
for pair in range(1, 4):
    if not all((R / f'c24-current-{role}-full{pair}-exit.json').exists() for role in ['control', 'candidate']):
        break
    a, b = audit('control', pair), audit('candidate', pair)
    for key in ['input', 'arena_fingerprint', 'arena_entries', 'initial_buffers']:
        assert a[key] == b[key], key
    for i, (x, y) in enumerate(zip(a['rows'], b['rows'])):
        for key in ['iteration', 'index', 'warmup', 'gaps', 'evs']:
            assert x[key] == y[key], (pair, i, key)
            if i < 3:
                assert x[key] == screen['rows'][i][key], ('screen', i, key)
    if reference:
        assert a['arena_fingerprint'] == reference['arena_fingerprint']
        assert [(r['gaps'], r['evs']) for r in a['rows']] == [(r['gaps'], r['evs']) for r in reference['rows']]
    reference = a
    assert a['initial_buffers'] == a['final_buffers']
    assert [k for k in a['final_buffers'] if a['final_buffers'][k] != b['final_buffers'][k]] == ['d_mw_cdf']
    assert a['final_device_bytes'] - b['final_device_bytes'] == 1792219820
    assert a['static_cdf'] is None and b['static_cdf']['row_stride'] == 333
    pairs.append(dict(pair=pair, control_seconds=a['complete_seconds'], candidate_seconds=b['complete_seconds'],
                      ratio=b['complete_seconds']/a['complete_seconds']))
assert pairs, 'No completed full pair'
ratio = statistics.median(p['ratio'] for p in pairs)
result = dict(verified=True, admitted=ratio <= .97, retained=False,
    status=f'Full native timing: {(1-ratio)*100:.2f}% less time across {len(pairs)}/3 pairs; comparison gates pending',
    exact_checkpoints_and_arena=True, full_solver_integrated=True, normal_app_integrated=False,
    pairs=pairs, rounds=6, complete_ratio=ratio, complete_state_fingerprint=reference['arena_fingerprint'],
    saved_device_bytes=1792219820, fixture='current',
    remaining='Complete all three alternating native pairs and supported comparison fixtures before retention.',
    scope='Fixed-work throughput with matching full-arena fingerprints and checkpoint values. No deployment or convergence-speed claim.')
(R / 'c24-full-verified.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
(R / 'c24-verified.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(result))
