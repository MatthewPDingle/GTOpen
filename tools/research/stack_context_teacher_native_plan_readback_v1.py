"""Independent receipt, transport and label-arithmetic readback of CPU controls.

No native execution, fitting or scientific accuracy evaluation. Original
teacher inference parity was checked by the consumed qualification itself.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import time
import psutil
import stack_context_teacher_conditioning_v1 as condition
from stack_context_teacher_path_v1 import Binding, encoded

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE = OUT/'stack-context-teacher-native-plan-check-v1'
NAME = 'stack-context-teacher-native-plan-readback-v1-result.json'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def close(a, b, limit=1e-10):assert math.isfinite(a) and math.isfinite(b) and abs(a-b) < limit


def main():
    target = OUT/NAME
    if target.exists():raise ValueError('Preserve recorded readback')
    result_path = OUT/'stack-context-teacher-native-plan-check-v1-result.json'
    attempt_path = OUT/'stack-context-teacher-native-plan-check-v1-attempt.json'
    r, a = read(result_path), read(attempt_path)
    assert r['complete'] and r['passed'] and r['inputs'] == a['inputs']
    assert not (OUT/'stack-context-teacher-native-plan-check-v1-failure.json').exists()
    for p, h in r['inputs'].items():assert sha(p) == h, p
    for p, h in r['artifacts'].items():assert sha(p) == h, p
    assert sum(Path(p).stat().st_size for p in r['artifacts']) == r['artifact_bytes'] < a['maximum_bytes']
    assert r['native_calls'] == 64 and r['conditional_plans'] == 32 and r['qualification_draws'] == 256
    assert r['fits'] == r['scientific_samples'] == 0 and r['gpu'] is False
    assert r['qualification_only'] is True and r['production_modified'] is False
    assert r['fixture_teacher_width'] == 362 and r['fixture_teacher_generations'] == [0, 1]
    for field in ('actual_fixed64_teacher_available', 'actual_diagnostic_registered',
                  'actual_diagnostic_complete', 'scientific_accuracy_evidence', 'scientific_label_noise_budget_registered'):
        assert r[field] is False
    assert len(r['negative_cases']) == len(set(r['negative_cases'])) == 10
    assert len(r['records']) == 16 and {(t['depth'], t['phase'], t['actor']) for t in r['records']} == {
        (d, p, a) for d in (20, 60) for p in range(4) for a in range(2)}
    manifest_identity = None;mixture_error = 0.;fold_error = 0.;reduction_error = 0.;draws = 0;profiles = 0
    for t in r['records']:
        assert len(t['replicates']) == 2
        actions = []
        for repeat, record in enumerate(t['replicates']):
            folder = Path(record['folder']);assert folder.parent == STORE
            assert sha(folder/'result.json') == record['result_sha256']
            receipt = read(folder/'result.json')
            for p, h in receipt['artifacts'].items():assert sha(folder/p) == h
            manifest = read(folder/'teacher-manifest.json')
            assert manifest['scope'] == 'implementation-fixture-only' and manifest['width'] == 362
            assert manifest['generations'] == [0, 1] and manifest['completed_cycles'] == 2
            assert manifest['generation_weights_by_player'] == [[1, 2], [1, 2]] and manifest['actual_fixed64_teacher'] is False
            identity = hashlib.sha256(encoded(manifest)).hexdigest()
            if manifest_identity is None:manifest_identity = identity
            assert receipt['teacher_manifest_sha256'] == identity == manifest_identity
            posterior, plan, start = [read(folder/name) for name in ('posterior.json', 'chance-plan.json', 'chance-start.json')]
            condition.audit_plan(posterior, plan, start)
            assert plan['draw_count'] == 8 and posterior['teacher_state_supported'] is True
            assert posterior['target']['phase'] == t['phase'] and posterior['target']['actor'] == t['actor']
            assert posterior['sha256'] == receipt['posterior_sha256'] == t['posterior_sha256']
            sigma = posterior['original_sigma'];n = len(sigma);context = json.loads(posterior['context_source'])
            assert context['config']['stack'] == t['depth']
            query = read(folder/'queries.json');binding = Binding(query)
            batch, conditional = read(folder/'batch.json'), read(folder/'conditional-batch.json')
            assert batch['deals'] == conditional['deals'] == plan['deals']
            assert query['context_source'] == posterior['context_source']
            assert query['batch_source'].encode() == (folder/'batch.json').read_bytes()
            for d, count in zip(plan['deals'], conditional['allin_counts']):
                assert count['private_cards'] == d[:4] and count['boards'] == 1712304
                assert count['wins']+count['ties']+count['losses'] == count['boards']
            assert len(conditional['allin_counts']) == len(plan['deals'])
            transport = read(folder/'profiles.json')
            assert transport['context_source'] == query['context_source']
            assert transport['batch_source'].encode() == (folder/'conditional-batch.json').read_bytes()
            native = read(folder/'native.json');names = ['original-target-mix']+['action'+str(i) for i in range(n)]
            assert [p['name'] for p in native['profiles']] == [p['name'] for p in transport['profiles']] == names
            assert native['terminal_estimator'] == 'conditional-preflop-allin-v1'
            for label in ('queries', 'evaluation'):assert read(folder/(label+'-process.json'))['code'] == 0
            q = receipt['per_draw_action_values'];assert len(q) == 8 and all(len(v) == n for v in q)
            forced = {};targets = set()
            for deal in plan['deals']:
                index, path = binding.trace(deal, t['hi']);targets.add(index)
                for i, selected, _ in path:
                    if i in forced:assert forced[i] == selected
                    forced[i] = selected
            assert len(targets) == 1;target_index = next(iter(targets));assert target_index not in forced
            for j, profile in enumerate(transport['profiles']):
                assert len(profile['policies']) == len(query['observations'])
                for i, (row, observation) in enumerate(zip(profile['policies'], query['observations'])):
                    assert (row['hi'], row['lo'], row['actor'], row['n']) == (
                        observation['hi'], observation['lo'], observation['actor'], observation['n'])
                    p = row['probabilities'];assert len(p) == 4
                    assert all(math.isfinite(v) and v >= 0 for v in p) and all(v == 0 for v in p[row['n']:])
                    close(math.fsum(p), 1, 1e-12)
                    if i in forced:assert p == [float(k == forced[i]) for k in range(4)]
                    elif i == target_index:
                        expected = list(sigma)+[0.]*(4-n) if j == 0 else [float(k == j-1) for k in range(4)]
                        assert p == expected
                    else:assert p == transport['profiles'][0]['policies'][i]['probabilities']
            for did in range(8):
                for j, profile in enumerate(native['profiles']):
                    v = profile['deals'][did];assert v['deal_index'] == did
                    close(v['terminal_mass'], 1, 1e-12)
                    close(sum(v['values'])+v['expected_rake'], context['dead_money'])
                    if j:close(v['values'][t['actor']], q[did][j-1], 1e-12)
                mix = math.fsum(sigma[j]*q[did][j] for j in range(n))
                error = abs(mix-native['profiles'][0]['deals'][did]['values'][t['actor']]);assert error < 1e-10
                mixture_error = max(mixture_error, error)
            mean = [math.fsum(v[j] for v in q)/8 for j in range(n)]
            baseline = math.fsum(v*p for v, p in zip(mean, sigma))
            for j, value in enumerate(mean):
                error = abs(value-receipt['action_values'][j]);assert error < 1e-12;reduction_error = max(reduction_error, error)
                close((value-baseline)/t['depth'], receipt['normalized_advantage'][j], 1e-12)
            close(baseline, receipt['value'], 1e-12)
            close(math.fsum(p*v for p, v in zip(sigma, receipt['normalized_advantage'])), 0, 1e-12)
            fold_error = max(fold_error, record['fold_cashflow_error']);assert record['fold_cashflow_error'] < 1e-10
            actions.append(mean);draws += 8;profiles += len(names)
        for i, value in enumerate(t['label_difference_in_starting_stack_units']):
            close(value, (actions[0][i]-actions[1][i])/t['depth'], 1e-12)
    reg = OUT/'stack-context-matched-learning-v1-registration.json'
    assert sha(reg) == 'ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3'
    identities = []
    for pid, created, parent in ((84788,1790752536.9318762,2980),(94544,1790753443.077002,84788),
        (100604,1790753511.1853917,94544),(93416,1790753512.997676,94544),
        (104568,1790753514.8583736,94544),(81788,1790753516.7905183,94544)):
        p = psutil.Process(pid);assert abs(p.create_time()-created) < .01 and p.ppid() == parent
        identities.append(dict(pid=pid, created=p.create_time(), parent=p.ppid(), command=p.cmdline()))
    status_path = OUT/'stack-context-parallel-continuation-v2-status.json';status = read(status_path)
    assert time.time()-status_path.stat().st_mtime < 60 and status['pid'] == 94544 and status['stage'] == 'parallel-training'
    assert not list(OUT.glob('stack-context-parallel-continuation-v2*failure.json'))
    training = Path('S:/GTOpen-research/stack-context-matched-learning-v1')
    counts = {a:read(training/a/'progress.json')['completed_cycles'] for a in ('A-baseline','A-relative','B-baseline','B-relative')}
    answer = dict(complete=True, passed=True, unix=time.time(), reader_source_sha256=sha(__file__),
        result_sha256=sha(result_path), attempt_sha256=sha(attempt_path), inputs_authenticated=len(r['inputs']),
        artifacts_authenticated=len(r['artifacts']), artifact_bytes=r['artifact_bytes'],
        conditional_plans=32, qualification_draws=draws, native_profiles=profiles,
        teacher_manifest_sha256=manifest_identity, maximum_mixture_error=mixture_error,
        maximum_fold_cashflow_error=fold_error, maximum_reduction_error=reduction_error,
        registration_sha256=sha(reg), live_processes=identities, published_cycles=counts,
        native_transport_and_arithmetic_checked=True, original_teacher_parity_from_consumed_qualification=True,
        qualification_only=True, scientific_samples=0, fits=0, new_native_calls=0, gpu=False,
        production_modified=False, actual_fixed64_teacher_available=False,
        actual_diagnostic_registered=False, actual_diagnostic_complete=False, scientific_accuracy_evidence=False)
    with target.open('xb') as stream:stream.write(encoded(answer));stream.flush();os.fsync(stream.fileno())
    print(json.dumps({k:answer[k] for k in ('passed','artifacts_authenticated','qualification_draws',
        'maximum_mixture_error','maximum_fold_cashflow_error','published_cycles')}))


if __name__ == '__main__':main()
