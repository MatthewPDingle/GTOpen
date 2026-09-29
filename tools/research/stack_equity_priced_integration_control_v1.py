"""One registered synthetic GPU integration control, without poker fitting."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import copy
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import torch
import stack_equity_priced_comparison_v1 as compare
from test_stack_equity_priced_comparison_v1 import fixture
from stack_price_learning_fit_v1 import Dataset as LegacyDataset
from stack_board_balanced_metrics_v1 import reference_context, compare_evaluations, evaluation_summary
from river_matched_training_pilot_v1 import ROOT, OUT, available, LOCK, OTHER, sha, verify
from bounded_parallel_evaluation_archive_v2 import production_available
from board_prefix_publication_v1 import atomic_json

NAME = 'stack-equity-priced-integration-control-v1'
REG, ATTEMPT, RESULT, FAILURE = (OUT / (NAME + s + '.json')
                                for s in ('-registration', '-attempt', '-result', '-failure'))


def main():
    assert not any(p.exists() for p in (REG, ATTEMPT, RESULT, FAILURE, LOCK, OTHER))
    ready, probe = available()
    if not ready:
        print(json.dumps(dict(deferred=True, probe=probe)))
        return
    paths = [Path(__file__).resolve(), Path(compare.__file__).resolve()]
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix == '.py':
            paths.append(Path(path))
    spec = dict(inputs={str(p): sha(p) for p in paths}, seeds=[9297501, 9297502],
                batch_sizes=[31, 8192], arms=list(compare.ARMS), maximum_seconds=180,
                maximum_cuda_bytes=512_000_000, absolute_raw_tolerance=2e-12,
                synthetic_boards=2, synthetic_contexts=2, synthetic_states=5,
                scientific_training=False, poker_labels=False, precision='widened-float64')
    atomic_json(REG, spec)
    with LOCK.open('x') as f:
        f.write(str(os.getpid()))
    started = time.monotonic()
    try:
        atomic_json(ATTEMPT, dict(pid=os.getpid(), process_created=psutil.Process().create_time(),
                                registration_sha256=sha(REG), admission=probe))
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(spec['maximum_cuda_bytes'] / torch.cuda.get_device_properties(0).total_memory)

        def guard():
            assert time.monotonic() - started < spec['maximum_seconds']
            assert not OTHER.exists() and production_available()
            assert psutil.virtual_memory().available > 24_000_000_000
            assert torch.cuda.memory_reserved() < spec['maximum_cuda_bytes']

        boards, contexts, data = fixture('cuda')
        old = LegacyDataset(boards, contexts)
        records, checks = [], []
        for seed in spec['seeds']:
            a, b = (torch.Generator(device='cuda').manual_seed(seed) for _ in range(2))
            for n in spec['batch_sizes']:
                guard()
                batch = data.sample(n, a)
                legacy = old.sample(n, 387, b)
                assert all(torch.equal(batch[key], value) for key, value in zip(('x', 'actors', 'target'), legacy))
                assert torch.equal(a.get_state(), b.get_state())
                for arm in compare.ARMS:
                    model = compare.fresh(seed, arm)
                    with torch.no_grad():
                        for p in model.parameters():
                            p.add_(.013)
                    wide = copy.deepcopy(model).to(device='cuda', dtype=torch.float64)
                    raw = compare.predict(wide, arm, batch).detach().cpu().numpy()
                    reference = compare.numpy_scores(compare.arrays(model, arm), arm,
                                                     batch['x'].cpu().numpy(), batch['economics'].cpu().numpy())
                    error = float(np.max(np.abs(raw - reference)))
                    records.append(dict(seed=seed, arm=arm, rows=n, maximum_raw_error=error))
                    assert error <= spec['absolute_raw_tolerance'], records[-1]
                    del wide
            for arm in compare.ARMS:
                guard()
                model = compare.fresh(seed, arm, 'cuda')
                with torch.no_grad():
                    for p in model.parameters():
                        p.add_(.013)
                weights = compare.arrays(model, arm)
                computed = compare.evaluate(model, arm, data, guard, detail=True)
                cpu_contexts = []
                for context in contexts:
                    def rows():
                        for state, public in zip(context['economics'], context['features']):
                            features = data.card_np + public.astype(np.float32)
                            economics = np.broadcast_to(state, (len(features), 5))
                            yield compare.numpy_scores(weights, arm, features, economics)
                    cpu_contexts.append(reference_context(rows(), data.equity_np, context['economics'],
                        data.category_np, context['stack'], data.board_count, detail=True, guard=guard))
                proof = compare_evaluations(computed, evaluation_summary(cpu_contexts))
                checks.append(dict(seed=seed, arm=arm, comparison=proof))
                assert proof['passed'], proof
                assert all(p.dtype == torch.float32 for p in model.parameters())
                del model
        guard()
        verify(spec['inputs'])
        atomic_json(RESULT, dict(passed=True, registration_sha256=sha(REG), raw_checks=records,
            complete_metric_checks=checks, legacy_batches_exact=True, seconds=time.monotonic() - started,
            peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            runtime=dict(torch=torch.__version__, numpy=np.__version__, cuda=torch.version.cuda),
            scientific_training=False, poker_labels=False, preflop_accuracy_qualified=False))
        print(json.dumps(dict(passed=True, raw_checks=len(records), metric_checks=len(checks),
                              seconds=time.monotonic() - started)))
    except BaseException as error:
        atomic_json(FAILURE, dict(error=repr(error), traceback=traceback.format_exc(), retry_allowed=False))
        raise
    finally:
        assert LOCK.read_text() == str(os.getpid())
        LOCK.unlink()


if __name__ == '__main__':
    main()
