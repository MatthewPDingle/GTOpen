"""One bounded synthetic CPU/CUDA implementation control; no poker fitting."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import hashlib
import json
from pathlib import Path
import time
import traceback
import numpy as np
import torch
import stack_equity_priced_model_v1 as candidate
from river_matched_training_pilot_v1 import available, LOCK, OTHER
from bounded_parallel_evaluation_archive_v2 import production_available

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME = 'stack-equity-priced-control-v1'
REG, ATTEMPT, RESULT, FAILURE = (OUT / (NAME + suffix + '.json')
                                for suffix in ('-registration', '-attempt', '-result', '-failure'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def main():
    assert not any(p.exists() for p in (REG, ATTEMPT, RESULT, FAILURE, LOCK, OTHER))
    ready, probe = available()
    if not ready:
        print(json.dumps(dict(deferred=True, scientific_fit_started=False, probe=probe)))
        return
    import psutil
    inputs = {str(p): sha(p) for p in (Path(__file__).resolve(), Path(candidate.__file__).resolve(),
              Path(candidate.__file__).with_name('test_stack_equity_priced_model_v1.py'),
              Path(__file__).with_name('river_matched_training_pilot_v1.py'),
              Path(__file__).with_name('bounded_parallel_evaluation_archive_v2.py'))}
    spec = dict(inputs=inputs, scope='Synthetic implementation qualification only', seeds=[9297401, 9297402],
                batch_sizes=[31, 257, 8192], wall_seconds=120, cuda_bytes=512_000_000,
                float32_absolute_tolerance=2e-6, float64_absolute_tolerance=2e-12,
                new_poker_labels=False, scientific_training=False, accuracy_claim=False)
    write(REG, spec)
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    start = time.monotonic()
    try:
        write(ATTEMPT, dict(pid=os.getpid(), process_created=psutil.Process().create_time(),
                            registration_sha256=sha(REG), admission=probe))
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(spec['cuda_bytes']/torch.cuda.get_device_properties(0).total_memory)

        def guard():
            assert time.monotonic() - start < spec['wall_seconds']
            assert not OTHER.exists() and production_available()
            assert torch.cuda.memory_reserved() <= spec['cuda_bytes']
            assert psutil.virtual_memory().available > 24_000_000_000

        rows = []
        for dtype, tolerance in ((torch.float32, 2e-6), (torch.float64, 2e-12)):
            for seed in spec['seeds']:
                for count in spec['batch_sizes']:
                    guard()
                    cpu = candidate.fresh(seed, scope=candidate.SCOPE)
                    with torch.no_grad():
                        cpu.net[-1].weight.copy_(torch.linspace(-.6, .7, 64).reshape(1, 64))
                        cpu.net[-1].bias.fill_(.13)
                    cpu = cpu.to(dtype=dtype)
                    gpu = candidate.fresh(seed, scope=candidate.SCOPE, dtype=dtype, device='cuda')
                    gpu.load_state_dict(cpu.state_dict())
                    rng = np.random.default_rng(seed + count)
                    x = torch.tensor(rng.uniform(-1, 1, (count, 387)), dtype=dtype)
                    net = np.linspace(3, 190, count)
                    cost = net*np.linspace(.07, .43, count)
                    e = torch.tensor(np.column_stack((np.full(count, 100), net, cost,
                                                      np.arange(count) % 2, cost/net)), dtype=dtype)
                    candidate.validate_economics(e.double().numpy(), terminal_call_confirmed=True) if dtype == torch.float64 else None
                    xc, ec = x.to('cuda'), e.to('cuda')
                    c = cpu.normalized_values(x, e, terminal_call_confirmed=True)
                    g = gpu.normalized_values(xc, ec, terminal_call_confirmed=True)
                    qc, qg = cpu(x), gpu(xc)
                    weights = {k: v.detach().cpu().numpy().copy() for k, v in cpu.state_dict().items()}
                    reference = candidate.numpy_equity(weights, x.double().numpy())
                    errors = dict(equity_cpu_cuda=float((qc-qg.cpu()).abs().max()),
                                  values_cpu_cuda=float((c-g.cpu()).abs().max()),
                                  numpy_cpu=float(np.max(np.abs(reference-qc.detach().numpy()))),
                                  numpy_cuda=float(np.max(np.abs(reference-qg.detach().cpu().numpy()))))
                    assert torch.count_nonzero(c[:, 0]) == 0 and torch.count_nonzero(g[:, 0]) == 0
                    target = torch.linspace(-.7, 1.1, count, dtype=dtype)
                    lc = (c[:, 0].square() + (c[:, 1]-target).square()).mean()/2
                    lg = (g[:, 0].square() + (g[:, 1]-target.to('cuda')).square()).mean()/2
                    lc.backward()
                    lg.backward()
                    errors['gradient_cpu_cuda'] = max(float((a.grad-b.grad.cpu()).abs().max())
                                                     for a, b in zip(cpu.parameters(), gpu.parameters()))
                    errors['loss_cpu_cuda'] = abs(float(lc.detach())-float(lg.detach()))
                    assert all(np.isfinite(v) and v <= tolerance for v in errors.values()), errors
                    rows.append(dict(dtype=str(dtype), seed=seed, rows=count, absolute_tolerance=tolerance, errors=errors))
                    del cpu, gpu, xc, ec, x, e, c, g, qc, qg, lc, lg
        torch.cuda.synchronize()
        guard()
        for path, digest in inputs.items():
            assert sha(path) == digest, path
        write(RESULT, dict(passed=True, registration_sha256=sha(REG), records=rows,
              seconds=time.monotonic()-start, peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
              peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
              runtime=dict(torch=torch.__version__, numpy=np.__version__, cuda=torch.version.cuda,
                           device=torch.cuda.get_device_name()),
              scientific_fit_started=False, new_poker_labels=False, preflop_accuracy_qualified=False))
        print(json.dumps(dict(passed=True, cases=len(rows), seconds=time.monotonic()-start,
                              peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved())))
    except BaseException as error:
        write(FAILURE, dict(error=repr(error), traceback=traceback.format_exc(), retry_allowed=False))
        raise
    finally:
        assert LOCK.read_text() == str(os.getpid())
        LOCK.unlink()


if __name__ == '__main__':
    main()
