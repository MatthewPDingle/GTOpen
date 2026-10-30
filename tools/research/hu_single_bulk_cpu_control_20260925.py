"""CPU-only frozen-fixture qualification of single-policy bulk features.

Runs alongside the existing GPU trial without changing its sources or inputs.
No fresh deals, training, GPU work, or strategy-quality claim.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import ast
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import psutil
from threadpoolctl import threadpool_limits
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle
from hu_action_integrated_exact_20260925 import bank_args
from frozen_complete_trial_bank_v1 import load_completed_trial
from action_integrated_policy_v1 import predict as reference
from action_integrated_single_bulk64_v1 import predict as candidate, later_probabilities
from later_action_policy_v1 import probabilities as later_reference
from later_action_checkpoint_v1 import restore_checkpoint, model_document

PREFIX = 'single-bulk-cpu-control-v1'


def digest(a):
    return hashlib.sha256(a.tobytes()).hexdigest()


def main():
    start = time.monotonic()
    last = 0.
    def guard():
        nonlocal last
        now = time.monotonic()
        assert now - start < 1200, 'Control deadline'
        if now - last > 2:
            assert idle(), 'Production busy'
            assert psutil.virtual_memory().available > 20_000_000_000
            assert psutil.disk_usage('T:/').free > 40_000_000_000
            last = now
    guard()
    scripts = ROOT/'tools/research'
    original = (scripts/'exact_initial_single_policy64_v1.py').read_text()
    expected = ast.parse(original.replace('from sampled_visible_initialization_v1 import features',
                                         'from sampled_visible_features_bulk_v1 import features'))
    actual = ast.parse((scripts/'exact_initial_single_policy_bulk64_v1.py').read_text())
    # Only the module docstring and feature import may differ in the predictor.
    assert ast.dump(ast.Module(body=expected.body[1:], type_ignores=[])) == ast.dump(
        ast.Module(body=actual.body[1:], type_ignores=[]))
    context = OUT/'bb-context-candidate.json'
    cases = [('later-action-joint-control-v1', 2,
              Path('T:/GTOpen-research/later-action-joint-control-v1/average-queries.json')),
             ('action-integrated-fresh-pilot-v1', 78,
              Path('T:/GTOpen-research/action-integrated-fresh-pilot-v1/iteration-0078/batch-00/queries.json'))]
    paths = [context, OUT/'preflop-allin-matrix-control-v1-matrix.json',
             Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')]
    paths.extend(scripts.glob('*.py'))
    for prefix, _, query in cases:
        paths.append(query)
        paths.extend(OUT/f'{prefix}-{part}.json' for part in
                     ('registration', 'result', 'readback-registration', 'independent-review'))
    inputs = {str(p): sha(p) for p in paths}
    rp = OUT/f'{PREFIX}-registration.json'
    save(rp, dict(inputs=inputs, cases=[dict(prefix=p, updates=n, query=str(q)) for p,n,q in cases],
        maximum_seconds=1200, maximum_output_bytes=2_000_000, cpu_math_threads=1,
        gpu_used=False, fresh_holdout=False, production_modified=False,
        scope='Exact scores/probabilities/coverage on two audited historical models and two native query batches; alternating two repetitions. CPU only, no live implementation switch.'))
    args = bank_args(context.read_text())
    infer_args = {k:v for k,v in args.items() if k != 'context_source'}
    results = []
    with threadpool_limits(limits=1):
        for index, (prefix, count, query_path) in enumerate(cases):
            guard()
            models, _, identity = load_completed_trial(OUT, prefix,
                expected_updates=count, bank_args=args, guard=guard)
            model = models[-1]
            queries = read(query_path)
            timings = [[], []]
            expected_output = None
            coverage = None
            for repeat in range(2):
                order = (0,1) if (index+repeat)%2 == 0 else (1,0)
                for implementation in order:
                    guard()
                    before = time.monotonic()
                    scores, p, matched = (reference, candidate)[implementation](
                        queries, model, device='cpu', **infer_args)
                    timings[implementation].append(time.monotonic()-before)
                    output = [digest(scores), digest(p)]
                    if expected_output is None:
                        expected_output, coverage = output, matched
                    assert output == expected_output and matched == coverage
            version7_exact = None
            if count == 2:
                result = read(OUT/f'{prefix}-result.json')
                objects = Path(result['store'])/'objects'
                state = restore_checkpoint(objects, result['final_checkpoint'],
                                           config=result['config'], **args)
                v7 = model_document(objects, state['played_bank'][-1], **args)
                p, c = later_reference(queries, v7, device='cpu', **infer_args)
                q, d = later_probabilities(queries, v7, device='cpu', **infer_args)
                assert digest(p) == digest(q) == expected_output[1] and c == d == coverage
                version7_exact = True
            row = dict(prefix=prefix, generation=model['generation'], bank_identity=identity,
                observations=len(queries['observations']), reference_seconds=timings[0],
                bulk_seconds=timings[1], scores_sha256=expected_output[0],
                probabilities_sha256=expected_output[1], coverage=coverage,
                byte_identical=True, version7_adapter_exact=version7_exact)
            results.append(row)
            print(json.dumps({k:v for k,v in row.items() if k!='bank_identity'}), flush=True)
            del models, model, queries
    for path, h in inputs.items():
        guard()
        assert sha(path) == h, path
    result = dict(passed=True, registration_sha256=sha(rp), cases=results,
        predictor_ast_identical_except_feature_import=True,
        seconds=time.monotonic()-start, gpu_used=False, production_modified=False,
        accuracy_qualified=False, cuda_qualified=False, live_trial_modified=False,
        scope='CPU frozen-batch implementation equivalence and paired timing only; GPU qualification still required.')
    encoded = json.dumps(result, allow_nan=False)
    assert len(encoded.encode()) + rp.stat().st_size < 2_000_000
    save(OUT/f'{PREFIX}-result.json', result)
    print(json.dumps(dict(passed=True, seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
