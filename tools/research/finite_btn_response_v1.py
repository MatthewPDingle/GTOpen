"""Integrate BTN's fold/call response over a supplied finite private population.

This routine does not certify that the supplied population is the full game.
That requires an external population/provenance audit. Policy probabilities
must already be qualified as class-constant at the two first-own-action nodes.
Equity labels enter only here, after all policy inference is finished.
"""
import hashlib
import json
import math
import numpy as np
from sampled_allin_protocol_v3 import BOARDS, canonical
from sampled_physical_root_evaluation_v1 import hand_class


def integrate(context_source, population, root_policy, btn_call, cache_rows):
    context = json.loads(context_source)
    if (population.get('context_sha256') != hashlib.sha256(context_source.encode()).hexdigest()
            or population.get('player_roles_fixed') is not True):
        raise ValueError('Population context and player roles must match')
    root = context['nodes'][0]
    if root['actor'] != 0 or [a['kind'] for a in root['actions']] != ['fold', 'call', 'raise', 'jam']:
        raise ValueError('Expected BB root menu')
    response = context['nodes'][root['children'][3]]
    if response['actor'] != 1 or [a['kind'] for a in response['actions']] != ['fold', 'call']:
        raise ValueError('Expected BTN fold/call response')
    folded, called = [context['nodes'][i] for i in response['children']]
    if (folded['leaf']['type'] != 'fold' or called['leaf']['type'] != 'showdown'
            or context['config']['ante'] != 0):
        raise ValueError('Unsupported terminal cashflow context')
    fold = float(folded['leaf']['utilities'][1])
    pot, invested = float(called['pot']), float(called['invested'][1])
    fraction, cap = float(context['rake_fraction']), float(context['rake_cap'])
    if (not all(math.isfinite(v) for v in (fold, pot, invested, fraction, cap))
            or min(pot, invested, fraction, cap) < 0 or fraction > 1):
        raise ValueError('Invalid terminal economics')
    rake = pot * fraction
    if cap > 0:
        rake = min(rake, cap)
    root_policy = np.asarray(root_policy, dtype=np.float64)
    btn_call = np.asarray(btn_call, dtype=np.float64)
    if (root_policy.shape != (169, 4) or not np.isfinite(root_policy).all()
            or np.any(root_policy < 0) or np.max(abs(root_policy.sum(1) - 1)) > 1e-12):
        raise ValueError('Normalized BB policies required for all classes')
    if btn_call.shape != (169,):
        raise ValueError('169 BTN class slots required; unsupported slots may be NaN')
    rows = population.get('rows')
    if not isinstance(rows, list) or not rows:
        raise ValueError('Nonempty finite population required')
    seen = set()
    masses, classes, reaches, calls, baselines = [], [], [], [], []
    for row in rows:
        cards = row['private_cards']
        key = canonical(cards)
        if key != tuple(cards) or key in seen:
            raise ValueError('Unique canonical private pairs required')
        seen.add(key)
        weight = row['probability']
        if not isinstance(weight, (float, int)) or not math.isfinite(weight) or weight <= 0:
            raise ValueError('Positive finite population probabilities required')
        if key not in cache_rows:
            raise ValueError('Incomplete equity coverage; no missing-pair fallback')
        label = cache_rows[key]
        if (label['private_cards'] != cards
                or any(type(label[k]) is not int or label[k] < 0 for k in ('wins', 'ties', 'losses', 'boards'))
                or label['boards'] != BOARDS
                or label['wins'] + label['ties'] + label['losses'] != BOARDS):
            raise ValueError('Complete role-preserving integer board counts required')
        bb, btn = hand_class(cards[:2]), hand_class(cards[2:])
        prob = float(btn_call[btn])
        if not math.isfinite(prob) or not 0 <= prob <= 1:
            raise ValueError('Valid BTN policy required on every populated class')
        # Cache wins belong to BB. BTN wins are the cache losses.
        call = -invested + (pot - rake) * (label['losses'] + .5 * label['ties']) / BOARDS
        masses.append(float(weight)); classes.append(btn)
        reaches.append(weight * root_policy[bb, 3])
        calls.append(call); baselines.append((1 - prob) * fold + prob * call)
    if abs(math.fsum(masses) - 1) > 1e-12:
        raise ValueError('Population must sum to one; no implicit renormalization')
    classes = np.asarray(classes, dtype=np.int64)
    reach = np.asarray(reaches)
    entry = np.bincount(classes, weights=masses, minlength=169)
    jam = np.bincount(classes, weights=reach, minlength=169)
    fold_totals = jam * fold
    call_totals = np.bincount(classes, weights=reach * calls, minlength=169)
    baseline = np.bincount(classes, weights=reach * baselines, minlength=169)
    best = np.maximum(fold_totals, call_totals)
    actions = np.where(jam == 0, -1, (call_totals > fold_totals).astype(int))
    if np.min(best - baseline) < -1e-10:
        raise ValueError('Best class response cannot underperform class-constant baseline')
    per_class = [dict(hand_class=c, entry_probability=float(entry[c]), jam_probability=float(jam[c]),
        baseline_call_probability=float(btn_call[c]) if entry[c] > 0 else None,
        best_action=int(actions[c]), fold_value_per_entry=float(fold_totals[c]),
        call_value_per_entry=float(call_totals[c]), baseline_value_per_entry=float(baseline[c]),
        best_value_per_entry=float(best[c]), gain_per_entry=float(best[c] - baseline[c])) for c in range(169)]
    total_jam = math.fsum(jam)
    baseline_call_mass = math.fsum(jam[c] * btn_call[c] for c in range(169) if entry[c] > 0)
    best_call_mass = math.fsum(jam[c] for c in range(169) if actions[c] == 1)
    return dict(scope='BTN fold/call response on supplied finite population; whole-game coverage requires separate audit',
        private_pairs=len(rows), entry_mass=math.fsum(masses), jam_probability=total_jam,
        baseline_value_per_entry=math.fsum(baseline),
        gains_per_entry=dict(best=math.fsum(best - baseline),
            always_fold=math.fsum(fold_totals - baseline), always_call=math.fsum(call_totals - baseline)),
        baseline_call_given_jam=baseline_call_mass / total_jam if total_jam else None,
        best_call_given_jam=best_call_mass / total_jam if total_jam else None,
        tie_rule='fold', zero_reach_action=-1, classes=per_class)
