"""Final independent review of all 65,536 routed evaluation deals."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_physical_deals_v1 import PhysicalDeals
from weighted_evaluation_checkpoint_v1 import restore_latest
from weighted_complete_control_review_20260927 import verify_identities
from weighted_evaluation_readback_v1 import verify_analysis, verify_stability, worker_guard
from weighted_routed_evaluation_readback_v1 import parallel

PREFIX = 'weighted-complete-evaluation-study-v1'
ARMS = ('9266201-baseline', '9266201-stratified', '9266301-baseline', '9266301-stratified')
DEALS = 65536
SEED = 9278101


def main():
    started, last = time.monotonic(), 0.
    def guard():
        nonlocal last
        assert time.monotonic() - started < 7200
        if time.monotonic() - last > 2:
            worker_guard()
            last = time.monotonic()
    guard()
    assert psutil.cpu_percent(interval=1) < 60
    rp, pp = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    reg, result = read(rp), read(pp)
    assert result['passed'] and result['complete'] and result['mode'] == reg['mode'] == 'study'
    assert result['registration_sha256'] == sha(rp)
    assert reg['deals'] == result['deals'] == DEALS and reg['test_seed'] == result['test_seed'] == SEED
    assert tuple(reg['arms']) == tuple(result['arms']) == ARMS and reg['batch_size'] == 32
    store = Path(result['store'])
    assert str(store) == reg['store']
    for path, digest in reg['inputs'].items():
        guard()
        assert sha(path) == digest, path
    for file, key in [('bank-identities.json', 'bank_identities_sha256'), ('root-stability.json', 'root_stability_sha256'),
                      ('analysis.json', 'analysis_sha256'), ('sampler-initial.json', 'sampler_initial_sha256'),
                      ('sampler-final.json', 'sampler_final_sha256')]:
        assert sha(store / file) == result[key]
    verify_identities(read(store / 'bank-identities.json'))
    roots = verify_stability(read(store / 'root-stability.json'), read(OUT / 'preflop-allin-matrix-control-v1-matrix.json'))
    source = (OUT / 'bb-context-candidate.json').read_text()
    sampler = PhysicalDeals(source, mode='full_deck', seed=SEED)
    assert read(store / 'sampler-initial.json') == sampler.checkpoint()
    recovered, accumulator, routes, reference = restore_latest(store, registration_sha256=sha(rp),
        bank_identities_sha256=result['bank_identities_sha256'], context_source=source,
        total_deals=DEALS, seed=SEED, guard=guard)
    assert reference == result['checkpoint'] and routes == result['routes'] and recovered.draws == DEALS
    assert read(store / 'sampler-final.json') == recovered.checkpoint()
    expected_analysis = accumulator.finish()
    expected_analysis['control_only'] = False
    assert expected_analysis == read(store / 'analysis.json')
    qr, qp = [OUT / f'weighted-routed-readback-control-v1-{s}.json' for s in ('registration', 'result')]
    qualified = read(qp)
    assert qualified['passed'] and qualified['serial_and_parallel_exactly_equal'] and qualified['attempts'] == 2
    assert qualified['registration_sha256'] == sha(qr)
    assert qualified['helper_sha256'] == sha(ROOT / 'tools/research/weighted_routed_evaluation_readback_v1.py')
    review_registration = OUT / f'{PREFIX}-readback-registration.json'
    destination = OUT / f'{PREFIX}-independent-review.json'
    assert not review_registration.exists() and not destination.exists()
    inputs = dict(reg['inputs'])
    inputs.update({str(p): sha(p) for p in [rp, pp, qr, qp, store / reference['file'], *Path(__file__).parent.glob('*.py')]})
    save(review_registration, dict(inputs=inputs, workers=8, queue_limit=16, deals=DEALS,
        maximum_seconds=7200, source_result_sha256=sha(pp), gpu_used=False, production_modified=False,
        scope='All registered deals and original scalar checks; no independent neural inference or poker engine.'))
    expected_names = [f'test-{n:06d}' for n in range(0, DEALS, 32)]
    assert set(routes) == set(expected_names)
    def jobs():
        for name in expected_names:
            guard()
            yield name, dict(format=2, batch_id=f'{PREFIX}-{name}', seed=0, query_limit=100000,
                             deals=sampler.sample(32)['deals'])
    values, observations, reviewed = [], 0, []
    for name, (delta, count, digest) in parallel(jobs(), store=store, routes=routes, source=source,
                                               roots=roots, guard=guard, workers=8):
        assert digest == routes[name]['summary_sha256']
        reviewed.append(name)
        values.extend(delta)
        observations += count
        if len(reviewed) % 64 == 0:
            print(json.dumps(dict(reviewed_deals=len(reviewed) * 32, total=DEALS)), flush=True)
    assert reviewed == expected_names and len(values) == DEALS
    assert sampler.checkpoint() == recovered.checkpoint()
    error = verify_analysis(read(store / 'analysis.json'), values, json.loads(source), expected_deals=DEALS, control_only=False)
    for path, digest in inputs.items():
        guard()
        assert sha(path) == digest, path
    output = dict(passed=True, source_registration_sha256=sha(rp), source_result_sha256=sha(pp),
                  readback_registration_sha256=sha(review_registration), deals=DEALS,
                  batches=len(reviewed), attempts=len({r['attempt'] for r in routes.values()}),
                  observations=observations, maximum_statistical_error=error,
                  seconds=time.monotonic() - started, gpu_used=False, production_modified=False,
                  accuracy_qualified=False, scientific_interpretation_pending=True)
    save(destination, output)
    print(json.dumps(output), flush=True)


if __name__ == '__main__':
    main()
