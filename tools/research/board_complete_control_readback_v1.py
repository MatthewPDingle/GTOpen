"""CPU readback of the actual complete-bank control, including bank identities.

Shares the poker engine and policy implementations. Independently checks frozen
archives, hand sampling, actor routing, cashflows and scalar statistical sums.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import argparse
import json
from pathlib import Path
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha
from board_prefix_publication_v1 import atomic_json
from weighted_evaluation_readback_v1 import parallel, verify_analysis, verify_stability, worker_guard
from board_complete_evaluation_support_v1 import ARMS, design

PREFIX = 'board-complete-evaluation-control-v1'


def verify_identities(identities):
    candidates, _ = design()
    assert len(identities) == 4
    for i, (name, identity) in enumerate(zip(ARMS, identities, strict=True)):
        assert identity['arm'] == name and identity['purpose'] == 'evaluation'
        assert identity['completed_iterations'] == 78 and identity['unplayed_excluded']['generation'] == 78
        assert len(identity['model_references']) == 78
        assert [r['generation'] for r in identity['model_references']] == list(range(78))
        if i % 2:
            tr = OUT / 'board-root-matched-continuation-v1-registration.json'
            tp = OUT / 'board-root-matched-continuation-v1-result.json'
            ar = OUT / 'board-matched-complete-readback-v1-registration.json'
            ap = OUT / 'board-matched-complete-readback-v1-result.json'
            trial, end, audit_reg, audit = map(read, (tr, tp, ar, ap))
            assert trial['arms'] == candidates and trial['generations_per_arm'] == 78
            assert end['passed'] and end['training_complete']
            assert audit['passed'] and audit['complete_training']
            assert audit['registration_sha256'] == sha(ar) and audit['source_result_sha256'] == sha(tp)
            endpoint = [r for r in end['arms'] if r['arm'] == name]
            checked = [r for r in audit['arms'] if r['arm'] == name]
            jobs = [r for r in audit_reg['jobs'] if r['name'] == name]
            assert len(endpoint) == len(checked) == len(jobs) == 1
            endpoint, checked, job = endpoint[0], checked[0], jobs[0]
            assert checked['generations'] == 78 and checked['boards_checked'] == 312
            assert checked['physical_roots_checked'] == 39936
            assert job['cfg'] == candidates[i//2]['config']
            assert identity['root_config'] == job['cfg']['board_root']
            pp = Path(endpoint['progress_path'])
            assert sha(pp) == endpoint['progress_sha256'] == audit_reg['inputs'][str(pp)]
            progress = read(pp)
            assert progress['completed'] == 78 and progress['registration_sha256'] == sha(tr)
            assert progress['generations'] == job['generations']
            assert progress['checkpoint'] == endpoint['checkpoint'] == checked['final_checkpoint']
            rows = progress['generations']
            metric_paths = [(Path(r['path']), r['sha256']) for r in rows]
        else:
            tr = OUT / 'weighted-stratified-study-v1-registration.json'
            tp = OUT / 'weighted-stratified-study-v1-training-result.json'
            prefix = f'weighted-training-readback-parallel-v1-w4-{name}-0078'
            ar, ap = [OUT / f'{prefix}-{s}.json' for s in ('registration', 'result')]
            trial, end, audit_reg, audit = map(read, (tr, tp, ar, ap))
            assert trial['generations'] == 78 and end['training_complete']
            assert audit['passed'] and audit['complete_arm'] and audit['arm'] == name
            assert audit['completed_updates'] == 78 and audit['bb_roots_reconstructed'] == 39936
            assert audit['source_registration_sha256'] == sha(tr)
            assert audit['readback_registration_sha256'] == sha(ar)
            endpoint = end['arms'][name]
            assert endpoint['checkpoint'] == audit['final_checkpoint']
            metric_paths = [(Path(f)/'metrics.json', audit_reg['inputs'][str(Path(f)/'metrics.json')])
                            for f in audit_reg['folders']]
        assert end['registration_sha256'] == sha(tr)
        assert identity['training_registration_sha256'] == sha(tr)
        assert identity['training_result_sha256'] == sha(tp)
        assert identity['independent_audit_sha256'] == sha(ap)
        assert identity['independent_registration_sha256'] == sha(ar)
        assert identity['checkpoint'] == endpoint['checkpoint'] and endpoint['completed'] == 78
        assert len(metric_paths) == 78
        references, previous = [], None
        for generation, (mp, digest) in enumerate(metric_paths):
            assert sha(mp) == digest == audit_reg['inputs'][str(mp)]
            metric = read(mp)
            assert metric['iteration'] == generation+1 and metric['used_model']['generation'] == generation
            assert metric['next_model']['generation'] == generation+1
            if previous is not None:
                assert metric['used_model'] == previous
            references.append(metric['used_model']); previous = metric['next_model']
        assert metric['checkpoint'] == endpoint['checkpoint']
        assert references == identity['model_references'] and previous == identity['unplayed_excluded']


def main(run=False):
    rp, result_path = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    pending = [str(p) for p in (rp, result_path) if not p.exists()]
    if not run:
        print(json.dumps(dict(ready=not pending, pending=pending, gpu_used=False,
            complete_control_verified=False, production_modified=False)), flush=True)
        return
    assert not pending, 'The actual complete-bank control must finish first'
    began, last = time.monotonic(), 0.
    def guard():
        nonlocal last
        assert time.monotonic()-began < 1800
        if time.monotonic()-last > 2:
            worker_guard(); last = time.monotonic()
    guard()
    assert psutil.cpu_percent(interval=1) < 30
    reg, result = read(rp), read(result_path)
    assert result['passed'] and result['complete'] and result['control_only']
    assert result['mode'] == reg['mode'] == 'control'
    assert result['registration_sha256'] == sha(rp)
    assert reg['deals'] == result['deals'] == 64 and reg['batch_size'] == 32
    assert tuple(reg['arms']) == tuple(result['arms']) == ARMS
    assert reg['fresh_test_deals_drawn'] == result['fresh_test_deals_drawn'] == 0
    assert len(result['cpu_checks']) == 8 and len(result['root_cpu_checks']) == 4
    assert {(x['batch'], x['bank']) for x in result['cpu_checks']} == {
        (f'test-{o:06d}', k) for o in (0, 32) for k in range(4)}
    assert {x['bank'] for x in result['root_cpu_checks']} == set(range(4))
    for row in result['cpu_checks'] + result['root_cpu_checks']:
        assert 0 <= row['maximum_policy_error'] < 1e-10 and 0 <= row['maximum_reach_error'] < 1e-10
    for p, h in reg['inputs'].items():
        guard(); assert sha(p) == h, p
    qr, qp = [OUT / f'weighted-evaluation-readback-control-v1-{s}.json' for s in ('registration', 'result')]
    qualified = read(qp)
    assert qualified['passed'] and qualified['serial_and_parallel_exactly_equal']
    assert qualified['registration_sha256'] == sha(qr)
    assert qualified['source_sha256'] == sha(ROOT / 'tools/research/weighted_evaluation_readback_v1.py')
    store = Path(result['store'])
    assert store == Path('S:/GTOpen-research') / PREFIX and reg['store'] == str(store)
    for file, key in [('root-stability.json', 'root_stability_sha256'), ('analysis.json', 'analysis_sha256'),
                      ('bank-identities.json', 'bank_identities_sha256')]:
        assert sha(store / file) == result[key]
    verify_identities(read(store / 'bank-identities.json'))
    roots = verify_stability(read(store / 'root-stability.json'), read(OUT / 'preflop-allin-matrix-control-v1-matrix.json'))
    rr = OUT / f'{PREFIX}-readback-registration.json'
    destination = OUT / f'{PREFIX}-independent-review.json'
    assert not rr.exists() and not destination.exists()
    inputs = dict(reg['inputs'])
    inputs.update({str(p): sha(p) for p in [rp, result_path, qr, qp, *Path(__file__).parent.glob('*.py')]})
    atomic_json(rr, dict(inputs=inputs, workers=2, maximum_seconds=1800,
        source_result_sha256=sha(result_path), gpu_used=False, production_modified=False,
        scope='Complete identities, old control chance, actor transports, archived native values and scalar statistics; shared poker engine and inference implementations.'))
    source = (OUT / 'bb-context-candidate.json').read_text()
    deals = read(reg['reused_batch'])['deals']
    jobs = [(f'test-{offset:06d}', dict(format=2, batch_id=f'{PREFIX}-test-{offset:06d}',
        seed=0, query_limit=100000, deals=deals[offset:offset+32])) for offset in (0, 32)]
    assert set(result['archive_manifest_hashes']) == set(result['batch_summary_hashes']) == {j[0] for j in jobs}
    values, observations = [], 0
    for name, (delta, count, digest) in parallel(jobs, store=store, manifests=result['archive_manifest_hashes'],
            source=source, roots=roots, guard=guard, workers=2):
        assert digest == result['batch_summary_hashes'][name]
        values.extend(delta); observations += count
    error = verify_analysis(read(store / 'analysis.json'), values, json.loads(source), expected_deals=64, control_only=True)
    for p, h in inputs.items():
        guard(); assert sha(p) == h, p
    output = dict(passed=True, source_registration_sha256=sha(rp), source_result_sha256=sha(result_path),
        readback_registration_sha256=sha(rr), deals=64, observations=observations,
        maximum_statistical_error=error, seconds=time.monotonic()-began,
        gpu_used=False, production_modified=False, accuracy_qualified=False)
    atomic_json(destination, output); print(json.dumps(output), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
