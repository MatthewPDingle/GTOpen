"""Rebuild exhaustive BTN values with scalar sums and repeat CPU policy lookup.

Reuses the separately audited full population/equity table. Does not call the
finite integration helper or rerun the GPU/native showdown enumerator.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
import json
import math
from pathlib import Path
import time
import numpy as np
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_allin_protocol_v3 import AllinCache
from reboot_research_idle_v1 import idle
from hu_exhaustive_btn_response_20260923 import load_models

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'exhaustive-btn-response-v1'


def read(p):
    return json.loads(Path(p).read_text())


def classify(cards):
    first, second = cards
    r, s = first//4, second//4
    if r == s:
        return r*14
    high, low = max(r, s), min(r, s)
    return high*13+low if first % 4 == second % 4 else low*13+high


def main():
    began = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        now = time.monotonic()
        assert now-began < 900
        if now-last >= 2:
            assert idle(); last = now
    guard()
    regpath = OUT/f'{PREFIX}-registration.json'; result_path = OUT/f'{PREFIX}-result.json'
    reg, result = read(regpath), read(result_path); status = read(OUT/f'{PREFIX}-status.json')
    assert status['state'] == 'complete' and status['error'] is None and result['passed']
    assert result['registration_sha256'] == sha(regpath) and result['seconds'] < reg['maximum_seconds']
    assert reg['complete_played_models'] == 78 and reg['excluded_generation'] == 78
    for path, h in {**reg['inputs'], **result['artifacts']}.items():
        assert sha(path) == h, path
    context_path = OUT/'bb-context-candidate.json'; source = context_path.read_text(); context = json.loads(source)
    population = read(reg['population']); cache = AllinCache(reg['exact_cache'], reg['exact_cache_sha256'])
    assert population['context_sha256'] == sha(context_path)
    assert len(population['rows']) == len(cache.rows) == result['canonical_private_pairs'] == 47478
    assert population['physical_pairs'] == result['physical_private_pairs'] == 776650
    root = context['nodes'][0]; node = context['nodes'][root['children'][3]]
    folded, called = [context['nodes'][i] for i in node['children']]
    assert root['actor'] == 0 and node['actor'] == 1
    assert [a['kind'] for a in node['actions']] == ['fold', 'call']
    fold = folded['leaf']['utilities'][1]
    rake = called['pot']*context['rake_fraction']
    if context['rake_cap'] > 0:
        rake = min(rake, context['rake_cap'])
    catalog = read(reg['catalog'])['native_observations']
    checks = {}; maximum_error = 0.; conservation_error = 0.
    for name, item in result['candidates'].items():
        guard(); assert name in reg['candidates']
        policy = read(item['policy_artifact']); assert sha(item['policy_artifact']) == item['policy_sha256']
        assert policy['context_sha256'] == sha(context_path) and policy['played_generations'] == list(range(78))
        assert policy['excluded_generation'] == 78
        candidate_registration = read(OUT/f'{reg["candidates"][name]}-evaluation-v1-registration.json')
        assert policy['checkpoint'] == candidate_registration['checkpoint']
        models, CpuBank, _ = load_models(name, candidate_registration, source)
        bank = CpuBank(models, context_source=source)
        p, support = bank.average(dict(context_source=source, observations=[r['observation'] for r in catalog]), guard=guard)
        assert np.array_equal(support, np.full(265, 78.))
        policy_error = 0.
        for r, row in zip(catalog, p):
            c = r['hand_class']
            expected = policy['root_probabilities'][c] if r['player'] == 0 else [1-policy['btn_call_probabilities'][c], policy['btn_call_probabilities'][c], 0., 0.]
            policy_error = max(policy_error, float(np.max(abs(row-expected))))
        assert policy_error < 1e-12
        del models, bank
        entries = [[] for _ in range(169)]; reaches = [[] for _ in range(169)]; calls = [[] for _ in range(169)]
        for i, r in enumerate(population['rows']):
            if i % 2048 == 0:
                guard()
            h = r['private_cards']; label = cache.rows[tuple(h)]
            bb, btn = classify(h[:2]), classify(h[2:])
            weight = r['probability']; reach = weight*policy['root_probabilities'][bb][3]
            # Scalar reconstruction uses the separate payout for each outcome.
            # This also checks both players' cashflow conservation per pair.
            net = called['pot']-rake; boards = label['boards']; assert boards == 1712304
            call = (label['losses']*(-called['invested'][1]+net)
                    + label['wins']*(-called['invested'][1])
                    + label['ties']*(-called['invested'][1]+net/2))/boards
            bb_call = (label['wins']*(-called['invested'][0]+net)
                       + label['losses']*(-called['invested'][0])
                       + label['ties']*(-called['invested'][0]+net/2))/boards
            conserved = called['pot']-sum(called['invested'])-rake
            conservation_error = max(conservation_error, abs(call+bb_call-conserved))
            entries[btn].append(weight); reaches[btn].append(reach); calls[btn].append(reach*call)
        entry = list(map(math.fsum, entries)); jam = list(map(math.fsum, reaches)); call = list(map(math.fsum, calls))
        baseline = []; chosen = []; folded_values = []; near_ties = []
        values = item['values']; assert len(values['classes']) == 169
        for c in range(169):
            prob = policy['btn_call_probabilities'][c]
            f = jam[c]*fold
            b = 0. if entry[c] == 0 else (1-prob)*f+prob*call[c]
            best = max(f, call[c]); action = -1 if jam[c] == 0 else int(call[c] > f)
            got = values['classes'][c]
            assert got['hand_class'] == c
            expected = dict(entry_probability=entry[c], jam_probability=jam[c],
                fold_value_per_entry=f, call_value_per_entry=call[c], baseline_value_per_entry=b,
                best_value_per_entry=best, gain_per_entry=best-b)
            for field, v in expected.items():
                maximum_error = max(maximum_error, abs(got[field]-v))
            if action != got['best_action']:
                assert jam[c] > 0 and abs(call[c]-f) < 1e-10
                near_ties.append(c)
            assert got['baseline_call_probability'] == (prob if entry[c] else None)
            baseline.append(b); chosen.append(best); folded_values.append(f)
        total = math.fsum(jam); base = math.fsum(baseline)
        expected_gains = dict(best=math.fsum(chosen)-base, always_fold=math.fsum(folded_values)-base, always_call=math.fsum(call)-base)
        for field, v in expected_gains.items():
            maximum_error = max(maximum_error, abs(values['gains_per_entry'][field]-v))
        maximum_error = max(maximum_error, abs(total-values['jam_probability']), abs(base-values['baseline_value_per_entry']))
        baseline_call = math.fsum(jam[c]*policy['btn_call_probabilities'][c] for c in range(169) if entry[c])/total if total else None
        selected_call = math.fsum(jam[c] for c in range(169) if values['classes'][c]['best_action'] == 1)/total if total else None
        if total:
            maximum_error = max(maximum_error, abs(baseline_call-values['baseline_call_given_jam']), abs(selected_call-values['best_call_given_jam']))
        else:
            assert values['baseline_call_given_jam'] is None and values['best_call_given_jam'] is None
        assert expected_gains['best'] >= -1e-10 and abs(math.fsum(entry)-1) < 1e-12
        checks[name] = dict(cpu_policy_rows_reconstructed=265, maximum_policy_error=policy_error,
            gains_per_entry=expected_gains, floating_point_near_tie_classes=near_ties)
    assert set(checks) == set(reg['candidates']) and maximum_error < 1e-9 and conservation_error < 1e-9
    change = checks['visible_302']['gains_per_entry']['best']-checks['combined_269']['gains_per_entry']['best']
    assert abs(change-result['best_response_gain_change_bb_per_entry']) < 1e-9
    for path, h in {**reg['inputs'], **result['artifacts']}.items():
        assert sha(path) == h, path
    guard()
    review = dict(passed=True, registration_sha256=sha(regpath), result_sha256=sha(result_path),
        reviewer_sha256=sha(Path(__file__)), candidates=checks,
        maximum_scalar_sum_error_bb=maximum_error, maximum_pair_cashflow_conservation_error_bb=conservation_error,
        seconds=time.monotonic()-began, production_modified=False, accuracy_qualified=False,
        scope='Complete scalar weighted-value and class-response reconstruction, all-pair cashflow checks and repeated complete-bank CPU policy lookup. Reuses separately audited population/equities; GPU and board enumeration are not repeated. No full-game convergence claim.')
    save(OUT/f'{PREFIX}-independent-review.json', review); print(json.dumps(review))


if __name__ == '__main__':
    main()
