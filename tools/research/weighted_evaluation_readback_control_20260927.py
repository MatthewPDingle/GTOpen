"""Qualify the CPU reviewer on existing evidence without consuming fresh deals."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import copy
import json
from pathlib import Path
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from owned_columnar_evaluation_archive_v1 import restore
from weighted_evaluation_readback_v1 import initialize, check_one, parallel, verify_analysis, verify_stability, worker_guard

PREFIX = 'weighted-evaluation-readback-control-v1'


def main():
    started = time.monotonic()
    last = 0.
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
    old = OUT / 'showdown-composite-evaluation-control-v1-result.json'
    result = read(old)
    assert result['passed'] and result['complete'] and result['deals'] == 64
    old_registration = OUT / 'showdown-composite-evaluation-control-v1-registration.json'
    assert result['registration_sha256'] == sha(old_registration)
    store = Path(result['store'])
    root_path, analysis_path = store / 'root-stability.json', store / 'analysis.json'
    assert sha(root_path) == result['root_stability_sha256'] and sha(analysis_path) == result['analysis_sha256']
    source_path = OUT / 'bb-context-candidate.json'
    matrix_path = OUT / 'preflop-allin-matrix-control-v1-matrix.json'
    source = source_path.read_text()
    roots = verify_stability(read(root_path), read(matrix_path))
    jobs, archive_paths = [], []
    for name, identity in sorted(result['archive_manifest_hashes'].items()):
        mp, ap = store / (name + '.manifest.json'), store / (name + '.xz')
        assert sha(mp) == identity
        parts = restore(ap, read(mp), guard=guard)
        jobs.append((name, json.loads(parts['query-batch.json'])))
        archive_paths.extend([mp, ap])
    assert len(jobs) == 2
    inputs = {str(p): sha(p) for p in [old, old_registration, root_path, analysis_path, source_path,
              matrix_path, *archive_paths, *Path(__file__).parent.glob('*.py')]}
    save(rp, dict(inputs=inputs, workers=4, deals=64, reused_evidence=str(old), maximum_seconds=600,
                  gpu_used=False, production_modified=False,
                  scope='Serial versus parallel scalar readback, statistics and malformed-input rejection.'))
    initialize(store, result['archive_manifest_hashes'], source, roots)
    began = time.monotonic()
    serial = [check_one(job) for job in jobs]
    serial_seconds = time.monotonic() - began
    kwargs = dict(store=store, manifests=result['archive_manifest_hashes'], source=source,
                  roots=roots, guard=guard, workers=4)
    began = time.monotonic()
    actual = list(parallel(jobs, **kwargs))
    parallel_seconds = time.monotonic() - began
    assert actual == serial
    values = []
    for name, (delta, _, digest) in actual:
        assert digest == result['batch_summary_hashes'][name]
        values.extend(delta)
    error = verify_analysis(read(analysis_path), values, json.loads(source), expected_deals=64, control_only=True)
    rejected = []
    bad = (jobs[0][0], dict(jobs[0][1], batch_id='deliberately-invalid-control'))
    try:
        list(parallel([bad], **kwargs))
    except AssertionError:
        rejected.append('changed deal batch identity')
    else:
        raise AssertionError('Malformed evidence accepted')
    try:
        list(parallel([jobs[0], jobs[0]], **kwargs))
    except ValueError:
        rejected.append('duplicate batch')
    else:
        raise AssertionError('Duplicate evidence accepted')
    changed = copy.deepcopy(read(analysis_path))
    changed['contrasts'][0]['mean'] += 1.
    try:
        verify_analysis(changed, values, json.loads(source), expected_deals=64, control_only=True)
    except AssertionError:
        rejected.append('changed statistical result')
    else:
        raise AssertionError('Changed mean accepted')
    for p, digest in inputs.items():
        assert sha(p) == digest, p
    output = dict(passed=True, registration_sha256=sha(rp), deals=64, observations=sum(v[1] for _, v in actual),
                  serial_seconds=serial_seconds, parallel_seconds=parallel_seconds,
                  serial_and_parallel_exactly_equal=True, maximum_statistical_error=error,
                  rejections=rejected, source_sha256=sha(ROOT / 'tools/research/weighted_evaluation_readback_v1.py'),
                  seconds=time.monotonic() - started, gpu_used=False, production_modified=False,
                  accuracy_qualified=False, scope='Two reused batches; no full-study speed or accuracy claim.')
    save(result_path, output)
    print(json.dumps(output), flush=True)


if __name__ == '__main__':
    main()
