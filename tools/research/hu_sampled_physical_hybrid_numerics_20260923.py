"""Diagnose the failed full-bank numerical control without drawing new deals.

Reconstruct both saved averages from per-generation scores. Double-precision
scores on the discrepant row explain rounding sensitivity, not poker quality.
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
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from loopback_research_validation import idle
from sampled_physical_hybrid_checkpoint_v1 import read_object, model_document
from sampled_physical_hybrid_gpu_bank_v1 import HybridCudaBank
from sampled_physical_bank_v1 import histories
from sampled_physical_preflop_table_v1 import Table
from sampled_batch_model_v1 import predict

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-hybrid-numerics-v1'
SOURCE = 'sampled-physical-hybrid-evaluation-v1'
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def probabilities(scores, observations):
    scores = np.asarray(scores, dtype=np.float64)
    legal = np.arange(4)[None, :] < np.asarray([o['n'] for o in observations])[:, None]
    p = np.maximum(scores, 0.)*legal
    sums = p.sum(1); positive = sums > 0
    p[positive] /= sums[positive, None]
    for i in np.flatnonzero(~positive):
        p[i, int(np.argmax(scores[i, :observations[i]['n']]))] = 1.
    return p


def main():
    import torch
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    started = time.monotonic(); last = 0.

    def guard():
        nonlocal last
        now = time.monotonic()
        if now-last >= 2:
            assert now-started < 600 and idle()
            assert psutil.virtual_memory().available >= 20_000_000_000
            assert torch.cuda.mem_get_info()[0] >= 3_000_000_000
            last = now

    guard()
    assert not LOCK.exists() and not OTHER.exists()
    regpath = OUT/f'{SOURCE}-registration.json'
    statuspath = OUT/f'{SOURCE}-status.json'
    reg = json.loads(regpath.read_text()); status = json.loads(statuspath.read_text())
    assert status['state'] == 'stopped' and status['exit_code'] == 1
    for p, h in reg['inputs'].items(): assert sha(p) == h, p
    store = Path(reg['store'])
    assert not list(store.glob('*-test-*')) and not (store/'response.json').exists()
    failures = [f for f in store.glob('*-train-*') if (f/'profiles.json').exists() and not (f/'summary.json').exists()]
    assert len(failures) == 1
    folder = failures[0]; offset = folder.name.rsplit('-', 1)[-1]
    reference = Path(reg['cpu_reference_batches'][offset]['folder'])
    queries = json.loads((folder/'queries.json').read_text())
    assert queries['observations'] == json.loads((reference/'queries.json').read_text())['observations']
    obs = queries['observations']; context = queries['context_source']
    old = json.loads((reference/'profiles.json').read_text())['profiles'][0]['policies']
    new = json.loads((folder/'profiles.json').read_text())['profiles'][0]['policies']
    expected = [np.asarray([r['probabilities'] for r in rows]) for rows in (old, new)]
    error = np.max(np.abs(expected[0]-expected[1]), axis=1)
    target = int(np.argmax(error)); assert error[target] > 1e-4
    history = histories(obs); indices = sorted({target, *[i for i, _ in history[target]]})
    objects = Path(reg['objects']); checkpoint = json.loads(read_object(objects, reg['checkpoint']))
    models = [model_document(objects, r, context_source=context) for r in checkpoint['played_bank']]
    assert len(models) == 78
    paths = [Path(__file__), regpath, statuspath, *[folder/n for n in ('queries.json', 'profiles.json', 'native.json')],
             *[reference/n for n in ('queries.json', 'profiles.json', 'native.json')],
             *[ROOT/'tools/research'/n for n in ('sampled_physical_hybrid_gpu_bank_v1.py',
                 'sampled_physical_gpu_bank_v1.py', 'sampled_batch_model_v1.py',
                 'sampled_physical_preflop_table_v1.py', 'sampled_physical_bank_v1.py')]]
    registration = dict(inputs={str(p): sha(p) for p in paths}, source=SOURCE,
        failed_batch=str(folder), selected_row=target, inspected_rows=indices,
        scope='Numerical diagnosis of the existing failed control only; no new chance draws, training, test outcomes, tolerance changes or policy promotion.')
    regout = OUT/f'{PREFIX}-registration.json'; save(regout, registration)
    with LOCK.open('x') as stream: stream.write(str(os.getpid()))
    try:
        bank = HybridCudaBank(models, [[1.]*78]*2, context_source=context, guard=guard)
        x = np.zeros((len(obs), 269), np.float32)
        actors = np.asarray([o['actor'] for o in obs])
        for i, o in enumerate(obs): x[i, o['active_features']] = 1.
        features = torch.as_tensor(x, device='cuda')
        ids = [torch.as_tensor(np.flatnonzero(actors == p), device='cuda') for p in (0, 1)]
        gpu = np.empty((78, len(obs), 4), dtype=np.float32)
        with torch.no_grad():
            for start in range(0, 78, bank.chunk):
                guard(); stop = min(78, start+bank.chunk)
                scores = torch.zeros((stop-start, len(obs), 4), dtype=torch.float32, device='cuda')
                for player in (0, 1):
                    y = features[ids[player]].unsqueeze(0).expand(stop-start, -1, -1)
                    for layer in range(3):
                        w = bank.parameters[f'w{layer}'][start:stop, player]
                        b = bank.parameters[f'b{layer}'][start:stop, player]
                        y = torch.bmm(y, w.transpose(1, 2))+b.unsqueeze(1)
                        if layer != 2: y = torch.relu(y)
                    scores[:, ids[player]] = y
                gpu[start:stop] = scores.cpu().numpy()
        numerators = [np.zeros((len(obs), 4)) for _ in range(2)]
        denominators = [np.zeros(len(obs)) for _ in range(2)]
        rows = []
        for generation, model in enumerate(models):
            guard(); cpu, cp = predict(obs, model['networks'], 'cpu')
            gp = probabilities(gpu[generation], obs)
            for player, table in enumerate(model['preflop_tables']):
                if table is not None:
                    t = Table(table, context); cp, _ = t.apply(obs, cp); gp, _ = t.apply(obs, gp)
            local = []
            for i in indices:
                net = model['networks'][obs[i]['actor']]; y = x[i].astype(np.float64)
                for layer, shape in enumerate(((64, 269), (64, 64), (4, 64))):
                    w = np.asarray(net[f'w{layer}'], dtype=np.float32).astype(np.float64).reshape(shape)
                    b = np.asarray(net[f'b{layer}'], dtype=np.float32).astype(np.float64)
                    y = w@y+b
                    if layer != 2: y = np.maximum(y, 0.)
                local.append(dict(index=i, cpu_scores=cpu[i].tolist(), gpu_scores=gpu[generation, i].astype(float).tolist(),
                    double_scores=y.tolist(), cpu_probability=cp[i].tolist(), gpu_probability=gp[i].tolist(),
                    double_neural_probability=probabilities(y[None, :], [obs[i]])[0].tolist()))
            reaches = []
            for k, p in enumerate((cp, gp)):
                reach = np.ones(len(obs))
                for i, prior in enumerate(history):
                    for ancestor, action in prior: reach[i] *= p[ancestor, action]
                numerators[k] += p*reach[:, None]; denominators[k] += reach
                reaches.append(float(reach[target]))
            rows.append(dict(generation=generation, target_own_reaches=reaches, observations=local))
        rebuilt = [num/den[:, None] for num, den in zip(numerators, denominators)]
        reconstruction_errors = [float(np.max(np.abs(p-e))) for p, e in zip(rebuilt, expected)]
        assert max(reconstruction_errors) < 1e-10
        for p, h in registration['inputs'].items(): assert sha(p) == h, p
        guard()
        result = dict(passed=True, registration_sha256=sha(regout), training_batch_offset=int(offset),
            observations=len(obs), maximum_saved_policy_error=float(error.max()),
            rows_over_registered_policy_tolerance=int(np.count_nonzero(error > 1e-4)),
            reconstruction_errors=reconstruction_errors, target_observation=obs[target],
            maximum_error_by_phase={str(p): float(error[[o['phase'] == p for o in obs]].max()) for p in range(4)},
            target_cpu_average=expected[0][target].tolist(), target_gpu_average=expected[1][target].tolist(),
            generations=rows, held_out_deals_generated=0, production_modified=False,
            seconds=time.monotonic()-started, scope=registration['scope'])
        save(OUT/f'{PREFIX}-result.json', result)
        print(json.dumps({k: v for k, v in result.items() if k not in ('generations', 'target_observation')}))
    finally:
        assert LOCK.read_text() == str(os.getpid())
        LOCK.unlink()


if __name__ == '__main__': main()
