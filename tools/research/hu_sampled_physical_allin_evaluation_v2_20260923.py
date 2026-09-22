"""Fresh reserved-deal evaluation of the completed conditional-all-in candidate."""
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
from sampled_physical_allin_evaluation_v2 import ROOT, sha, save, run

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-allin-evaluation-v2'
STORE = Path('S:/GTOpen-research') / PREFIX
CPU_STORE = Path('S:/GTOpen-research') / (PREFIX+'-cpu-control')
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
    assert idle() and not STORE.exists() and not CPU_STORE.exists()
    original = OUT/'sampled-physical-allin-evaluation-v1-registration.json'
    failed = OUT/'sampled-physical-allin-evaluation-v1-status.json'
    reg = json.loads(original.read_text()); verify(reg)
    assert json.loads(failed.read_text())['state'] == 'stopped'
    oldstore = Path(reg['store'])
    assert not list(oldstore.glob('*-test-*')) and not (oldstore/'response.json').exists()
    pr = OUT/'sampled-physical-allin-precision-control-v1-registration.json'
    pv = OUT/'sampled-physical-allin-precision-control-v1-result.json'
    pa = OUT/'sampled-physical-allin-precision-control-v1-independent-review.json'
    precision = json.loads(pr.read_text()); verify(precision)
    audit = json.loads(pa.read_text())
    assert audit['passed'] and audit['complete_deals'] == 256
    assert audit['registration_sha256'] == sha(pr) and audit['result_sha256'] == sha(pv)
    assert audit['reviewer_sha256'] == sha(ROOT/'tools/research/hu_sampled_physical_allin_precision_review_20260923.py')
    for p,h in audit['inputs'].items(): assert sha(p) == h,p
    for p,h in audit['artifacts'].items(): assert sha(p) == h,p
    assert precision['candidate_checkpoint'] == reg['checkpoint']
    paths = [original,failed,pr,pv,pa,*map(Path,precision['inputs']),Path(__file__),
        OUT/'ALLIN-NUMERICAL-REPAIR.md',
        *[ROOT/'tools/research'/n for n in (
            'sampled_physical_allin_evaluation_v2.py','sampled_physical_cpu64_v1.py',
            'sampled_physical_gpu_bank_v2.py','hu_sampled_physical_allin_precision_review_20260923.py',
            'hu_sampled_physical_allin_evaluation_review_v2_20260923.py',
            'hu_sampled_physical_allin_btn_evaluation_v2_20260923.py',
            'hu_sampled_physical_allin_btn_review_v2_20260923.py')]]
    reg.update(id=PREFIX,store=str(STORE),cpu_store=str(CPU_STORE),
        repair_of='sampled-physical-allin-evaluation-v1',
        numerical_precision='float64 inference of exactly widened stored float32 weights',
        repair_note='Same checkpoint, complete bank, seeds, counts, selection rules, sampled estimator and both alpha .025 families. Original failed artifacts preserved; no original test draws or responder. No retraining or tolerance change.',
        inputs={**reg['inputs'],**{str(p):sha(p) for p in paths}},
        cpu_reference_batches={str(offset):dict(folder=str(CPU_STORE/f'train-{offset}'),
            policy_tolerance=1e-4,payoff_tolerance_bb=1e-3) for offset in range(0,256,16)})
    assert reg['config'] == dict(training_deals=8192,evaluation_deals=16384,batch_size=16,minimum_training_deals=16,train_seed=79101,test_seed=79102)
    save(output('registration'),reg)
    print(json.dumps(dict(prepared=True,checkpoint=reg['checkpoint'],config=reg['config'])))


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
    from sampled_physical_allin_evaluation_v2 import batch_values as cpu_values
    from sampled_physical_cpu64_v1 import CpuBank64
    from sampled_physical_checkpoint_v1 import model_document
    from sampled_physical_deals_v1 import PhysicalDeals
    from sampled_physical_checkpoint_v1 import read_object
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    context = Path(reg['context']); objects = Path(reg['objects'])
    checkpoint = json.loads(read_object(objects,reg['checkpoint']))
    bank = CpuBank64([model_document(objects,r) for r in checkpoint['played_bank']], context_source=context.read_text())
    source = PhysicalDeals(context.read_text(),mode='full_deck',seed=reg['config']['train_seed'])
    CPU_STORE.mkdir(exist_ok=False)
    references = {}
    for offset in range(0,256,16):
        batch = dict(format=2,batch_id=f'{PREFIX}-train-{offset}',query_limit=100000,seed=0,
            deals=source.sample(16)['deals'])
        reference = Path(reg['cpu_reference_batches'][str(offset)]['folder'])
        cpu_values(context,batch,objects,checkpoint,reference,guard,bank)
        for name in ('batch.json','queries.json','profiles.json','native.json','summary.json'):
            references[str(reference/name)] = sha(reference/name)
    # Freeze numerical-control artifacts before CUDA training/test evaluation.
    save(output('cpu-control'),dict(artifacts=references,complete_deals=256,
        registration_sha256=sha(output('registration')),production_modified=False))
    result = run(reg, STORE, guard)
    for p,h in references.items(): assert sha(p) == h,p
    verify(reg)
    assert result['terminal']
    comparisons = []
    for offset in reg['cpu_reference_batches']:
        summary = json.loads((STORE / f'{PREFIX}-train-{offset}' / 'summary.json').read_text())
        assert summary['cpu_comparison']['passed']
        comparisons.append(summary['cpu_comparison'])
    result.update(cpu_reference_comparisons=comparisons, cpu_control_sha256=sha(output('cpu-control')), fresh_test_stream=True,
                  backend='cuda persistent bank', registration_sha256=sha(output('registration')))
    save(output('result'), result)


def execute():
    reg = json.loads(output('registration').read_text())
    verify(reg)
    assert idle() and not STORE.exists() and not CPU_STORE.exists() and not LOCK.exists() and not OTHER.exists()
    assert psutil.virtual_memory().available >= reg['host_reserve_bytes']
    assert free_gpu() >= reg['gpu_reserve_bytes']
    assert shutil.disk_usage(STORE.parent).free >= reg['disk_reserve_bytes'] + reg['maximum_store_bytes']
    with LOCK.open('x') as f: f.write(str(os.getpid()))
    child = None; error = None; samples = []; last_resource = 0.
    started = time.monotonic()
    try:
        env = os.environ.copy()
        env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8', OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', PYTHONUNBUFFERED='1')
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
                    used = sum(p.stat().st_size for base in (STORE,CPU_STORE) if base.exists() for p in base.rglob('*') if p.is_file())
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
