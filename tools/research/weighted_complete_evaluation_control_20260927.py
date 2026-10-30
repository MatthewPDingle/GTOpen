"""Full 78-policy control on old deals; never draw the prospective test stream."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from weighted_complete_evaluation_support_v1 import (
    ARMS, CONTEXT, MATRIX, LOCK, OTHER, complete_training_paths,
    load_banks, runtime_guard, setup_cuda, catalog_roots)
from bounded_parallel_evaluation_archive_v2 import ParallelArchives, production_available
from owned_columnar_evaluation_archive_v1 import OwnedColumnarEvaluationArchive
from crossed_complete_policy_batch_shared_v1 import evaluate_batch
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
from complete_bank_root_stability_v1 import summarize
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2')

PREFIX = 'weighted-complete-evaluation-control-v1'
STORE = Path('S:/GTOpen-research') / PREFIX


def old_deal_input():
    # Replay exactly the previously inspected 64-deal qualification batch.
    rp = OUT / 'action-integrated-replication-v1-result.json'
    result = read(rp)
    assert result['passed']
    metric = Path(result['store']) / 'iteration-0001/metrics.json'
    assert sha(metric) == result['steps'][0]['metrics_sha256']
    batch = metric.parent / 'batch-00/batch.json'
    assert sha(batch) == read(metric)['subbatches'][0]['artifacts']['batch']
    assert len(read(batch)['deals']) == 64
    return batch, [rp, metric, batch]


def main(check_ready=False):
    paths = complete_training_paths()
    if check_ready:
        print(json.dumps(dict(ready=True, training_paths=len(paths), arms=ARMS)))
        return
    assert production_available() and not LOCK.exists() and not OTHER.exists()
    assert psutil.cpu_percent(interval=1) < 50
    gpu = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free',
        '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=5,
        creationflags=subprocess.CREATE_NO_WINDOW)
    assert gpu.returncode == 0
    utilization, free = map(float, gpu.stdout.strip().splitlines()[0].split(','))
    assert utilization < 20 and free > 6000
    rp, result_path = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    assert not STORE.exists() and not rp.exists() and not result_path.exists()
    batch_path, old_paths = old_deal_input()
    archive_result = OUT / 'parallel-evaluation-archive-v2-control-result.json'
    archive_reg = OUT / 'parallel-evaluation-archive-v2-control-registration.json'
    control = read(archive_result)
    assert control['passed'] and control['registration_sha256'] == sha(archive_reg)
    assert control['worker_source_sha256'] == sha(ROOT / 'tools/research/bounded_parallel_evaluation_archive_v2.py')
    paths += [*old_paths, archive_result, archive_reg,
              OUT / 'WEIGHTED-COMPLETE-EVALUATION-PLAN.md',
              ROOT / 'target/release/examples/hu_sampled_bank_bridge.exe',
              ROOT / 'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe']
    inputs = {str(p): sha(p) for p in [*paths, *Path(__file__).parent.glob('*.py')]}
    reg = dict(inputs=inputs, arms=ARMS, store=str(STORE), mode='control', deals=64,
               reused_batch=str(batch_path), batch_size=32, generations=78,
               maximum_seconds=7200, maximum_output_bytes=100_000_000,
               tolerance=1e-10, gpu_utilization_before=utilization,
               gpu_free_MiB_before=free, production_modified=False, accuracy_qualified=False)
    save(rp, reg)
    acquired = False
    started = time.monotonic()
    try:
        with LOCK.open('x') as f:
            f.write(str(os.getpid()))
        acquired = True
        setup_cuda()
        guard = runtime_guard(STORE, maximum_seconds=reg['maximum_seconds'],
                              maximum_bytes=reg['maximum_output_bytes'])
        guard()
        banks, references, identities, load_seconds, args = load_banks(guard=guard, reference=True)
        roots, root_checks = catalog_roots(banks, references, args, guard=guard)
        writer = OwnedColumnarEvaluationArchive.create(STORE, guard=guard)
        save(STORE / 'bank-identities.json', identities)
        matrix = read(MATRIX)
        masses = np.asarray(matrix['class_mass']).sum(1)
        masses /= masses.sum()
        save(STORE / 'root-stability.json', summarize(roots, masses))
        cache = load_complete_cache()
        deals = read(batch_path)['deals']
        context = json.loads(args['context_source'])
        comparison = CompletePolicyComparison(stack=context['config']['stack'],
                                              dead_money=context['dead_money'], deals=64)
        checks, summaries = [], {}
        pool = ParallelArchives(writer, guard=guard, maximum_workers=4)
        try:
            for offset in (0, 32):
                name = f'test-{offset:06d}'
                batch = dict(format=2, batch_id=f'{PREFIX}-{name}', seed=0, query_limit=100000,
                             deals=deals[offset:offset + 32])
                folder = writer.begin(name)
                summary = evaluate_batch(batch=batch, folder=folder, context_path=CONTEXT,
                    banks=banks, cache=cache, guard=guard,
                    query_executable=ROOT / 'target/release/examples/hu_sampled_bank_bridge.exe',
                    evaluation_executable=ROOT / 'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe')
                comparison.add(summary['values'])
                queries, transport = read(folder / 'queries.json'), read(folder / 'profiles.json')
                assert any(o['own_history'] for o in queries['observations'])
                for k, reference in enumerate(references):
                    cp, cr = reference.average(queries, guard=guard)
                    gp, gr = banks[k].average(queries, guard=guard)
                    actual = np.asarray([r['probabilities'] for r in transport['profiles'][(0, 3, 4, 7)[k]]['policies']])
                    error = float(np.max(abs(cp - actual)))
                    reach_error = float(np.max(abs(cr - gr)))
                    assert np.array_equal(gp, actual)
                    assert error < 1e-10 and reach_error < 1e-10
                    checks.append(dict(batch=name, bank=k, maximum_policy_error=error,
                        maximum_reach_error=reach_error, observations=len(queries['observations'])))
                summaries[name] = sha(folder / 'summary.json')
                pool.submit(name)
                print(json.dumps(dict(batch=name, complete_cpu_checks=len(checks))), flush=True)
            manifests = pool.drain()
        finally:
            pool.close()
        analysis = comparison.finish()
        analysis['control_only'] = True
        save(STORE / 'analysis.json', analysis)
        for p, h in inputs.items():
            guard()
            assert sha(p) == h, p
        result = dict(passed=True, complete=True, control_only=True, mode='control', store=str(STORE),
                      registration_sha256=sha(rp), deals=64, arms=ARMS,
                      cpu_checks=checks, root_cpu_checks=root_checks, load_seconds=load_seconds,
                      archive_manifest_hashes=manifests, batch_summary_hashes=summaries,
                      archive_owner_sha256=writer.owner_sha256,
                      analysis_sha256=sha(STORE / 'analysis.json'),
                      bank_identities_sha256=sha(STORE / 'bank-identities.json'),
                      root_stability_sha256=sha(STORE / 'root-stability.json'),
                      archive_bytes=sum((STORE / (n + s)).stat().st_size
                                        for n in manifests for s in ('.xz', '.manifest.json')),
                      seconds=time.monotonic() - started, independent_review_required=True,
                      accuracy_qualified=False, production_modified=False)
        save(result_path, result)
        print(json.dumps(dict(passed=True, seconds=result['seconds'])), flush=True)
    finally:
        if acquired:
            assert LOCK.read_text() == str(os.getpid())
            LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-ready', action='store_true')
    main(parser.parse_args().check_ready)
