"""Qualify the actual four complete banks on an old 64-deal control batch.

Default: read-only readiness. --run never draws the prospective test stream.
This control establishes numerical/transport consistency, not playing strength.
"""
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
from sampled_physical_root_evaluation_v1 import ROOT, sha
from board_prefix_publication_v1 import atomic_json
from board_complete_evaluation_support_v1 import (
    ARMS, CONTEXT, MATRIX, readiness, load_banks, setup_cuda, catalog_roots)
from weighted_complete_evaluation_control_20260927 import old_deal_input
from weighted_learning_cuda_control_20260927 import LOCK, OTHER
from bounded_parallel_evaluation_archive_v2 import ParallelArchives, production_available
from owned_columnar_evaluation_archive_v1 import OwnedColumnarEvaluationArchive
from crossed_complete_policy_batch_shared_v1 import evaluate_batch
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
from complete_bank_root_stability_v1 import summarize

PREFIX = 'board-complete-evaluation-control-v1'
STORE = Path('S:/GTOpen-research') / PREFIX
SECONDS = 7200
CAP = 256_000_000


def runtime_guard():
    started = time.monotonic()
    resource_at = storage_at = 0.
    def guard():
        nonlocal resource_at, storage_at
        now = time.monotonic()
        assert now-started < SECONDS, 'Bounded control deadline reached'
        if now-resource_at > 2:
            assert production_available() and not OTHER.exists()
            assert psutil.virtual_memory().available > 24_000_000_000
            assert psutil.disk_usage('S:/').free > 40_000_000_000
            import torch
            assert torch.cuda.mem_get_info()[0] > 3_000_000_000
            resource_at = now
        if STORE.exists() and now-storage_at > 10:
            total = 0
            for p in STORE.rglob('*'):
                try:
                    st = p.lstat()
                    assert not st.st_file_attributes & 0x400, 'Linked control evidence'
                    if p.is_file():
                        total += st.st_size
                except FileNotFoundError:
                    assert p.is_relative_to(STORE / '.batch-work'), 'Durable evidence disappeared'
            assert total < CAP, 'Control evidence bound reached'
            storage_at = now
    return guard


def main(run=False):
    _, paths, pending = readiness()
    if not run:
        print(json.dumps(dict(ready=not pending, pending=pending, mode='control',
            deals=64, reused_control_deals=True, fresh_test_deals_drawn=0,
            full_bank_cuda_qualified=False, production_modified=False)), flush=True)
        return
    assert not pending, 'Complete audited candidate training is required before numerical qualification'
    assert production_available() and not LOCK.exists() and not OTHER.exists()
    assert psutil.cpu_percent(interval=1) < 30 and psutil.virtual_memory().available > 28_000_000_000
    gpu = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free',
        '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=5,
        creationflags=subprocess.CREATE_NO_WINDOW)
    assert gpu.returncode == 0
    utilization, free = map(float, gpu.stdout.strip().splitlines()[0].split(','))
    assert utilization < 10 and free > 6000
    rp, result_path, failure_path = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result', 'failure')]
    assert not STORE.exists() and not any(p.exists() for p in (rp, result_path, failure_path))
    batch_path, old_paths = old_deal_input()
    archive_result = OUT / 'parallel-evaluation-archive-v2-control-result.json'
    archive_reg = OUT / 'parallel-evaluation-archive-v2-control-registration.json'
    control = read(archive_result)
    assert control['passed'] and control['registration_sha256'] == sha(archive_reg)
    assert control['worker_source_sha256'] == sha(ROOT / 'tools/research/bounded_parallel_evaluation_archive_v2.py')
    paths += [*old_paths, archive_result, archive_reg,
        OUT / 'BOARD-ROOT-MATCHED-STUDY-PLAN.md',
        ROOT / 'target/release/examples/hu_sampled_bank_bridge.exe',
        ROOT / 'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe']
    inputs = {str(p): sha(p) for p in [*paths, *Path(__file__).parent.glob('*.py')]}
    acquired = registered = False
    started = time.monotonic()
    try:
        with LOCK.open('x') as f:
            f.write(str(os.getpid()))
        acquired = True
        assert production_available() and not OTHER.exists()
        from hu_root_retained_storage_admitted_study_20260924 import measure
        inventory = measure()
        total = sum(r['allocated_file_bytes'] for r in inventory)
        assert total + CAP + 2_000_000_000 <= 800_000_000_000
        assert psutil.disk_usage('S:/').free > 40_000_000_000 + CAP
        reg = dict(inputs=inputs, arms=ARMS, store=str(STORE), mode='control', deals=64,
            reused_batch=str(batch_path), batch_size=32, generations=78,
            maximum_seconds=SECONDS, maximum_output_bytes=CAP, tolerance=1e-10,
            global_storage=dict(roots=inventory, allocated_bytes=total,
                reserved_bytes=CAP+2_000_000_000, limit_bytes=800_000_000_000),
            gpu_utilization_before=utilization, gpu_free_MiB_before=free,
            fresh_test_deals_drawn=0, production_modified=False, accuracy_qualified=False)
        atomic_json(rp, reg); registered = True
        setup_cuda()
        guard = runtime_guard(); guard()
        banks, references, identities, load_seconds, args = load_banks(guard=guard, reference=True)
        roots, root_checks = catalog_roots(banks, references, args, guard=guard)
        writer = OwnedColumnarEvaluationArchive.create(STORE, guard=guard)
        atomic_json(STORE / 'bank-identities.json', identities)
        masses = np.asarray(read(MATRIX)['class_mass']).sum(1)
        masses /= masses.sum()
        atomic_json(STORE / 'root-stability.json', summarize(roots, masses))
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
                batch = dict(format=2, batch_id=f'{PREFIX}-{name}', seed=0,
                             query_limit=100000, deals=deals[offset:offset+32])
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
                    error = float(np.max(abs(cp-actual)))
                    reach_error = float(np.max(abs(cr-gr)))
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
        analysis = comparison.finish(); analysis['control_only'] = True
        atomic_json(STORE / 'analysis.json', analysis)
        for p, h in inputs.items():
            guard(); assert sha(p) == h, p
        result = dict(passed=True, complete=True, control_only=True, mode='control', store=str(STORE),
            registration_sha256=sha(rp), deals=64, arms=ARMS,
            cpu_checks=checks, root_cpu_checks=root_checks, load_seconds=load_seconds,
            archive_manifest_hashes=manifests, batch_summary_hashes=summaries,
            archive_owner_sha256=writer.owner_sha256,
            analysis_sha256=sha(STORE / 'analysis.json'),
            bank_identities_sha256=sha(STORE / 'bank-identities.json'),
            root_stability_sha256=sha(STORE / 'root-stability.json'),
            archive_bytes=sum((STORE / (n+s)).stat().st_size for n in manifests for s in ('.xz', '.manifest.json')),
            seconds=time.monotonic()-started, independent_review_required=True,
            fresh_test_deals_drawn=0, accuracy_qualified=False, production_modified=False)
        guard(); atomic_json(result_path, result)
        print(json.dumps(dict(passed=True, seconds=result['seconds'])), flush=True)
    except BaseException as exc:
        if registered:
            atomic_json(failure_path, dict(passed=False, registration_sha256=sha(rp),
                error=repr(exc), seconds=time.monotonic()-started, preserve_partial_outputs=True))
        raise
    finally:
        if acquired:
            assert LOCK.read_text() == str(os.getpid()); LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
