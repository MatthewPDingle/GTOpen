"""Nonuniform chance-weight controls on completed development workers only."""
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
import continuation_transfer_aggregate as a

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'


def main():
    paths = [ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json',
             ROOT/'research/preflop-evolution/integrated-coverage-20260919/old-two-orbits-result.json',
             OUT/'transfer-v3-streamed-two-0-result.json', OUT/'transfer-v3-streamed-two-1-result.json']
    subtree, source, *workers = map(a.read, paths)
    manifest = dict(suit_orbits=True, bet_menu='50',
                    boards=[dict(board=w['boards'][0], weight=q) for w,q in zip(workers,[1,3])])
    result = a.aggregate(subtree, manifest, source, workers)
    scaled = copy.deepcopy(manifest)
    for row in scaled['boards']:
        row['weight'] *= 95
    scale_result = a.aggregate(subtree, scaled, source, workers[::-1])
    e = result['records'][-1]['evaluation']
    other = scale_result['records'][-1]['evaluation']
    scalar_errors = {key:float(np.max(abs(np.asarray(e[key])-other[key]))) for key in
                     ['ev','gaps','postflop_gaps','root_frequencies','expected_rake','terminal_probability']}
    assert max(scalar_errors.values()) < 1e-12
    assert a.policy_bits(e['preflop_policy']) == a.policy_bits(source['records'][-1]['evaluation']['preflop_policy'])
    chance = np.array([.25,.75])
    z = np.array([w['root_normalizer'] for w in workers])
    conditional = chance*z/(chance@z)
    assert abs(result['root_normalizer']-chance@z) < 1e-8
    expected_ev = conditional@np.array([w['records'][-1]['evaluation']['ev'] for w in workers])
    ev_error = float(max(abs(expected_ev-e['ev'])))
    assert ev_error < 1e-8
    naive_ev = chance@np.array([w['records'][-1]['evaluation']['ev'] for w in workers])
    # Giving each preflop decision advance knowledge of the flop cannot
    # yield less value than maximizing after hiding/averaging that flop.
    clairvoyant = conditional@np.array([w['records'][-1]['evaluation']['best_response'] for w in workers])
    assert np.all(np.asarray(e['best_response']) <= clairvoyant+1e-8)
    for corrupted in [workers[:1], [workers[0],workers[0]]]:
        try:
            a.aggregate(subtree, manifest, source, corrupted)
        except AssertionError:
            pass
        else:
            raise AssertionError('Missing/duplicate development board was accepted')
    output = OUT/'weighted-transfer-controls.json'
    assert not output.exists()
    inputs = [Path(__file__), Path(a.__file__), *paths]
    summary = dict(passed=True, chance_weights=chance.tolist(),
        private_conditioned_weights=conditional.tolist(), scalar_scale_and_order_errors=scalar_errors,
        independently_weighted_ev_error=ev_error, naive_chance_only_ev_error=float(max(abs(naive_ev-e['ev']))),
        hidden_chance_best_response=e['best_response'], invalid_clairvoyant_upper_bound=clairvoyant.tolist(),
        missing_and_duplicate_boards_rejected=True, accounting=result['independent_accounting'],
        inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        note='CPU-only weighting controls using completed two-board development data. No new strategic solve or reserved outcome accessed.')
    output.write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k != 'inputs_sha256'}, indent=2))


if __name__ == '__main__':
    main()
