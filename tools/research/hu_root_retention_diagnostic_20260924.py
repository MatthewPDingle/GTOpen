"""Read-only, post-hoc BB root retention diagnostic on the completed pilot.

No new deals, policy deployment, test-set access, fitting or GPU work. Full
sample regret matching here is a counterfactual readout of the OLD trajectory;
it does not simulate training under a changed policy.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from reboot_research_idle_v1 import idle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
STORE = Path('T:/GTOpen-research/exact-initial-fresh-pilot-v1')
PREFIX = 'exact-initial-root-retention-diagnostic-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def save(path, data):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(data, separators=(',', ':'), allow_nan=False) + '\n')


def hand_class(key):
    a, b = key & 63, (key >> 6) & 63
    assert a < 52 and b < 52 and a != b
    assert [(key >> (6*i)) & 63 for i in range(2, 7)] == [63]*5
    assert key >> 42 == 0
    low, high = sorted((a//4, b//4))
    return high*13+low if a % 4 == b % 4 or high == low else low*13+high


def probabilities(scores):
    p = np.maximum(scores, 0.)
    totals = p.sum(axis=1)
    positive = totals > 0
    p[positive] /= totals[positive, None]
    p[~positive] = np.eye(4)[np.argmax(scores[~positive], axis=1)]
    assert np.isfinite(p).all() and np.max(abs(p.sum(1)-1)) < 1e-12
    return p


def main():
    start = time.monotonic()
    def guard():
        assert time.monotonic()-start < 600
        assert psutil.virtual_memory().available >= 20_000_000_000
        assert idle(), 'Production is active; diagnostic stopped'
    guard()
    rp = OUT / (PREFIX+'-registration.json')
    resultp = OUT / (PREFIX+'-result.json')
    assert not rp.exists() and not resultp.exists()
    inputs = {}
    def verified(path, expected=None):
        path = Path(path)
        h = sha(path)
        if expected is not None:
            assert h == expected, str(path)
        inputs[str(path)] = h
        return read(path)
    result_path = OUT/'exact-initial-fresh-pilot-v1-result.json'
    source = verified(result_path, '929f5b614247b513e63babcc0716c725f11e7ee8013e4747cc42ce472f0f20c1')
    review = verified(OUT/'exact-initial-fresh-pilot-v1-independent-review.json')
    assert source['passed'] and review['passed']
    assert review['source_result_sha256'] == sha(result_path)
    assert source['completed_iterations'] == review['completed_updates'] == 78
    matrix = verified(OUT/'preflop-allin-matrix-control-v1-matrix.json',
                      'ff61c30a7948470bbdeee289601d0cb894b29b5ac246194d2e06e44fc801e885')
    mass = np.asarray(matrix['class_mass']).sum(axis=1)
    assert mass.shape == (169,) and abs(mass.sum()-1) < 1e-12
    inputs[str(Path(__file__))] = sha(__file__)
    inputs[str(ROOT/'tools/research/reboot_research_idle_v1.py')] = sha(ROOT/'tools/research/reboot_research_idle_v1.py')
    metrics = []
    for iteration in range(1, 79):
        guard()
        p = STORE/f'iteration-{iteration:04d}'/'metrics.json'
        m = verified(p, source['artifacts'][str(p)])
        assert m['iteration'] == iteration and len(m['subbatches']) == 8
        model_path = STORE/'objects'/m['next_model']['file']
        assert sha(model_path) == m['next_model']['sha256']
        inputs[str(model_path)] = sha(model_path)
        for sub in m['subbatches']:
            p = STORE/f'iteration-{iteration:04d}'/f"batch-{sub['chunk']:02d}"/'derived-targets.json'
            assert sha(p) == sub['artifacts']['derived-targets']
            inputs[str(p)] = sha(p)
        metrics.append(m)
    save(rp, dict(inputs=inputs, maximum_seconds=600, gpu_used=False,
        generations=list(range(1,79)), final_generation_unplayed=True,
        method='Compare retained-root mean regret matching with all recorded root samples at each identical training boundary. Equal weight per sample; exact incoming class mass for aggregate differences.',
        primary_diagnostics=['retained_fraction', 'incoming_mass_weighted_total_variation', 'aggregate_action_mass_difference'],
        scope='Post-hoc training-data diagnostic only; no fresh accuracy interval, no policy evaluation or replacement, no claim of causal improvement. No wider test data is read.'))
    counts = np.zeros(169, dtype=np.int64)
    sums = np.zeros((169,4)); squares = np.zeros((169,4))
    samples = [[] for _ in range(169)]
    boundaries = []; no_discard_error = 0.
    for m in metrics:
        guard()
        iteration = m['iteration']; before = int(counts.sum())
        for sub in m['subbatches']:
            p = STORE/f'iteration-{iteration:04d}'/f"batch-{sub['chunk']:02d}"/'derived-targets.json'
            d = verified(p, inputs[str(p)])
            rows = d['bb_root_corrections']
            assert len(rows) == 64 and len({r['deal'] for r in rows}) == 64
            for r in rows:
                c = r['hand_class']; a = np.asarray(r['advantages'], dtype=np.float64)
                assert type(c) is int and 0 <= c < 169 and a.shape == (4,) and np.isfinite(a).all()
                counts[c] += 1; sums[c] += a; squares[c] += a*a
                samples[c].append(a.tolist())
        assert int(counts.sum())-before == 512
        model = verified(STORE/'objects'/m['next_model']['file'], m['next_model']['sha256'])
        assert model['generation'] == iteration
        table = model['base_model']['preflop_tables'][0]
        retained = np.zeros(169, dtype=np.int64); scores = np.zeros((169,4))
        for row in table['rows']:
            if int(row['hi']) != 1:
                continue
            assert row['actor'] == 0 and row['n'] == 4
            c = hand_class(int(row['lo']))
            assert retained[c] == 0, 'More than one canonical root row per class'
            retained[c] = row['count']; scores[c] = row['mean_regret']
        assert np.all(retained <= counts)
        full = np.divide(sums, counts[:,None], out=np.zeros_like(sums), where=counts[:,None]>0)
        seen = counts > 0; common = retained > 0
        pfull = probabilities(full); pkept = probabilities(scores)
        tv = abs(pfull-pkept).sum(1)/2
        if m['reservoirs'][0]['seen'] <= m['reservoirs'][0]['capacity']:
            assert np.array_equal(retained, counts)
            error = float(np.max(abs(scores[seen]-full[seen])))
            no_discard_error = max(no_discard_error, error)
            assert error < 1e-10
        entry = dict(generation=iteration, played=iteration<78,
            full_root_samples=int(counts.sum()), retained_root_samples=int(retained.sum()),
            retained_fraction=float(retained.sum()/counts.sum()),
            full_classes=int(seen.sum()), retained_classes=int(common.sum()),
            lost_class_incoming_mass=float(mass[seen & ~common].sum()),
            common_incoming_mass=float(mass[common].sum()),
            weighted_total_variation_common=float(mass[common]@tv[common]),
            maximum_total_variation_common=float(tv[common].max()),
            full_action_mass_common=(mass[common]@pfull[common]).tolist(),
            retained_action_mass_common=(mass[common]@pkept[common]).tolist(),
            mean_absolute_regret_difference_common=(mass[common]@abs(scores[common]-full[common])).tolist())
        boundaries.append(entry)
    assert int(counts.sum()) == 39936 and np.all(counts > 1)
    # Independent summation order using math.fsum verifies the streaming means.
    independent = np.array([[math.fsum(r[a] for r in samples[c])/len(samples[c]) for a in range(4)] for c in range(169)])
    sum_error = float(np.max(abs(independent-full)))
    assert sum_error < 1e-10
    classes = []
    for c in range(169):
        variance = np.maximum((squares[c]-sums[c]**2/counts[c])/(counts[c]-1), 0.)
        classes.append(dict(hand_class=c, incoming_mass=float(mass[c]), full_count=int(counts[c]),
            retained_count=int(retained[c]), full_mean_regret=full[c].tolist(),
            retained_mean_regret=scores[c].tolist(), full_policy=pfull[c].tolist(),
            retained_policy=pkept[c].tolist(), total_variation=float(tv[c]),
            sample_standard_deviation=np.sqrt(variance).tolist()))
    for p,h in inputs.items():
        assert sha(p) == h, p
    out = dict(passed=True, registration_sha256=sha(rp), boundaries=boundaries,
        final_unplayed_classes=classes, maximum_no_discard_mean_error=no_discard_error,
        maximum_independent_sum_error=sum_error, root_accumulator_payload_bytes=169*(4*8+8),
        gpu_used=False, production_modified=False, accuracy_qualified=False,
        seconds=time.monotonic()-start,
        limitation='Full-sample probabilities replay targets generated by the retained-policy trajectory. Changing training would change later targets; these are not replacement policies or evidence of improved EV. Per-sample dispersions mix changing training generations and are not confidence intervals.')
    save(resultp,out)
    print(json.dumps({k:v for k,v in out.items() if k not in ('boundaries','final_unplayed_classes')}))
    print(json.dumps(boundaries[-1]))


if __name__ == '__main__':
    main()
