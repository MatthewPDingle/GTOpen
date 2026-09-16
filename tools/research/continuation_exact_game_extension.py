"""Registered longer-run diagnostic; preserves original 5000-step failures."""
import datetime as dt
from pathlib import Path
import numpy as np
import continuation_exact_game as game
import continuation_exact_game_robust as robust
import continuation_exact_game_offsupport as off

OUT = game.OUT.with_name('exact-game-extension-20260917')


def run():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'freeze.json').exists()
    game.OUT = OUT
    game.CHECKPOINTS = [100, 500, 2000, 5000, 10000, 20000]
    game.linprog = robust.robust_linprog
    files = [Path(__file__), Path(game.__file__), Path(robust.__file__), Path(off.__file__),
             OUT/'PROTOCOL.md',
             OUT.with_name('exact-game-robust-20260917')/'exact_cutoff.json',
             OUT.with_name('exact-game-offsupport-20260917')/'exact_cutoff.json']
    game.write('freeze.json', {'registered_at': dt.datetime.now(dt.timezone.utc).isoformat(),
               'inputs': {str(p.relative_to(game.ROOT)): game.sha(p) for p in files},
               'checkpoints': game.CHECKPOINTS, 'lp_options': robust.OPTIONS,
               'production_enabled': False})
    a, b, value, gap = game.equilibrium(game.payoff(game.PURE[:, None], game.PURE[None, :]))
    reference = game.behavior_from_mixture(a, b)
    game.write('reference.json', {'game_value': value, 'lp_gap': gap, 'policy': reference.tolist(),
                                 'metrics': game.measure(reference)})
    full = game.run_arm('full_cfr', None, reference)
    plain = game.run_arm('exact_cutoff', game.exact, reference)
    # run_arm's completion intentionally uses the same original exact oracle for
    # both arms, so downstream reconstruction does not confound the upper comparison.
    completed = game.run_arm('offsupport_cutoff', off.completed_exact, reference)
    game.write('offsupport-diagnostic.json', off.COUNTS)
    # Require both exact arms to pass the unchanged threshold before training.
    passed = all(rows[-1]['full_game']['nashconv'] <= .005 for rows in [full, plain, completed])
    game.write('integration-gate.json', {'passed': passed, 'threshold': .005,
                                       'does_not_replace_original_5000_step_results': True})
    if not passed:
        print('Longer exact integration screen failed; no surrogate', flush=True)
        return
    train, test = game.dataset(512, 20260917), game.dataset(128, 20260918)
    model = game.Surrogate(train)
    game.write('datasets.json', {part: {str(c): {k: v.tolist() for k, v in data.items()}
                                         for c, data in ds.items()}
                                for part, ds in [('training', train), ('held_out', test)]})
    raw_errors, errors = [], []
    for c, data in test.items():
        for features, target in zip(data['x'], data['y']):
            x = np.r_[features[:2], 1-features[:2].sum()]
            y = np.r_[features[2:], 1-features[2:].sum()]
            raw_errors.extend(np.abs(model.raw(c, x, y).ravel()-target*c))
            errors.extend(np.abs(model(c, x, y)[0].ravel()-target*c))
    game.write('prediction-errors.json', {label: {'mae_chips': float(np.mean(e)),
            'p95_absolute_error': float(np.quantile(e, .95)), 'max_absolute_error': float(np.max(e))}
            for label, e in [('raw', raw_errors), ('corrected', errors)]})
    predicted = game.run_arm('predicted_cutoff', model, reference)
    ng = predicted[-1]['full_game']['nashconv']
    game.write('prediction-gate.json', {'passed': ng <= .005 and ng <= plain[-1]['full_game']['nashconv']+.002,
                         'oracle_completed_nashconv': ng, 'production_enabled': False})
    print('All registered extension arms finished', flush=True)


if __name__ == '__main__':
    run()
