"""Exact fold/jam components over an explicitly supplied private population.

Does not certify population coverage or evaluate postflop continuations. The
BB jam value is counterfactual: never multiply it by BB's own jam frequency.
"""
import json
import math
import numpy as np
from finite_btn_response_v1 import integrate
from sampled_physical_root_evaluation_v1 import hand_class


def components(source, population, baseline, btn_call, cache_rows):
    # Reuse the previously controlled population/policy/role validation. This
    # helper still needs an external coverage audit for a full-population claim.
    integrate(source, population, baseline, btn_call, cache_rows)
    context = json.loads(source); root = context['nodes'][0]
    response = context['nodes'][root['children'][3]]
    folded, called = [context['nodes'][i] for i in response['children']]
    root_fold = context['nodes'][root['children'][0]]
    assert root_fold['leaf']['type'] == 'fold'
    fold_value = root_fold['leaf']['utilities'][0]
    won_uncontested = folded['leaf']['utilities'][0]
    rake = called['pot']*context['rake_fraction']
    if context['rake_cap'] > 0:
        rake = min(rake, context['rake_cap'])
    mass = [[] for _ in range(169)]; jam = [[] for _ in range(169)]
    for row in population['rows']:
        cards = row['private_cards']; bb, btn = hand_class(cards[:2]), hand_class(cards[2:])
        label = cache_rows[tuple(cards)]; call_prob = btn_call[btn]
        showdown = -called['invested'][0] + (called['pot']-rake)*(label['wins']+.5*label['ties'])/label['boards']
        value = (1-call_prob)*won_uncontested + call_prob*showdown
        mass[bb].append(row['probability']); jam[bb].append(row['probability']*value)
    mass = list(map(math.fsum, mass)); jam = list(map(math.fsum, jam))
    return dict(scope='Fold/jam expectations on supplied population only; call/raise values absent',
        classes=[dict(hand_class=c, entry_probability=mass[c],
            fold_value_per_entry=mass[c]*fold_value, jam_value_per_entry=jam[c],
            conditional_jam_value=jam[c]/mass[c] if mass[c] else None) for c in range(169)])


def exact_difference(table, baseline, response):
    """Exact fold/jam part of response-minus-baseline value, per original entry.

Response must be fixed before independent residual test deals are generated.
Add sampled call/raise residuals using the ORIGINAL population, not an
unweighted class-balanced training stream. No uncertainty is attached here.
"""
    baseline, response = [np.asarray(p, dtype=float) for p in (baseline, response)]
    for p in (baseline, response):
        if (p.shape != (169, 4) or not np.isfinite(p).all() or np.any(p < 0)
                or np.max(abs(p.sum(1)-1)) > 1e-12):
            raise ValueError('Normalized 169-by-4 class policies required')
    assert [r['hand_class'] for r in table['classes']] == list(range(169))
    return math.fsum((response[c, 0]-baseline[c, 0])*row['fold_value_per_entry']
                    +(response[c, 3]-baseline[c, 3])*row['jam_value_per_entry']
                    for c, row in enumerate(table['classes']))
