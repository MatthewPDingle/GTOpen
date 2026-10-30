"""Finite-population expectation control, using only old and synthetic policies.

Checks the proposed arithmetic without modifying the active experiment. BB
ordinary call/raise values below are synthetic covariance stress cases, not
new postflop evaluations or estimates of real training variance.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import time
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class
from reboot_research_idle_v1 import idle
from preflop_allin_matrix_v1 import AllinMatrix
from initial_allin_targets_v1 import bb_correction, btn_targets

PREFIX = 'initial-allin-target-control-v1'


def main():
    start = time.monotonic()
    def guard():
        assert idle() and psutil.virtual_memory().available > 20_000_000_000 and time.monotonic()-start < 300
    guard()
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists(), 'Version a new attempt; do not overwrite registered evidence'
    mrp, mpp, mapath = [OUT/f'preflop-allin-matrix-control-v1-{k}.json' for k in ('registration', 'result', 'independent-review')]
    mr, mp, ma = map(read, (mrp, mpp, mapath))
    assert ma['passed'] and ma['result_sha256'] == sha(mpp) and ma['registration_sha256'] == sha(mrp) == mp['registration_sha256']
    for p, h in mr['inputs'].items():
        assert sha(p) == h, p
    matrix_path = Path(mp['matrix_artifact'])
    assert sha(matrix_path) == mp['matrix_sha256'] == ma['matrix_sha256']
    source_path = OUT/'bb-context-candidate.json'
    source = source_path.read_text()
    matrix = AllinMatrix(read(matrix_path), source)
    crp = OUT/'complete-private-allin-cache-v2-registration.json'
    cr = read(crp)
    pop_path = Path(cr['population'])
    population = read(pop_path)
    cache = load_complete_cache()
    endpoint_path = OUT/'exhaustive-btn-response-v2-result.json'
    endpoint = read(endpoint_path)
    inputs = {str(p): sha(p) for p in (Path(__file__), ROOT/'tools/research/initial_allin_targets_v1.py',
        ROOT/'tools/research/preflop_allin_matrix_v1.py', mrp, mpp, mapath, matrix_path, source_path, crp, pop_path, endpoint_path)}
    policies = {}
    for name in ('combined_269', 'visible_302'):
        path = Path(endpoint['candidates'][name]['policy_artifact'])
        assert sha(path) == endpoint['candidates'][name]['policy_sha256']
        inputs[str(path)] = sha(path)
        doc = read(path)
        policies[name] = (np.asarray(doc['root_probabilities']), np.asarray([0. if x is None else x for x in doc['btn_call_probabilities']]))
    policies['zero-jam'] = (np.tile([.5, .25, .25, 0.], (169, 1)), np.zeros(169))
    policies['all-jam'] = (np.tile([0., 0., 0., 1.], (169, 1)), np.ones(169))
    save(rp, dict(inputs=inputs, scope='Conditional-expectation arithmetic only; no native integration, candidate training or strategic qualification.',
        pairings=16, synthetic_call_raise_stress_cases=2, maximum_seconds=300, production_modified=False, gpu_used=False))
    context = read(source_path)
    jam = context['nodes'][context['nodes'][0]['children'][3]]
    terminal = context['nodes'][jam['children'][1]]
    rake = terminal['pot']*context['rake_fraction']
    if context['rake_cap'] > 0:
        rake = min(rake, context['rake_cap'])
    net = terminal['pot']-rake
    b, t, w, bpay, tpay = [], [], [], [], []
    for row in population['rows']:
        cards = row['private_cards']; label = cache.rows[tuple(cards)]; n = label['boards']
        b.append(hand_class(cards[:2])); t.append(hand_class(cards[2:])); w.append(row['probability'])
        # Outcome-wise payout calculation, independent of matrix arithmetic.
        cb, ct = terminal['invested']
        bpay.append((label['wins']*(net-cb)+label['ties']*(net/2-cb)-label['losses']*cb)/n)
        tpay.append((label['losses']*(net-ct)+label['ties']*(net/2-ct)-label['wins']*ct)/n)
    b, t = np.array(b), np.array(t)
    w, bpay, tpay = map(np.asarray, (w, bpay, tpay))
    errors = dict(bb_conditional_correction=0., btn_conditional_correction=0., own_policy_mean=0., helper_recompute=0.)
    checks = {}
    for bn, (root, _) in policies.items():
        for tn, (_, call) in policies.items():
            guard(); exact = matrix.evaluate(root, call)
            qjam = exact['bb_jam_entries']/exact['bb_entries']
            # Expand both BTN responses for each compatible physical pair.
            bc = np.tile(b, 2)
            prob = np.concatenate((w*(1-call[t]), w*call[t]))
            j = np.concatenate((np.full(len(w), matrix.bb_win), bpay))
            d = qjam[bc]-j
            total = np.bincount(bc, weights=prob*d, minlength=169)/matrix.bb_mass
            errors['bb_conditional_correction'] = max(errors['bb_conditional_correction'], float(np.max(abs(total))))
            variance_cases = []
            for sign in (1., -1.):
                # Deliberately correlated returns expose why every coordinate
                # must be measured, rather than promising universal reduction.
                values = np.column_stack((np.full(len(j), matrix.bb_fold), sign*j*.5, -sign*j*.25, j))
                p = root[bc]; old = values-np.sum(values*p, axis=1)[:, None]
                change = -p[:, 3, None]*d[:, None]*np.ones((1, 4)); change[:, 3] += d
                new = old+change
                errors['own_policy_mean'] = max(errors['own_policy_mean'], float(np.max(abs(np.sum(new*p, axis=1)))))
                # Exercise exported helper for every class on a deterministic row.
                for c in range(169):
                    i = int(np.flatnonzero(bc == c)[0])
                    dv, dr = bb_correction(root[c], j[i], qjam[c])
                    edited = values[i].copy(); edited[3] = qjam[c]
                    direct = edited-edited@root[c]
                    errors['helper_recompute'] = max(errors['helper_recompute'], float(np.max(abs(old[i]+dr-direct))), abs(dv-(edited@root[c]-values[i]@root[c])))
                vars_old, vars_new = [], []
                for a in range(4):
                    mu = np.bincount(bc, weights=prob*old[:, a], minlength=169)/matrix.bb_mass
                    vars_old.append(float(np.sum(prob*(old[:, a]-mu[bc])**2)))
                    vars_new.append(float(np.sum(prob*(new[:, a]-mu[bc])**2)))
                variance_cases.append(dict(covariance_sign=sign, old=vars_old, corrected=vars_new))
            # Node visitation already carries shove reach. Compare expected
            # targets conditional on that event; do not weight targets again.
            reach = exact['btn_jam_mass']; conditional = np.zeros(169)
            supported = reach > 0
            conditional[supported] = exact['btn_call_entries'][supported]/reach[supported]
            visit = w*root[b, 3]
            err = np.bincount(t, weights=visit*(conditional[t]-tpay), minlength=169)
            if supported.any():
                errors['btn_conditional_correction'] = max(errors['btn_conditional_correction'], float(np.max(abs(err[supported]/reach[supported]))))
            for c in np.flatnonzero(supported):
                _, target = btn_targets(call[c], matrix.btn_fold, exact['btn_call_entries'][c], reach[c])
                errors['own_policy_mean'] = max(errors['own_policy_mean'], abs(float(target@np.array([1-call[c], call[c]]))))
            assert np.all(np.bincount(t, weights=visit, minlength=169)[~supported] == 0)
            checks[f'{bn}/{tn}'] = dict(visited_btn_classes=int(supported.sum()), synthetic_bb_variance=variance_cases)
    rejected = []
    for label, fn in [('zero-reach', lambda: btn_targets(.5, -2., 0., 0.)),
                      ('nan-payoff', lambda: bb_correction([.25]*4, float('nan'), 0.)),
                      ('bad-policy', lambda: bb_correction([1.]*4, 0., 0.)),
                      ('bad-btn-policy', lambda: btn_targets(2., -2., 0., .1))]:
        try:
            fn()
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError(label)
    assert max(errors.values()) < 1e-9, errors
    for p, h in inputs.items():
        assert sha(p) == h, p
    guard()
    result = dict(passed=True, registration_sha256=sha(rp), errors_bb=errors, pairings=checks,
        physical_canonical_pairs=len(w), rejected=rejected, seconds=time.monotonic()-start,
        caveat='Arithmetic control only. Synthetic call/raise returns do not measure actual training variance. Current policies, native transport, RNG preservation and production integration remain unqualified.',
        production_modified=False, gpu_used=False, accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json', result)
    print({k:v for k,v in result.items() if k != 'pairings'})


if __name__ == '__main__':
    main()
