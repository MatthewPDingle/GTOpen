"""Full played-bank float64 control on the existing 256 training fixtures.

No new training, response selection or held-out chance draws. Keeps the failed
evaluation's policy/payoff tolerances and independently checks both backends.
"""
import os
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_cuda_v1 import ROOT, sha, save, batch_values
from sampled_physical_hybrid_checkpoint_v1 import read_object, model_document, verify_bank
from sampled_physical_hybrid_cpu64_v1 import HybridCpuBank64
from sampled_physical_hybrid_gpu_bank_v2 import HybridCudaBank64
from sampled_physical_preflop_table_v1 import Table
from sampled_physical_bank_v1 import histories

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-hybrid-precision-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    import torch
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    started = time.monotonic(); last = 0.; resources = []
    def guard():
        nonlocal last
        now = time.monotonic()
        if now-last >= 2:
            assert now-started < 1200 and idle()
            host = psutil.virtual_memory().available
            gpu = torch.cuda.mem_get_info()[0]
            disk = psutil.disk_usage(str(STORE.parent)).free
            assert host >= 20_000_000_000 and gpu >= 3_000_000_000 and disk >= 40_000_000_000
            resources.append(dict(seconds=now-started, free_host_bytes=host, free_gpu_bytes=gpu, free_disk_bytes=disk))
            last = now
    guard(); assert not LOCK.exists() and not OTHER.exists() and not STORE.exists()
    oldreg = OUT/'sampled-physical-hybrid-evaluation-v1-registration.json'
    oldcontrol = OUT/'sampled-physical-hybrid-evaluation-v1-cpu-control.json'
    failed = OUT/'sampled-physical-hybrid-evaluation-v1-status.json'
    diagnosis = OUT/'sampled-physical-hybrid-numerics-v1-result.json'
    reg = json.loads(oldreg.read_text()); diag = json.loads(diagnosis.read_text())
    assert json.loads(failed.read_text())['state'] == 'stopped'
    assert diag['passed'] and diag['held_out_deals_generated'] == 0
    for p, h in reg['inputs'].items(): assert sha(p) == h, p
    original_control = json.loads(oldcontrol.read_text())
    for p, h in original_control['artifacts'].items(): assert sha(p) == h, p
    objects = Path(reg['objects']); context = Path(reg['context'])
    checkpoint = json.loads(read_object(objects, reg['checkpoint']))
    verify_bank(objects, 78, checkpoint['played_bank'], checkpoint['next_model'], context_source=context.read_text())
    models = [model_document(objects, r, context_source=context.read_text()) for r in checkpoint['played_bank']]
    paths = [Path(__file__), oldreg, oldcontrol, failed, diagnosis,
        *[ROOT/'tools/research'/n for n in ('sampled_physical_hybrid_cpu64_v1.py',
            'sampled_physical_hybrid_gpu_bank_v2.py', 'sampled_physical_root_evaluation_cuda_v1.py')]]
    registration = dict(inputs={str(p): sha(p) for p in paths}, source_registration_sha256=sha(oldreg),
        candidate_checkpoint=reg['checkpoint'], played_generations=list(range(78)),
        source_control_artifacts=original_control['artifacts'], policy_tolerance=1e-4, payoff_tolerance_bb=1e-3,
        source_deals=256, scope='Float64 inference control for the unchanged stored hybrid weights, preflop tables and complete played bank. Existing training fixtures only; no new chance draws or poker-strength claim.')
    regpath = OUT/f'{PREFIX}-registration.json'; save(regpath, registration)
    with LOCK.open('x') as f: f.write(str(os.getpid()))
    error = None
    try:
        STORE.mkdir()
        cpu = HybridCpuBank64(models, context_source=context.read_text())
        gpu = HybridCudaBank64(models, [[1.]*78]*2, context_source=context.read_text(), guard=guard)
        records = []; scalar_check = None
        for offset in range(0, 256, 16):
            guard(); old = Path(reg['cpu_reference_batches'][str(offset)]['folder'])
            batch = json.loads((old/'batch.json').read_text())
            began = time.monotonic()
            cpufolder = STORE/f'cpu-{offset}'
            batch_values(context, batch, objects, checkpoint, cpufolder, guard, cpu)
            cpu_seconds = time.monotonic()-began; began = time.monotonic()
            gpufolder = STORE/f'gpu-{offset}'
            summary = batch_values(context, batch, objects, checkpoint, gpufolder, guard, gpu,
                dict(folder=str(cpufolder), policy_tolerance=1e-4, payoff_tolerance_bb=1e-3))
            gpu_seconds = time.monotonic()-began
            if offset == diag['training_batch_offset']:
                q = json.loads((gpufolder/'queries.json').read_text()); obs = q['observations']
                dr = json.loads((OUT/'sampled-physical-hybrid-numerics-v1-registration.json').read_text())
                target = dr['selected_row']; h = histories(obs)[target]
                numerator = np.zeros(4); denominator = 0.
                for generation, model in zip(diag['generations'], models):
                    rows = generation['observations']; indices = [r['index'] for r in rows]
                    p = np.asarray([r['double_neural_probability'] for r in rows])
                    for table in model['preflop_tables']:
                        if table is not None: p, _ = Table(table, context.read_text()).apply([obs[i] for i in indices], p)
                    byindex = dict(zip(indices, p)); reach = 1.
                    for ancestor, action in h: reach *= byindex[ancestor][action]
                    numerator += byindex[target]*reach; denominator += reach
                expected = numerator/denominator
                policies = json.loads((gpufolder/'profiles.json').read_text())['profiles'][0]['policies']
                scalar_error = float(np.max(np.abs(expected-policies[target]['probabilities'])))
                assert scalar_error < 1e-8
                scalar_check = dict(policy=expected.tolist(), maximum_error=scalar_error, generation_count=78)
            record = dict(offset=offset, cpu_seconds=cpu_seconds, gpu_seconds=gpu_seconds,
                comparison=summary['cpu_comparison'], summaries={str(f/'summary.json'): sha(f/'summary.json') for f in (cpufolder, gpufolder)})
            records.append(record); print(json.dumps(record), flush=True)
        assert scalar_check is not None
        for p, h in registration['inputs'].items(): assert sha(p) == h, p
        guard()
        result = dict(passed=True, registration_sha256=sha(regpath), complete_deals=256, records=records,
            scalar_reference_check=scalar_check, maximum_policy_error=max(r['comparison']['maximum_policy_error'] for r in records),
            maximum_payoff_error_bb=max(r['comparison']['maximum_payoff_error_bb'] for r in records),
            total_cpu_seconds=sum(r['cpu_seconds'] for r in records), total_gpu_seconds=sum(r['gpu_seconds'] for r in records),
            seconds=time.monotonic()-started, production_modified=False, scope=registration['scope'])
        save(OUT/f'{PREFIX}-result.json', result)
        print(json.dumps({k: v for k, v in result.items() if k != 'records'}), flush=True)
    except Exception as exc:
        error = str(exc); raise
    finally:
        save(OUT/f'{PREFIX}-resources.json', resources)
        save(OUT/f'{PREFIX}-status.json', dict(state='stopped' if error is not None else 'complete', error=error,
            seconds=time.monotonic()-started, production_modified=False))
        assert LOCK.read_text() == str(os.getpid()); LOCK.unlink()


if __name__ == '__main__': main()
