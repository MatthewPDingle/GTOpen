"""N26: label-free own/opponent value response; never fits or promotes a model."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import datetime as dt
from pathlib import Path
import sys
import numpy as np
import continuation_range_sensitivity as sensitivity
import continuation_pairwise_values as guard

study = sensitivity.study
OUT = sensitivity.OUT.parent/'own-range-drift-20260916'
EPSILONS = [.001, .0001, .00001]


def components(before, after, mass, tv):
    assert tv > 0 and np.isfinite(tv)
    delta = np.asarray(after)-np.asarray(before)
    mass = np.asarray(mass)
    assert delta.shape == mass.shape == (2, 169)
    assert np.isfinite(delta).all() and (mass >= 0).all()
    np.testing.assert_allclose(mass.sum(axis=1), 1., atol=1e-12)
    return dict(signed=(mass*delta).sum(axis=1).tolist(),
                absolute=(mass*np.abs(delta)).sum(axis=1).tolist(),
                signed_per_tv=((mass*delta).sum(axis=1)/tv).tolist(),
                absolute_per_tv=((mass*np.abs(delta)).sum(axis=1)/tv).tolist())


def prepare():
    paths = [Path(__file__), OUT/'README.md', Path(sensitivity.__file__),
             Path(sensitivity.network.__file__), Path(study.fit.__file__),
             Path(study.pilot.__file__), sensitivity.MODEL,
             study.night.OUT/'fixtures.json', study.ROOT/'cache/preflop_eq169.bin',
             study.ROOT/'cache/realization_fit.json']
    inputs = dict(study.read(sensitivity.MODEL.parent/'implementation-freeze.json')['inputs'])
    inputs.update({str(p.resolve().relative_to(study.ROOT)).replace('\\', '/'):
                   study.pilot.sha(p) for p in paths})
    for path, expected in inputs.items():
        assert study.pilot.sha(study.ROOT/path) == expected, path
    path = OUT/'protocol-freeze.json'
    if path.exists():
        assert study.read(path)['inputs'] == inputs
    else:
        study.freeze(path, dict(registered_at=study.night.now(), inputs=inputs,
                               epsilons=EPSILONS, production_enabled=False))


def run():
    guard.require_no_timing(); prepare()
    assert not (OUT/'diagnostic.json').exists(), 'Already completed'
    cases = [c for c in study.read(study.night.OUT/'fixtures.json')['cases'] if c['partition'] == 'train']
    assert len(cases) == 24
    model = study.read(sensitivity.MODEL)
    assert study.pilot.sha(sensitivity.MODEL) == study.read(sensitivity.MODEL.parent/'candidate-freeze.json')['sha256']
    counts, eq = study.pilot.matrices()
    masks = dict(premium_pairs=np.array([a == b and a >= 8 for a,b,s in study.pilot.PARTS]),
                 offsuit_broadways=np.array([a != b and not s and min(a,b) >= 8 for a,b,s in study.pilot.PARTS]),
                 suited_connectors=np.array([s and 0 < a-b <= 2 for a,b,s in study.pilot.PARTS]))
    rows = []
    for case in cases:
        assert dt.datetime.now(dt.timezone.utc) < guard.DEADLINE
        baseline = sensitivity.context(case, counts, eq)
        before = sensitivity.predictions(baseline, model)
        for side in [0, 1]:
            for direction, mask in masks.items():
                for epsilon in EPSILONS:
                    weights, tv = sensitivity.perturb(case['weights'], side, mask, epsilon)
                    after = sensitivity.predictions(sensitivity.context(dict(case, weights=weights.tolist()), counts, eq), model)
                    values = {name: components(before[name], after[name], baseline['mass'], tv) for name in before}
                    assert values['raw']['absolute'][side] < 1e-12
                    assert values['balanced']['absolute'][side] < 1e-12
                    rows.append(dict(case=case['id'], side=side, direction=direction,
                                     epsilon=epsilon, tv=tv, values=values))
    assert len(rows) == 432
    summaries = []
    for epsilon in EPSILONS:
        for model_name in before:
            selected = [r for r in rows if r['epsilon'] == epsilon]
            signed = [abs(r['values'][model_name]['signed_per_tv'][r['side']]) for r in selected]
            absolute = [r['values'][model_name]['absolute_per_tv'][r['side']] for r in selected]
            summaries.append(dict(epsilon=epsilon, model=model_name,
                                  median_abs_signed_own_response=float(np.median(signed)),
                                  p95_abs_signed_own_response=float(np.quantile(signed, .95)),
                                  median_absolute_own_response=float(np.median(absolute))))
    study.freeze(OUT/'diagnostic.json', dict(checked_at=study.night.now(), rows=rows,
                 summaries=summaries, production_enabled=False,
                 caveat='Training-input descriptive response only; no labels, fitting, accuracy or causal/convergence proof.'))
    print(summaries, flush=True)


if __name__ == '__main__':
    {'prepare': prepare, 'run': run}[sys.argv[1]]()
