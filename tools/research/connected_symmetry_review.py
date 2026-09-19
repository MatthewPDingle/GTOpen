"""Audit projected connected games against registered comparison gates."""
import json
from pathlib import Path
import sys
import numpy as np
import integrated_coverage_review as review

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/symmetric-bridge-20260919'


def compare(panel):
    runs = {}
    audits = {}
    for mode in ['explicit', 'compact']:
        path = OUT / f'connected-{panel}-{mode}-result.json'
        run = json.loads(path.read_text())
        assert run['records'][-1]['iteration'] == 2000
        audits[mode] = review.audit_result(run)
        runs[mode] = run['records'][-1]['evaluation']
    c = review.c
    entry = json.loads((ROOT / 'research/preflop-evolution/conditional-hu-20260919/subtree.json').read_text())
    w = np.array(entry['incoming_class_mass'])[:, c.CLASSES] / c.COUNTS[c.CLASSES]
    w /= w.max(1)[:, None]
    w[w < 1e-5] = 0
    joint = w[0, :, None] * w[1, None, :] * ((c.MASKS[:, None] & c.MASKS[None, :]) == 0)
    prior = joint.sum(1) / joint.sum()
    a, b = [runs[m] for m in ['explicit', 'compact']]
    diff = abs(np.array(a['preflop_policy'][0]) - np.array(b['preflop_policy'][0]))
    ev_diff = float(np.max(abs(np.array(a['ev']) - b['ev'])))
    tv = float((diff.sum(0) / 2) @ prior)
    old_name = 'old-two-orbits' if panel == 'two' else 'panel-ab'
    old = json.loads((ROOT / f'research/preflop-evolution/integrated-coverage-20260919/{old_name}-result.json').read_text())['records'][-1]['evaluation']
    changes = {}
    for mode, e in runs.items():
        changes[mode] = dict(
            ev_delta=(np.array(e['ev']) - old['ev']).tolist(),
            prior_weighted_policy_tv=float((abs(np.array(e['preflop_policy'][0]) - old['preflop_policy'][0]).sum(0) / 2) @ prior))
    gates = dict(converged=all(e['gap_total'] < .01 for e in runs.values()),
                 nonnegative_gains=all(min(e['gaps']) > -1e-5 for e in runs.values()),
                 ev_agreement=ev_diff < .002, policy_agreement=tv < .01)
    result = dict(panel=panel, audits=audits, gates=gates, passed=all(gates.values()),
                  max_ev_difference_bb=ev_diff, prior_weighted_policy_tv=tv,
                  max_supported_hand_action_difference=float(diff[:, prior > 0].max()),
                  summary={m: {k: e[k] for k in ['ev', 'gaps', 'gap_total', 'root_frequencies']} for m, e in runs.items()},
                  changes_from_original=changes,
                  limitation='Finite development-panel game. Passing does not validate full poker or erase the rapid-range stress failure.')
    path = OUT / f'connected-{panel}-review.json'
    assert not path.exists(), 'Preserve completed comparisons.'
    path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    compare(sys.argv[1])
