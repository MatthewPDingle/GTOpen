"""Independent final readback of the complete fixed-count CUDA evaluation.

Refuses incomplete runs. Replays chance and reconstructs root choices, paired
observations and intervals; does not rerun the neural bank or native evaluator.
"""
import json
import math
from pathlib import Path
import time

import numpy as np
import psutil

from loopback_research_validation import idle
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-hybrid-evaluation-v1'


def main():
    started = time.monotonic()
    last = 0.

    def guard():
        nonlocal last
        now = time.monotonic()
        if now-last >= 2:
            assert now-started < 900 and idle(), 'Audit budget or production activity'
            assert psutil.virtual_memory().available >= 20_000_000_000
            last = now

    guard()
    regpath = OUT / (PREFIX + '-registration.json')
    statuspath = OUT / (PREFIX + '-status.json')
    resultpath = OUT / (PREFIX + '-result.json')
    status = json.loads(statuspath.read_text())
    assert status['state'] == 'complete' and status['error'] is None and status['exit_code'] == 0
    assert not (ROOT / 'research/preflop-evolution/representative-coverage-20260919/running.lock').exists()
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        if (p.info['name'] or '').lower().startswith('python'):
            assert not any(Path(a).name == 'hu_sampled_physical_hybrid_evaluation_20260922.py'
                           for a in (p.info['cmdline'] or [])[1:]), p.info['pid']
    reg = json.loads(regpath.read_text())
    result = json.loads(resultpath.read_text())
    assert result['terminal'] and result['registration_sha256'] == sha(regpath)
    for p, expected in reg['inputs'].items(): assert sha(p) == expected, p
    store = Path(reg['store'])
    disk_result = json.loads((store / 'result.json').read_text())
    assert all(result[k] == value for k, value in disk_result.items())
    training = json.loads(Path(reg['training_registration']).read_text())
    training_review = json.loads(Path(reg['training_review']).read_text())
    assert training_review['passed'] and training_review['terminal_complete']
    assert training_review['completed_iterations'] == reg['selected_iterations'] == 78
    assert training_review['checkpoint'] == reg['checkpoint']
    assert training_review['source_registration_sha256'] == sha(reg['training_registration'])
    assert training['config']['deals_per_iteration'] == 512
    assert reg['config']['train_seed'] == 69101 and reg['config']['test_seed'] == 69102
    control_path = OUT/(PREFIX+'-cpu-control.json')
    assert result['cpu_control_sha256'] == sha(control_path) and result['fresh_test_stream']
    control = json.loads(control_path.read_text())
    assert control['complete_deals'] == 256 and control['registration_sha256'] == sha(regpath)
    assert len(control['artifacts']) == 16*5
    for p,h in control['artifacts'].items(): assert sha(p) == h,p
    assert control_path.stat().st_mtime_ns <= (store/'response.json').stat().st_mtime_ns
    resources = json.loads((OUT/(PREFIX+'-resources.json')).read_text())
    assert resources and 0 < status['seconds'] < reg['maximum_seconds']
    assert all(r['free_host_bytes'] >= reg['host_reserve_bytes'] and r['free_gpu_bytes'] >= reg['gpu_reserve_bytes']
        and r['free_disk_bytes'] >= reg['disk_reserve_bytes'] and r['store_bytes'] <= reg['maximum_store_bytes'] for r in resources)
    assert result['checkpoint'] == reg['checkpoint']
    assert result['played_generations'] == list(range(reg['selected_iterations']))
    assert result['excluded_unused_generation'] == reg['selected_iterations']
    cfg = reg['config']
    assert result['completed_training_deals'] == cfg['training_deals'] == 8192
    assert result['completed_evaluation_deals'] == cfg['evaluation_deals'] == 16384
    assert cfg['batch_size'] == 16 and cfg['minimum_training_deals'] == 16
    context_source = Path(reg['context']).read_text()
    context = json.loads(context_source)
    from sampled_physical_hybrid_checkpoint_v1 import read_object, verify_bank
    objects = Path(reg['objects'])
    checkpoint = json.loads(read_object(objects,reg['checkpoint']))
    verify_bank(objects,78,checkpoint['played_bank'],checkpoint['next_model'],context_source=context_source)
    stack, dead = context['config']['stack'], context['dead_money']
    width = 2*stack+dead
    response_path = store / 'response.json'
    response = json.loads(response_path.read_text())
    response_hash = sha(response_path)
    assert response_hash == result['response_sha256']
    counts = [0]*169
    sums = [[0.]*4 for _ in range(169)]
    train_ids = []
    test_counts = [0]*169
    paired_rows = []
    applied = 0
    checked_batches = []
    cpu_comparisons = []
    max_mixture = 0.
    max_conservation = 0.
    max_forward = 0.
    series = ('trained-response', 'always-fold', 'always-call', 'always-raise', 'always-jam')

    for phase, total, seed in [('train', cfg['training_deals'], cfg['train_seed']),
                               ('test', cfg['evaluation_deals'], cfg['test_seed'])]:
        sampler = PhysicalDeals(context_source, mode='full_deck', seed=seed)
        for offset in range(0, total, cfg['batch_size']):
            guard()
            name = f'{PREFIX}-{phase}-{offset}'
            folder = store / name
            batch_path = folder / 'batch.json'
            batch = json.loads(batch_path.read_text())
            assert batch == dict(format=2, batch_id=name, query_limit=100000, seed=0,
                                 deals=sampler.sample(cfg['batch_size'])['deals'])
            summary_path = folder / 'summary.json'
            assert sha(summary_path) == result['batch_summary_hashes'][name]
            summary = json.loads(summary_path.read_text())
            assert set(summary['artifacts']) == {'batch.json', 'queries.json', 'profiles.json', 'native.json'}
            for artifact, expected in summary['artifacts'].items(): assert sha(folder / artifact) == expected
            queries = json.loads((folder / 'queries.json').read_text())
            profiles = json.loads((folder / 'profiles.json').read_text())
            assert queries['context_source'] == profiles['context_source'] == context_source
            assert queries['batch_source'] == profiles['batch_source'] == batch_path.read_text()
            obs = queries['observations']
            roots = [i for i, o in enumerate(obs) if o['phase'] == 0 and int(o['hi']) == 1]
            assert roots and all(obs[i]['actor'] == 0 and obs[i]['n'] == 4 for i in roots)
            keys = [(o['hi'], o['lo'], o['actor'], o['n']) for o in obs]
            by_name = {}
            for profile in profiles['profiles']:
                rows = profile['policies']
                assert [(r['hi'], r['lo'], r['actor'], r['n']) for r in rows] == keys
                probabilities = np.asarray([r['probabilities'] for r in rows])
                assert probabilities.shape == (len(obs), 4)
                assert np.isfinite(probabilities).all() and np.min(probabilities) >= 0
                assert np.max(np.abs(probabilities.sum(1)-1)) < 1e-12
                for n in (2, 3):
                    indices = [i for i, o in enumerate(obs) if o['n'] == n]
                    assert not np.any(probabilities[indices, n:])
                by_name[profile['name']] = probabilities
            assert set(by_name) == {'baseline', 'action-0', 'action-1', 'action-2', 'action-3'}
            for action in range(4):
                expected = by_name['baseline'].copy()
                expected[roots] = 0.
                expected[roots, action] = 1.
                assert np.array_equal(expected, by_name[f'action-{action}'])
            root_by_class = {}
            for i in roots:
                key = int(obs[i]['lo'])
                c = hand_class([key & 63, (key >> 6) & 63])
                if c in root_by_class:
                    assert np.max(np.abs(root_by_class[c] - by_name['baseline'][i])) < 1e-12
                root_by_class[c] = by_name['baseline'][i]
            classes = [hand_class(d[:2]) for d in batch['deals']]
            mixes = np.asarray([root_by_class[c] for c in classes])
            assert classes == summary['classes'] and np.array_equal(mixes, summary['root_probabilities'])
            native = json.loads((folder / 'native.json').read_text())
            max_forward = max(max_forward, native['maximum_forward_cashflow_error'])
            max_conservation = max(max_conservation, native['maximum_conservation_error'])
            assert native['fixed_policy_evaluation_only'] and not native['bounds_best_response_above']
            values = {}
            for profile in native['profiles']:
                assert [d['deal_index'] for d in profile['deals']] == list(range(cfg['batch_size']))
                for d in profile['deals']:
                    assert abs(d['terminal_mass']-1.) < 1e-10
                    assert abs(sum(d['values'])+d['expected_rake']-dead) < 1e-8
                    assert -1e-10 <= d['expected_rake'] <= context['config']['rake_cap']+1e-10
                values[profile['name']] = np.asarray([d['values'] for d in profile['deals']])
            assert set(values) == set(by_name)
            actions = np.stack([values[f'action-{a}'] for a in range(4)], axis=1)
            baseline = values['baseline']
            assert np.max(np.abs(actions[:, 0, 0]+context['nodes'][0]['invested'][0])) < 1e-12
            assert np.min(actions) >= -stack-1e-10 and np.max(actions) <= stack+dead+1e-10
            mixture = float(np.max(np.abs((mixes[:, :, None]*actions).sum(1)-baseline)))
            max_mixture = max(max_mixture, mixture)
            assert mixture < 1e-10
            assert np.array_equal(actions[:, :, 0], summary['action_values'])
            assert np.array_equal(baseline[:, 0], summary['baseline_values'])
            if phase == 'train':
                for j, c in enumerate(classes):
                    counts[c] += 1
                    for a in range(4): sums[c][a] += float(actions[j, a, 0])
                    train_ids.append(f'{name}-{j}')
                if str(offset) in reg['cpu_reference_batches']:
                    reference = reg['cpu_reference_batches'][str(offset)]
                    ref = Path(reference['folder'])
                    for artifact in ('batch.json','queries.json','profiles.json','native.json','summary.json'):
                        assert str(ref/artifact) in control['artifacts']
                    old_batch = json.loads((ref/'batch.json').read_text())
                    assert old_batch == batch
                    old_queries = json.loads((ref/'queries.json').read_text())
                    assert old_queries['observations'] == obs and old_queries['context_source'] == context_source
                    old_profiles = json.loads((ref/'profiles.json').read_text())
                    old_rows = old_profiles['profiles'][0]['policies']
                    assert [(r['hi'],r['lo'],r['actor'],r['n']) for r in old_rows] == keys
                    old_p = np.asarray([r['probabilities'] for r in old_rows])
                    old_summary = json.loads((ref/'summary.json').read_text())
                    policy_error = float(np.max(np.abs(old_p-by_name['baseline'])))
                    payoff_error = float(max(np.max(np.abs(np.asarray(old_summary['action_values'])-actions[:,:,0])),
                        np.max(np.abs(np.asarray(old_summary['baseline_values'])-baseline[:,0]))))
                    assert policy_error <= reference['policy_tolerance'] == 1e-4
                    assert payoff_error <= reference['payoff_tolerance_bb'] == 1e-3
                    expected_comparison = dict(reference_folder=str(ref),observations=len(obs),
                        maximum_policy_error=policy_error,maximum_payoff_error_bb=payoff_error,passed=True)
                    assert summary['cpu_comparison'] == expected_comparison
                    cpu_comparisons.append(expected_comparison)
            else:
                assert response_path.stat().st_mtime_ns <= batch_path.stat().st_mtime_ns
                matrix = np.zeros((cfg['batch_size'], 5))
                matrix[:, 1:] = actions[:, :, 0]-baseline[:, 0, None]
                for j, c in enumerate(classes):
                    selected = response['actions'][c]
                    test_counts[c] += 1
                    if selected >= 0:
                        matrix[j, 0] = actions[j, selected, 0]-baseline[j, 0]
                        applied += 1
                saved = json.loads((folder / 'paired.json').read_text())
                assert saved['series'] == list(series) and saved['response_sha256'] == response_hash
                assert np.array_equal(saved['differences'], matrix)
                assert np.isfinite(matrix).all() and np.max(np.abs(matrix)) <= width
                paired_rows.extend(matrix.tolist())
            checked_batches.append(name)
        assert sampler.draws == total
        if phase == 'train':
            expected_actions = [max(range(4), key=lambda a: sums[c][a]) if counts[c] >= cfg['minimum_training_deals']
                                else -1 for c in range(169)]
            assert response == dict(format=1, training_ids=train_ids, actions=expected_actions,
                                    training_counts=counts, action_count=4, minimum_training_deals=16,
                                    fallback='unchanged baseline', tie_rule='first maximizing legal action')

    assert set(checked_batches) == set(result['batch_summary_hashes'])
    assert len(checked_batches) == 1536 and len(paired_rows) == 16384
    assert test_counts == result['evaluation_class_counts']
    assert applied == result['applied_response_deals']
    assert 16384-applied == result['fallback_deals']
    assert cpu_comparisons == result['cpu_reference_comparisons'] and len(cpu_comparisons) == 16
    rebuilt = {}
    for index, name in enumerate(series):
        xs = [row[index] for row in paired_rows]
        n = len(xs)
        mean = math.fsum(xs)/n
        variance = math.fsum((x-mean)**2 for x in xs)/(n-1)
        logarithm = math.log(4*len(series)/.05)
        radius = math.sqrt(2*variance*logarithm/n)+7*(2*width)*logarithm/(3*(n-1))
        expected = dict(count=n, mean=mean, sample_variance=variance, radius=radius,
                        lower=max(-width, mean-radius), upper=min(width, mean+radius),
                        family_error_probability=.05, bounds_best_response_above=False)
        actual = result['intervals'][name]
        assert actual.keys() == expected.keys()
        for key, value in expected.items():
            if isinstance(value, float): assert math.isclose(value, actual[key], rel_tol=2e-12, abs_tol=1e-10), (name, key)
            else: assert value == actual[key]
        rebuilt[name] = expected
    assert max_forward < 1e-8 and max_conservation < 1e-8
    assert sha(response_path) == response_hash
    assert sha(control_path) == result['cpu_control_sha256']
    for p,h in control['artifacts'].items(): assert sha(p) == h,p
    for p, expected in reg['inputs'].items(): assert sha(p) == expected, p
    guard()
    review = dict(passed=True, registration_sha256=sha(regpath), result_sha256=sha(resultpath),
                  terminal_status_sha256=sha(statuspath), reviewer_sha256=sha(Path(__file__)),
                  registered_inputs_verified=len(reg['inputs']), completed_batches_verified=len(checked_batches),
                  training_deals_replayed=8192, evaluation_deals_replayed=16384,
                  training_response_reconstructed=True, paired_differences_reconstructed=16384*5,
                  intervals_reconstructed=rebuilt, supported_training_classes=sum(c>=16 for c in counts),
                  fallback_test_deals=16384-applied, maximum_root_mixture_error=max_mixture,
                  maximum_forward_cashflow_error=max_forward, maximum_conservation_error=max_conservation,
                  seconds=time.monotonic()-started, production_modified=False,
                  physical_poker_convergence_qualified=False,
                  scope='Complete final readback: replayed both independent chance streams; checked all batch artifact hashes, pure root deviations, legal policies, native payoff identities, training-only response selection, paired outcomes and final family-adjusted intervals. Neural inference and native traversal were not rerun. This remains a restricted deviation evaluation, not an equilibrium or Wizard-equivalence certificate.')
    save(OUT / (PREFIX + '-independent-review.json'), review)
    print(json.dumps(dict(passed=True, batches=len(checked_batches), seconds=review['seconds'],
                          supported_classes=review['supported_training_classes'], fallback_deals=review['fallback_test_deals'])))


if __name__ == '__main__':
    main()
