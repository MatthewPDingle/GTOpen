"""Read-only replay audit of the conditional all-in fixed-policy control."""
import hashlib
import json
from pathlib import Path
import random
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-allin-evaluation-control-v1'
STORE = Path('S:/GTOpen-research') / PREFIX


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private_class(cards):
    return tuple(sorted(c//4 for c in cards)) + (cards[0] % 4 == cards[1] % 4,)


def main():
    started = time.monotonic()
    reg_path = OUT / f'{PREFIX}-registration.json'
    result_path = OUT / f'{PREFIX}-result.json'
    reg, result = read(reg_path), read(result_path)
    assert result['passed'] and result['registration_sha256'] == sha(reg_path)
    checked = {}
    for paths in (reg['inputs'], result['artifacts']):
        for name, digest in paths.items():
            assert sha(Path(name)) == digest, name
            checked[name] = digest
    records_path = STORE / 'paired-control-rows.json'
    records = read(records_path)
    assert len(records) == 6 * 16 * 16 == result['paired_profile_deals']
    by_key = {(r['replicate'], r['profile'], r['pair']): r for r in records}
    assert len(by_key) == len(records)
    # This audit deliberately does not import the control's correction helper.
    # It independently enumerates complete preflop action paths, then computes
    # the expected-minus-realized all-in cashflow from each leaf's investments.
    context = read(OUT / 'bb-context-candidate.json')
    rng = random.Random(reg['seed'])
    max_error = 0.0
    counts = 0
    for rep in range(reg['replicates']):
        folder = STORE / f'runout-{rep:02d}'
        old_batch, new_batch = read(folder/'batch-2.json'), read(folder/'batch-3.json')
        expected = [h + rng.sample([c for c in range(52) if c not in h], 5)
                    for h in reg['private_pairs']]
        assert old_batch['deals'] == new_batch['deals'] == expected
        assert len(new_batch['allin_counts']) == len(expected) == 16
        old_profiles, new_profiles = read(folder/'profiles-2.json'), read(folder/'profiles-3.json')
        assert old_profiles['profiles'] == new_profiles['profiles']
        assert old_profiles['context_source'] == new_profiles['context_source']
        assert old_profiles['batch_source'] == (folder/'batch-2.json').read_text()
        assert new_profiles['batch_source'] == (folder/'batch-3.json').read_text()
        old_result, new_result = read(folder/'sampled.json'), read(folder/'conditional.json')
        assert len(old_result['profiles']) == len(new_result['profiles']) == 6
        for profile, old, new in zip(old_profiles['profiles'], old_result['profiles'], new_result['profiles']):
            name = profile['name']
            assert name == old['name'] == new['name']
            assert len(old['deals']) == len(new['deals']) == 16
            lookup = {(int(r['hi'])-1, r['actor'], private_class([int(r['lo']) & 63, (int(r['lo']) >> 6) & 63])): r['probabilities']
                      for r in profile['policies'] if int(r['hi']) < 2**63}
            for i, deal in enumerate(expected):
                label = new_batch['allin_counts'][i]
                assert label['private_cards'] == deal[:4]
                assert label['boards'] == 1712304
                assert 0 <= label['wins'] + label['ties'] <= label['boards']
                equity = (label['wins'] + label['ties']/2) / label['boards']
                # Reconstruct all-in path coefficients and check that each
                # saved correction implies a legal sampled winner share.
                # The control already independently evaluates those winners;
                # this audit verifies saved accounting without rerunning it.
                paths = [(0, 1.0)]
                allin_ev_coeff = 0.0
                allin_mass = 0.0
                while paths:
                    index, reach = paths.pop()
                    node = context['nodes'][index]
                    if node['children']:
                        actor = node['actor']
                        key = private_class(deal[2*actor:2*actor+2])
                        p = lookup[index, actor, key]
                        paths.extend((child, reach*p[a]) for a, child in enumerate(node['children']))
                    elif node['leaf']['type'] == 'showdown':
                        assert node['leaf']['effective_stack'] == 0
                        pot = sum(node['invested']) + context['dead_money']
                        assert abs(pot - node['pot']) < 1e-10
                        rake = pot*context['rake_fraction']
                        if context['rake_cap'] > 0:
                            rake = min(rake, context['rake_cap'])
                        allin_ev_coeff += reach*(pot-rake)
                        allin_mass += reach
                row = by_key[rep, name, i]
                assert row['original'] == old['deals'][i]['values']
                assert row['conditional'] == new['deals'][i]['values']
                assert abs(allin_mass - row['allin_mass']) < 1e-12
                assert old['deals'][i]['expected_rake'] == new['deals'][i]['expected_rake']
                assert old['deals'][i]['terminal_mass'] == new['deals'][i]['terminal_mass']
                if allin_ev_coeff > 0:
                    sampled_share = equity-row['correction'][0]/allin_ev_coeff
                    assert min(abs(sampled_share-x) for x in (0, 0.5, 1)) < 1e-12
                    jam = by_key[rep, 'jam', i]
                    # The same two private hands and board must produce the
                    # same winner for all profiles that reach a preflop all-in.
                    jam_sign = np.sign(jam['correction'][0])
                    assert np.sign(row['correction'][0]) == jam_sign
                error = float(np.max(np.abs(np.array(row['original']) + row['correction'] - row['conditional'])))
                max_error = max(max_error, error)
                assert abs(sum(row['correction'])) < 1e-10
                if name in ('fold', 'call'):
                    assert allin_mass == 0 and row['original'] == row['conditional']
                counts += 1
    assert max_error < 1e-9
    recomputed = []
    for item in result['within_pair_variance']:
        name = item['profile']
        before = after = 0.0
        for pair in range(16):
            group = [by_key[rep, name, pair] for rep in range(16)]
            before += float(np.var([r['original'][0] for r in group], ddof=1))
            after += float(np.var([r['conditional'][0] for r in group], ddof=1))
            if name == 'jam':
                assert np.max(np.ptp([r['conditional'] for r in group], axis=0)) < 1e-10
        assert abs(before-item['sum_within_pair_variance_sampled']) < 1e-9
        assert abs(after-item['sum_within_pair_variance_conditional']) < 1e-9
        ratio = after/before if before else None
        assert (ratio is None and item['ratio'] is None) or abs(ratio-item['ratio']) < 1e-14
        recomputed.append(dict(profile=name, ratio=ratio))
    report = dict(passed=True, source_result_sha256=sha(result_path),
                  registration_sha256=sha(reg_path), reviewer_sha256=sha(Path(__file__)),
                  checked_file_count=len(checked), profile_deals_replayed=counts,
                  maximum_value_reconstruction_error_bb=max_error,
                  variance_ratios=recomputed, seconds=time.monotonic()-started,
                  scope='Saved-artifact replay, source hashes, chance replay, path mass, cashflow corrections and fixture variances. Does not rerun native binaries or re-enumerate all-in boards; does not validate learned-policy strength or population precision.',
                  production_modified=False)
    path = OUT / f'{PREFIX}-independent-review.json'
    assert not path.exists()
    path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
