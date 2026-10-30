"""Combine frozen-policy leaf CFVs before taking any preflop best response.

SUBTREE MANIFEST SOURCE OUTPUT BOARD_RESULT... . Board results may be gzip.
The chance sample is fixed by MANIFEST; missing/duplicate boards are rejected.
"""
import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys
import numpy as np
import integrated_coverage as coverage
import integrated_coverage_review as review


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def policy_bits(policy):
    return b''.join(struct.pack('<d', v) for node in policy for row in node for v in row)


def aggregate(subtree, manifest, source, workers):
    assert manifest['suit_orbits'] is True and source['suit_orbits'] is True
    assert manifest['bet_menu'] == source['manifest']['bet_menu'] == '50'
    assert source['entry_cutoff'] == 1e-5
    assert subtree['config']['rake_pct'] == 4 and subtree['config']['rake_cap'] == 6
    nodes = subtree['nodes']
    frozen = source['records'][-1]['evaluation']['preflop_policy']
    assert len(nodes) == len(frozen)
    sigma = [np.asarray(x) for x in frozen]
    for n, s in zip(nodes, sigma):
        assert np.all(np.isfinite(s)) and np.all((s >= 0) & (s <= 1))
        if n['kind'] == 0:
            assert s.shape == (len(n['children']), 1326)
            assert np.max(abs(s.sum(0) - 1)) < 1e-10
        else:
            assert s.size == 0
    expected = [b['board'] for b in manifest['boards']]
    assert len(set(expected)) == len(expected) == len(workers)
    by_board = {}
    for worker in workers:
        assert len(worker['boards']) == 1
        board = worker['boards'][0]
        assert board not in by_board and board in expected
        assert worker['manifest']['boards'][0]['board'] == board
        assert worker['manifest']['suit_orbits'] is True and worker['suit_orbits'] is True
        assert worker['manifest']['bet_menu'] == manifest['bet_menu']
        assert worker['entry_cutoff'] == 1e-5 and worker['preflop_unchanged'] is True
        assert worker['terminal_values'] is not None
        for record in worker['records']:
            assert policy_bits(record['evaluation']['preflop_policy']) == policy_bits(frozen)
        by_board[board] = worker
    iterations = {w['records'][-1]['iteration'] for w in workers}
    assert len(iterations) == 1
    chance = np.array([b['weight'] for b in manifest['boards']], dtype=float)
    assert np.all(np.isfinite(chance)) and np.all(chance > 0)
    chance /= chance.sum()
    weights = np.array(subtree['incoming_class_mass'])[:, coverage.CLASSES] / coverage.COUNTS[coverage.CLASSES]
    weights /= weights.max(1)[:, None]
    weights[weights < 1e-5] = 0
    leaves = np.zeros((4, len(nodes), 1326))
    root_mass = np.zeros(1326)
    z = rake = probability = seconds = 0.
    # This scalar is an independent average of local postflop deviation gains;
    # unlike a preflop best response it may be summed across known flops.
    independent_post_gaps = np.zeros(2)
    for board, weight in zip(expected, chance):
        w = by_board[board]
        e = w['records'][-1]['evaluation']
        values = w['terminal_values']['values']
        assert len(values) == 4 and all(len(v) == len(nodes) for v in values)
        for k in range(4):
            for i, n in enumerate(nodes):
                v = np.asarray(values[k][i])
                if n['kind'] == 0:
                    assert v.size == 0
                else:
                    assert v.shape == (1326,) and np.all(np.isfinite(v))
                    leaves[k, i] += weight * v
        mass = np.asarray(w['terminal_values']['root_opponent_mass'])
        assert mass.shape == (1326,) and np.all(np.isfinite(mass))
        assert abs(mass @ weights[0] / w['root_normalizer'] - 1) < 1e-10
        root_mass += weight * mass
        raw_weight = weight * w['root_normalizer']
        z += raw_weight
        rake += raw_weight * e['expected_rake']
        probability += raw_weight * e['terminal_probability']
        independent_post_gaps += raw_weight * np.array(e['independent_postflop_gaps'])
        seconds += w['records'][-1]['elapsed_seconds']

    def walk(p, i, post_br, pre_br):
        n = nodes[i]
        if n['kind'] != 0:
            return leaves[2 * p + int(post_br), i]
        children = np.array([walk(p, c, post_br, pre_br) for c in n['children']])
        if n['actor'] != p:
            return children.sum(0)  # opponent policy already in leaf reaches
        if pre_br:
            return children.max(0)  # only AFTER aggregation over hidden flops
        return (children * sigma[i]).sum(0)

    ev = np.array([walk(p, 0, False, False) @ weights[p] / z for p in range(2)])
    restricted = np.array([walk(p, 0, True, False) @ weights[p] / z for p in range(2)])
    best = np.array([walk(p, 0, True, True) @ weights[p] / z for p in range(2)])
    post_gaps = restricted - ev
    independent_post_gaps /= z
    assert max(abs(post_gaps - independent_post_gaps)) < 1e-5
    assert np.all(best >= restricted - 1e-5) and np.all(restricted >= ev - 1e-5)
    # A further independent scalar check for the fixed policy's average EV.
    weighted_ev = sum(q * by_board[b]['root_normalizer'] * np.array(by_board[b]['records'][-1]['evaluation']['ev']) for b, q in zip(expected, chance)) / z
    assert max(abs(ev - weighted_ev)) < 1e-8
    prior = root_mass * weights[0] / z
    freq = sigma[0] @ prior
    hands = []
    for cls in range(169):
        mask = coverage.CLASSES == cls
        mass = prior[mask].sum()
        actions = sigma[0][:, mask] @ prior[mask] / mass if mass > 0 else np.zeros(4)
        row, col = divmod(cls, 13)
        label = '23456789TJQKA'[max(row,col)]+'23456789TJQKA'[min(row,col)]+('' if row==col else 's' if row>col else 'o')
        hands.append(dict(hand=label, root_mass=float(mass), strategy=actions.tolist()))
    gaps = best - ev
    evaluation = dict(ev=ev.tolist(), best_response=best.tolist(), gaps=gaps.tolist(), gap_total=float(gaps.sum()),
                      postflop_gaps=post_gaps.tolist(), postflop_gap_total=float(post_gaps.sum()),
                      independent_postflop_gaps=independent_post_gaps.tolist(), root_frequencies=freq.tolist(),
                      hands=hands, preflop_policy=frozen, terminal_probability=probability/z,
                      expected_rake=rake/z, conservation_error=abs(ev.sum()+rake/z-3.5))
    result = dict(manifest=manifest, boards=expected, board_weights=chance.tolist(), suit_orbits=True,
                  preflop_unchanged=True, root_normalizer=z, entry_cutoff=1e-5,
                  records=[dict(iteration=iterations.pop(), elapsed_seconds=seconds, evaluation=evaluation)],
                  note='Frozen-policy transfer. Leaf CFVs aggregated before preflop maximization; summed worker time, not batch wall time. Earlier folded cards omitted.')
    result['independent_accounting'] = review.audit_result(result)
    return result


def main():
    subtree_path, manifest_path, source_path, output, *worker_paths = sys.argv[1:]
    output = Path(output)
    assert not output.exists()
    result = aggregate(read(subtree_path), read(manifest_path), read(source_path), [read(p) for p in worker_paths])
    result['frozen_preflop_source'] = source_path
    result['inputs_sha256'] = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in [subtree_path, manifest_path, source_path, *worker_paths]}
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result['independent_accounting']))


if __name__ == '__main__':
    main()
