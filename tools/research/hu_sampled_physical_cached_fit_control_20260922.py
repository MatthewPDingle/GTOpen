"""Compare prepared CUDA fitting with the frozen fitter on the actual reservoirs."""
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
from sampled_physical_checkpoint_v1 import read_object, restore_checkpoint, model_document
from sampled_physical_fit_v1 import grouped_rows, fresh_network, objective, fit as reference_fit
from sampled_physical_fit_cuda_cached_v1 import PreparedObjective, fit as cached_fit
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-cached-fit-v1'
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def output(suffix): return OUT/(PREFIX+'-'+suffix+'.json')


def verify(reg):
    for path, expected in reg['inputs'].items(): assert sha(path)==expected, path


def worker(reg):
    import torch
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    assert torch.cuda.is_available()
    started = time.monotonic()
    last = 0.

    def guard():
        nonlocal last
        now = time.monotonic()
        if now-last >= 2:
            assert now-started < reg['maximum_seconds'] and idle()
            assert psutil.virtual_memory().available >= 20_000_000_000
            assert torch.cuda.mem_get_info()[0] >= 3_000_000_000
            last = now

    verify(reg)
    guard()
    source = Path(reg['context']).read_text()
    objects = Path(reg['objects'])
    checkpoint = json.loads(read_object(objects, reg['checkpoint']))
    restored = restore_checkpoint(objects, reg['checkpoint'], context_source=source, config=checkpoint['config'])
    published = model_document(objects, checkpoint['next_model'])['networks']
    metrics = json.loads(Path(reg['source_metrics']).read_text())['fits']
    rows = []
    weights = []
    torch.cuda.reset_peak_memory_stats()
    for player, reservoir in enumerate(restored['reservoirs']):
        guard()
        metric = metrics[player]
        assert metric['player']==player and metric['steps']==512 and metric['chunk_size']==4096
        grouped = grouped_rows(reservoir)
        a = fresh_network(metric['seed']).cuda()
        b = fresh_network(metric['seed']).cuda()
        cache = PreparedObjective(grouped, next(b.parameters()).device, guard)
        cpu_rng = torch.get_rng_state().clone()
        gpu_rng = torch.cuda.get_rng_state().clone()
        loss_a = objective(a, grouped, 4096, guard, backward=True)
        loss_b = cache.objective(b, 4096, guard, backward=True)
        gradient_error = max(float((p.grad-q.grad).abs().max()) for p,q in zip(a.parameters(),b.parameters()))
        assert abs(loss_a-loss_b) <= reg['loss_tolerance']
        assert gradient_error <= reg['gradient_tolerance']
        torch.optim.Adam(a.parameters(), lr=metric['learning_rate']).step()
        torch.optim.Adam(b.parameters(), lr=metric['learning_rate']).step()
        step_error = max(float((p-q).abs().max()) for p,q in zip(a.parameters(),b.parameters()))
        assert step_error <= reg['parameter_tolerance']
        assert torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state())
        del a, b, cache, grouped
        arguments = dict(seed=metric['seed'], steps=512, device='cuda', chunk_size=4096,
                         learning_rate=metric['learning_rate'], guard=guard)
        torch.cuda.synchronize()
        t = time.monotonic()
        ref, ref_metric = reference_fit(reservoir, **arguments)
        torch.cuda.synchronize()
        ref_seconds = time.monotonic()-t
        t = time.monotonic()
        prepared, prepared_metric = cached_fit(reservoir, **arguments)
        torch.cuda.synchronize()
        prepared_seconds = time.monotonic()-t
        reference_error = max(float(np.max(np.abs(np.asarray(ref[k])-published[player][k]))) for k in ref)
        weight_error = max(float(np.max(np.abs(np.asarray(ref[k])-prepared[k]))) for k in ref)
        loss_error = abs(ref_metric['normalized_grouped_loss_after']-prepared_metric['normalized_grouped_loss_after'])
        assert reference_error <= reg['parameter_tolerance'], ('Original fit did not reproduce published model', reference_error)
        assert weight_error <= reg['parameter_tolerance'], ('Cached trajectory changed', weight_error)
        assert loss_error <= reg['loss_tolerance']
        assert torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state())
        for key in ('retained_examples','grouped_observations','legal_target_count','advantage_scale','normalized_within_observation_variance'):
            assert ref_metric[key]==prepared_metric[key]==metric[key], key
        rows.append(dict(player=player, retained_examples=reservoir.size, initial_loss_error=abs(loss_a-loss_b),
                         maximum_gradient_error=gradient_error, first_step_parameter_error=step_error,
                         published_model_error=reference_error, cached_reference_parameter_error=weight_error,
                         final_loss_error=loss_error, reference_seconds=ref_seconds, cached_seconds=prepared_seconds,
                         speedup=ref_seconds/prepared_seconds, reference_metric=ref_metric, cached_metric=prepared_metric))
        weights.append(dict(reference=ref,cached=prepared))
    save(output('weights'),weights)
    verify(reg)
    save(output('result'),dict(passed=True, rows=rows, weights_sha256=sha(output('weights')),
         peak_tensor_bytes=torch.cuda.max_memory_allocated(), seconds=time.monotonic()-started,
         rng_unchanged=True, source_generation=checkpoint['next_model']['generation'],
         algorithm_unchanged=True, new_training_deals=0, production_modified=False,
         scope='Same final pilot reservoirs, seeds, 512 full-gradient Adam steps and 4096-row chunk order; reference and cached trajectories compared with the published unused model. This checks execution fidelity and timing, not improved poker strength or larger-data convergence.'))


