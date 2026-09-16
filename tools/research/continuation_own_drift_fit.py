"""N30: targeted own-mean response regularization, same inference architecture."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from pathlib import Path
import sys
import numpy as np
import continuation_smooth_fit as smooth
import continuation_pairwise_values as guard

study = smooth.study
OUT = smooth.OUT.parent/'own-drift-fit-20260916'


def tilt(weights, side, mask, epsilon=.001):
    d = np.asarray(weights, dtype=float)*study.pilot.COMBOS
    d /= d.sum(axis=1, keepdims=True)
    portion = float(d[side, mask].sum())
    if portion <= 1e-14 or portion >= 1-1e-14: return None
    target = d[side]*mask/portion
    shifted = d.copy(); shifted[side] = (1-epsilon)*d[side]+epsilon*target
    tv = float(np.abs(shifted[side]-d[side]).sum()/2)
    assert 0 < tv <= epsilon+1e-12
    assert np.array_equal(shifted == 0, d == 0)
    return shifted/study.pilot.COMBOS, tv


def variants(c, counts, eq):
    rows = []
    for side in [0, 1]:
        for mask in smooth.masks():
            shifted = tilt(c['case']['weights'], side, mask)
            if shifted is None: continue
            weights, tv = shifted
            v = smooth.sensitivity.context(dict(c['case'], weights=weights.tolist()), counts, eq)
            rows.append((v, tv, side))
    assert rows, 'No nontrivial support-preserving direction'
    return rows


def direction(before, after, mass, side, tv):
    assert tv > 0 and before.shape == after.shape and before.shape[:2] == (2, 169)
    return ((after[side]-before[side])*mass[side,:,None]).sum(axis=0)/tv


def penalty(cases, base, altered):
    matrix = np.zeros((104, 104))
    for c in cases:
        z = smooth.centered(smooth.standardized(c, base), c['mass'])
        directions = altered[c['case']['id']]
        for v, tv, side in directions:
            zv = smooth.centered(smooth.standardized(v, base), v['mass'])
            g = direction(z, zv, c['mass'], side, tv)
            matrix += np.outer(g, g)/(len(cases)*len(directions))
    np.testing.assert_allclose(matrix, matrix.T, atol=1e-10)
    return matrix


def responsiveness(c, model, altered):
    before = smooth.network.predict(c, model)
    return float(np.mean([abs(float((c['mass'][side]*(smooth.network.predict(v, model)[side]-before[side])).sum()))/tv
                          for v,tv,side in altered]))


def prepare():
    paths = [Path(__file__), OUT/'README.md', Path(smooth.__file__)]
    inputs = dict(study.read(smooth.OUT/'implementation-freeze.json')['inputs'])
    inputs.update({str(p.resolve().relative_to(study.ROOT)).replace('\\', '/'):study.pilot.sha(p) for p in paths})
    for path,h in inputs.items(): assert study.pilot.sha(study.ROOT/path)==h,path
    frozen = OUT/'implementation-freeze.json'
    if frozen.exists(): assert study.read(frozen)['inputs']==inputs
    else: study.freeze(frozen, dict(registered_at=study.night.now(), inputs=inputs,
                                  strengths=smooth.STRENGTHS, production_enabled=False))


def run():
    guard.require_no_timing(); prepare()
    # Replace only the registered hooks in this isolated process. The frozen
    # dependency file and all numerical settings remain unchanged on disk.
    original_inputs = study.read(OUT/'implementation-freeze.json')['inputs']
    smooth.OUT = OUT
    smooth.prepare = lambda: None  # our complete freeze was checked above
    smooth.variants = variants; smooth.penalty = penalty; smooth.responsiveness = responsiveness
    smooth.run()
    for path,h in original_inputs.items(): assert study.pilot.sha(study.ROOT/path)==h,path
    study.night.dump(OUT/'dependency-audit.json', dict(inputs_verified=len(original_inputs),
                       all_inputs_unchanged=True, production_enabled=False))


if __name__ == '__main__': {'prepare':prepare,'run':run}[sys.argv[1]]()
