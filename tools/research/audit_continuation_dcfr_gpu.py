"""Independent result/provenance audit and targeted value-transfer edge cases."""
import datetime as dt
import json
from pathlib import Path
import numpy as np
import torch
import continuation_exact_game as game
import continuation_exact_game_robust as robust
import continuation_exact_game_offsupport as off
import continuation_dcfr_gpu as fixture

OUT = fixture.OUT


def read(path): return json.loads(path.read_text(encoding='utf-8'))


def extra_transfer_checks():
    driver = fixture.Driver(OUT/'audit-cuda')
    gpu = fixture.GPU(driver, True)
    rng = np.random.default_rng(71029)
    max_error = 0.; tested = 0
    # Direct tests, including zero whole-opponent reach and hypothetical shares
    # outside [0,1]. This audit is separate from the registered learning runs.
    for case in range(32):
        reach = np.zeros_like(gpu.reach)
        reach[:, :3] = rng.random((len(reach), 3)).astype(np.float32)
        if case < 3: reach[:, case] = 0
        if case == 3: reach[:] = 0
        gpu.reach_gpu.copy_(torch.from_numpy(reach))
        for p in [0, 1]:
            pred = rng.uniform(-1, 2, (gpu.nnode, 3))
            gpu.transfer(p, pred)
            actual = gpu.val.cpu().numpy()
            for n in gpu.leaves:
                c = 1 if n == 2 else 2 if n == 4 else fixture.TERMINALS[n][0]
                opp = reach[gpu.refs[n, 1-p], :3].astype(np.float64)
                expected = ((game.LEGAL@opp)/(2/3)*(2*c*pred[n]-c)).astype(np.float32)
                error = float(np.max(np.abs(actual[n, :3]-expected)))
                max_error = max(max_error, error)
                np.testing.assert_allclose(actual[n, :3], expected, atol=2e-6, rtol=2e-6)
                assert not np.any(actual[n, 3:])
                tested += 1
    return {'leaf_vectors_checked': tested, 'maximum_absolute_error': max_error,
            'zero_opponent_mass_checked': True, 'out_of_unit_interval_shares_checked': True}


def main(edges_only=False):
    game.linprog = robust.robust_linprog
    if edges_only:
        result = extra_transfer_checks()
        (OUT/'transfer-edge-checks.json').write_text(json.dumps(result, indent=2)+'\n')
        print(result); return
    frozen = read(OUT/'freeze.json')['inputs']
    for path, expected in frozen.items(): assert game.sha(game.ROOT/path) == expected, path
    matrix = game.payoff(game.PURE[:, None], game.PURE[None, :])
    a, b, value, gap = game.equilibrium(matrix)
    assert abs(value-1/18) < 1e-10 and gap < 1e-10
    data = read(OUT.with_name('exact-game-extension-20260917')/'datasets.json')['training']
    model = game.Surrogate({int(c): {k: np.array(v) for k, v in row.items()} for c, row in data.items()})
    files = []; local_errors = []; completion_sensitivity = []
    for name, oracle in [('full_dcfr', None), ('exact_cutoff', game.exact),
                         ('offsupport_cutoff', off.completed_exact), ('predicted_cutoff', model)]:
        path = OUT/(name+'.json'); doc = read(path)
        assert doc['complete']
        for row in doc['rows']:
            policy = np.array(row['policy'])
            assert np.isfinite(policy).all() and policy.min() >= -1e-12 and policy.max() <= 1+1e-12
            np.testing.assert_allclose(policy.sum(axis=2), 1, atol=1e-12, rtol=0)
            measured = game.measure(policy)
            for key, val in measured.items(): assert abs(val-row['full_game'][key]) < 1e-12
            tree = game.CFR()
            recursive = sum(tree.walk(0, np.ones((2, 3)), policy, br=p)[p].sum() for p in [0, 1])
            assert abs(recursive-measured['nashconv']) < 1e-12
            if oracle:
                frozen_gap = game.CFR(oracle).frozen_gap(policy)
                assert abs(frozen_gap-row['frozen_value_gap']) < 1e-10
        files.append({'name': name, 'sha256': game.sha(path), 'checkpoints': len(doc['rows'])})
        if oracle:
            # Post-hoc diagnostic only: tiny support probabilities fall beneath
            # LP tolerances. Keep upper policies unchanged; reconstruct using a
            # fixed 1e-6 normalized-range floor, never replace registered results.
            for checkpoint in doc['rows'] if name == 'predicted_cutoff' else doc['rows'][-1:]:
                original = np.array(checkpoint['policy']); regularized = original.copy()
                for c, (x, y), node in zip([1, 2], game.upper_ranges(original), [2, 4]):
                    x = game.normalize(np.maximum(game.normalize(x), 1e-6))
                    y = game.normalize(np.maximum(game.normalize(y), 1e-6))
                    _, (bet, call), _, _ = game.exact(c, x, y)
                    regularized[node, :, 1] = bet; regularized[node+1, :, 1] = call
                    regularized[node:node+2, :, 0] = 1-regularized[node:node+2, :, 1]
                alternative = game.measure(regularized)
                completion_sensitivity.append({'arm': name, 'iteration': checkpoint['iteration'],
                    'post_hoc': True, 'range_floor': 1e-6,
                    'registered_metrics': game.measure(original), 'regularized_completion_metrics': alternative,
                    'on_policy_ev_change': alternative['ev_p0']-game.measure(original)['ev_p0'],
                    'upper_policy_max_difference': float(np.max(np.abs(original[:2]-regularized[:2]))),
                    'regularized_completion_policy': regularized.tolist()})
        if name in ['full_dcfr', 'exact_cutoff', 'predicted_cutoff']:
            for c, (x, y) in zip([1, 2], game.upper_ranges(policy)):
                predicted = model(c, x, y)[0]; exact = game.exact(c, x, y)[0]
                local_errors.append({'arm': name, 'contribution': c, 'p0_range': game.normalize(x).tolist(),
                    'p1_range': game.normalize(y).tolist(), 'predicted_net_values': predicted.tolist(),
                    'exact_net_values': exact.tolist(), 'error': (predicted-exact).tolist(),
                    'maximum_absolute_error': float(np.max(np.abs(predicted-exact)))})
    controls = all(read(OUT/(name+'.json'))['rows'][-1]['full_game']['nashconv'] <= .005
                   for name in ['full_dcfr', 'exact_cutoff', 'offsupport_cutoff'])
    assert read(OUT/'integration-gate.json')['passed'] == controls
    prediction_gap = read(OUT/'predicted_cutoff.json')['rows'][-1]['full_game']['nashconv']
    exact_gap = read(OUT/'exact_cutoff.json')['rows'][-1]['full_game']['nashconv']
    assert read(OUT/'prediction-gate.json')['passed'] == (controls and prediction_gap <= .005
                                                       and prediction_gap <= exact_gap+.002)
    result = {'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'frozen_inputs_checked': len(frozen), 'reference_value': value, 'reference_lp_gap': gap,
              'result_files': files, 'prediction_endpoint_errors': local_errors,
              'completion_sensitivity': completion_sensitivity,
              'production_enabled': False}
    (OUT/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    import sys
    main('--edges-only' in sys.argv)
