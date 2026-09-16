"""Read-only independent result checks for the final N32/N35 controls."""
import math
import sys
import continuation_paired_blend_gpu as gpu
import continuation_policy_stability as stability

study = gpu.study


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12), (a, b)


def snapshot(path, start, end, config):
    s = study.read(path)
    assert s['config'] == config
    assert (s['start_iteration'], s['iteration'], s['warmup_iterations']) == (start, end, 0)
    assert len(s['gaps']) == len(s['evs']) == len(config['positions'])
    assert all(math.isfinite(x) for x in s['gaps'] + s['evs'])
    assert all(x >= -1e-6 for x in s['gaps'])
    assert abs(sum(s['evs'])) < .0002
    assert s['learning_seconds'] > 0
    for row in s['views']:
        v = row['view']
        n = len(v['actions'])
        assert len(v['strategy']) == 169*n
        assert all(math.isfinite(x) and x >= -1e-6 for x in v['strategy'] + v['reach'])
        if n:
            for h in range(169):
                total = sum(v['strategy'][k*169+h] for k in range(n))
                assert abs(total-1) < 1e-5, (row['path'], h, total)
    return s


def audit(which):
    assert which in ['N32', 'N35']
    folder = gpu.BASE / ('zero-fallback-20260916' if which == 'N32' else 'paired-blend-gpu-20260916')
    protocol = study.read(folder/'protocol-freeze.json')
    for p, expected in protocol['inputs'].items():
        assert study.pilot.sha(study.ROOT/p) == expected, p
    result = study.read(folder/'result.json')
    assert result['production_enabled'] is False
    hashes = {}
    if which == 'N32':
        source = study.read(gpu.BASE/'policy-stability-20260916/candidate/1500/iteration-1500.json')
        assert [r['arm'] for r in result['rows']] == ['control', 'uniform_prior']
        for row in result['rows']:
            p = folder/row['arm']/'iteration-2000.json'
            s = snapshot(p, 1500, 2000, source['config'])
            assert study.pilot.sha(p) == row['snapshot_sha256']
            assert row['gaps'] == s['gaps']
            close(row['gap_total_bb'], sum(s['gaps']))
            close(row['learning_seconds'], s['learning_seconds'])
            assert row['changes'] == stability.changes(source, s)
            hashes[str(p.relative_to(study.ROOT)).replace('\\', '/')] = study.pilot.sha(p)
        ratio = result['rows'][1]['gap_total_bb']/result['rows'][0]['gap_total_bb']
        close(result['gap_ratio'], ratio)
        assert result['interesting_reduction'] == (ratio <= .75)
        assert result['reaches_desired_gap'] == (result['rows'][1]['gap_total_bb'] <= .005)
        import continuation_full_precision as full
        parity = full.action_difference(study.read(folder/'oracle/control.json'), study.read(folder/'oracle/uniform_prior.json'))
        assert parity == study.read(folder/'oracle-parity.json')
        assert parity['max_action_difference_bb'] == 0
    else:
        source = study.read(gpu.BASE/'chance-control-20260916/500/iteration-500.json')
        times = {}
        for arm in ['control', 'blend']:
            ss = []
            for end in [750, 1000]:
                p = folder/arm/str(end)/f'iteration-{end}.json'
                ss.append(snapshot(p, end-250, end, source['config']))
                rel = str(p.relative_to(study.ROOT)).replace('\\', '/')
                hashes[rel] = study.pilot.sha(p)
            assert stability.changes(*ss) == result['changes'][arm]
            times[arm] = sum(s['learning_seconds'] for s in ss)
            close(times[arm], result['learning_seconds'][arm])
        assert hashes == result['snapshot_hashes']
        close(result['learning_time_ratio'], times['blend']/times['control'])
        assert result['desired_time_ratio_met'] == (times['blend'] <= 1.1*times['control'])
        parity = gpu.linearity(*[study.read(folder/f'oracle/{name}.json') for name in ['balanced', 'learned', 'blend']])
        assert parity == study.read(folder/'oracle-linearity.json') and parity['passed']
    for n in [2, 3, 8]:
        s = study.read(folder/f'oracle/zero-{n}.json')
        assert all(math.isfinite(v) for v in s['gaps'] + s['evs']) and abs(sum(s['evs'])) < .0002
        assert all(math.isfinite(v) for row in s['frontier']['rows'] for h in row['hands'] for v in h['action_values_counterfactual_bb'])
    record = dict(checked_at=study.night.now(), experiment=which, frozen_inputs=len(protocol['inputs']),
        snapshot_hashes=hashes, result_sha256=study.pilot.sha(folder/'result.json'),
        oracle_recomputed=True, sparse_safety_rechecked=True, production_enabled=False)
    study.freeze(folder/'result-audit.json', record)
    print(which, 'verified:', len(protocol['inputs']), 'inputs;', len(hashes), 'snapshots')


if __name__ == '__main__':
    audit(sys.argv[1])
