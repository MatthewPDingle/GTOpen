"""Post-hoc root action diagnosis on the frozen 190-board evaluation.

No training, policy edits, new panel selection, or Wizard accuracy claim.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from storage_strategic_common_prior_20260920 import CLASSES, COUNTS
from storage_strategic_policy_report_20260920 import hand_label
from storage_strategic_confirm_analysis_20260922 import evaluate

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'research/preflop-evolution'
SRC = BASE/'ssd-storage-20260920'
OUT = BASE/'blind-defense-20260922'
PREFIX = 'root-action-diagnostic-v1'


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def emit(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def main():
    started = time.monotonic()
    review_path = SRC/'strategic-confirm190-recovery-v1-review.json'
    review = read(review_path)
    assert review['comparison_complete'] and review['response_convergence_passed']
    frozen = {**review['inputs_sha256'], **review['evidence_sha256']}
    tree_path = BASE/'conditional-hu-20260919/subtree.json'
    panel_path = SRC/'strategic-confirm190-v1-manifest.json'
    combined_path = SRC/'strategic-confirm190-recovery-v1-weighted-result.json'
    paths = [tree_path, panel_path, combined_path]
    workers = [SRC/((('strategic-confirm190-v1' if i*3 < 176 else
                     'strategic-confirm190-recovery-v1') + f'-weighted-{i:03}-result.json'))
               for i in range(190)]
    paths += workers
    hashes = {}
    for p in paths:
        name = str(p.relative_to(ROOT))
        expected = frozen.get(name)
        if p == combined_path:
            expected = next(x['result_sha256'] for x in review['results'] if x['source'] == 'weighted')
        assert expected is not None, name
        hashes[name] = sha(p)
        assert hashes[name] == expected, name
    hashes[str(review_path.relative_to(ROOT))] = sha(review_path)
    for p in [Path(__file__), ROOT/'tools/research/storage_strategic_common_prior_20260920.py',
              ROOT/'tools/research/storage_strategic_policy_report_20260920.py',
              ROOT/'tools/research/storage_strategic_confirm_analysis_20260922.py']:
        hashes[str(p.relative_to(ROOT))] = sha(p)
    emit(OUT/(PREFIX+'-registration.json'), dict(
        purpose='Post-hoc diagnosis only; retain all 190 boards and all supported hands.',
        inputs_sha256=hashes, production_changed=False, training=False,
        metrics=['root action values against fixed opponent', 'call minus fold',
                 'postflop / later-preflop / root deviation decomposition',
                 'paired single-board omission sensitivity'],
        caveats='Evaluation panel already inspected; not a new confirmation and not a tuning set.'))
    tree = read(tree_path); nodes = tree['nodes']; panel = read(panel_path)
    final = read(combined_path)['records'][-1]['evaluation']
    sigma = [np.asarray(x) for x in final['preflop_policy']]
    assert nodes[0]['actor'] == 0 and nodes[0]['children'] == [1, 2, 3, 9]
    assert [a['kind'] for a in nodes[0]['actions']] == ['fold', 'call', 'raise', 'jam']
    weights = np.asarray(tree['incoming_class_mass'])[:, CLASSES]/COUNTS[CLASSES]
    weights /= weights.max(1)[:, None]; weights[weights < 1e-5] = 0
    chance = np.asarray([b['weight'] for b in panel['boards']], dtype=float)
    chance /= chance.sum()
    dense = np.zeros((190, 4, len(nodes), 1326))
    masses = np.zeros((190, 1326)); zs = np.zeros(190)
    for i, path in enumerate(workers):
        worker = read(path)
        assert worker['boards'] == [panel['boards'][i]['board']]
        assert worker['records'][-1]['iteration'] == 2000
        assert worker['records'][-1]['evaluation']['preflop_policy'] == final['preflop_policy']
        masses[i] = worker['terminal_values']['root_opponent_mass']
        zs[i] = worker['root_normalizer']
        for k, values in enumerate(worker['terminal_values']['values']):
            for j, n in enumerate(nodes):
                if n['kind'] != 0:
                    dense[i, k, j] = values[j]
        assert np.max(abs(dense[i, 0, 1] + 6*masses[i])) < 1e-9
        assert abs(weights[0]@masses[i] - zs[i]) < 1e-8
    leaves = np.einsum('b,bknh->knh', chance, dense)
    mass = chance@masses; z = float(chance@zs)

    def walk(node, post_br, later_br):
        n = nodes[node]
        if n['kind'] != 0:
            return leaves[int(post_br), node]
        children = np.asarray([walk(c, post_br, later_br) for c in n['children']])
        if n['actor'] != 0:
            return children.sum(0)  # Opponent probabilities already in leaf CFVs.
        return children.max(0) if later_br else (children*sigma[node]).sum(0)

    q = np.asarray([[walk(c, post, later) for c in nodes[0]['children']]
                    for post, later in [(False, False), (True, False), (True, True)]])
    # Independent explicit expansion of this 12-node tree, including later own action.
    for k in [0, 1]:
        explicit = np.asarray([leaves[k, 1], leaves[k, 2],
            leaves[k, 4]+leaves[k, 5]+sigma[6][0]*leaves[k, 7]+sigma[6][1]*leaves[k, 8],
            leaves[k, 10]+leaves[k, 11]])
        assert np.max(abs(explicit-q[k])) < 1e-10
    v = np.einsum('kah,ah->kh', q, sigma[0])
    best = q[2].max(0)
    components = np.asarray([v[1]-v[0], v[2]-v[1], best-v[2]])
    component_bb = components@weights[0]/z
    ev, gaps, postgaps, _ = evaluate(nodes, sigma, leaves, weights, z)
    assert np.max(abs(ev-final['ev'])) < 1e-9
    assert np.max(abs(gaps-final['gaps'])) < 1e-9
    assert abs(component_bb.sum()-gaps[0]) < 1e-10
    assert abs(component_bb[0]-postgaps[0]) < 1e-10
    assert abs(v[0]@weights[0]/z-ev[0]) < 1e-10
    assert np.min(components) > -1e-5
    root_only = float((q[0].max(0)-v[0])@weights[0]/z)
    rows = []
    for c in range(169):
        mask = CLASSES == c; w = weights[0, mask]
        denominator = float(w@mass[mask])
        if denominator <= 0:
            continue
        values = q[:, :, mask]@w/denominator
        frequencies = sigma[0][:, mask]@(w*mass[mask])/denominator
        omissions = []
        for i in range(190):
            den = denominator-chance[i]*(w@masses[i, mask])
            assert den > 0
            numerator = (q[1, 1, mask]-q[1, 0, mask])@w
            removed = chance[i]*((dense[i, 1, 2, mask]-dense[i, 1, 1, mask])@w)
            omissions.append(float((numerator-removed)/den))
        assert np.max(abs(values[:, 0]+6)) < 1e-10
        rows.append(dict(hand=hand_label(c), evaluation_entry_probability=denominator/z,
            action_frequencies=frequencies.tolist(), action_ev_bb=values.tolist(),
            call_minus_fold_bb=float(values[1, 1]-values[1, 0]),
            call_minus_fold_omission_range_bb=[min(omissions), max(omissions)],
            deviation_components_bb=(components[:, mask]@w/z).tolist()))
    assert abs(sum(r['evaluation_entry_probability'] for r in rows)-1) < 1e-10
    reconstructed = sum(r['evaluation_entry_probability']*np.dot(r['action_frequencies'], r['action_ev_bb'][0]) for r in rows)
    assert abs(reconstructed-ev[0]) < 1e-10
    selected = ['22','33','44','55','66','77','88','99','TT','JJ','QQ','54s','65s','76s','87s','98s','T9s','ATs','AJs','AQs','KQs']
    result = dict(passed=True, actions=['fold','call','4-bet','jam'],
        value_modes=['frozen continuation', 'postflop best response; later preflop fixed',
                     'postflop and later preflop best response'],
        total_p0_gap_bb=float(gaps[0]), root_only_deviation_bb=root_only,
        additive_decomposition=dict(postflop=float(component_bb[0]),
            later_preflop_after_postflop=float(component_bb[1]),
            root_after_all_later_optimization=float(component_bb[2])),
        hands=rows, selected_hands=[r for h in selected for r in rows if r['hand']==h],
        source_registration_sha256=sha(OUT/(PREFIX+'-registration.json')),
        limitations='Conditional on fixed input ranges/opponent and restricted evaluated game. Class EVs average compatible physical combos. EV includes prior 6bb investment; fold=-6. Omission range is sensitivity, not confidence. Best response is not a new equilibrium. Do not fit these inspected boards.',
        elapsed_seconds=time.monotonic()-started)
    # Recheck identity after analysis, including input sources and this script.
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    emit(OUT/(PREFIX+'-result.json'), result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['hands','selected_hands']}, indent=2))
    for r in result['selected_hands']:
        print(r['hand'], 'call%', round(r['action_frequencies'][1]*100,2),
              'call-fold', round(r['call_minus_fold_bb'],4),
              'omit', [round(x,4) for x in r['call_minus_fold_omission_range_bb']])


if __name__ == '__main__':
    main()
