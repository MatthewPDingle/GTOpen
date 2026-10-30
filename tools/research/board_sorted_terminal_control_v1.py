"""Independent dense-pair check of sorted fixed-river terminal arithmetic.

CPU-only; no policy updates, production access or training modifications.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from board_sorted_terminal_v2 import masses, values
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'


def main():
    began = time.perf_counter()
    exe = ROOT / 'target/release/examples/hu_board_hand_ranks_v1.exe'
    context = OUT / 'bb-context-candidate.json'
    sampler = PhysicalDeals(context.read_text(), mode='full_deck', seed=0)
    indices = {tuple(h): i for i, h in enumerate(PAIRS)}
    rng = np.random.default_rng(9279401)
    rows = []
    for board in ([0, 5, 10, 15, 20], [48, 49, 50, 0, 4],
                  [0, 4, 8, 12, 16], [32, 36, 40, 44, 48]):
        native = json.loads(subprocess.check_output([str(exe), *map(str, board)],
                           creationflags=subprocess.CREATE_NO_WINDOW))
        assert native['larger_rank_is_stronger'] and native['board'] == list(board)
        h = np.array([x['hand'] for x in native['rows']], dtype=np.int64)
        ranks = np.array([x['rank'] for x in native['rows']], dtype=np.int64)
        assert len(h) == 1081 and not np.isin(h, board).any()
        if board[0] == 32:
            assert len(np.unique(ranks)) == 1, 'Royal-flush board must play for every hand'
        # Independent reference: enumerate every pair, explicitly exclude any
        # shared card, then compare the native strengths. No prefix formulas.
        compatible = (h[:, None, 0] != h[None, :, 0]) & (h[:, None, 0] != h[None, :, 1])
        compatible &= (h[:, None, 1] != h[None, :, 0]) & (h[:, None, 1] != h[None, :, 1])
        masks = dict(valid=compatible, win=compatible & (ranks[:, None] > ranks[None, :]),
                     lose=compatible & (ranks[:, None] < ranks[None, :]),
                     tie=compatible & (ranks[:, None] == ranks[None, :]))
        matrices = {k: v.astype(np.float64) for k, v in masks.items()}
        ids = np.array([indices[tuple(x)] for x in h])
        single = np.zeros(len(h)); single[123] = 1.
        variants = dict(uniform=np.ones(len(h)), random=rng.random(len(h)),
                        bb=sampler.weights[0, ids], btn=sampler.weights[1, ids],
                        single=single, zero=np.zeros(len(h)))
        for name, reach in variants.items():
            started = time.perf_counter()
            actual = masses(h, ranks, h, ranks, reach)
            compact_seconds = time.perf_counter() - started
            started = time.perf_counter()
            expected = {k: matrix @ reach for k, matrix in matrices.items()}
            dense_seconds = time.perf_counter() - started
            error = max(float(np.max(np.abs(actual[k] - expected[k]))) for k in masks)
            payout_error = float(np.max(np.abs(values(actual, 97.3, -101.2, -1.7) -
                (97.3 * expected['win'] - 101.2 * expected['lose'] - 1.7 * expected['tie']))))
            fold_error = float(np.max(np.abs(-7.5 * actual['valid'] + 7.5 * expected['valid'])))
            assert error < 1e-9 and payout_error < 1e-7 and fold_error < 1e-8
            assert np.max(np.abs(actual['win'] + actual['lose'] + actual['tie'] - actual['valid'])) < 1e-9
            if name == 'single':
                assert actual['valid'][123] == 0., 'A hand cannot face itself'
            # Unequal/reordered lists are supported, including zero-weight omission.
            hero_ids = np.arange(0, len(h), 7)[::-1]
            opp_ids = np.flatnonzero(reach)[::-1]
            subset = masses(h[hero_ids], ranks[hero_ids], h[opp_ids], ranks[opp_ids], reach[opp_ids])
            subset_error = max(float(np.max(np.abs(subset[k] - expected[k][hero_ids]))) for k in masks)
            assert subset_error < 1e-9
            rows.append(dict(board=board, reach=name, mass_error=error, payout_error=payout_error,
                             fold_error=fold_error, subset_error=subset_error,
                             compact_seconds=compact_seconds, dense_multiply_seconds=dense_seconds))
    h = np.array([[0, 1], [2, 3]]); ranks = np.array([1, 2]); reach = np.ones(2)
    bad = [((h, ranks, h, ranks, [-1., 1.]), 'negative reach'),
           ((h, ranks, h, ranks, [float('nan'), 1.]), 'nonfinite reach'),
           ((h, ranks, h, ranks, [1.]), 'reach length'),
           ((h, ranks, h, [1, 3], reach), 'inconsistent shared rank'),
           ((h, [-1, 2], h, ranks, reach), 'negative rank'),
           ((h[:, ::-1], ranks, h, ranks, reach), 'reversed cards'),
           ((np.array([[0, 1], [0, 1]]), ranks, h, ranks, reach), 'duplicate hand'),
           ((np.array([[0, 52], [2, 3]]), ranks, h, ranks, reach), 'illegal card'),
           ((h.astype(float), ranks, h, ranks, reach), 'noninteger cards'),
           ((h, ranks[:1], h, ranks, reach), 'rank length')]
    rejected = []
    for args, name in bad:
        try: masses(*args)
        except ValueError: rejected.append(name)
        else: raise AssertionError(name)
    paths = [Path(__file__), exe, context, ROOT / 'crates/solver/examples/hu_board_hand_ranks_v1.rs',
             ROOT / 'crates/solver/src/evaluator.rs',
             *[ROOT / 'tools/research' / f for f in ('board_sorted_terminal_v1.py',
                'board_sorted_terminal_v2.py', 'sampled_physical_deals_v1.py',
                'storage_strategic_common_prior_20260920.py')]]
    result = dict(passed=True, fixtures=rows, rejected=rejected, seconds=time.perf_counter() - began,
                  inputs={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                  gpu_used=False, training_changed=False, production_modified=False,
                  scope='Fixed-river terminal arithmetic only; not full tree propagation, chance integration, range accuracy or whole-solver performance.')
    with (OUT / 'board-sorted-terminal-control-v1-result.json').open('x') as f:
        json.dump(result, f, separators=(',', ':'), allow_nan=False)
    print(json.dumps(dict(passed=True, fixtures=len(rows), rejected=len(rejected),
                         max_mass_error=max(r['mass_error'] for r in rows), seconds=result['seconds'])))


if __name__ == '__main__': main()
