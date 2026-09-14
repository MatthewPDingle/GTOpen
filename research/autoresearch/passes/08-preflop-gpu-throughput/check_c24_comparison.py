"""Audit comparison evidence and apply all registered C24 timing gates."""
import functools
import hashlib
import json
import math
import statistics
from pathlib import Path

P = Path(__file__).resolve().parent
R = P / 'raw'
ROOT = P.parents[3]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))

@functools.cache
def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

native = read(R / 'c24-full-verified.json')
assert native['verified'] and len(native['pairs']) == 3 and native['complete_ratio'] <= .97
for file, item in read(P / 'artifacts/c24-benchmark-source-map.json').items():
    assert sha(str(ROOT / file)) == sha(str(P / item['archive'])) == item['sha256']
for file in ['candidate.cu', 'candidate.ptx', 'resources.json']:
    assert sha(str(R / 'c24-native-artifacts-v1' / file)) == sha(str(R / 'c24-integrated-v1' / file))

fixtures = {}
for fixture in ['small', 'large']:
    rows = []
    reference = None
    for pair in range(1, 4):
        if not all((R / f'c24-witness{fixture}-{role}-full{pair}-exit.json').exists() for role in ['control', 'candidate']):
            break
        values = []
        for role in ['control', 'candidate']:
            name = f'c24-witness{fixture}-{role}-full{pair}'
            receipt = read(R / (name + '-exit.json'))
            assert receipt['returncode'] == 0 and receipt['reason'] is None and receipt['seconds'] <= 300
            assert receipt['exe_sha256'] == read(R / 'c24-native-frozen.json')['sha256']
            for file, digest in receipt['inputs'].items():
                assert sha(file) == digest, file
            for file, digest in receipt['solver_source_files'].items():
                assert sha(str(ROOT / file)) == digest, file
            x = read(R / (name + '-bench.json'))
            assert (x['batch'], x['hu_cache'], x['budget_mb'], x['samples']) == (32, 1, 23911, 1024)
            assert x['nodes'] == (23038 if fixture == 'small' else 1567754)
            assert x['iteration'] == x['initial_iteration'] + 6 and len(x['rows']) == 6
            for i, row in enumerate(x['rows']):
                assert row['iteration'] == x['initial_iteration'] + i + 1 and row['warmup'] == (i < 2)
                assert all(math.isfinite(v) for key in ['gaps', 'evs'] for v in row[key])
            assert x['packed'] == (role == 'candidate')
            assert len(x['final_buffers']) == 46
            assert sum(x['final_buffers'].values()) + (x['static_cdf'] or {}).get('static_bytes', 0) == x['final_device_bytes']
            values.append(x)
        a, b = values
        for key in ['input', 'arena_entries', 'arena_fingerprint', 'initial_buffers', 'initial_iteration', 'iteration']:
            assert a[key] == b[key], (fixture, pair, key)
        for x, y in zip(a['rows'], b['rows']):
            for key in ['index', 'iteration', 'warmup', 'gaps', 'evs']:
                assert x[key] == y[key], (fixture, pair, key)
        if reference:
            assert a['arena_fingerprint'] == reference['arena_fingerprint']
            assert [(r['gaps'], r['evs']) for r in a['rows']] == [(r['gaps'], r['evs']) for r in reference['rows']]
        reference = a
        assert a['initial_buffers'] == a['final_buffers'] and a['static_cdf'] is None
        assert [k for k in a['final_buffers'] if a['final_buffers'][k] != b['final_buffers'][k]] == ['d_mw_cdf']
        assert b['static_cdf']['row_stride'] == 2160
        assert b['final_buffers']['d_mw_cdf'] * 5440 == a['final_buffers']['d_mw_cdf'] * 2160
        rows.append(dict(pair=pair, control_seconds=a['complete_seconds'], candidate_seconds=b['complete_seconds'],
                         ratio=b['complete_seconds']/a['complete_seconds']))
    if rows:
        ratio = statistics.median(r['ratio'] for r in rows)
        fixtures[fixture] = dict(pairs=rows, median_ratio=ratio, passes_no_regression=ratio <= 1.03,
                                 fingerprint=reference['arena_fingerprint'])
complete = all(len(fixtures.get(f, {}).get('pairs', [])) == 3 for f in ['small', 'large'])
passed = complete and all(f['passes_no_regression'] for f in fixtures.values())
result = dict(verified=True, admitted=all(f['passes_no_regression'] for f in fixtures.values()), retained=passed,
    status=('Retained research result: 24.94% less native time; all comparison gates pass' if passed else
            'Native pairs verified; comparison fixtures ' + ('failed' if complete else 'in progress')),
    exact_checkpoints_and_arena=True, full_solver_integrated=True, normal_app_integrated=False,
    current=native, comparisons=fixtures, comparison_complete=complete,
    complete_ratio=native['complete_ratio'],
    scope='Ordinary-path fixed-work timing qualification only. Current four-sample and comparison 32-sample paths are independent controls; no cross-fixture chaining. Normal app integration and deployment remain.')
(R / 'c24-comparison-verified.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
if complete:
    (R / 'c24-verified.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(result))
