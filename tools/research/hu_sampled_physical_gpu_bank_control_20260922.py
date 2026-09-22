"""Bounded equivalence/timing check on old deals, never new evaluation draws."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import numpy as np
import psutil

from loopback_research_validation import idle
from sampled_batch_protocol_v2 import policy_document
from sampled_physical_bank_v1 import average
from sampled_physical_checkpoint_v1 import read_object, model_document
from sampled_physical_gpu_bank_v1 import CudaBank
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-gpu-bank-v1'
STORE = Path('S:/GTOpen-research') / PREFIX
LOCK = ROOT / 'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT / 'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def output(suffix):
    return OUT / (PREFIX + '-' + suffix + '.json')


def verify(reg):
    for path, expected in reg['inputs'].items():
        assert sha(path) == expected, path


def worker(reg):
    import torch
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    assert torch.cuda.is_available()
    started = time.monotonic()
    last_guard = 0.

    def guard():
        nonlocal last_guard
        now = time.monotonic()
        if now - last_guard >= 2:
            assert now - started < reg['maximum_seconds'] and idle()
            assert psutil.virtual_memory().available >= 20_000_000_000
            assert torch.cuda.mem_get_info()[0] >= 3_000_000_000
            assert shutil.disk_usage(STORE.parent).free >= 40_000_000_000
            last_guard = now

    def invoke(name, arguments):
        guard()
        r = subprocess.run([str(ROOT / 'target/release/examples' / (name + '.exe')), *map(str, arguments)],
                           cwd=ROOT, capture_output=True, text=True, timeout=120,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        assert r.returncode == 0, r.stderr[-2000:]
        guard()

    verify(reg)
    STORE.mkdir(exist_ok=False)
    admission = json.loads(Path(reg['source_admission']).read_text())
    objects = Path(admission['objects'])
    checkpoint = json.loads(read_object(objects, admission['checkpoint']))
    played = checkpoint['played_bank']
    weights = [[1.] * len(played)] * 2

    def pairs():
        for reference in played:
            yield model_document(objects, reference)['networks']

    querypath = STORE / 'queries.json'
    invoke('hu_sampled_bank_bridge', ['queries', reg['context'], reg['batch'], '-', querypath])
    queries = json.loads(querypath.read_text())
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    cpu_rng = torch.get_rng_state().clone()
    gpu_rng = torch.cuda.get_rng_state().clone()
    t = time.monotonic()
    cpu, cpu_support = average(queries, pairs(), weights, device='cpu', guard=guard)
    cpu_seconds = time.monotonic() - t
    t = time.monotonic()
    bank = CudaBank(pairs(), weights, models_per_chunk=8, guard=guard)
    torch.cuda.synchronize()
    load_seconds = time.monotonic() - t
    t = time.monotonic()
    gpu, gpu_support = bank.average(queries, guard=guard)
    torch.cuda.synchronize()
    gpu_seconds = time.monotonic() - t
    # Reuse the resident bank with one model per chunk: catches batch-axis,
    # final partial chunk, and inference-kernel dependence on chunk shape.
    bank.chunk = 1
    t = time.monotonic()
    single, single_support = bank.average(queries, guard=guard)
    torch.cuda.synchronize()
    single_seconds = time.monotonic() - t
    policy_error = float(np.max(np.abs(cpu - gpu)))
    chunk_error = float(np.max(np.abs(single - gpu)))
    support_error = float(np.max(np.abs(cpu_support - gpu_support)))
    zero_support_equal = bool(np.array_equal(cpu_support == 0, gpu_support == 0)
                              and np.array_equal(cpu_support == 0, single_support == 0))
    assert policy_error <= reg['policy_tolerance'] and chunk_error <= reg['policy_tolerance']
    assert support_error <= reg['support_tolerance'] and zero_support_equal
    assert torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state())

    roots = [i for i, o in enumerate(queries['observations']) if o['phase'] == 0 and int(o['hi']) == 1]
    assert roots and all(queries['observations'][i]['actor'] == 0 for i in roots)
    profiles = []
    for label, policy in [('cpu', cpu), ('cuda', gpu)]:
        profiles.append(dict(name=label, policies=policy_document(queries, policy)['policies']))
        for action in range(4):
            changed = policy.copy()
            changed[roots] = 0.
            changed[roots, action] = 1.
            profiles.append(dict(name=f'{label}-{action}', policies=policy_document(queries, changed)['policies']))
    profilepath = STORE / 'profiles.json'
    save(profilepath, dict(format=1, context_source=queries['context_source'],
                           batch_source=queries['batch_source'], profiles=profiles))
    nativepath = STORE / 'native.json'
    invoke('hu_sampled_profile_evaluation', [reg['context'], reg['batch'], profilepath, nativepath])
    native = json.loads(nativepath.read_text())
    values = {p['name']: np.asarray([d['values'] for d in p['deals']]) for p in native['profiles']}
    payoff_error = max(float(np.max(np.abs(values['cpu' + s] - values['cuda' + s])))
                       for s in ['', '-0', '-1', '-2', '-3'])
    assert payoff_error <= reg['payoff_tolerance_bb']
    verify(reg)
    save(output('result'), dict(passed=True, played_models=len(played), observations=len(cpu),
         cpu_average_seconds=cpu_seconds, gpu_load_once_seconds=load_seconds,
         gpu_average_seconds=gpu_seconds, gpu_single_chunk_seconds=single_seconds,
         maximum_policy_error=policy_error, maximum_chunk_policy_error=chunk_error,
         maximum_support_error=support_error, zero_support_equal=zero_support_equal,
         maximum_payoff_error_bb=payoff_error, maximum_forward_cashflow_error=native['maximum_forward_cashflow_error'],
         rng_unchanged=True, peak_tensor_bytes=torch.cuda.max_memory_allocated(),
         artifacts={str(p): sha(p) for p in (querypath, profilepath, nativepath)},
         seconds=time.monotonic()-started, accuracy_qualified=False, production_modified=False,
         scope='Inference and payoff equivalence on an old 16-deal fixture with the full frozen played bank; no fresh study outcomes or poker-strength claim. Timing is concurrent with the ongoing two-thread CPU study.'))


def main():
    assert idle() and not LOCK.exists() and not OTHER.exists() and not STORE.exists()
    source = OUT / 'sampled-physical-root-study-v1-admission.json'
    admission = json.loads(source.read_text())
    paths = [*map(Path, admission['inputs']), source, Path(__file__),
             ROOT / 'tools/research/sampled_physical_gpu_bank_v1.py',
             OUT / 'sampled-batch-bridge-v2-batch.json']
    reg = dict(inputs={str(p): sha(p) for p in paths}, source_admission=str(source),
               context=admission['context'], batch=str(paths[-1]), maximum_seconds=600,
               policy_tolerance=1e-4, support_tolerance=1e-3, payoff_tolerance_bb=1e-3,
               source_selection='Frozen final pilot bank; old fixture, never study test draws.',
               production_modified=False)
    save(output('registration'), reg)
    child = None
    error = None
    with LOCK.open('x') as f: f.write(str(os.getpid()))
    started = time.monotonic()
    try:
        env = os.environ.copy()
        env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8', OMP_NUM_THREADS='2', PYTHONUNBUFFERED='1')
        with (OUT / (PREFIX + '.log')).open('x') as log:
            child = subprocess.Popen([sys.executable, str(Path(__file__)), '--worker', str(output('registration'))],
                                     cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2)
                assert time.monotonic()-started < reg['maximum_seconds'] and idle(), 'Deadline or production activity'
        assert child.returncode == 0, 'Read worker log; no automatic retry'
        verify(reg)
        result = json.loads(output('result').read_text())
        assert result['passed']
        for path, expected in result['artifacts'].items(): assert sha(path) == expected
        save(output('review'), dict(passed=True, registration_sha256=sha(output('registration')),
             result_sha256=sha(output('result')), registered_inputs_verified=len(reg['inputs']),
             artifacts_verified=len(result['artifacts']), production_modified=False))
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        if child is not None and child.poll() is None:
            for p in reversed(psutil.Process(child.pid).children(recursive=True)):
                try: p.terminate()
                except psutil.NoSuchProcess: pass
            child.terminate()
            child.wait(timeout=20)
        save(output('status'), dict(state='failed' if error else 'complete', error=error,
             seconds=time.monotonic()-started, exit_code=child.returncode if child else None,
             production_modified=False))
        assert LOCK.read_text().strip() == str(os.getpid())
        LOCK.unlink()


if __name__ == '__main__':
    if '--worker' in sys.argv: worker(json.loads(Path(sys.argv[-1]).read_text()))
    else: main()
