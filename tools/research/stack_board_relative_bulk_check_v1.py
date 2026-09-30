"""Exact representation regression, separate from the live training control."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = Path('T:/Dev/GTOpen')
sys.path.insert(0, str(ROOT / 'tools/research'))
sys.path.insert(0, str(HERE))
from stack_board_relative_features_v1 import relative_features
from stack_board_relative_features_bulk_v1 import relative_features_bulk


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, separators=(',', ':'))
        stream.write('\n')


def main():
    name = HERE / 'stack-board-relative-bulk-check-v1'
    attempt, result, failure = (Path(str(name) + suffix + '.json') for suffix in ('-attempt', '-result', '-failure'))
    if any(path.exists() for path in (attempt, result, failure)):
        raise ValueError('Preserve existing implementation check')
    identities = {str(path): sha(path) for path in (Path(__file__), HERE / 'stack_board_relative_features_bulk_v1.py',
        ROOT / 'tools/research/stack_board_relative_features_v1.py',
        ROOT / 'tools/research/sampled_visible_poker_features_v1.py',
        ROOT / 'tools/research/visible_summaries_vector_v1.py')}
    save(attempt, dict(inputs=identities, label='Feature equivalence, not poker quality', random_seed=9302301))
    try:
        boards = [(0,5,14,27,44), (0,1,14,27,44), (0,1,14,15,44), (0,1,2,27,44),
                  (0,5,10,15,16), (0,8,20,32,44), (0,1,2,12,13), (0,1,2,3,44),
                  (0,4,8,12,16), (48,0,4,8,12)]
        rows = [[*hole, *board] for board in boards for hole in combinations([c for c in range(52) if c not in board], 2)]
        rng = np.random.Generator(np.random.PCG64(9302301))
        rows.extend(rng.choice(52, 7, replace=False).tolist() for _ in range(8192))
        cards = np.asarray(rows, dtype=np.int16)
        before = time.perf_counter()
        reference = np.array([relative_features(row[:2], row[2:]) for row in rows])
        reference_seconds = time.perf_counter() - before
        before = time.perf_counter()
        actual = relative_features_bulk(cards)
        bulk_seconds = time.perf_counter() - before
        if not np.array_equal(reference, actual) or reference.dtype != actual.dtype:
            raise ValueError('Feature bytes disagree with scalar reference')
        reordered = cards.copy()
        reordered[:, :2] = reordered[:, :2][:, ::-1]
        reordered[:, 2:] = reordered[:, 2:][:, ::-1]
        if not np.array_equal(relative_features_bulk(reordered), reference):
            raise ValueError('Card-order invariance changed')
        if relative_features_bulk(np.empty((0, 7), dtype=np.int16)).shape != (0, 25):
            raise ValueError('Empty batch shape')
        bad = [cards[:1].astype(float), cards[:1].astype(bool), cards[:1, :6],
               np.array([[-1,1,2,3,4,5,6]]), np.array([[0,1,2,3,4,5,52]]),
               np.array([[0,0,2,3,4,5,6]])]
        for value in bad:
            try:
                relative_features_bulk(value)
            except ValueError:
                pass
            else:
                raise ValueError('Malformed visible input was accepted')
        for path, expected in identities.items():
            if sha(path) != expected:
                raise ValueError('Implementation source changed')
        report = dict(passed=True, rows=len(rows), board_categories=sorted(set(np.argmax(actual[:, :9], axis=1).tolist())),
            exact_float32_equality=True, card_order_invariant=True, malformed_cases_rejected=len(bad),
            reference_seconds=reference_seconds, bulk_seconds=bulk_seconds,
            measured_ratio=reference_seconds/bulk_seconds, training_pipeline_modified=False,
            scope='One CPU feature microbenchmark; no end-to-end speedup or poker-quality claim', inputs=identities)
        save(result, report)
        print(json.dumps(report), flush=True)
    except BaseException as error:
        save(failure, dict(error=repr(error), traceback=traceback.format_exc()))
        raise


if __name__ == '__main__':
    main()
