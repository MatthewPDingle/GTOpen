"""Four fixed-input throughput candidates; explicit idle-GPU execution only.

32/64 retained deals x deepcopy/JSON snapshot, four balanced-order repeats.
No fresh poker deals, learning, scientific effect interpretation or deployment.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from weighted_complete_evaluation_support_v1 import load_banks, setup_cuda, complete_training_paths, CONTEXT, LOCK, OTHER
from bounded_parallel_evaluation_archive_v2 import production_available
from board_study_storage_v1 import create, measure
from board_prefix_publication_v1 import atomic_json, storage_boundary
from weighted_gpu_throughput_inputs_v1 import retained_inputs, joined_batch, pack, compare
from crossed_complete_policy_batch_shared_v1 import evaluate_batch as old_evaluate
from crossed_complete_policy_batch_snapshot_v1 import evaluate_batch as new_evaluate

PREFIX = 'weighted-gpu-throughput-control-v1'
STORE = Path('S:/GTOpen-research') / PREFIX
PREPARATION = 'weighted-gpu-throughput-preparation-v1'
CASES = (('deepcopy32', 32, old_evaluate), ('deepcopy64', 64, old_evaluate),
         ('snapshot32', 32, new_evaluate), ('snapshot64', 64, new_evaluate))


def prerequisites():
    paths = complete_training_paths(); pending = []
    for prefix in ('weighted-complete-evaluation-queue-v1', 'board-training-pipeline-queue-v2', PREPARATION):
        rp = OUT / f'{prefix}-registration.json'; result_path = OUT / f'{prefix}-result.json'
        if not result_path.exists(): pending.append(prefix); continue
        result, reg = read(result_path), read(rp)
        assert result['passed'] and result['registration_sha256'] == sha(rp)
        for p, h in reg['inputs'].items(): assert sha(p) == h, p
        paths.extend((rp, result_path))
        for stage in result.get('stages', []): assert sha(stage['result']) == stage['sha256']
    return paths, pending


class RecordingBank:
    def __init__(self, bank): self.bank = bank; self.records = []

    def average_prepared(self, prepared, *, guard):
        p, reach = self.bank.average_prepared(prepared, guard=guard)
        self.records.append((prepared.queries, p.copy(), reach.copy()))
        return p, reach


def main(run=False):
    paths, pending = prerequisites()
    if not run:
        print(json.dumps(dict(ready=not pending, pending=pending, cases=[c[0] for c in CASES],
            retained_deals=64, warmups_per_case=1, measured_repeats_per_case=4,
            benchmark_started=False, fresh_resource_and_storage_admission_required=True)))
        return
    assert not pending, 'Finish queued studies and preparation first'
    assert not STORE.exists() and not (OUT / f'{PREFIX}-registration.json').exists()
    assert production_available() and not LOCK.exists() and not OTHER.exists()
    assert psutil.cpu_percent(interval=1) < 20 and psutil.virtual_memory().available > 28_000_000_000
    status = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free', '--format=csv,noheader,nounits'],
        capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
    assert status.returncode == 0
    util, free = map(float, status.stdout.strip().splitlines()[0].split(',')); assert util < 10 and free > 8000
    batches, _, retained_paths = retained_inputs(); paths.extend(retained_paths)
    joined = joined_batch(batches)
    query_exe = ROOT / 'target/release/examples/hu_sampled_bank_bridge.exe'
    eval_exe = ROOT / 'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    paths.extend((query_exe, eval_exe, *Path(__file__).parent.glob('*.py')))
    inputs = {str(p): sha(p) for p in paths}
    rp = OUT / f'{PREFIX}-registration.json'
    reg = dict(inputs=inputs, store=str(STORE), cases=[c[0] for c in CASES], deals=64,
        warmups_per_case=1, repeats=4, order=[[CASES[(r+i)%4][0] for i in range(4)] for r in range(4)],
        maximum_seconds=1800, maximum_allocated_bytes=2_000_000_000, maximum_logical_bytes=2_000_000_000,
        policy_tolerance=1e-10, reach_tolerance=1e-10, cashflow_tolerance=1e-9,
        scope='Identical previously used deals and four frozen 78-model banks. Raw-batch wall time includes query preparation, GPU/CPU averaging, JSON/native work and recording copies; excludes bank loading, archive compression and post-timing equivalence checks.',
        no_fresh_deals=True, training_started=False, production_modified=False)
    acquired = False; started = time.monotonic(); last = 0.; began_free = None
    def guard():
        nonlocal last
        now = time.monotonic(); assert now-started < 1800
        if now-last > 3:
            assert production_available() and not OTHER.exists()
            assert psutil.virtual_memory().available > 24_000_000_000
            free_bytes = psutil.disk_usage('S:/').free
            assert free_bytes > 40_000_000_000
            if began_free is not None: assert max(0, began_free-free_bytes) < reg['maximum_allocated_bytes']
            import torch
            assert torch.cuda.mem_get_info()[0] > 4_000_000_000
            last = now
    try:
        with LOCK.open('x') as stream: stream.write(str(os.getpid()))
        acquired = True
        from hu_root_retained_storage_admitted_study_20260924 import measure as inventory
        roots = inventory(); total = sum(r['allocated_file_bytes'] for r in roots)
        assert total + 4_000_000_000 <= 800_000_000_000
        reg['storage_admission'] = dict(roots=roots, allocated_bytes=total, reserve_bytes=4_000_000_000)
        atomic_json(rp, reg); create(STORE); began_free = psutil.disk_usage('S:/').free
        setup_cuda(); import torch
        banks, _, identities, load_seconds, _ = load_banks(guard=guard)
        assert identities == read(Path('S:/GTOpen-research/weighted-complete-evaluation-study-v1/bank-identities.json'))
        save(STORE / 'bank-identities.json', identities)
        cache = load_complete_cache(); recorders = [RecordingBank(b) for b in banks]
        reference_pack = reference_values = None; runs = []
        schedule = [('warmup', i, CASES[i]) for i in range(4)]
        schedule += [(f'repeat-{r+1}', i, CASES[(r+i)%4]) for r in range(4) for i in range(4)]
        for phase, position, (name, size, evaluate) in schedule:
            guard(); storage_boundary(STORE, reg, phase+':'+name, reserve_bytes=150_000_000, guard=guard)
            folder = STORE / f'{phase}-{name}'; folder.mkdir()
            captures = []; summaries = []; wall = 0.; peaks = []
            for index, batch in enumerate(batches if size == 32 else [joined]):
                for recorder in recorders: recorder.records.clear()
                part = folder / f'batch-{index}'; torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
                t = time.perf_counter()
                summary = evaluate(batch=batch, folder=part, context_path=CONTEXT, banks=recorders, cache=cache,
                    query_executable=query_exe, evaluation_executable=eval_exe, guard=guard)
                torch.cuda.synchronize(); wall += time.perf_counter()-t
                peaks.append(dict(allocated=torch.cuda.max_memory_allocated(), reserved=torch.cuda.max_memory_reserved()))
                assert all(len(recorder.records) == 1 for recorder in recorders)
                records = [r.records[0] for r in recorders]; q = records[0][0]
                assert all(row[0] is q for row in records)
                capture = dict(queries=q, policies=np.stack([r[1] for r in records]), reaches=np.stack([r[2] for r in records]))
                captures.append(capture); summaries.append(summary)
                # Retain own reach as well as existing complete-policy native artifacts.
                with (part / 'bank-capture.npz').open('xb') as stream:
                    np.savez(stream, policies=capture['policies'], reaches=capture['reaches'])
            packed = pack(captures); values = np.concatenate([np.asarray(s['values']) for s in summaries])
            if reference_pack is None: reference_pack, reference_values = packed, values
            comparison = compare(reference_pack, packed)
            assert values.shape == reference_values.shape == (64, 2, 4, 2)
            error = float(np.max(abs(reference_values-values))); assert error < 1e-9
            allocation = storage_boundary(STORE, reg, phase+':'+name+':complete', guard=guard)
            evidence = dict(phase=phase, order_position=position, case=name, batch_size=size,
                seconds_per_64_deals=wall, deals_per_second=64/wall, peaks=peaks, comparison=comparison,
                maximum_cashflow_error=error, duplicate_policy_error=packed['duplicate_policy_error'],
                duplicate_reach_error=packed['duplicate_reach_error'], measurement=allocation,
                artifacts={str(p): sha(p) for p in folder.rglob('*') if p.is_file()})
            save(folder / 'comparison.json', evidence); runs.append(evidence)
            print(json.dumps({k: evidence[k] for k in ('phase', 'case', 'seconds_per_64_deals', 'comparison', 'maximum_cashflow_error')}), flush=True)
        medians = {name: statistics.median(r['seconds_per_64_deals'] for r in runs if r['case']==name and r['phase']!='warmup') for name, _, _ in CASES}
        for p, h in inputs.items(): guard(); assert sha(p)==h, p
        final_size = storage_boundary(STORE, reg, 'before-success', guard=guard)
        final_roots = inventory(); assert sum(r['allocated_file_bytes'] for r in final_roots)+2_000_000_000 <= 800_000_000_000
        result = dict(passed=True, registration_sha256=sha(rp), runs=runs,
            median_seconds_per_64_deals=medians, ratios_to_deepcopy32={n: t/medians['deepcopy32'] for n,t in medians.items()},
            load_seconds=load_seconds, seconds=time.monotonic()-started, measurement=final_size,
            final_global_storage=final_roots, gpu_used=True, no_fresh_deals=True, production_modified=False,
            limitation='Restricted warmed fixed-input throughput and numerical equivalence. Four timing repeats do not establish a universal speedup; archive/whole-study timing and an independent capture readback remain outstanding. No candidate automatically selected or deployed.')
        atomic_json(OUT / f'{PREFIX}-result.json', result)
    except BaseException as error:
        if rp.exists(): save(OUT / f'{PREFIX}-failure.json', dict(error=repr(error), registration_sha256=sha(rp), production_modified=False))
        raise
    finally:
        if acquired:
            assert LOCK.read_text()==str(os.getpid()); LOCK.unlink()


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
