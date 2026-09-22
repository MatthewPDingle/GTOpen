"""Export frozen research policies for a read-only local range comparison."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import hashlib
import json
from pathlib import Path
import numpy as np
from storage_strategic_common_prior_20260920 import CLASSES, COUNTS, MASKS, prior
from storage_strategic_policy_report_20260920 import hand_label

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'research/preflop-evolution'
OUT = BASE/'range-preview'


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    tree_path = BASE/'conditional-hu-20260919/subtree.json'
    common_path = BASE/'ssd-storage-20260920/strategic-common-prior-v1.json'
    frozen = read(BASE/'ssd-storage-20260920/strategic-confirm190-v1-registration.json')['inputs_sha256']
    tree = read(tree_path)
    common = read(common_path)
    assert digest(tree_path) == common['inputs_sha256'][str(tree_path.relative_to(ROOT))]
    weights = np.asarray(tree['incoming_class_mass'])[:, CLASSES]/COUNTS[CLASSES]
    weights /= weights.max(1)[:, None]
    weights[weights < common['entry_cutoff']] = 0
    root_prior, root_z, error = prior(weights)
    assert np.max(abs(root_prior - common['combo_prior'])) < 1e-12
    sources = [
        ('weighted', 'Research · weighted 112 flops', BASE/'ssd-storage-20260920/strategic-weighted112-2000-v1-result.json'),
        ('equal', 'Research · equal-weight 112 flops', BASE/'ssd-storage-20260920/strategic-equal112-2000-v1-result.json'),
        ('report47', 'Earlier research · 47 flops', BASE/'representative-coverage-20260919/report47-full-result.json'),
    ]
    policies = []
    hashes = {str(tree_path.relative_to(ROOT)):digest(tree_path), str(common_path.relative_to(ROOT)):digest(common_path)}
    for key, label, path in sources:
        assert digest(path) == frozen[str(path.relative_to(ROOT))]
        source = read(path)
        last = source['records'][-1]
        policies.append((key, label, last['evaluation']['preflop_policy'], last['iteration']))
        hashes[str(path.relative_to(ROOT))] = digest(path)
    original = [np.asarray(n['strategy']).reshape(len(n['actions']), 169)[:, CLASSES].tolist()
                if n['actions'] else [] for n in tree['nodes']]
    policies.append(('balanced', 'Saved GTOpen · Balanced', original, tree['iteration']))
    labels = {0:'UTG facing LJ’s 3-bet', 3:'LJ facing UTG’s 4-bet',
              6:'UTG facing LJ’s 5-bet shove', 9:'LJ facing UTG’s shove'}
    paths = {0:'UTG opens to 6 · LJ 3-bets to 18 · everyone else folds',
             3:'UTG opens to 6 · LJ 3-bets to 18 · UTG 4-bets to 45',
             6:'UTG opens to 6 · LJ 3-bets to 18 · UTG 4-bets to 45 · LJ shoves to 200',
             9:'UTG opens to 6 · LJ 3-bets to 18 · UTG shoves to 200'}
    models = []
    checked = 0
    for key, label, policy, iteration in policies:
        node_rows = {}
        def walk(index, reach):
            nonlocal checked
            n = tree['nodes'][index]
            if not n['actions']:
                return
            p = n['actor']
            sigma = np.asarray(policy[index])
            assert sigma.shape == (len(n['actions']), 1326)
            assert np.isfinite(sigma).all() and sigma.min() >= 0 and sigma.max() <= 1+1e-7
            # Saved f32 probabilities can differ from 1 by one rounding unit.
            assert np.max(abs(sigma.sum(0)-1)) < 2e-7
            sigma = sigma/sigma.sum(0)
            marginal, z, local_error = prior(reach)
            cp = np.bincount(CLASSES, weights=marginal[p], minlength=169)
            class_rows = []
            for c in range(169):
                mask = CLASSES == c
                f = (sigma[:, mask] @ marginal[p, mask]/cp[c]).tolist() if cp[c] > 0 else None
                class_rows.append({'hand':hand_label(c), 'mass':float(cp[c]),
                    'relative_weight':float((cp[c]/COUNTS[c])/np.max(cp/COUNTS)), 'frequencies':f})
            freq = sigma @ marginal[p]
            restored = sum(r['mass']*np.asarray(r['frequencies']) for r in class_rows if r['frequencies'] is not None)
            assert np.max(abs(freq-restored)) < 1e-12
            actions = []
            for a, child in zip(n['actions'], n['children']):
                if a['kind'] == 'call':
                    action_label = f"Call {a['to']-n['invested'][p]:g} bb"
                elif a['kind'] == 'raise':
                    action_label = f"4-bet to {a['to']:g} bb"
                elif a['kind'] == 'jam':
                    action_label = f"Shove to {a['to']:g} bb"
                else:
                    action_label = 'Fold'
                actions.append({'label':action_label, 'kind':a['kind'], 'child':child,
                                'next_decision':child in labels})
            node_rows[str(index)] = {'label':labels[index], 'path':paths[index], 'actor':['UTG','LJ'][p],
                'actions':actions, 'frequencies':freq.tolist(), 'hands':class_rows,
                'entry_probability':float(z/root_z), 'marginal_check_error':local_error}
            checked += 1
            for a, child in enumerate(n['children']):
                child_reach = reach.copy()
                child_reach[p] *= sigma[a]
                walk(child, child_reach)
        walk(0, weights.copy())
        models.append({'id':key, 'label':label, 'iterations':iteration, 'nodes':node_rows})
    payload = {'models':models, 'node_order':[0,3,6,9], 'source_hashes':hashes,
        'scope':'Frozen conditional two-player policies; no new solves. Earlier actions and incoming ranges stay fixed.',
        'setup':'200 bb · SB 0.5 / BB 1 / straddle 2 · 4% rake, 6 bb cap · eight-player source',
        'seat_note':'Study names UTG / LJ correspond to GTOpen seats UTG1 / MP, after the straddler.',
        'method':'Class frequencies use physical-card-compatible arriving hand weights. Later-node arrival ranges vary by policy. Unsupported hands have no displayed strategy.',
        'not_deployed':True, 'production_port_untouched':56708}
    OUT.mkdir(exist_ok=True)
    (OUT/'data.json').write_text(json.dumps(payload, indent=2, allow_nan=False), encoding='utf-8', newline='\n')
    review = {'passed':True, 'models':len(models), 'decision_nodes_checked':checked,
        'root_common_prior_max_error':float(np.max(abs(root_prior-common['combo_prior']))),
        'data_sha256':digest(OUT/'data.json'), 'builder_sha256':digest(Path(__file__)),
        'sources':hashes, 'note':'Saved f32 policy columns normalized for presentation only; source files unchanged.'}
    (OUT/'data-review.json').write_text(json.dumps(review, indent=2), encoding='utf-8', newline='\n')
    print(json.dumps(review, indent=2))


if __name__ == '__main__':
    main()
