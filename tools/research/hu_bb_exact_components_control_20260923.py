"""Control the exact-component identity on old native-verified fixture deals.

No current candidate, policy inference, new deals, GPU work or strength claim.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
import json
import math
from collections import Counter
from pathlib import Path
import time
import numpy as np
from finite_bb_root_components_v1 import components, exact_difference
from sampled_allin_protocol_v3 import AllinCache, canonical
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class
from reboot_research_idle_v1 import idle

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'bb-exact-components-control-v1'
STORE = Path('S:/GTOpen-research/btn-stratified-conditional-control-v1')


def read(p):
    return json.loads(Path(p).read_text())


def main():
    began = time.monotonic(); assert idle()
    fixture_path = OUT/'btn-stratified-conditional-control-v1-result.json'
    fixture_reg = OUT/'btn-stratified-conditional-control-v1-registration.json'
    fixture = read(fixture_path)
    assert fixture['passed'] and fixture['registration_sha256'] == sha(fixture_reg)
    for p, h in {**read(fixture_reg)['inputs'], **fixture['artifacts']}.items():
        assert sha(p) == h, p
    context_path = OUT/'bb-context-candidate.json'; source = context_path.read_text()
    cache_path = STORE/'cache/cache.json'
    cache = AllinCache(cache_path, fixture['cache_result']['cache_sha256'])
    paths = [Path(__file__), context_path, fixture_path, fixture_reg, cache_path,
        *[ROOT/'tools/research'/n for n in ('finite_bb_root_components_v1.py',
          'finite_btn_response_v1.py', 'sampled_allin_protocol_v3.py',
          'sampled_physical_root_evaluation_v1.py', 'reboot_research_idle_v1.py')]]
    inputs = {str(p):sha(p) for p in paths}; inputs.update(fixture['artifacts'])
    rp = OUT/f'{PREFIX}-registration.json'
    save(rp, dict(inputs=inputs, complete_fixture_deals=192, maximum_seconds=180,
        policy_alternatives=['fold', 'call', 'raise', 'jam', 'deterministic-class-menu', 'mixed'],
        scope='Exact-component arithmetic on a completed four-model fixture; class-balanced fixture is not the game population.',
        production_modified=False))
    deals = []; action_values = []; baseline_values = []; rows = []
    baseline = np.tile([1., 0., 0., 0.], (169, 1)); seen = set(); btn = [None]*169
    context = json.loads(source); jam_hi = context['nodes'][0]['children'][3]+1
    for offset in range(0, 192, 16):
        folder = STORE/f'batch-{offset:04d}'
        batch, profiles, summary, native = [read(folder/n) for n in ('query-batch.json', 'profiles.json', 'summary.json', 'native.json')]
        # Bind every input consumed here to the successful old fixture.
        for name in ('query-batch.json', 'profiles.json', 'summary.json', 'native.json'):
            p = folder/name; assert fixture['artifacts'][str(p)] == sha(p), p
        for p in profiles['profiles'][0]['policies']:
            if int(p['hi']) == jam_hi:
                key = int(p['lo']); c = hand_class([key & 63, (key >> 6) & 63])
                if btn[c] is not None:
                    assert btn[c] == p['probabilities'][1]
                btn[c] = p['probabilities'][1]
        for c, mix in zip(summary['classes'], summary['root_probabilities']):
            if c in seen:
                assert np.max(abs(baseline[c]-mix)) < 1e-12
            baseline[c] = mix; seen.add(c)
        values = {p['name']: [d['values'][0] for d in p['deals']] for p in native['profiles']}
        actions = np.asarray([values[f'action-{a}'] for a in range(4)]).T
        assert np.max(abs(actions-np.asarray(summary['action_values']))) < 1e-12
        assert np.max(abs(np.asarray(values['baseline'])-summary['baseline_values'])) < 1e-12
        deals.extend(batch['deals']); action_values.extend(actions); baseline_values.extend(values['baseline'])
    counts = Counter(canonical(d[:4]) for d in deals)
    population = dict(context_sha256=sha(context_path), player_roles_fixed=True,
        rows=[dict(private_cards=list(k), probability=n/192) for k, n in sorted(counts.items())])
    table = components(source, population, baseline, btn, cache.rows)
    classes = np.asarray([hand_class(d[:2]) for d in deals]); values = np.asarray(action_values)
    maximum_error = 0.
    for c in seen:
        row = table['classes'][c]; mask = classes == c
        maximum_error = max(maximum_error, abs(row['conditional_jam_value']-math.fsum(values[mask, 3])/sum(mask)))
        assert abs(row['entry_probability']-sum(mask)/192) < 1e-12
    alternatives = [np.tile(np.eye(4)[a], (169, 1)) for a in range(4)]
    alternatives += [np.eye(4)[np.arange(169) % 4], np.tile([.1, .2, .3, .4], (169, 1))]
    errors = []
    for response in alternatives:
        direct = math.fsum((response[classes]*values).sum(1)-baseline_values)/192
        exact = exact_difference(table, baseline, response)
        residual = math.fsum(((response[classes, 1:3]-baseline[classes, 1:3])*values[:, 1:3]).sum(1))/192
        errors.append(abs(direct-exact-residual))
    # The jam action value must be unchanged if BB's actual policy never jams.
    nojam = np.tile([1., 0., 0., 0.], (169, 1))
    assert components(source, population, nojam, btn, cache.rows) == table
    assert exact_difference(table, baseline, baseline) == 0
    assert maximum_error < 1e-9 and max(errors) < 1e-9
    for p, h in inputs.items():
        assert sha(p) == h, p
    assert idle() and time.monotonic()-began < 180
    save(OUT/f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(rp),
        native_fixture_deals=192, supported_bb_fixture_classes=len(seen),
        maximum_counterfactual_jam_value_error_bb=maximum_error,
        maximum_decomposition_error_bb=max(errors), alternatives_checked=len(alternatives),
        counterfactual_independent_of_own_jam_frequency=True,
        seconds=time.monotonic()-began, production_modified=False, accuracy_qualified=False,
        scope='Identity validated on the old finite fixture; no full-population coverage, variance reduction or strategic result established.'))
    print(json.dumps(dict(passed=True, maximum_native_jam_error=maximum_error,
        maximum_decomposition_error=max(errors), seconds=time.monotonic()-began)))


if __name__ == '__main__':
    main()
