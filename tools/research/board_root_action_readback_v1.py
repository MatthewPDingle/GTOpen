"""Independent saved-file readback of the two-batch root-only control.

Uses the qualified routed archive reader, direct row comparisons and Decimal
mixture arithmetic. Does not rerun neural models or the native evaluator.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import time
from weighted_routed_evaluation_readback_v1 import RoutedReader
from weighted_evaluation_readback_v1 import worker_guard

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'board-root-action-control-v1'
ACTIONS = ('fold','call','raise','jam')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def native_class(a, b):
    ar, br = a//4, b//4
    if ar == br:
        return ar*14
    high, low = max(ar,br), min(ar,br)
    return high*13+low if a % 4 == b % 4 else low*13+high


def main():
    began = time.monotonic()
    destination = OUT/'board-root-action-control-v1-review.json'
    assert not destination.exists()
    worker_guard()
    rp, pp = (OUT/(PREFIX+'-'+s+'.json') for s in ('registration','result'))
    reg, result = read(rp), read(pp)
    assert result['passed'] and result['registration_sha256'] == sha(rp)
    assert reg['batches'] == ['test-000000','test-032768']
    for path,h in reg['inputs'].items(): assert sha(path) == h
    study = read(OUT/'weighted-complete-board-root-study-v1-result.json')
    source_store = Path(study['store'])
    reader = RoutedReader(source_store, study['routes'], guard=worker_guard)
    store = Path('S:/GTOpen-research')/PREFIX
    assert read(store/'control-owner.json') == dict(root=str(store),registration_sha256=sha(rp))
    context = (OUT/'bb-context-candidate.json').read_bytes().decode()
    dead = Decimal(str(json.loads(context)['dead_money']))
    biggest = Decimal(0)
    checked_rows = mixtures = 0
    artifact_bindings = {}
    for name, report in zip(reg['batches'], result['batches'], strict=True):
        worker_guard()
        assert name == report['name'] and reg['routes'][name] == study['routes'][name]
        folder = store/name
        for path,h in report['new_artifacts'].items():
            assert Path(path).parent == folder and sha(path) == h
            artifact_bindings[path] = h
        raw = {n:reader.read_bytes(source_store/name/n) for n in
            ('query-batch.json','conditional-batch.json','profiles.json','queries.json','native.json')}
        assert all(hashlib.sha256(v).hexdigest() == report['original_artifacts'][n] for n,v in raw.items())
        original = json.loads(raw['profiles.json'])
        query = json.loads(raw['queries.json'])
        deals = json.loads(raw['query-batch.json'])['deals']
        assert (folder/'profiles.json').read_bytes() == raw['profiles.json']
        assert (folder/'conditional-batch.json').read_bytes() == raw['conditional-batch.json']
        forced = read(folder/'forced-profiles.json')
        assert {k:v for k,v in forced.items() if k != 'profiles'} == {
            k:v for k,v in original.items() if k != 'profiles'}
        assert forced['context_source'] == context and forced['batch_source'] == raw['conditional-batch.json'].decode()
        saved = json.loads(raw['native.json'])
        repeated = read(folder/'replayed-native.json')
        assert saved == repeated, 'Original native replay must be exactly identical'
        evaluated = read(folder/'forced-native.json')
        compact = read(folder/'action-values.json')
        assert len(forced['profiles']) == len(evaluated['profiles']) == 32
        assert len(original['profiles']) == len(saved['profiles']) == len(compact['profiles']) == 8
        root_by_class = {}
        for i,o in enumerate(query['observations']):
            if o['hi'] != '1': continue
            assert o['actor'] == 0 and o['phase'] == 0 and o['own_history'] == [] and o['n'] == 4
            lo = int(o['lo']); c = native_class(lo & 63, (lo >> 6) & 63)
            assert c not in root_by_class
            root_by_class[c] = i
        assert len(root_by_class) == report['root_rows']
        for p, baseline in enumerate(original['profiles']):
            for a, action in enumerate(ACTIONS):
                fp = forced['profiles'][4*p+a]
                assert fp['name'] == evaluated['profiles'][4*p+a]['name'] == baseline['name']+':root-'+action
                assert len(fp['policies']) == len(baseline['policies'])
                for i,(old,new) in enumerate(zip(baseline['policies'],fp['policies'],strict=True)):
                    expected = dict(old)
                    if query['observations'][i]['hi'] == '1':
                        expected['probabilities'] = [int(k == a) for k in range(4)]
                    assert expected == new
                    checked_rows += 1
            assert compact['profiles'][p]['name'] == baseline['name']
            assert len(compact['profiles'][p]['deals']) == len(deals) == 32
            for did,deal in enumerate(deals):
                c = native_class(*deal[:2]); row = compact['profiles'][p]['deals'][did]
                probs = baseline['policies'][root_by_class[c]]['probabilities']
                assert row['deal_index'] == did and row['native_class_index'] == c and row['root_probabilities'] == probs
                values = []
                for a in range(4):
                    sample = evaluated['profiles'][4*p+a]['deals'][did]
                    assert sample['deal_index'] == did and abs(sample['terminal_mass']-1) < 1e-12
                    v = [*sample['values'],sample['expected_rake']]
                    assert row['action_values'][a] == v
                    assert abs(sum(map(lambda x:Decimal(str(x)),v))-dead) < Decimal('1e-10')
                    values.append(v)
                target = saved['profiles'][p]['deals'][did]
                with localcontext() as ctx:
                    ctx.prec = 40
                    for k,wanted in enumerate([*target['values'],target['expected_rake']]):
                        mixed = sum(Decimal(str(probs[a]))*Decimal(str(values[a][k])) for a in range(4))
                        error = abs(mixed-Decimal(str(wanted)))
                        assert error < Decimal('1e-10')
                        biggest = max(biggest,error);mixtures += 1
        assert report['tamper_rejections'] == ['non_root_probability','root_actor','root_identity','batch_source','root_mixture']
    for path,h in reg['inputs'].items(): assert sha(path) == h
    worker_guard()
    result = dict(passed=True, control_registration_sha256=sha(rp), control_result_sha256=sha(pp),
        reviewer_sha256=sha(Path(__file__)), retained_artifacts=artifact_bindings,
        batches=2, deals=64, forced_profiles_per_batch=32, policy_rows_compared=checked_rows,
        decimal_mixtures_checked=mixtures, maximum_decimal_mixture_error=str(biggest),
        original_native_replays_exactly_equal=True, non_root_policies_unchanged=True,
        seconds=time.monotonic()-began, gpu_used=False, new_deals=0, accuracy_qualified=False,
        independent_native_engine=False, new_neural_inference=False, full_replay_launched=False)
    with destination.open('xb') as stream:
        stream.write(json.dumps(result,separators=(',',':'),allow_nan=False).encode())
    print(json.dumps({k:v for k,v in result.items() if k != 'retained_artifacts'}))


if __name__ == '__main__':
    main()
