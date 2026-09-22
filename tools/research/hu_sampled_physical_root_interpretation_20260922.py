"""Descriptive action allocation after the fixed GPU evaluation was audited.

No new response fitting or confidence claims; test-group decompositions below
are post-hoc descriptions of the already published overall result.
"""
import json
from pathlib import Path
import time

import numpy as np

from loopback_research_validation import idle
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import CLASSES
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-root-study-gpu-v1'


def main():
    started = time.monotonic()
    resultpath = OUT / (PREFIX + '-result.json')
    reviewpath = OUT / (PREFIX + '-independent-review.json')
    regpath = OUT / (PREFIX + '-registration.json')
    review = json.loads(reviewpath.read_text())
    assert review['passed'] and review['result_sha256'] == sha(resultpath)
    assert review['registration_sha256'] == sha(regpath)
    result = json.loads(resultpath.read_text())
    reg = json.loads(regpath.read_text())
    store = Path(reg['store'])
    response_path = store / 'response.json'
    response = json.loads(response_path.read_text())
    assert sha(response_path) == result['response_sha256']
    context_source = Path(reg['context']).read_text()
    sampler = PhysicalDeals(context_source, mode='full_deck', seed=0)  # no draws
    marginal = np.bincount(CLASSES, weights=sampler.first[0], minlength=169)
    assert abs(marginal.sum()-1) < 1e-12
    count = np.zeros(169, dtype=int)
    policy_sum = np.zeros((169, 4))
    first_policy = {}
    maximum_policy_spread = 0.
    for offset in range(0, reg['config']['training_deals'], reg['config']['batch_size']):
        assert idle() and time.monotonic()-started < 180
        name = f'{PREFIX}-train-{offset}'
        path = store / name / 'summary.json'
        assert sha(path) == result['batch_summary_hashes'][name]
        s = json.loads(path.read_text())
        for c, p in zip(s['classes'], s['root_probabilities']):
            count[c] += 1
            policy_sum[c] += p
            if c not in first_policy: first_policy[c] = np.asarray(p)
            maximum_policy_spread = max(maximum_policy_spread, float(np.max(np.abs(first_policy[c]-p))))
    assert count.tolist() == response['training_counts'] and np.min(count) > 0
    baseline = policy_sum/count[:, None]
    changed = baseline.copy()
    for c, action in enumerate(response['actions']):
        if action >= 0:
            changed[c] = 0.
            changed[c, action] = 1.
    baseline_frequency = marginal @ baseline
    response_frequency = marginal @ changed
    # Attribute the original held-out paired gain by the response action chosen
    # on TRAINING data. No per-class test argmax or new statistical look.
    groups = {str(a): dict(test_deals=0, total_gain_bb=0.) for a in (-1, 0, 1, 2, 3)}
    baseline_total = 0.
    for offset in range(0, reg['config']['evaluation_deals'], reg['config']['batch_size']):
        assert idle() and time.monotonic()-started < 180
        name = f'{PREFIX}-test-{offset}'
        path = store / name / 'summary.json'
        assert sha(path) == result['batch_summary_hashes'][name]
        s = json.loads(path.read_text())
        for c, values, original in zip(s['classes'], s['action_values'], s['baseline_values']):
            a = response['actions'][c]
            g = groups[str(a)]
            g['test_deals'] += 1
            g['total_gain_bb'] += values[a]-original if a >= 0 else 0.
            baseline_total += original
    n = reg['config']['evaluation_deals']
    for group in groups.values(): group['contribution_bb_per_entry'] = group['total_gain_bb']/n
    gain = sum(g['contribution_bb_per_entry'] for g in groups.values())
    assert abs(gain-result['intervals']['trained-response']['mean']) < 1e-10
    assert abs(-1-baseline_total/n-result['intervals']['always-fold']['mean']) < 1e-10
    rows = []
    ranks = '23456789TJQKA'
    for c in range(169):
        row, col = divmod(c, 13)
        name = ranks[row]+ranks[col] if row == col else ranks[max(row, col)]+ranks[min(row, col)]+('s' if row > col else 'o')
        rows.append(dict(hand=name, entry_probability=float(marginal[c]), training_count=int(count[c]),
                         baseline_policy=baseline[c].tolist(), selected_response_action=response['actions'][c]))
    value = dict(result_sha256=sha(resultpath), review_sha256=sha(reviewpath), source_sha256=sha(Path(__file__)),
                 action_order=['fold', 'call to 2 bb', 'raise to 6 bb', 'jam to 200 bb'],
                 baseline_root_frequencies=baseline_frequency.tolist(),
                 trained_response_root_frequencies=response_frequency.tolist(),
                 maximum_observed_same_class_policy_spread=maximum_policy_spread,
                 baseline_sample_ev_bb=baseline_total/n, response_sample_ev_bb=baseline_total/n+gain,
                 response_action_groups=groups, classes=rows,
                 scope='Post-hoc description, not independent confirmation or a new fitted policy. Frequencies use exact compatible-entry class mass and training-observed root policies. Grouped gains describe the existing held-out result; no group-specific confidence claims. The response is against the frozen opponent, not a jointly solved equilibrium.',
                 production_modified=False)
    save(OUT / (PREFIX + '-interpretation.json'), value)
    print(json.dumps({k: value[k] for k in ('baseline_root_frequencies', 'trained_response_root_frequencies',
           'baseline_sample_ev_bb', 'response_sample_ev_bb', 'response_action_groups', 'maximum_observed_same_class_policy_spread')}, indent=2))


if __name__ == '__main__':
    main()
