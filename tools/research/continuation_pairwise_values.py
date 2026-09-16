"""N25 training-only fixed pairwise value model; no production changes."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import datetime as dt
from pathlib import Path
import sys
import numpy as np
import continuation_policy_refinement as study
import continuation_night_queue as queue

OUT = study.ROOT/'research/preflop-evolution/continuation/pairwise-values-20260916'
N15 = OUT.parent/'shrunk-residual-20260916'
STRENGTHS = [.01, .1, 1.]
DEADLINE = dt.datetime(2026, 9, 16, 20, 49, 2, tzinfo=dt.timezone.utc)


def hand_features():
    return np.array([[1., float(a == b), float(s), a/12, b/12, (a/12)**2,
                      (b/12)**2, (a-b)/12, float(a == 12), float(0 < a-b <= 2),
                      float(b >= 8)] for a, b, s in study.pilot.PARTS])


def bases(spr):
    assert np.isfinite(spr) and spr >= 0
    return np.array([1., min(spr/8, 1.), np.log1p(spr)/np.log(21.)])


def design(c, counts):
    f = hand_features()
    w = np.array(c['case']['weights'])
    assert w.shape == (2, 169) and np.isfinite(w).all() and (w >= 0).all()
    rows = []
    for p in range(2):
        opponent = counts*w[1-p][None, :]
        conditional = opponent/opponent.sum(axis=1, keepdims=True)
        summary = conditional@f
        pair = f[:, :, None]*summary[:, None, :] if p == 0 else -summary[:, :, None]*f[:, None, :]
        rows.append((bases(c['case']['stack']/c['case']['pot'])[:, None, None, None]
                     *pair[None, :, :, :]).transpose(1, 0, 2, 3).reshape(169, -1))
    result = np.array(rows)
    np.testing.assert_allclose((result*c['mass'][..., None]).sum(axis=(0, 1)), 0., atol=2e-14)
    return result


def fit(cases, features, strength):
    x = np.concatenate([features[c['case']['id']].reshape(-1, 363) for c in cases])
    y = np.concatenate([c['residual'].ravel() for c in cases])
    assert all((c['mass']*(c['observed'] == 0)).sum() < 1e-12 for c in cases)
    w = np.concatenate([c['mass'].ravel()/2 for c in cases]); w /= w.sum()
    scale = np.maximum(np.sqrt((w[:, None]*x*x).sum(axis=0)), 1e-8)
    z = x/scale
    coef = np.linalg.solve(z.T@(w[:, None]*z) + np.eye(363)*strength/len(cases), z.T@(w*y))
    return dict(kind='fixed_pairwise_values', strength=strength, scale=scale.tolist(),
                coef=coef.tolist(), feature_count=363, production_enabled=False)


def predict(c, features, model):
    correction = (features/np.array(model['scale']))@np.array(model['coef'])
    result = c['raw']+correction
    assert np.isfinite(result).all() and abs((c['mass']*result).sum()-1) < 1e-10
    return result


def gate(means, linear_means, n15_means):
    mean = float(np.mean(list(means.values())))
    return mean <= .95*np.mean(list(linear_means.values())) and mean <= 1.05*np.mean(list(n15_means.values())) \
        and all(means[f] <= 1.05*n15_means[f] for f in means)


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [Path(__file__), OUT/'README.md', N15/'training-screen.json',
             OUT.parent/'nonlinear-residual-20260916/training-screen.json',
             study.ROOT/'tools/research/continuation_overnight_fit.py',
             study.ROOT/'tools/research/range_value_pilot.py',
             study.ROOT/'tools/research/continuation_policy_refinement.py']
    inputs = dict(study.read(N15/'implementation-freeze.json')['inputs'])
    inputs.update({str(p.resolve().relative_to(study.ROOT)).replace('\\', '/'): study.pilot.sha(p) for p in paths})
    for path, expected in inputs.items():
        assert study.pilot.sha(study.ROOT/path) == expected, path
    frozen = OUT/'protocol-freeze.json'
    if frozen.exists():
        assert study.read(frozen)['inputs'] == inputs
    else:
        study.freeze(frozen, dict(registered_at=study.night.now(), inputs=inputs, strengths=STRENGTHS, production_enabled=False))


def require_no_timing():
    for p in queue.processes():
        if p['ProcessId'] == os.getpid():
            continue
        command = (p['CommandLine'] or '').lower()
        if p['Name'].lower() in ['python.exe', 'pythonw.exe']:
            assert not any(t in command for t in ['continuation_policy_stability.py run',
                'continuation_full_precision.py run', 'continuation_chance_control.py run',
                'continuation_pairwise_values.py run']), 'An isolated timing/training controller remains active'
        assert p['Name'].lower() != 'learned_interface.exe', 'Research solver timing is active'
    assert (DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds() >= 1200


def run():
    require_no_timing(); prepare()
    assert not (OUT/'training-screen.json').exists(), 'Completed experiment; do not rerun blindly'
    cases = study.fit.load_cases('train') + study.contexts('development')
    assert len(cases) == 26 and all(c['case']['partition'] == 'train' for c in cases)
    counts, _ = study.pilot.matrices()
    features = {c['case']['id']: design(c, counts) for c in cases}
    families = sorted({c['case']['family'] for c in cases})
    assert len(families) == 4
    recorded = study.read(OUT.parent/'nonlinear-residual-20260916/training-screen.json')['scores'][0]
    controls = {r['case']: r for r in recorded['cases']}
    n15 = study.read(N15/'training-screen.json')
    rows = {strength: [] for strength in STRENGTHS}
    linear_rows = []
    for family in families:
        assert dt.datetime.now(dt.timezone.utc) < DEADLINE
        train = [c for c in cases if c['case']['family'] != family]
        validate = [c for c in cases if c['case']['family'] == family]
        linear = study.fit.fit(train, 'shape', .1)
        for c in validate:
            value = study.pilot.metrics(c, study.fit.predict(c, linear))['candidate']
            assert abs(value-controls[c['case']['id']]['candidate']) < 1e-9, 'Original linear control changed'
            linear_rows.append(dict(case=c['case']['id'], family=family, candidate=value))
        for strength in STRENGTHS:
            model = fit(train, features, strength)
            for c in validate:
                error = study.pilot.metrics(c, predict(c, features[c['case']['id']], model))['candidate']
                rows[strength].append(dict(case=c['case']['id'], family=family, candidate=error))
        print('Excluded family', family, flush=True)
    linear_means = {f: float(np.mean([r['candidate'] for r in linear_rows if r['family'] == f])) for f in families}
    scores = []
    for strength, entries in rows.items():
        means = {f: float(np.mean([r['candidate'] for r in entries if r['family'] == f])) for f in families}
        scores.append(dict(strength=strength, cases=entries, family_means=means, mean=float(np.mean(list(means.values()))),
                           eligible=gate(means, linear_means, n15['family_means'])))
    eligible = [s for s in scores if s['eligible']]
    result = dict(scores=scores, linear_family_means=linear_means, n15_family_means=n15['family_means'],
                  eligible=bool(eligible), production_enabled=False,
                  note='Training-family screen only. Fixed pairwise values remove own-range dependence but do not establish full-game convergence or GPU runtime.')
    if eligible:
        chosen = min(eligible, key=lambda s: s['mean'])
        model = fit(cases, features, chosen['strength'])
        model['training_case_ids'] = [c['case']['id'] for c in cases]
        study.freeze(OUT/'candidate.json', model)
        study.freeze(OUT/'candidate-freeze.json', dict(frozen_at=study.night.now(), sha256=study.pilot.sha(OUT/'candidate.json'), production_enabled=False))
    study.freeze(OUT/'training-screen.json', result)
    print('Eligible:', bool(eligible), flush=True)


if __name__ == '__main__':
    {'prepare': prepare, 'run': run}[sys.argv[1]]()
