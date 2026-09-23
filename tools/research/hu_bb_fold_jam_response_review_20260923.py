"""Independent scalar reconstruction of the restricted BB response gain."""
import json
import math
from pathlib import Path
import time
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_allin_protocol_v3 import AllinCache
from reboot_research_idle_v1 import idle

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'bb-fold-jam-response-v1'


def read(path):
    return json.loads(Path(path).read_text())


def classify(cards):
    a, b = cards
    high, low = max(a//4,b//4), min(a//4,b//4)
    return high*13+low if high == low or a%4 == b%4 else low*13+high


def main():
    began = time.monotonic(); assert idle()
    rp = OUT/f'{PREFIX}-registration.json'; result_path = OUT/f'{PREFIX}-result.json'
    reg, result = read(rp), read(result_path); status = read(OUT/f'{PREFIX}-status.json')
    assert result['passed'] and result['registration_sha256'] == sha(rp)
    assert status['state'] == 'complete' and status['error'] is None and result['seconds'] < 180
    for p, h in reg['inputs'].items():
        assert sha(p) == h, p
    sr, sreg = read(reg['source_result']), read(reg['source_registration'])
    population = read(sreg['population']); cache = AllinCache(sreg['exact_cache'], sreg['exact_cache_sha256'])
    assert len(population['rows']) == len(cache.rows) == 47478 and population['physical_pairs'] == 776650
    context = read(OUT/'bb-context-candidate.json'); root = context['nodes'][0]
    jam = context['nodes'][root['children'][3]]
    f, called = [context['nodes'][i] for i in jam['children']]
    fold_value = context['nodes'][root['children'][0]]['leaf']['utilities'][0]
    rake = called['pot']*context['rake_fraction']
    if context['rake_cap'] > 0:
        rake = min(rake, context['rake_cap'])
    net = called['pot']-rake; cost = called['invested'][0]
    checks = {}; max_error = 0.
    assert set(result['candidates']) == set(reg['candidates']) == {'combined_269', 'visible_302'}
    for name in reg['candidates']:
        policy = read(sr['candidates'][name]['policy_artifact'])
        masses = [[] for _ in range(169)]; returns = [[] for _ in range(169)]
        for i, row in enumerate(population['rows']):
            if i % 4096 == 0:
                assert idle() and time.monotonic()-began < 180
            h = row['private_cards']; bb, btn = classify(h[:2]), classify(h[2:])
            label = cache.rows[tuple(h)]; count = label['boards']
            assert label['wins']+label['ties']+label['losses'] == count == 1712304
            paid = (label['wins']*(net-cost)+label['ties']*(net/2-cost)-label['losses']*cost)/count
            pcall = policy['btn_call_probabilities'][btn]
            payoff = pcall*paid+(1-pcall)*f['leaf']['utilities'][0]
            masses[bb].append(row['probability']); returns[bb].append(row['probability']*payoff)
        gains = []; near_ties = []
        rows = result['candidates'][name]['classes']; assert [r['hand_class'] for r in rows] == list(range(169))
        for c, row in enumerate(rows):
            m, j = math.fsum(masses[c]), math.fsum(returns[c]); assert m > 0
            baseline = policy['root_probabilities'][c]; response = row['response']
            assert row['baseline'] == baseline and response[1:3] == baseline[1:3]
            assert all(math.isfinite(p) and p >= 0 for p in response) and abs(sum(response)-1) < 1e-12
            assert abs(response[0]+response[3]-baseline[0]-baseline[3]) < 1e-12
            qj = j/m; expected = (baseline[0]+baseline[3])*max(m*fold_value,j)-baseline[0]*m*fold_value-baseline[3]*j
            actual = (response[0]-baseline[0])*m*fold_value+(response[3]-baseline[3])*j
            max_error = max(max_error,abs(row['entry_probability']-m),abs(row['fold_value']-fold_value),
                abs(row['jam_value']-qj),abs(row['gain_per_entry']-expected),abs(actual-expected))
            if abs(qj-fold_value) > 1e-10:
                assert response[0 if qj>fold_value else 3] == 0.
            else:
                near_ties.append(c)
            assert expected >= -1e-10
            gains.append(expected)
        total = math.fsum(gains)
        max_error = max(max_error,abs(total-result['candidates'][name]['gain_bb_per_entry']))
        assert result['candidates'][name]['unchanged_call_raise'] is True
        assert result['candidates'][name]['positive_gain_classes'] == sum(r['gain_per_entry']>1e-10 for r in rows)
        checks[name] = dict(gain_bb_per_entry=total, scalar_classes_reconstructed=169, numerical_near_ties=near_ties)
    assert max_error < 1e-9
    for p,h in reg['inputs'].items():
        assert sha(p) == h, p
    assert idle() and time.monotonic()-began < 180
    review = dict(passed=True, registration_sha256=sha(rp), result_sha256=sha(result_path),
        reviewer_sha256=sha(Path(__file__)), candidates=checks, maximum_scalar_error_bb=max_error,
        seconds=time.monotonic()-began, production_modified=False, accuracy_qualified=False,
        scope='Scalar reconstruction over separately audited population/equities and policies; no new model inference, full-game bound or deployment qualification.')
    save(OUT/f'{PREFIX}-independent-review.json', review); print(json.dumps(review))


if __name__ == '__main__':
    main()