def main():
    assert idle() and not LOCK.exists() and not OTHER.exists()
    admission_path = OUT/'sampled-physical-root-study-gpu-v1-registration.json'
    admission = json.loads(admission_path.read_text())
    verify(admission)
    objects = Path(admission['objects'])
    checkpoint = json.loads(read_object(objects, admission['checkpoint']))
    n = checkpoint['completed_iterations']
    metricpath = objects.parent/f'iteration-{n:04d}'/'metrics.json'
    paths = [*map(Path,admission['inputs']),admission_path,metricpath,Path(__file__),
             ROOT/'tools/research/sampled_physical_fit_v1.py',
             ROOT/'tools/research/sampled_physical_fit_cuda_cached_v1.py',
             objects/admission['checkpoint']['file'],
             *[objects/r['file'] for r in checkpoint['reservoirs']]]
    reg = dict(inputs={str(p):sha(p) for p in paths},objects=str(objects),context=admission['context'],
               checkpoint=admission['checkpoint'],source_metrics=str(metricpath),maximum_seconds=600,
               loss_tolerance=1e-7,gradient_tolerance=1e-7,parameter_tolerance=1e-7,
               changes='Cache visible feature, target and count-weight tensors on CUDA. Preserve chunk size/order, seeds, objective and optimizer steps. No new chance draws.',
               production_modified=False)
    save(output('registration'),reg)
    child=None;error=None
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    started=time.monotonic()
    try:
        env=os.environ.copy()
        env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',OMP_NUM_THREADS='2',PYTHONUNBUFFERED='1')
        with (OUT/(PREFIX+'.log')).open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__)),'--worker',str(output('registration'))],
                cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2)
                assert time.monotonic()-started<reg['maximum_seconds'] and idle(),'Deadline or production activity'
        assert child.returncode==0,'Read worker log; no automatic retry'
        verify(reg)
        result=json.loads(output('result').read_text())
        assert result['passed'] and result['weights_sha256']==sha(output('weights'))
        save(output('review'),dict(passed=True,registration_sha256=sha(output('registration')),
             result_sha256=sha(output('result')),registered_inputs_verified=len(reg['inputs']),production_modified=False))
    except Exception as exc:
        error=str(exc)
        raise
    finally:
        if child is not None and child.poll() is None:
            for p in reversed(psutil.Process(child.pid).children(recursive=True)):
                try:p.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20)
        save(output('status'),dict(state='failed' if error else 'complete',error=error,
             seconds=time.monotonic()-started,exit_code=child.returncode if child else None,production_modified=False))
        assert LOCK.read_text().strip()==str(os.getpid())
        LOCK.unlink()


if __name__=='__main__':
    if '--worker' in sys.argv:worker(json.loads(Path(sys.argv[-1]).read_text()))
    else:main()
