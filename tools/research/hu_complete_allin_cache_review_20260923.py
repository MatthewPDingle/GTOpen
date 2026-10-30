"""Independent coverage/orbit reconstruction and saved exact-label audit.

Does not rerun billions of board evaluations: audits the native artifacts,
reused reviewed caches, conservation and independently scored sample boards.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
import itertools
import json
import math
from pathlib import Path
import time
import numpy as np
from sampled_allin_protocol_v3 import AllinCache, BOARDS
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown
from reboot_research_idle_v1 import idle

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'complete-private-allin-cache-v1'


def read(path):
    return json.loads(Path(path).read_text())


def main():
    began = time.monotonic()
    def guard():
        assert time.monotonic()-began < 900 and idle()
    guard()
    regpath = OUT / f'{PREFIX}-registration.json'; result_path = OUT / f'{PREFIX}-result.json'
    reg, result = read(regpath), read(result_path)
    status = read(OUT / f'{PREFIX}-status.json')
    assert status['state'] == 'complete' and status['error'] is None
    assert result['passed'] and result['registration_sha256'] == sha(regpath)
    assert result['seconds'] < reg['maximum_seconds']
    for p, h in reg['inputs'].items():
        assert sha(p) == h, p
    assert sha(result['builder_result']) == result['builder_result_sha256']
    built = read(result['builder_result']); folder = Path(result['builder_result']).parent
    assert built['passed'] and built['registration_sha256'] == sha(folder / 'registration.json')
    for p, h in built['artifacts'].items():
        assert sha(p) == h, p
    for p, h in read(folder / 'registration.json')['inputs'].items():
        assert sha(p) == h, p
    cache = AllinCache(result['cache_artifact'], result['cache_sha256'])
    base = AllinCache(reg['base_union'], reg['base_union_sha256'])
    original = AllinCache(reg['reviewed_base_cache'], reg['reviewed_base_sha256'])
    extra = AllinCache(reg['reviewed_additional_cache'], reg['reviewed_additional_sha256'])
    union = dict(original.rows)
    for key, row in extra.rows.items():
        if key in union:
            assert union[key] == row
        union[key] = row
    population = read(reg['population']); context_path = OUT / 'bb-context-candidate.json'
    assert population['context_sha256'] == sha(context_path)
    context = read(context_path)
    # Independently rebuild physical private support without PhysicalDeals or
    # the planner's vectorized suit-orbit grouping. Reproduce the frozen cutoff.
    pairs = list(itertools.combinations(range(52), 2))
    classes = [hand_class(list(p)) for p in pairs]
    counts = [classes.count(c) for c in range(169)]
    weights = np.array([[m[c]/counts[c] for c in classes] for m in context['incoming_class_mass']])
    weights /= weights.max(axis=1)[:, None]; weights[weights < 1e-5] = 0
    masks = np.array([(1 << a) | (1 << b) for a, b in pairs], dtype=np.uint64)
    compatible = (masks[:, None] & masks[None, :]) == 0
    joint = weights[0, :, None] * weights[1, None, :] * compatible
    total = float(joint.sum()); physical = int(np.count_nonzero(joint))
    lookup = {p: i for i, p in enumerate(pairs)}
    permutations = list(itertools.permutations(range(4)))
    seen = set(); represented = 0; maximum_mass_error = 0.
    for i, row in enumerate(population['rows']):
        if i % 1024 == 0:
            guard()
        h = tuple(row['private_cards'])
        orbit = {tuple(sorted(4*(c//4)+p[c%4] for c in h[:2]) + sorted(4*(c//4)+p[c%4] for c in h[2:])) for p in permutations}
        assert h == min(orbit) and h not in seen and len(set(h)) == 4
        seen.add(h)
        assert row['physical_pairs'] == len(orbit)
        # Suit relabelling preserves both classes and the uniform per-combo
        # incoming weights. Distinct canonical orbits cannot overlap.
        a, b = lookup[h[:2]], lookup[h[2:]]
        assert joint[a, b] > 0 and h in cache.rows
        expected = len(orbit) * joint[a, b] / total
        maximum_mass_error = max(maximum_mass_error, abs(expected-row['probability']))
        represented += len(orbit)
    assert represented == physical == population['physical_pairs'] == reg['physical_private_pairs']
    assert seen == set(cache.rows) and len(seen) == reg['canonical_private_pairs']
    assert maximum_mass_error < 1e-12 and abs(math.fsum(r['probability'] for r in population['rows'])-1) < 1e-12
    keys = sorted(seen); missing = [k for k in keys if k not in base.rows]
    assert base.rows == {k: union[k] for k in keys if k in union}
    assert built['base_sha256'] == base.sha256
    assert sha(folder / 'source-deals.json') == built['source_sha256']
    deals = read(folder / 'source-deals.json')
    assert len(deals) == len(population['rows'])
    for deal, row in zip(deals, population['rows']):
        assert deal[:4] == row['private_cards'] and len(deal) == len(set(deal)) == 9
    assert read(folder / 'keys.json') == [list(k) for k in keys]
    assert len(missing) == reg['new_keys'] == built['new_keys']
    for key in seen & base.rows.keys():
        assert cache.rows[key] == base.rows[key]
    native_seconds = 0.; reconstructed = []
    for offset in range(0, len(missing), 20):
        guard()
        inp = read(folder / f'input-{offset:06d}.json'); native = read(folder / f'native-{offset:06d}.json')
        assert len(inp['cases']) == len(native) == len(missing[offset:offset+20])
        for key, case, row in zip(missing[offset:offset+20], inp['cases'], native):
            assert list(key) == case['private_cards'] == row['private_cards']
            expected = dict(private_cards=list(key), wins=row['wins'], ties=row['ties'], losses=row['losses'], boards=row['exact_boards'])
            assert cache.rows[key] == expected and row['exact_boards'] == BOARDS
            assert row['equity'] == (row['wins'] + .5*row['ties'])/BOARDS
            scores = []
            for board in case['sampled_boards']:
                outcome = showdown(list(key)+board)
                scores.append(1 if outcome < 0 else 2 if outcome == 0 else 0)
            assert row['sampled_scores'] == scores
            native_seconds += row['exact_seconds']; reconstructed.append(key)
    assert reconstructed == missing and abs(native_seconds-result['native_seconds']) < 1e-8
    review = dict(passed=True, registration_sha256=sha(regpath), result_sha256=sha(result_path),
        reviewer_sha256=sha(Path(__file__)), cache_artifact=result['cache_artifact'], cache_sha256=cache.sha256,
        canonical_private_pairs=len(seen), physical_private_pairs=physical,
        independently_reconstructed_probability_error=maximum_mass_error,
        reused_reviewed_keys=len(seen)-len(missing), new_native_keys=len(missing),
        complete_board_count_per_pair=BOARDS, seconds=time.monotonic()-began, production_modified=False,
        scope='Complete private support and suit-orbit probability reconstruction, cache reuse equality, native artifact reconstruction and independent sample-board scoring. Does not rerun exhaustive board enumeration or qualify any policy.')
    save(OUT / f'{PREFIX}-independent-review.json', review); print(json.dumps(review))


if __name__ == '__main__':
    main()
