"""CPU-only controls of conditional hand coverage; no strategy evaluation."""
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from sampled_stratified_response_deals_v1 import sample
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class
from storage_strategic_common_prior_20260920 import PAIRS, MASKS, CLASSES

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'


def main():
    started = time.monotonic()
    cp = OUT/'bb-context-candidate.json'; source = cp.read_text()
    sources = [cp, Path(__file__), ROOT/'tools/research/sampled_stratified_response_deals_v1.py',
        ROOT/'tools/research/sampled_physical_deals_v1.py',
        ROOT/'tools/research/storage_strategic_common_prior_20260920.py']
    inputs = {str(p): sha(p) for p in sources}
    classes = list(range(169))
    a = sample(source, seed=193923, per_class=16, classes=classes)
    b = sample(source, seed=193923, per_class=16, classes=classes)
    assert a == b and a['context_sha256'] == hashlib.sha256(source.encode()).hexdigest()
    assert np.bincount(a['hand_classes'], minlength=169).tolist() == [16]*169
    assert [hand_class(d[:2]) for d in a['deals']] == a['hand_classes']
    assert all(len(d) == len(set(d)) == 9 and all(0 <= x < 52 for x in d) for d in a['deals'])
    assert sample(source, seed=193924, per_class=16, classes=classes)['deals'] != a['deals']
    # Independently enumerate compatible private-pair products. This checks the
    # exact conditioning law, rather than treating a small histogram as proof.
    base = PhysicalDeals(source, mode='full_deck', seed=0)
    combo_mass = np.zeros(1326)
    for i in range(1326):
        for j in range(1326):
            if not (int(MASKS[i]) & int(MASKS[j])):
                combo_mass[i] += base.weights[0,i]*base.weights[1,j]
    combo_mass /= combo_mass.sum()
    error = float(np.max(abs(combo_mass-base.first[0])))
    assert error < 1e-14
    maximum_conditional_error = 0.
    for c in classes:
        live = CLASSES == c
        expected = combo_mass[live]/combo_mass[live].sum()
        actual = base.first[0][live]/base.first[0][live].sum()
        maximum_conditional_error = max(maximum_conditional_error, float(np.max(abs(expected-actual))))
    assert maximum_conditional_error < 1e-12
    rejected = 0
    for kwargs in [dict(per_class=0, classes=classes), dict(per_class=True, classes=classes),
        dict(per_class=513, classes=classes), dict(per_class=1, classes=[1,1]),
        dict(per_class=1, classes=[169]), dict(per_class=1, classes=[2,1]), dict(per_class=1, classes=[])]:
        try: sample(source, seed=0, **kwargs)
        except ValueError: rejected += 1
        else: raise AssertionError('Invalid request accepted')
    sparse = json.loads(source)
    sparse['incoming_class_mass'][0][0] = 0
    try: sample(json.dumps(sparse), seed=0, per_class=1, classes=[0])
    except ValueError: rejected += 1
    else: raise AssertionError('Unsupported class accepted')
    assert rejected == 8
    for p,h in inputs.items(): assert sha(p) == h
    result = dict(passed=True, inputs=inputs, deals=len(a['deals']), classes=169,
        deals_per_class=16, repeat_exact=True, distinct_seed_differs=True,
        maximum_combo_mass_error=error, maximum_conditional_error=maximum_conditional_error,
        negative_controls=rejected, seconds=time.monotonic()-started,
        gpu_used=False, production_modified=False, strategic_evaluation=False,
        scope='Fixed class coverage with the original within-class compatible opponent and board law. This control does not test response quality, solve poker, change the active trial, or qualify unweighted use as a population test stream.')
    save(OUT/'stratified-response-control-v1-result.json', result)
    print(json.dumps({k:v for k,v in result.items() if k != 'inputs'}, indent=2))


if __name__ == '__main__': main()
