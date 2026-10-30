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
from sampled_physical_allin_evaluation_v1 import ROOT, sha, save, run

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-allin-evaluation-v1'
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
    from sampled_physical_checkpoint_v1 import read_object, verify_bank
    assert idle() and not STORE.exists() and not CPU_STORE.exists()
    train_reg_path = OUT/'sampled-physical-allin-pilot-v1-registration.json'
    train_reg = json.loads(train_reg_path.read_text())
    for p,h in train_reg['inputs'].items(): assert sha(ROOT/p) == h,p
    review_path = OUT/'sampled-physical-allin-pilot-v1-independent-review.json'
    review = json.loads(review_path.read_text())
    assert review['passed'] and review['terminal_complete'] and review['completed_iterations'] == 78
    assert review['source_registration_sha256'] == sha(train_reg_path)
    for p,h in review['evidence_hashes'].items(): assert sha(p) == h,p
    objects = Path(train_reg['store'])/'checkpoint-objects'
    checkpoint = json.loads(read_object(objects,review['checkpoint']))
    assert checkpoint['completed_iterations'] == 78
    verify_bank(objects,78,checkpoint['played_bank'],checkpoint['next_model'])
    old_path = OUT/'sampled-physical-root-study-gpu-v1-registration.json'
    old = json.loads(old_path.read_text()); verify(old)
    control_path = OUT/'sampled-physical-gpu-bank-v1-independent-review.json'
    control = json.loads(control_path.read_text()); assert control['passed']
    paths = [*map(Path,old['inputs']),old_path,control_path,review_path,train_reg_path,
        *[ROOT/p for p in train_reg['inputs']],Path(__file__),
        ROOT/'tools/research/hu_sampled_physical_allin_evaluation_review_20260923.py',
        objects/review['checkpoint']['file'],
        *[objects/r['file'] for r in [*checkpoint['played_bank'],checkpoint['next_model']]]]
    reg = dict(id=PREFIX,context=old['context'],objects=str(objects),checkpoint=review['checkpoint'],
        inputs={str(p):sha(p) for p in paths},store=str(STORE),cpu_store=str(CPU_STORE),
        config=dict(old['config'],train_seed=79101,test_seed=79102),selected_iterations=78,
        training_registration=str(train_reg_path),training_review=str(review_path),
        maximum_seconds=7200,host_reserve_bytes=20_000_000_000,gpu_reserve_bytes=3_000_000_000,
        disk_reserve_bytes=40_000_000_000,maximum_store_bytes=30_000_000_000,
        device='cuda',threads=2,models_per_chunk=8,
        cpu_reference_batches={str(offset):dict(folder=str(CPU_STORE/f'train-{offset}'),
            policy_tolerance=1e-4,payoff_tolerance_bb=1e-3) for offset in range(0,256,16)},
        source_selection='Exactly 78 complete dense-training iterations, all played generations 0..77; next model excluded. No test-dependent selection.',
        btn_family_error_probability=.025,
        additional_gate='Before GPU evaluation, independently generate CPU reference policies and payoffs for the first 256 response-training deals from the same frozen candidate. Compare all rows before creating the held-out stream. References are numerical controls, not independent strength evidence.',
        interval='One final look at 16384 paired deals; 2.5% family error across five BB root comparisons, reserving 2.5% for three predeclared BTN-vs-jam comparisons. No intermediate significance stop.',comparisons=old['comparisons'],chance=old['chance'],
        arithmetic=old['arithmetic'],
        stopping='All fixed counts or two-hour total ceiling including CPU numerical controls; stop on production activity, resources, integrity or numerical failure. No retry or partial quality claim.',
        scope='Fresh-deal BB root-deviation test of the conditional-all-in physical candidate. Fixed incoming ranges and later behavior; limited betting menu, earlier folded cards omitted. New chance seeds relative to the inspected pilot evaluation. No BR upper bound, joint-equilibrium or Wizard-equivalence certificate.',
        production_modified=False)
    assert reg['config'] == dict(training_deals=8192,evaluation_deals=16384,batch_size=16,minimum_training_deals=16,train_seed=79101,test_seed=79102)
    save(output('registration'),reg)
    print(json.dumps(dict(prepared=True,config=reg['config'],checkpoint=reg['checkpoint'],registration=str(output('registration')))))


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
    from sampled_physical_root_evaluation_v1 import batch_values as cpu_values
    from sampled_physical_deals_v1 import PhysicalDeals
    from sampled_physical_checkpoint_v1 import read_object
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    context = Path(reg['context']); objects = Path(reg['objects'])
    checkpoint = json.loads(read_object(objects,reg['checkpoint']))
    source = PhysicalDeals(context.read_text(),mode='full_deck',seed=reg['config']['train_seed'])
    CPU_STORE.mkdir(exist_ok=False)
    references = {}
    for offset in range(0,256,16):
        batch = dict(format=2,batch_id=f'{PREFIX}-train-{offset}',query_limit=100000,seed=0,
            deals=source.sample(16)['deals'])
        reference = Path(reg['cpu_reference_batches'][str(offset)]['folder'])
        cpu_values(context,batch,objects,checkpoint,reference,guard)
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
