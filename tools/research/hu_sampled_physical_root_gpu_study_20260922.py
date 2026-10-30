"""GPU execution of the frozen physical evaluation plan, with CPU cross-checks.

Same candidate, seeds, deal counts, support threshold and one final look as the
CPU study. This is a different numerical backend, not independent replication.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import psutil

from loopback_research_validation import idle
from sampled_physical_root_evaluation_cuda_v1 import ROOT, sha, save, run

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-root-study-gpu-v1'
STORE = Path('S:/GTOpen-research') / PREFIX
LOCK = ROOT / 'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT / 'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def output(suffix):
    return OUT / (PREFIX + '-' + suffix + '.json')


def status(value):
    path = output('status')
    temporary = path.with_suffix('.tmp')
    save(temporary, value)
    temporary.replace(path)


def verify(reg):
    for path, expected in reg['inputs'].items():
        assert sha(path) == expected, path


def free_gpu():
    return int(subprocess.check_output(
        ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
        text=True).splitlines()[0]) * 1024**2


def prepare():
    assert idle() and not STORE.exists()
    source = OUT / 'sampled-physical-root-study-v1-admission.json'
    original = json.loads(source.read_text())
    verify(original)
    check_paths = [OUT / ('sampled-physical-gpu-bank-v1-' + suffix + '.json')
                   for suffix in ('registration', 'result', 'review', 'independent-review')]
    control_reg, control_result, control_review, independent = [json.loads(p.read_text()) for p in check_paths]
    assert control_result['passed'] and control_review['passed'] and independent['passed']
    assert independent['registration_sha256'] == sha(check_paths[0])
    assert independent['result_sha256'] == sha(check_paths[1])
    verify(control_reg)
    assert control_reg['source_admission'] == str(source)
    refs = {}
    reference_paths = []
    cpu_store = Path(original['store'])
    for offset in range(0, 16 * original['config']['batch_size'], original['config']['batch_size']):
        folder = cpu_store / f"{original['id']}-train-{offset}"
        summary = json.loads((folder / 'summary.json').read_text())
        for name, expected in summary['artifacts'].items():
            assert sha(folder / name) == expected
        reference_paths.extend(folder / name for name in ('batch.json', 'queries.json', 'profiles.json', 'native.json', 'summary.json'))
        refs[str(offset)] = dict(folder=str(folder), policy_tolerance=control_reg['policy_tolerance'],
                                payoff_tolerance_bb=control_reg['payoff_tolerance_bb'])
    paths = [*map(Path, original['inputs']), source, *check_paths, *reference_paths, Path(__file__),
             ROOT / 'tools/research/sampled_physical_gpu_bank_v1.py',
             ROOT / 'tools/research/sampled_physical_root_evaluation_cuda_v1.py']
    reg = dict(original)
    reg.update(id=PREFIX, store=str(STORE), inputs={str(p): sha(p) for p in paths},
               source_cpu_admission=str(source), source_cpu_admission_sha256=sha(source),
               device='cuda', no_gpu=False, models_per_chunk=8, gpu_reserve_bytes=3_000_000_000,
               cpu_reference_batches=refs,
               backend_change='Keep the full played bank resident on CUDA, encode visible features once, batch eight models, and preserve own-reach weighting. CPU study remains unmodified. This uses the identical predeclared candidate, deal streams, counts, responder threshold and final statistical look; it is not independent replication.',
               arithmetic='Float32 CUDA network inference, TF32 disabled; float64 regret matching and own-reach accumulation in model order. Numerical equivalence, not bitwise identity.',
               additional_gate='Compare every policy row and root payoff against 16 completed CPU training batches (256 deals) before test-stream creation. Freeze their hashes at preparation. Tolerances fixed by the separate old-fixture control, not study accuracy outcomes.',
               stopping='Complete original sample counts or stop at two hours, production activity, resource or numerical-gate failure. No automatic retry, extension or partial-result accuracy claim.',
               scope=original['scope'] + ' CUDA backend; same streams as CPU execution, so results are not independent corroboration.')
    assert reg['config'] == original['config']
    reg['source_cpu_protocol_sha256'] = reg.pop('protocol_sha256')
    save(output('registration'), reg)
    print(json.dumps(dict(prepared=True, cpu_reference_batches=len(refs), config=reg['config'],
                          registration=str(output('registration')))))


def worker(reg):
    import torch
    torch.set_num_threads(2)
    started = time.monotonic()
    last = 0.

    def guard():
        nonlocal last
        now = time.monotonic()
        if now - last >= 2:
            assert now-started < reg['maximum_seconds'] and idle()
            assert psutil.virtual_memory().available >= reg['host_reserve_bytes']
            assert torch.cuda.mem_get_info()[0] >= reg['gpu_reserve_bytes']
            assert shutil.disk_usage(STORE.parent).free >= reg['disk_reserve_bytes']
            last = now

    verify(reg)
    result = run(reg, STORE, guard)
    verify(reg)
    assert result['terminal']
    comparisons = []
    for offset in reg['cpu_reference_batches']:
        summary = json.loads((STORE / f'{PREFIX}-train-{offset}' / 'summary.json').read_text())
        assert summary['cpu_comparison']['passed']
        comparisons.append(summary['cpu_comparison'])
    result.update(cpu_reference_comparisons=comparisons, same_streams_as_cpu_study=True,
                  backend='cuda persistent bank', registration_sha256=sha(output('registration')))
    save(output('result'), result)


def execute():
    reg = json.loads(output('registration').read_text())
    verify(reg)
    assert idle() and not STORE.exists() and not LOCK.exists() and not OTHER.exists()
    assert psutil.virtual_memory().available >= reg['host_reserve_bytes']
    assert free_gpu() >= reg['gpu_reserve_bytes']
    assert shutil.disk_usage(STORE.parent).free >= reg['disk_reserve_bytes'] + reg['maximum_store_bytes']
    with LOCK.open('x') as f: f.write(str(os.getpid()))
    child = None; error = None; samples = []; last_resource = 0.
    started = time.monotonic()
    try:
        env = os.environ.copy()
        env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8', OMP_NUM_THREADS='2', PYTHONUNBUFFERED='1')
        status(dict(state='running', controller_pid=os.getpid(), production_modified=False))
        with (OUT / (PREFIX + '.log')).open('x') as log:
            child = subprocess.Popen([sys.executable, str(Path(__file__)), '--worker', str(output('registration'))],
                                     cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2)
                elapsed = time.monotonic()-started
                assert elapsed < reg['maximum_seconds'] and idle(), 'Deadline or production activity'
                if elapsed-last_resource >= 10:
                    host = psutil.virtual_memory().available
                    gpu = free_gpu()
                    disk = shutil.disk_usage(STORE.parent).free
                    used = sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) if STORE.exists() else 0
                    completed = len(list(STORE.glob('*/summary.json'))) if STORE.exists() else 0
                    samples.append(dict(seconds=elapsed, free_host_bytes=host, free_gpu_bytes=gpu,
                                        free_disk_bytes=disk, store_bytes=used, completed_batches=completed))
                    assert host >= reg['host_reserve_bytes'] and gpu >= reg['gpu_reserve_bytes']
                    assert disk >= reg['disk_reserve_bytes'] and used <= reg['maximum_store_bytes']
                    status(dict(state='running', controller_pid=os.getpid(), completed_batches=completed,
                                seconds=elapsed, production_modified=False))
                    last_resource = elapsed
        assert child.returncode == 0, f'GPU evaluation worker failed: {child.returncode}'
        verify(reg)
        result = json.loads(output('result').read_text())
        assert result['terminal'] and result['completed_training_deals'] == reg['config']['training_deals']
        assert result['completed_evaluation_deals'] == reg['config']['evaluation_deals']
        assert len(result['cpu_reference_comparisons']) == 16
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        if child is not None and child.poll() is None:
            for p in reversed(psutil.Process(child.pid).children(recursive=True)):
                try: p.terminate()
                except psutil.NoSuchProcess: pass
            child.terminate(); child.wait(timeout=20)
        status(dict(state='stopped' if error else 'complete', error=error,
                    exit_code=child.returncode if child else None, seconds=time.monotonic()-started,
                    store=str(STORE), production_modified=False))
        save(output('resources'), samples)
        assert LOCK.read_text().strip() == str(os.getpid())
        LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--prepare', action='store_true')
    action.add_argument('--run', action='store_true')
    action.add_argument('--worker')
    args = parser.parse_args()
    if args.prepare: prepare()
    elif args.worker: worker(json.loads(Path(args.worker).read_text()))
    else: execute()
