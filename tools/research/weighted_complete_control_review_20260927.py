"""Independent scalar readback of the full weighted/baseline bank control."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from weighted_evaluation_readback_v1 import parallel, verify_analysis, verify_stability, worker_guard

PREFIX = 'weighted-complete-evaluation-control-v1'
ARMS = ('9266201-baseline', '9266201-stratified', '9266301-baseline', '9266301-stratified')


def verify_identities(identities):
    trial_path = OUT / 'weighted-stratified-study-v1-registration.json'
    final_path = OUT / 'weighted-stratified-study-v1-training-result.json'
    trial, final = read(trial_path), read(final_path)
    assert final['training_complete'] and final['registration_sha256'] == sha(trial_path)
    baseline_trial_path = OUT / 'showdown-matched-training-v1-registration.json'
    baseline_trial = read(baseline_trial_path)
    assert len(identities) == 4
    for index, (name, identity) in enumerate(zip(ARMS, identities, strict=True)):
        assert identity['arm'] == name and identity['purpose'] == 'evaluation'
        assert len(identity['model_references']) == 78
        assert [r['generation'] for r in identity['model_references']] == list(range(78))
        if index % 2:
            assert identity['completed_iterations'] == 78 and identity['unplayed_excluded']['generation'] == 78
            assert identity['training_registration_sha256'] == sha(trial_path)
            assert identity['training_result_sha256'] == sha(final_path)
            audit_prefix = f'weighted-training-readback-parallel-v1-w4-{name}-0078'
            ap, ar = [OUT / f'{audit_prefix}-{s}.json' for s in ('result', 'registration')]
            audit, registration = read(ap), read(ar)
            assert audit['passed'] and audit['complete_arm'] and audit['completed_updates'] == 78
            assert audit['arm'] == name and audit['source_registration_sha256'] == sha(trial_path)
            assert audit['readback_registration_sha256'] == sha(ar)
            assert identity['independent_audit_sha256'] == sha(ap)
            assert identity['independent_registration_sha256'] == sha(ar)
            assert identity['checkpoint'] == audit['final_checkpoint'] == final['arms'][name]['checkpoint']
            assert len(registration['folders']) == 78
            references = []
            for folder in registration['folders']:
                metric_path = Path(folder) / 'metrics.json'
                assert sha(metric_path) == registration['inputs'][str(metric_path)]
                metric = read(metric_path)
                if references:
                    assert previous == metric['used_model']
                references.append(metric['used_model'])
                previous = metric['next_model']
            assert identity['model_references'] == references and identity['unplayed_excluded'] == previous
        else:
            assert identity['treatment'] == 'baseline' and identity['evaluation_qualified']
            assert identity['played_generations'] == list(range(78)) and identity['excluded_generation'] == 78
            assert identity['weights'] == [list(range(1, 79))] * 2
            assert identity['registration_sha256'] == sha(baseline_trial_path)
            endpoint = read(Path(baseline_trial['store']) / name / 'result.json')
            assert identity['checkpoint'] == endpoint['final_checkpoint']
            assert identity['model_references'] == endpoint['played_bank']
            ap, ar = [OUT / f'showdown-training-readback-v2-{name}-0078-{s}.json' for s in ('result', 'registration')]
            audit = read(ap)
            assert audit['passed'] and audit['complete_arm'] and audit['completed_updates'] == 78
            assert audit['arm'] == name and audit['source_registration_sha256'] == sha(baseline_trial_path)
            assert audit['readback_registration_sha256'] == sha(ar)
            assert identity['audit_sha256'] == sha(ap) and identity['readback_registration_sha256'] == sha(ar)
            for path, digest in identity['complete_study_bindings'].items():
                assert sha(path) == digest, path


def main():
    started, last = time.monotonic(), 0.
    def guard():
        nonlocal last
        assert time.monotonic() - started < 1800
        if time.monotonic() - last > 2:
            worker_guard()
            last = time.monotonic()
    guard()
    assert psutil.cpu_percent(interval=1) < 60
    rp, result_path = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    reg, result = read(rp), read(result_path)
    assert result['passed'] and result['complete'] and result['mode'] == reg['mode'] == 'control'
    assert reg['deals'] == result['deals'] == 64 and reg['batch_size'] == 32
    assert result['registration_sha256'] == sha(rp) and tuple(reg['arms']) == ARMS
    assert len(result['cpu_checks']) == 8 and len(result['root_cpu_checks']) == 4
    for check in result['cpu_checks'] + result['root_cpu_checks']:
        assert 0 <= check['maximum_policy_error'] < 1e-10 and 0 <= check['maximum_reach_error'] < 1e-10
    for p, h in reg['inputs'].items():
        guard()
        assert sha(p) == h, p
    qualified_result = OUT / 'weighted-evaluation-readback-control-v1-result.json'
    qualified_reg = OUT / 'weighted-evaluation-readback-control-v1-registration.json'
    qualified = read(qualified_result)
    assert qualified['passed'] and qualified['serial_and_parallel_exactly_equal']
    assert qualified['registration_sha256'] == sha(qualified_reg)
    assert qualified['source_sha256'] == sha(Path(__file__).parent / 'weighted_evaluation_readback_v1.py')
    store = Path(result['store'])
    assert str(store) == reg['store']
    for file, key in [('root-stability.json', 'root_stability_sha256'), ('analysis.json', 'analysis_sha256'),
                      ('bank-identities.json', 'bank_identities_sha256')]:
        assert sha(store / file) == result[key]
    verify_identities(read(store / 'bank-identities.json'))
    roots = verify_stability(read(store / 'root-stability.json'), read(OUT / 'preflop-allin-matrix-control-v1-matrix.json'))
    readback_registration = OUT / f'{PREFIX}-readback-registration.json'
    destination = OUT / f'{PREFIX}-independent-review.json'
    assert not readback_registration.exists() and not destination.exists()
    inputs = dict(reg['inputs'])
    inputs.update({str(p): sha(p) for p in [rp, result_path, qualified_result, qualified_reg,
                                          *Path(__file__).parent.glob('*.py')]})
    save(readback_registration, dict(inputs=inputs, workers=4, maximum_seconds=1800,
        source_result_sha256=sha(result_path), gpu_used=False, production_modified=False,
        scope='Chance, bank identities, transports, native values, scalar statistics and root summaries; no independent poker engine.'))
    source = (OUT / 'bb-context-candidate.json').read_text()
    deals = read(reg['reused_batch'])['deals']
    jobs = [(f'test-{offset:06d}', dict(format=2, batch_id=f'{PREFIX}-test-{offset:06d}',
              seed=0, query_limit=100000, deals=deals[offset:offset + 32])) for offset in (0, 32)]
    assert set(result['archive_manifest_hashes']) == set(result['batch_summary_hashes']) == {j[0] for j in jobs}
    values, observations = [], 0
    for name, (delta, count, digest) in parallel(jobs, store=store, manifests=result['archive_manifest_hashes'],
                                               source=source, roots=roots, guard=guard, workers=4):
        assert digest == result['batch_summary_hashes'][name]
        values.extend(delta)
        observations += count
    error = verify_analysis(read(store / 'analysis.json'), values, json.loads(source), expected_deals=64, control_only=True)
    for p, h in inputs.items():
        guard()
        assert sha(p) == h, p
    output = dict(passed=True, source_registration_sha256=sha(rp), source_result_sha256=sha(result_path),
                  readback_registration_sha256=sha(readback_registration), deals=64, observations=observations,
                  maximum_statistical_error=error, seconds=time.monotonic() - started,
                  gpu_used=False, production_modified=False, accuracy_qualified=False)
    save(destination, output)
    print(json.dumps(output), flush=True)


if __name__ == '__main__':
    main()
