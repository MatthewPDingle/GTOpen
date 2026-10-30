"""Check scalar review across two actual resumed archive attempts."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import copy
import json
from pathlib import Path
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from weighted_routed_evaluation_readback_v1 import RoutedReader, initialize, check_one, parallel
from weighted_evaluation_readback_v1 import worker_guard, verify_analysis, verify_stability

PREFIX = 'weighted-routed-readback-control-v1'


def main():
    started, last = time.monotonic(), 0.
    def guard():
        nonlocal last
        assert time.monotonic() - started < 600
        if time.monotonic() - last > 2:
            worker_guard()
            last = time.monotonic()
    guard()
    assert psutil.cpu_percent(interval=1) < 60
    rp, result_path = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    assert not rp.exists() and not result_path.exists()
    previous = 'weighted-complete-driver-control-v2'
    old_paths = [OUT / f'{previous}-{s}.json' for s in ('registration', 'result', 'integration-proof')]
    registration, result, proof = map(read, old_paths)
    assert proof['passed'] and proof['source_result_sha256'] == sha(old_paths[1])
    assert result['registration_sha256'] == sha(old_paths[0]) and result['deals'] == 64
    store = Path(result['store'])
    assert len({r['attempt'] for r in result['routes'].values()}) == 2
    source_path = OUT / 'bb-context-candidate.json'
    matrix_path = OUT / 'preflop-allin-matrix-control-v1-matrix.json'
    root_path, analysis_path = store / 'root-stability.json', store / 'analysis.json'
    assert sha(root_path) == result['root_stability_sha256'] and sha(analysis_path) == result['analysis_sha256']
    source = source_path.read_text()
    roots = verify_stability(read(root_path), read(matrix_path))
    reader = RoutedReader(store, result['routes'], guard=guard)
    jobs = [(name, json.loads(reader.read_bytes(store / name / 'query-batch.json'))) for name in sorted(result['routes'])]
    # These were copied old outcomes, whose original chance identities remain.
    assert all(j[1]['batch_id'].startswith('showdown-composite-evaluation-study-v1-') for j in jobs)
    paths = [*old_paths, source_path, matrix_path, root_path, analysis_path]
    for name, route in result['routes'].items():
        paths.extend(store / route['attempt'] / (name + suffix) for suffix in ('.xz', '.manifest.json'))
    inputs = {str(p): sha(p) for p in [*paths, *Path(__file__).parent.glob('*.py')]}
    save(rp, dict(inputs=inputs, workers=4, deals=64, attempts=2, maximum_seconds=600,
                  gpu_used=False, production_modified=False,
                  scope='Routed original scalar checks; reused recorded policies and outcomes.'))
    initialize(store, result['routes'], source, roots)
    serial = [check_one(job) for job in jobs]
    actual = list(parallel(jobs, store=store, routes=result['routes'], source=source, roots=roots, guard=guard, workers=4))
    assert actual == serial
    values = [v for _, (rows, _, _) in actual for v in rows]
    error = verify_analysis(read(analysis_path), values, json.loads(source), expected_deals=64, control_only=False)
    rejected = []
    def reject(label, action):
        try:
            action()
        except (ValueError, AssertionError):
            rejected.append(label)
        else:
            raise AssertionError('Accepted ' + label)
    bad = copy.deepcopy(result['routes'])
    bad['test-000000']['attempt'] = '../escape'
    reject('escaping attempt', lambda: RoutedReader(store, bad, guard=guard))
    reject('missing first batch', lambda: RoutedReader(store, {'test-000032': result['routes']['test-000032']}, guard=guard))
    bad = copy.deepcopy(result['routes'])
    bad['test-000000']['owner_sha256'] = '0' * 64
    reject('wrong owner', lambda: RoutedReader(store, bad, guard=guard))
    bad = copy.deepcopy(result['routes'])
    bad['test-000000']['summary_sha256'] = '0' * 64
    reject('changed summary identity', lambda: RoutedReader(store, bad, guard=guard).read_bytes(store / 'test-000000/summary.json'))
    for path, digest in inputs.items():
        assert sha(path) == digest, path
    output = dict(passed=True, registration_sha256=sha(rp), deals=64, attempts=2,
                  observations=sum(v[1] for _, v in actual), serial_and_parallel_exactly_equal=True,
                  maximum_statistical_error=error, rejections=rejected,
                  helper_sha256=sha(ROOT / 'tools/research/weighted_routed_evaluation_readback_v1.py'),
                  seconds=time.monotonic() - started, gpu_used=False, production_modified=False,
                  accuracy_qualified=False)
    save(result_path, output)
    print(json.dumps(output), flush=True)


if __name__ == '__main__':
    main()
