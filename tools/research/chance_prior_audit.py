"""Chance-only private-prior audit; never reads reserved strategic outcomes."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import integrated_coverage as c
from independent_validation_panel import signature

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
DEV = c.OUT


def main():
    tree_path = ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
    fixtures_path = c.s.OUT/'fixtures.json'
    paths = {'two': DEV/'old-two-orbits.json', 'ten': DEV/'panel-ab.json',
             'report47': OUT/'report-47.json', 'reserved10': DEV/'reserved.json',
             'validation95': OUT/'validation-95.json'}
    manifests = {k: c.s.read(p) for k, p in paths.items()}
    tree = c.s.read(tree_path)
    weights = np.array(tree['incoming_class_mass'])[:, c.CLASSES]/c.COUNTS[c.CLASSES]
    weights /= weights.max(1)[:, None]
    weights[weights < 1e-5] = 0
    ix = [np.flatnonzero(w) for w in weights]
    masks = [c.MASKS[x] for x in ix]
    classes = [c.CLASSES[x] for x in ix]
    compatible = (masks[0][:, None] & masks[1][None, :]) == 0
    base = weights[0, ix[0]][:, None]*weights[1, ix[1]][None, :]*compatible
    full = base/base.sum()
    cache = {}

    def orbit_legal(board):
        if board not in cache:
            chance = np.zeros_like(base)
            for perm in c.PERMS:
                board_mask = np.uint64(sum(1 << x for x in c.cards(c.relabel(board, perm))))
                legal = [(m & board_mask) == 0 for m in masks]
                chance += legal[0][:, None]*legal[1][None, :]/24
            cache[board] = chance
        return cache[board]

    def panel_joint(manifest):
        assert manifest['suit_orbits'] is True
        total = sum(b['weight'] for b in manifest['boards'])
        return base*sum(b['weight']*orbit_legal(b['board']) for b in manifest['boards'])/total

    excluded = {signature(b['board']) for k in ['two', 'ten', 'report47', 'reserved10']
                for b in manifests[k]['boards']}
    boards = c.s.read(fixtures_path)['canonical_flops']
    total_physical = sum(m for _, m in boards)
    assert total_physical == math.comb(52, 3)
    blocked = [(b, m) for b, m in boards if signature(b) in excluded]
    eligible_count = total_physical-sum(m for _, m in blocked)
    assert eligible_count == 21100
    # Every compatible four-card private deal permits exactly C(48,3) flops.
    # Subtract complete excluded orbits to obtain the eligible validation
    # population exactly, without iterating all 22,100 physical flops.
    eligible_legal = (np.full_like(base, math.comb(48, 3))-
                      sum(m*orbit_legal(b) for b, m in blocked))/eligible_count
    assert eligible_legal[compatible].min() >= 0 and eligible_legal[compatible].max() <= 1
    eligible_raw = base*eligible_legal
    eligible = eligible_raw/eligible_raw.sum()

    def compare(joint, target):
        p = joint/joint.sum()
        class_rows = []
        for seat in range(2):
            a = np.bincount(classes[seat], weights=p.sum(1-seat), minlength=169)
            b = np.bincount(classes[seat], weights=target.sum(1-seat), minlength=169)
            class_rows.append(dict(tv=float(abs(a-b).sum()/2),
                                   maximum_share_error_pp=float(abs(a-b).max()*100)))
        return dict(joint_tv=float(abs(p-target).sum()/2), seats=class_rows,
                    target_mass_absent=float(target[p == 0].sum()))

    rows = []
    for name, manifest in manifests.items():
        joint = panel_joint(manifest)
        target = eligible if name == 'validation95' else full
        row = dict(panel=name, target='eligible complement' if name == 'validation95' else 'full deck',
                   canonical_boards=len(manifest['boards']), normalizer=float(joint.sum()),
                   versus_target=compare(joint, target), versus_full_deck=compare(joint, full))
        if name == 'report47':
            # This inspects only the independently computed normalizer from
            # the already-running development solve, never reserved outcomes.
            initial = c.s.read(OUT/'report47-full-result.json')
            assert abs(initial['root_normalizer']/joint.sum()-1) < 1e-7
            row['independent_runtime_normalizer_agrees'] = True
        rows.append(row)
    earlier_path = DEV/'coverage-audit.json'
    earlier = c.s.read(earlier_path)['panels']
    agreement = {}
    for name, old_name in [('two', 'old-two-orbits'), ('ten', 'panel-ab')]:
        current = next(r for r in rows if r['panel'] == name)
        error = abs(current['versus_full_deck']['joint_tv']-earlier[old_name]['joint_prior_tv'])
        assert error < 1e-12
        agreement[name] = error
    result = dict(eligible_physical_flops=eligible_count, full_physical_flops=total_physical,
                  supported_private_combinations=[len(x) for x in ix],
                  agreement_with_prior_dense_enumeration=agreement,
                  eligible_population_vs_full=compare(eligible, full), panels=rows,
                  note='Chance-only exact enumeration over supported private pairs and all suit relabelings. No reserved strategy outcomes read. Total variation measures changed probability mass, not strategy error or EV loss. Small prior distortion cannot establish adequate rank, draw or value coverage.',
                  inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in [Path(__file__), tree_path, fixtures_path, earlier_path, *paths.values()]})
    output = OUT/'chance-private-prior-audit.json'
    assert not output.exists()
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'inputs_sha256'}, indent=2))


if __name__ == '__main__':
    main()
