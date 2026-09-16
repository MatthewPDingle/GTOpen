"""Read-only numerical/provenance audit of the bounded exact-game experiments."""
import datetime as dt
import json
from pathlib import Path
import numpy as np
import continuation_exact_game as game

BASE = game.OUT.parent
FINAL = BASE/'exact-game-extension-20260917'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    inputs = 0
    checked = []
    for folder in ['exact-game-20260917', 'exact-game-precision-20260917',
                   'exact-game-robust-20260917', 'exact-game-offsupport-20260917',
                   'exact-game-extension-20260917']:
        directory = BASE/folder
        freeze = read(directory/'freeze.json')
        for path, expected in freeze['inputs'].items():
            assert game.sha(game.ROOT/path) == expected, path
            inputs += 1
        for path in directory.glob('*cfr.json'):
            checked.append(check_rows(path))
        for path in directory.glob('*cutoff.json'):
            checked.append(check_rows(path))
    repeats = []
    for name, prior in [('full_cfr', 'exact-game-robust-20260917'),
                        ('exact_cutoff', 'exact-game-robust-20260917'),
                        ('offsupport_cutoff', 'exact-game-offsupport-20260917')]:
        current = read(FINAL/(name+'.json'))
        original = read(BASE/prior/('exact_cutoff.json' if name == 'offsupport_cutoff' else name+'.json'))
        for row in original['rows']:
            match = next(x for x in current['rows'] if x['iteration'] == row['iteration'])
            # Same root policy. Off-support run used completed reconstruction;
            # extension deliberately uses plain reconstruction for both arms.
            np.testing.assert_allclose(np.array(match['policy'])[:2], np.array(row['policy'])[:2], atol=1e-12)
        repeats.append(name)
    assert read(FINAL/'integration-gate.json')['passed']
    assert read(FINAL/'predicted_cutoff.json')['complete']
    values = read(FINAL/'datasets.json')
    train = np.concatenate([np.array(d['x']) for d in values['training'].values()])
    test = np.concatenate([np.array(d['x']) for d in values['held_out'].values()])
    assert len(train) == 1024 and len(test) == 256
    assert not set(map(tuple, train)) & set(map(tuple, test))
    model = game.Surrogate({int(c): {k: np.array(v) for k, v in data.items()}
                            for c, data in values['training'].items()})
    raw_errors, corrected_errors, max_conservation_error = [], [], 0.
    for context, data in values['held_out'].items():
        c = int(context)
        for features, target in zip(np.array(data['x']), np.array(data['y'])):
            x = np.r_[features[:2], 1-features[:2].sum()]
            y = np.r_[features[2:], 1-features[2:].sum()]
            raw = model.raw(c, x, y)
            corrected = model(c, x, y)[0]
            assert np.isfinite(corrected).all() and np.max(np.abs(corrected)) <= c+2+1e-12
            weights = np.array([x*(game.LEGAL@y), y*(game.LEGAL.T@x)])
            error = abs(float(np.sum(weights*corrected)))
            assert error < 1e-9
            max_conservation_error = max(max_conservation_error, error)
            raw_errors.extend(np.abs(raw.ravel()-target*c))
            corrected_errors.extend(np.abs(corrected.ravel()-target*c))
    claimed = read(FINAL/'prediction-errors.json')
    for label, errors in [('raw',raw_errors),('corrected',corrected_errors)]:
        for key, expected in [('mae_chips',np.mean(errors)),('p95_absolute_error',np.quantile(errors,.95)),
                              ('max_absolute_error',np.max(errors))]:
            assert abs(claimed[label][key]-expected)<1e-10
    out = {'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
           'frozen_inputs_checked_including_repeats': inputs,
           'result_files': checked, 'repeated_upper_policies_match': repeats,
           'training_contexts': len(train), 'held_out_contexts': len(test),
           'max_surrogate_zero_sum_error': max_conservation_error,
           'exact_train_test_overlap': 0, 'production_enabled': False}
    (FINAL/'audit.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('Verified', inputs, 'frozen input entries,', len(checked), 'result files and repeated policies')


def check_rows(path):
    doc = read(path)
    assert doc['complete'], path
    for row in doc['rows']:
        policy = np.array(row['policy'])
        assert np.isfinite(policy).all() and policy.min() >= -1e-12 and policy.max() <= 1+1e-12
        np.testing.assert_allclose(policy.sum(axis=2), 1., atol=1e-12)
        metrics = game.measure(policy)
        for key, value in metrics.items():
            assert abs(row['full_game'][key]-value) < 1e-12, (path, key)
        # Separate extensive-form recursive BR must agree with normal-form enumeration.
        tree = game.CFR()
        br = sum(float(tree.walk(0, np.ones((2, 3)), policy, br=p)[p].sum()) for p in [0, 1])
        assert abs(br-metrics['nashconv']) < 1e-12
    return {'path': str(path.relative_to(game.ROOT)), 'sha256': game.sha(path), 'checkpoints': len(doc['rows'])}


if __name__ == '__main__':
    main()
