"""Post-hoc stability diagnosis of the completed combined candidate's responder.

Reads existing evaluation evidence only. Does not inspect the running visible
trial, choose a new deployed policy, or produce new confidence claims.
"""
import json
from pathlib import Path
import time
import numpy as np
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-hybrid-allin-evaluation-v1'
OUTPUT = 'sampled-combined-response-stability-v1'


def main():
    started = time.monotonic()
    paths = {k: OUT/f'{PREFIX}-{k}.json' for k in ('registration', 'result', 'independent-review', 'status')}
    docs = {k: json.loads(p.read_text()) for k, p in paths.items()}
    reg, result, review = (docs[k] for k in ('registration', 'result', 'independent-review'))
    assert docs['status']['state'] == 'complete' and result['terminal'] and review['passed']
    assert review['result_sha256'] == sha(paths['result'])
    assert review['registration_sha256'] == sha(paths['registration'])
    evidence = {str(p): sha(p) for p in paths.values()}
    store = Path(reg['store'])
    rp = store/'response.json'
    assert sha(rp) == result['response_sha256']
    response = json.loads(rp.read_text())
    evidence[str(rp)] = sha(rp)
    selected = np.asarray(response['actions'])
    threshold = response['minimum_training_deals']
    streams = {}
    for split, count in [('train', 8192), ('test', 16384)]:
        classes, values, baselines = [], [], []
        for offset in range(0, count, 16):
            p = store/f'{PREFIX}-{split}-{offset}'/'summary.json'
            h = sha(p)
            assert h == result['batch_summary_hashes'][p.parent.name]
            d = json.loads(p.read_text())
            classes.extend(d['classes']); values.extend(d['action_values']); baselines.extend(d['baseline_values'])
            evidence[str(p)] = h
        c, v, b = np.asarray(classes), np.asarray(values), np.asarray(baselines)
        assert len(c) == count and v.shape == (count, 4) and np.isfinite(v).all()
        actions = selected[c]
        gains = np.where(actions >= 0, v[np.arange(count), actions.clip(min=0)]-b, 0.)
        streams[split] = dict(c=c, v=v, b=b, gains=gains)
    train, test = streams['train'], streams['test']
    assert abs(test['gains'].mean()-result['intervals']['trained-response']['mean']) < 1e-10
    counts = np.bincount(train['c'], minlength=169)
    assert counts.tolist() == response['training_counts']
    rows = []
    first, second = np.arange(8192) < 4096, np.arange(8192) >= 4096
    for c in range(169):
        tr, te = train['c'] == c, test['c'] == c
        expected = int(np.argmax(train['v'][tr].mean(0))) if counts[c] >= threshold else -1
        assert expected == selected[c]
        half_counts, half_actions = [], []
        for mask in (first, second):
            take = tr & mask; n = int(take.sum()); half_counts.append(n)
            half_actions.append(int(np.argmax(train['v'][take].mean(0))) if n >= threshold else -1)
        rows.append(dict(hand_class=c, training_deals=int(tr.sum()), test_deals=int(te.sum()),
            selected_action=int(selected[c]), half_counts=half_counts, half_actions=half_actions,
            training_gain_bb=float(train['gains'][tr].mean()), test_gain_bb=float(test['gains'][te].mean())))
    eligible = np.array([min(r['half_counts']) >= threshold for r in rows])
    disagree = np.array([r['half_actions'][0] != r['half_actions'][1] for r in rows]) & eligible
    out = dict(passed=True, inputs=evidence, class_rows=rows,
        training_gain_bb=float(train['gains'].mean()), test_gain_bb=float(test['gains'].mean()),
        apparent_selection_optimism_bb=float(train['gains'].mean()-test['gains'].mean()),
        half_sample_eligible_classes=int(eligible.sum()), half_sample_disagreeing_classes=int(disagree.sum()),
        half_sample_disagreement_test_mass=float(disagree[test['c']].mean()),
        half_sample_eligible_test_mass=float(eligible[test['c']].mean()),
        training_count_min=int(counts.min()), training_count_median=float(np.median(counts)),
        training_count_max=int(counts.max()), seconds=time.monotonic()-started,
        production_modified=False, new_evaluation=False, accuracy_qualified=False,
        scope='Post-hoc diagnosis of an already inspected completed evaluation. Apparent training advantage is selected on the same training sample and is optimistically biased. Half-sample disagreement uses training data only, with the original support threshold; splitting also reduces support. Test mass is descriptive. No new confidence interval, checkpoint choice, action patch, or full best-response estimate.')
    out['inputs'][str(Path(__file__))] = sha(Path(__file__))
    for p, h in evidence.items(): assert sha(p) == h, p
    save(OUT/f'{OUTPUT}-result.json', out)
    print(json.dumps({k:v for k,v in out.items() if k not in ('inputs', 'class_rows')}, indent=2))


if __name__ == '__main__': main()
