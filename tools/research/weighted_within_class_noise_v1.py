"""Descriptive within-update target dispersion in an already audited arm.

No new deals, fits, policy selection, inferential intervals or strength claims.
Three observations give a very uncertain variance estimate; retain every cell.
"""
import concurrent.futures
import hashlib
import json
import math
from pathlib import Path
import statistics
import time
import psutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'weighted-within-class-noise-v1-first-arm'
CONTRASTS = {'call_minus_fold': (1, 0), 'raise_minus_call': (2, 1)}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, separators=(',', ':'), allow_nan=False)


def describe(values):
    assert len(values) >= 3 and all(math.isfinite(v) for v in values)
    mean = math.fsum(values) / len(values)
    variance = math.fsum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return dict(mean=mean, sample_sd=math.sqrt(variance),
                descriptive_se=math.sqrt(variance / len(values)),
                both_positive_and_negative=min(values) < 0 < max(values),
                minimum=min(values), maximum=max(values))


def controls():
    a = describe([-1., 0., 1.])
    assert a['mean'] == 0 and a['sample_sd'] == 1 and a['both_positive_and_negative']
    assert abs(a['descriptive_se'] - 1 / math.sqrt(3)) < 1e-15
    assert describe([4., 4., 4.])['sample_sd'] == 0
    # Pair before measuring dispersion: perfectly correlated action values cancel.
    assert describe([b-a for a,b in [(1,3),(5,7),(9,11)]])['sample_sd'] == 0
    for values in ([1., 2.], [1., 2., float('nan')]):
        try:
            describe(values)
        except AssertionError:
            continue
        raise AssertionError('Invalid observations accepted')
    return dict(known_answer_cases=3, invalid_cases_rejected=2, passed=True)


def inspect(job):
    folder, expected_hashes = job
    def checked(path):
        assert sha(path) == expected_hashes[str(path)], str(path)
        return read(path)
    folder = Path(folder)
    source = checked(folder / 'source-generation.json')
    metrics = checked(folder / 'metrics.json')
    groups = [[] for _ in range(169)]
    assert len(source['deals']) == len(source['hand_classes']) == 512
    for chunk in range(8):
        path = folder / f'batch-{chunk:02d}' / 'integrated-targets.json'
        targets = checked(path)
        assert sha(path) == metrics['subbatches'][chunk]['artifacts']['integrated-targets.json']
        assert targets['iteration'] == metrics['iteration']
        assert targets['method'] == 'action-integrated-bb-root-targets-v1'
        rows = targets['bb_root_corrections']
        assert len(rows) == 64 and [r['deal'] for r in rows] == list(range(64))
        for j, row in enumerate(rows):
            c = source['hand_classes'][chunk*64+j]
            assert row['hand_class'] == c
            q = row['action_values']
            assert len(q) == 4 and all(math.isfinite(x) for x in q)
            groups[c].append(q)
    cells = []
    for c, values in enumerate(groups):
        assert len(values) == source['class_counts'][c] and len(values) >= 3
        weights = [w for h,w in zip(source['hand_classes'], source['deal_weights']) if h == c]
        # Source weights are identical within this class/update, so the paired
        # conditional sample mean is unchanged by importance weighting.
        assert max(weights) == min(weights)
        assert abs(weights[0]*len(values)/512-source['class_mass'][c]) < 1e-12
        assert max(q[0] for q in values)-min(q[0] for q in values) < 1e-12
        assert max(q[3] for q in values)-min(q[3] for q in values) < 1e-10
        cells.append(dict(hand_class=c, count=len(values), entry_mass=source['class_mass'][c],
            contrasts={name:describe([q[a]-q[b] for q in values]) for name,(a,b) in CONTRASTS.items()}))
    return dict(iteration=metrics['iteration'], cells=cells)


def main():
    start = time.monotonic()
    assert psutil.virtual_memory().available > 24_000_000_000 and psutil.cpu_percent(interval=1) < 60
    control = controls()
    stem = 'weighted-training-readback-parallel-v1-w4-9266201-stratified-0078'
    ar, ap = [OUT / f'{stem}-{suffix}.json' for suffix in ('registration', 'result')]
    audit, result = read(ar), read(ap)
    assert result['passed'] and result['complete_arm'] and result['completed_updates'] == 78
    assert result['readback_registration_sha256'] == sha(ar)
    assert len(audit['folders']) == 78
    inputs = {str(p):sha(p) for p in (ar, ap, Path(__file__))}
    jobs = []
    for folder in audit['folders']:
        folder = Path(folder)
        paths = [folder/'source-generation.json', folder/'metrics.json',
                 *[folder/f'batch-{i:02d}'/'integrated-targets.json' for i in range(8)]]
        bindings = {str(p):audit['inputs'][str(p)] for p in paths}
        inputs.update(bindings)
        jobs.append((str(folder), bindings))
    rp = OUT / f'{PREFIX}-registration.json'
    save(rp, dict(inputs=inputs, workers=4, controls=control, new_deals=0,
        scope='All 78 updates and 169 classes of first completed arm; descriptive only.'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        generations = list(pool.map(inspect, jobs))
    assert [g['iteration'] for g in generations] == list(range(1,79))
    windows = []
    for lo,hi in ((1,78),(1,26),(27,52),(53,78)):
        chosen = [g for g in generations if lo <= g['iteration'] <= hi]
        cells = [c for g in chosen for c in g['cells']]
        summary = {}
        for name in CONTRASTS:
            stats = [c['contrasts'][name] for c in cells]
            summary[name] = dict(median_sample_sd=statistics.median(x['sample_sd'] for x in stats),
                median_descriptive_se=statistics.median(x['descriptive_se'] for x in stats),
                fraction_cells_with_mixed_signs=sum(x['both_positive_and_negative'] for x in stats)/len(stats),
                mean_entry_weighted_mixed_sign_share=math.fsum(c['entry_mass']*c['contrasts'][name]['both_positive_and_negative'] for c in cells)/len(chosen))
        windows.append(dict(first_update=lo,last_update=hi,contrasts=summary))
    for p,h in inputs.items():
        assert sha(p)==h,p
    output = dict(passed=True,registration_sha256=sha(rp),controls=control,generations=generations,
        windows=windows,root_decisions=78*512,class_update_cells=78*169,
        seconds=time.monotonic()-start,gpu_used=False,new_deals=0,production_modified=False,
        scope='Dispersion of paired action targets within each fixed class/update. Policies change between updates; means are not pooled. Tiny within-cell samples are descriptive, not confidence intervals, accuracy evidence, or a policy-selection rule.')
    save(OUT / f'{PREFIX}-result.json', output)
    print(json.dumps(dict(passed=True,seconds=output['seconds'],windows=windows)),flush=True)


if __name__ == '__main__':
    main()
